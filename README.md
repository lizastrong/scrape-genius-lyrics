# Genius Lyrics Scraper

A Python script to fetch and scrape song lyrics from Genius.com for any artist. The script uses the Genius API to find songs and then scrapes the lyrics and metadata for each song.

## Features

- Fetch songs by artist name using the Genius API
- Scrape detailed song information including:
  - Title
  - Album
  - Release date
  - Complete lyrics with section preservation
- JSON output for easy data processing

## Prerequisites

- Python3
- A Genius API access token

## Installation

1. Clone this repository:
```bash
git clone [repository-url]
cd genius-lyrics-scraper
```

2. Install required packages:
```bash
pip install requests beautifulsoup4 tqdm
```

## Getting a Genius API Token

1. Create an account on [Genius](https://genius.com)
2. Visit the [API Clients](https://genius.com/api-clients) page
3. Create a new API Client
4. Copy your `Client Access Token`

## Configuration

1. Open the script and replace `'your-token-here'` with your Genius API token:
```python
GENIUS_API_TOKEN = 'your-token-here'
```

2. Set the artist name by modifying:
```python
ARTIST_NAME = 'Drake'  # Replace with your desired artist
```

## Usage

Run the script:
```bash
python lyrics_scraper.py
```

The script will:
1. Fetch song URLs for the specified artist
2. Scrape lyrics and metadata for each song
3. Save the results to `songs.json`

## Output Format

The script generates a JSON file with the following structure:

```json
[
  {
    "url": "https://genius.com/Drake-gods-plan-lyrics",
    "title": "God's Plan",
    "release_date": "January 19, 2018",
    "release_year": 2018,
    "album": "Scorpion",
    "lyrics": [
      ["First verse lines..."],
      ["Chorus lines..."],
      ["Second verse lines..."]
    ]
  }
]
```

## Customization

- Modify the `song_cap` parameter in `get_song_urls()` to change the number of songs to fetch
