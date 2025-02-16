import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
from tqdm import tqdm
import json
from pathlib import Path
import itertools

GENIUS_API_TOKEN = 'your-token-here'
ARTIST_NAME = 'Drake'

# get artist object from genius API
def get_artist_object(artist_name: str, page: int):
    return requests.get(
        'https://api.genius.com/search',
        params={'q': artist_name, 'per_page': 5, 'page': page},
        headers={'Authorization': f'Bearer {GENIUS_API_TOKEN}'}
    )


# get song url's from artist object
def get_song_urls(artist_name: str, song_cap: int) -> list[str]:
    songs = []
    artist_name = artist_name.lower()
    
    for page in itertools.count(1):  # infinite counter starting at 1
        response = get_artist_object(artist_name, page).json()
        
        # filter songs by matching artist name and extract URLs
        new_songs = [
            hit['result']['url'] 
            for hit in response['response']['hits']
            if artist_name in hit['result']['primary_artist']['name'].lower()
        ]
        
        songs.extend(new_songs[:song_cap - len(songs)])
        
        if len(songs) >= song_cap:
            songs = songs[:song_cap]  # ensure cap is not exceeded
            break
            
    print(f'Found {len(songs)} songs by {artist_name}')
    return songs

# # test
# song_urls = get_song_urls('Drake', 5)
# print(song_urls)

# scrape lyrics from a song URL
def scrape_song_lyrics(url: str) -> dict:
    def clean_text(text: str) -> str:
        text = text.strip()
        if text and not text[-1] in '.!?":;,':
            text += '.'
        return text
    
    def extract_metadata(html: BeautifulSoup) -> tuple[str, str, str, int]:
        # title
        title_h1 = html.find('h1', class_=lambda x: x and x.startswith('SongHeader'))
        title = title_h1.get_text().strip().replace('\u2019', "'") if title_h1 else None
        
        # album
        album_link = html.find('a', {'href': '#primary-album'})
        album = album_link.text.strip() if album_link else None
        
        # release date
        date, year = None, None
        if meta_div := html.find('div', class_=lambda x: x and x.startswith('MetadataStats')):
            if date_span := meta_div.find('span', class_=lambda x: x and x.startswith('LabelWithIcon')):
                date = date_span.get_text().strip()
                try:
                    year = int(date.split(', ')[-1])
                except (ValueError, IndexError):
                    pass
                    
        return title, album, date, year

    
    def process_span_content(span: BeautifulSoup) -> list[str]:
        lines = []
        current_line = ''
        
        for content in span.contents:
            if content.name == 'br':
                if current_line:
                    lines.append(clean_text(current_line))
                    current_line = ''
            elif content.name == 'i' or isinstance(content, str):
                current_line += content.get_text().strip() + ' '
        
        if current_line:
            lines.append(clean_text(current_line))
            
        return [line for line in lines if line and not (line.startswith('[') and line.endswith(']'))]

    # main scraping logic
    html = BeautifulSoup(requests.get(url).text, 'html.parser')
    title, album, release_date, release_year = extract_metadata(html)
    
    lyrics_sections = []
    current_section = []
    is_section_marker = False
    
    for lyrics_div in html.find_all('div', attrs={'data-lyrics-container': 'true'}):
        for element in lyrics_div.children:
            if isinstance(element, str):
                text = element.strip()
                if text.startswith('[') and text.endswith(']'):
                    if current_section:
                        lyrics_sections.append(current_section)
                        current_section = []
                    continue
                elif text.startswith('['):
                    is_section_marker = True
                    if current_section:
                        lyrics_sections.append(current_section)
                        current_section = []
                    continue
                elif ']' in text:
                    is_section_marker = False
                    continue
                elif text and not is_section_marker:
                    current_section.append(clean_text(text))
            
            elif element.name == 'a':
                if span := element.find('span', class_=lambda x: x and x.startswith('ReferentFragment-desktop')):
                    if span.get_text().strip().startswith('['):
                        if current_section:
                            lyrics_sections.append(current_section)
                            current_section = []
                        continue
                    
                    current_section.extend(process_span_content(span))
    
    if current_section:
        lyrics_sections.append(current_section)
    
    return {
        "title": title,
        "release_date": release_date,
        "release_year": release_year,
        "album": album,
        "lyrics": lyrics_sections
    }

# # test 
# result = scrape_song_lyrics('https://genius.com/Drake-gods-plan-lyrics')
# print(json.dumps(result, indent=2))

# fetch & scrape list of songs
def fetch_all_songs(limit: int = 5) -> List[Dict[str, Any]]:
    def extract_title_from_url(url: str, artist_name: str) -> str:
        # clean song title from url
        return (url.split('/')[-1]
                .replace('-lyrics', '')
                .replace('-', ' ')
                .replace(artist_name, '')
                .strip())

    # fetch song URLs
    print(f"Fetching song URLs for {ARTIST_NAME}...")
    songs = get_song_urls(ARTIST_NAME, limit)
    
    all_songs = []
    
    # process each song with progress bar
    for url in tqdm(songs, desc="Fetching lyrics"):
        try:
            song_data = scrape_song_lyrics(url)
            
            song_object = {
                "url": url,
                **song_data  # unpack song data directly
            }
            
            all_songs.append(song_object)
            
            # rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"\nError fetching {url}: {e}")
            continue
    
    print(f"\nSuccessfully fetched {len(all_songs)} out of {len(songs)} songs")
    return all_songs

def save_to_json(data, filename="songs.json"):
    # write to JSON file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(data)} songs to {filename}")

if __name__ == "__main__":
    print("Starting to fetch songs...")
    all_songs = fetch_all_songs()
    save_to_json(all_songs)
    print("Done!")

