import requests
from bs4 import BeautifulSoup
import json
import time
import re


def clean_value(value_str):
    """Converts a string like '€180.00m' into a raw integer like 180000000."""
    try:
        cleaned = value_str.replace('€', '').strip()
        if 'm' in cleaned:
            number = float(cleaned.replace('m', '')) * 1000000
        elif 'k' in cleaned:
            number = float(cleaned.replace('k', '')) * 1000
        else:
            number = 0
        return int(number)
    except ValueError:
        return 0


def get_wikipedia_image(player_name):
    """
    Fetches a large portrait image from Wikipedia.
    - First searches for the correct page title
    - Then grabs the main article image at 800px width
    This keeps the full portrait aspect ratio instead of a pre-cropped thumb.
    """
    # Step 1: find the best matching Wikipedia page
    search_url = (
        "https://en.wikipedia.org/w/api.php"
        f"?action=query&list=search&srsearch={requests.utils.quote(player_name + ' footballer')}"
        "&format=json&srlimit=1"
    )
    try:
        res = requests.get(search_url, timeout=8)
        results = res.json().get('query', {}).get('search', [])
        if not results:
            return None
        page_title = results[0]['title']
    except Exception as e:
        print(f"  Search failed for {player_name}: {e}")
        return None

    # Step 2: get the thumbnail at 800px (portrait images stay portrait)
    image_url = (
        "https://en.wikipedia.org/w/api.php"
        f"?action=query&titles={requests.utils.quote(page_title)}"
        "&prop=pageimages&format=json&pithumbsize=800&pilicense=any"
    )
    try:
        res = requests.get(image_url, timeout=8)
        data = res.json()
        pages = data.get('query', {}).get('pages', {})
        for page_id, page_info in pages.items():
            if 'thumbnail' in page_info:
                thumb = page_info['thumbnail']['source']
                # Ensure we request 800px width version
                full = re.sub(r'/\d+px-', '/800px-', thumb)
                return full
    except Exception as e:
        print(f"  Image fetch failed for {player_name}: {e}")

    return None


def scrape_players():
    url = 'https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print("Fetching data from Transfermarkt...")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    players_list = []

    table = soup.find('table', {'class': 'items'})
    if not table:
        print("Could not find the player table.")
        return

    rows = table.find('tbody').find_all('tr', recursive=False)

    for row in rows:
        try:
            name_tag = row.find('td', {'class': 'hauptlink'})
            name = name_tag.text.strip() if name_tag else "Unknown"

            value_tag = row.find('td', {'class': 'rechts hauptlink'})
            raw_value = value_tag.text.strip() if value_tag else "€0.00m"
            numeric_value = clean_value(raw_value)

            if name != "Unknown" and numeric_value > 0:
                print(f"Finding image for {name}...")
                image_url = get_wikipedia_image(name)

                # Fallback: Transfermarkt player header image
                if not image_url:
                    img_tag = row.find('img', {'class': 'bilderrahmen-fixed'})
                    if img_tag and 'src' in img_tag.attrs:
                        image_url = (img_tag['src']
                                     .replace('/small/', '/header/')
                                     .replace('/tiny/', '/header/'))
                    else:
                        image_url = ""

                players_list.append({
                    "name": name,
                    "value": numeric_value,
                    "display_value": raw_value,
                    "image": image_url
                })

                time.sleep(0.6)

        except Exception as e:
            print(f"Skipping a row due to error: {e}")
            continue

    with open('players.json', 'w', encoding='utf-8') as f:
        json.dump(players_list, f, indent=4, ensure_ascii=False)

    print(f"\nSuccess! Saved {len(players_list)} players to players.json")


if __name__ == "__main__":
    scrape_players()