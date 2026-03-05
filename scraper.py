import requests
from bs4 import BeautifulSoup
import json
import time

# ── Google Custom Search credentials ──────────────────────────────────────────
GOOGLE_API_KEY = "AIzaSyDfZ3NEew86HqzLbXTqYWYb53hwtwuZGwk"
SEARCH_ENGINE_ID = "1771ec3bd1ff54460"
# ──────────────────────────────────────────────────────────────────────────────


def clean_value(value_str):
    """Converts a string like '€180.00m' into a raw integer like 180000000."""
    try:
        cleaned = value_str.replace('€', '').strip()
        if 'm' in cleaned:
            number = float(cleaned.replace('m', '')) * 1_000_000
        elif 'k' in cleaned:
            number = float(cleaned.replace('k', '')) * 1_000
        else:
            number = 0
        return int(number)
    except ValueError:
        return 0


def get_google_image(player_name):
    """
    Uses Google Custom Search API to find a high-quality press photo
    of the player from Getty Images.
    Falls back to a general Google image search if Getty returns nothing.
    """
    def search(query):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": SEARCH_ENGINE_ID,
            "q": query,
            "searchType": "image",
            "imgType": "photo",
            "imgSize": "LARGE",
            "num": 1,
            "safe": "off",
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()
            items = data.get("items", [])
            if items:
                return items[0]["link"]
        except Exception as e:
            print(f"  Google search error for '{query}': {e}")
        return None

    # First try: Getty Images specifically
    image_url = search(f"{player_name} footballer portrait")

    # Second try: broader search
    if not image_url:
        image_url = search(f"{player_name} football player photo")

    return image_url


def scrape_players():
    url = 'https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print("Fetching player list from Transfermarkt...")
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

    for i, row in enumerate(rows):
        try:
            name_tag = row.find('td', {'class': 'hauptlink'})
            name = name_tag.text.strip() if name_tag else "Unknown"

            value_tag = row.find('td', {'class': 'rechts hauptlink'})
            raw_value = value_tag.text.strip() if value_tag else "€0.00m"
            numeric_value = clean_value(raw_value)

            if name == "Unknown" or numeric_value == 0:
                continue

            print(f"[{i+1}/{len(rows)}] Finding image for {name}...")
            image_url = get_google_image(name)

            if not image_url:
                print(f"  No image found for {name}, skipping image.")
                image_url = ""

            players_list.append({
                "name": name,
                "value": numeric_value,
                "display_value": raw_value,
                "image": image_url
            })

            # Respect Google's rate limit (100 free queries/day)
            time.sleep(0.3)

        except Exception as e:
            print(f"Skipping row due to error: {e}")
            continue

    with open('players.json', 'w', encoding='utf-8') as f:
        json.dump(players_list, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Done! Saved {len(players_list)} players to players.json")
    print(f"   Google API calls used: ~{len(players_list)} of your 100 free daily quota")


if __name__ == "__main__":
    scrape_players()