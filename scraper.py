import requests
from bs4 import BeautifulSoup
import json
import time
import re


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


def get_wikipedia_image(player_name):
    """
    Fetches the full original image from Wikipedia by:
    1. Searching for the player's Wikipedia page
    2. Getting the main image filename from the page
    3. Fetching the actual full-resolution file URL from Wikimedia Commons
    This gives us the real original upload, not a thumbnail.
    """
    session = requests.Session()
    session.headers.update({'User-Agent': 'FootballHigherLower/1.0 (educational project)'})

    # Step 1: find the Wikipedia page
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

    # Step 2: get the image filename used on that page
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
            # Skip icons, flags, logos — we want a real photo
            lower = title.lower()
            if any(skip in lower for skip in ['flag', 'icon', 'logo', 'kit', 'shield', 'coat', 'svg', 'map']):
                continue
            if title.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_filename = title
                break
        if image_filename:
            break

    if not image_filename:
        return None

    # Step 3: get the actual full-resolution URL from Wikimedia
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
            return info[0]['url']  # direct full-res Wikimedia URL

    return None


def get_transfermarkt_image(row):
    """Fallback: Transfermarkt player image."""
    img_tag = row.find('img', {'class': 'bilderrahmen-fixed'})
    if img_tag and 'src' in img_tag.attrs:
        return (img_tag['src']
                .replace('/small/', '/big/')
                .replace('/tiny/', '/big/'))
    return ""


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
    print(f"Found {len(rows)} players. Fetching images...\n")

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
            image_url = get_wikipedia_image(name)

            if image_url:
                print(f"  ✓ Wikipedia: {image_url[:70]}...")
            else:
                print(f"  ! Falling back to Transfermarkt image")
                image_url = get_transfermarkt_image(row)

            players_list.append({
                "name": name,
                "value": numeric_value,
                "display_value": raw_value,
                "image": image_url
            })

            time.sleep(0.5)  # be polite to Wikipedia

        except Exception as e:
            print(f"  Error on row: {e}")
            continue

    with open('players.json', 'w', encoding='utf-8') as f:
        json.dump(players_list, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Done! Saved {len(players_list)} players to players.json")


if __name__ == "__main__":
    scrape_players()