import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
from pathlib import Path


# Folder where player images will be saved
IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)


def clean_value(value_str):
    try:
        cleaned = value_str.replace('€', '').strip()
        if 'm' in cleaned:
            return int(float(cleaned.replace('m', '')) * 1_000_000)
        elif 'k' in cleaned:
            return int(float(cleaned.replace('k', '')) * 1_000)
        return 0
    except ValueError:
        return 0


def safe_filename(name):
    """Convert player name to a safe filename."""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name) + ".jpg"


def get_wikipedia_image_url(player_name):
    """Find the full-resolution image URL from Wikipedia."""
    session = requests.Session()
    session.headers.update({'User-Agent': 'FootballHigherLower/1.0 (educational project)'})

    # Step 1: find the page
    search_resp = session.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "list": "search",
            "srsearch": f"{player_name} footballer",
            "format": "json",
            "srlimit": 3,
        },
        timeout=10
    )
    results = search_resp.json().get('query', {}).get('search', [])
    if not results:
        return None

    page_title = results[0]['title']

    # Step 2: get image filenames on that page
    images_resp = session.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "titles": page_title,
            "prop": "images",
            "format": "json",
            "imlimit": 20,
        },
        timeout=10
    )
    pages = images_resp.json().get('query', {}).get('pages', {})
    image_filename = None
    for page in pages.values():
        for img in page.get('images', []):
            title = img['title']
            lower = title.lower()
            if any(skip in lower for skip in ['flag', 'icon', 'logo', 'kit', 'shield', 'coat', 'map', 'blank']):
                continue
            if lower.endswith(('.jpg', '.jpeg', '.png')):
                image_filename = title
                break
        if image_filename:
            break

    if not image_filename:
        return None

    # Step 3: get the actual full-resolution URL
    file_resp = session.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "titles": image_filename,
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
        },
        timeout=10
    )
    file_pages = file_resp.json().get('query', {}).get('pages', {})
    for page in file_pages.values():
        info = page.get('imageinfo', [])
        if info:
            return info[0]['url']

    return None


def download_image(url, player_name):
    """
    Download image from URL and save it locally.
    Returns the local file path string, or None on failure.
    """
    filename = safe_filename(player_name)
    filepath = IMAGES_DIR / filename

    # Skip if already downloaded
    if filepath.exists():
        print(f"  ✓ Already downloaded: {filename}")
        return str(filepath)

    try:
        headers = {'User-Agent': 'FootballHigherLower/1.0'}
        resp = requests.get(url, headers=headers, timeout=15, stream=True)
        if resp.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            size_kb = filepath.stat().st_size // 1024
            print(f"  ✓ Downloaded {filename} ({size_kb} KB)")
            return str(filepath)
        else:
            print(f"  ! HTTP {resp.status_code} for {url}")
    except Exception as e:
        print(f"  ! Download error: {e}")

    return None


def scrape_players():
    url = 'https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print("Fetching player list from Transfermarkt...")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    players_list = []

    table = soup.find('table', {'class': 'items'})
    if not table:
        print("Could not find the player table.")
        return

    rows = table.find('tbody').find_all('tr', recursive=False)
    print(f"Found {len(rows)} players. Fetching & downloading images...\n")

    for i, row in enumerate(rows):
        try:
            name_tag = row.find('td', {'class': 'hauptlink'})
            name = name_tag.text.strip() if name_tag else "Unknown"

            value_tag = row.find('td', {'class': 'rechts hauptlink'})
            raw_value = value_tag.text.strip() if value_tag else "€0.00m"
            numeric_value = clean_value(raw_value)

            if name == "Unknown" or numeric_value == 0:
                continue

            print(f"[{i+1}] {name} ({raw_value})")

            # Get URL then download it
            image_url = get_wikipedia_image_url(name)
            local_path = None

            if image_url:
                local_path = download_image(image_url, name)

            # Fallback: Transfermarkt image
            if not local_path:
                img_tag = row.find('img', {'class': 'bilderrahmen-fixed'})
                if img_tag and 'src' in img_tag.attrs:
                    tm_url = (img_tag['src']
                              .replace('/small/', '/big/')
                              .replace('/tiny/', '/big/'))
                    local_path = download_image(tm_url, name)

            players_list.append({
                "name": name,
                "value": numeric_value,
                "display_value": raw_value,
                # Store local path for Streamlit to serve
                "image": local_path or ""
            })

            time.sleep(0.5)

        except Exception as e:
            print(f"  Error on row: {e}")
            continue

    with open('players.json', 'w', encoding='utf-8') as f:
        json.dump(players_list, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Done! Saved {len(players_list)} players to players.json")
    print(f"   Images saved in: {IMAGES_DIR.resolve()}")


if __name__ == "__main__":
    scrape_players()