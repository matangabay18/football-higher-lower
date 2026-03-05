import requests
from bs4 import BeautifulSoup
import json
import time
import re

# ── How many players to scrape (max ~500 from Transfermarkt top list) ─────────
MAX_PAGES = 10   # 10 pages × ~50 players = ~500 players
# ──────────────────────────────────────────────────────────────────────────────

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Map Transfermarkt position codes → readable names
POSITION_MAP = {
    'Goalkeeper': 'Goalkeeper',
    'Centre-Back': 'Defender',
    'Left-Back': 'Defender',
    'Right-Back': 'Defender',
    'Defensive Midfield': 'Midfielder',
    'Central Midfield': 'Midfielder',
    'Attacking Midfield': 'Midfielder',
    'Left Midfield': 'Midfielder',
    'Right Midfield': 'Midfielder',
    'Left Winger': 'Attacker',
    'Right Winger': 'Attacker',
    'Second Striker': 'Attacker',
    'Centre-Forward': 'Attacker',
}

# Map common league names to short labels
LEAGUE_MAP = {
    'Premier League': 'Premier League',
    'LaLiga': 'La Liga',
    'Bundesliga': 'Bundesliga',
    'Serie A': 'Serie A',
    'Ligue 1': 'Ligue 1',
    'Primeira Liga': 'Primeira Liga',
    'Eredivisie': 'Eredivisie',
}


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


def get_wikipedia_image_url(player_name):
    session = requests.Session()
    session.headers.update({'User-Agent': 'FootballHigherLower/1.0'})

    try:
        search_resp = session.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search",
                    "srsearch": f"{player_name} footballer",
                    "format": "json", "srlimit": 3},
            timeout=10
        )
        results = search_resp.json().get('query', {}).get('search', [])
        if not results:
            return None
        page_title = results[0]['title']

        images_resp = session.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "titles": page_title,
                    "prop": "images", "format": "json", "imlimit": 20},
            timeout=10
        )
        pages = images_resp.json().get('query', {}).get('pages', {})
        image_filename = None
        for page in pages.values():
            for img in page.get('images', []):
                title = img['title']
                lower = title.lower()
                if any(s in lower for s in ['flag', 'icon', 'logo', 'kit', 'shield', 'coat', 'map', 'blank', 'silhouette']):
                    continue
                if lower.endswith(('.jpg', '.jpeg', '.png')):
                    image_filename = title
                    break
            if image_filename:
                break

        if not image_filename:
            return None

        file_resp = session.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "titles": image_filename,
                    "prop": "imageinfo", "iiprop": "url", "format": "json"},
            timeout=10
        )
        file_pages = file_resp.json().get('query', {}).get('pages', {})
        for page in file_pages.values():
            info = page.get('imageinfo', [])
            if info:
                return info[0]['url']
    except Exception as e:
        print(f"  Wikipedia error: {e}")

    return None


def scrape_player_details(player_url):
    """Scrape individual player page for position, league, nationality, club."""
    try:
        resp = requests.get(f"https://www.transfermarkt.com{player_url}", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        details = {
            'position': 'Unknown',
            'league': 'Unknown',
            'club': 'Unknown',
            'nationality': 'Unknown',
        }

        # Position
        pos_tag = soup.find('li', string=re.compile('Position'))
        if not pos_tag:
            for li in soup.find_all('li', {'class': 'data-header__label'}):
                if 'Position' in li.get_text():
                    pos_tag = li
                    break

        # Try info table
        info_table = soup.find('div', {'class': 'info-table'})
        if info_table:
            items = info_table.find_all('span', {'class': 'info-table__content'})
            labels = info_table.find_all('span', {'class': 'info-table__content--regular'})

        # Use header data box
        data_items = soup.find_all('li', {'class': 'data-header__label'})
        for item in data_items:
            text = item.get_text(separator=' ', strip=True)
            if 'Position' in text:
                span = item.find('span', {'class': 'data-header__content'})
                if span:
                    pos_raw = span.get_text(strip=True)
                    details['position'] = POSITION_MAP.get(pos_raw, pos_raw)

        # Club & League from header
        club_tag = soup.find('span', {'class': 'data-header__club'})
        if not club_tag:
            club_tag = soup.find('a', {'class': 'data-header__club-link'})
        if club_tag:
            details['club'] = club_tag.get_text(strip=True)

        # League
        league_tag = soup.find('span', {'class': 'data-header__league'})
        if not league_tag:
            league_tag = soup.find('a', {'class': 'data-header__league-link'})
        if league_tag:
            league_raw = league_tag.get_text(strip=True)
            details['league'] = LEAGUE_MAP.get(league_raw, league_raw)

        # Nationality from flag img alt text
        nat_section = soup.find('span', {'itemprop': 'nationality'})
        if nat_section:
            details['nationality'] = nat_section.get_text(strip=True)
        else:
            flag = soup.find('img', {'class': 'flaggenrahmen'})
            if flag:
                details['nationality'] = flag.get('title', 'Unknown')

        return details

    except Exception as e:
        print(f"  Detail scrape error: {e}")
        return {'position': 'Unknown', 'league': 'Unknown', 'club': 'Unknown', 'nationality': 'Unknown'}


def scrape_players():
    players_list = []
    seen_names = set()

    for page_num in range(1, MAX_PAGES + 1):
        url = (f'https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop'
               f'?ajax=yw1&page={page_num}')

        print(f"\n📄 Scraping page {page_num}/{MAX_PAGES}...")
        response = requests.get(url, headers=HEADERS, timeout=15)

        if response.status_code != 200:
            print(f"  Failed (status {response.status_code}), stopping.")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'items'})
        if not table:
            print("  No table found, stopping.")
            break

        rows = table.find('tbody').find_all('tr', recursive=False)
        if not rows:
            print("  No rows found, stopping.")
            break

        for row in rows:
            try:
                name_tag = row.find('td', {'class': 'hauptlink'})
                if not name_tag:
                    continue
                name = name_tag.get_text(strip=True)
                if not name or name in seen_names:
                    continue
                seen_names.add(name)

                value_tag = row.find('td', {'class': 'rechts hauptlink'})
                raw_value = value_tag.get_text(strip=True) if value_tag else "€0"
                numeric_value = clean_value(raw_value)
                if numeric_value == 0:
                    continue

                # Get player page URL for detail scraping
                player_link = name_tag.find('a')
                player_url = player_link['href'] if player_link and 'href' in player_link.attrs else None

                print(f"  [{len(players_list)+1}] {name} ({raw_value})")

                # Get position/league/club from player page
                details = {'position': 'Unknown', 'league': 'Unknown', 'club': 'Unknown', 'nationality': 'Unknown'}
                if player_url:
                    details = scrape_player_details(player_url)
                    time.sleep(0.3)

                # Get Wikipedia image
                image_url = get_wikipedia_image_url(name)
                if not image_url:
                    img_tag = row.find('img', {'class': 'bilderrahmen-fixed'})
                    if img_tag and 'src' in img_tag.attrs:
                        image_url = img_tag['src'].replace('/small/', '/big/').replace('/tiny/', '/big/')
                    else:
                        image_url = ""

                players_list.append({
                    "name": name,
                    "value": numeric_value,
                    "display_value": raw_value,
                    "image": image_url,
                    "position": details['position'],
                    "league": details['league'],
                    "club": details['club'],
                    "nationality": details['nationality'],
                })

                time.sleep(0.4)

            except Exception as e:
                print(f"  Row error: {e}")
                continue

        time.sleep(1)

    with open('players.json', 'w', encoding='utf-8') as f:
        json.dump(players_list, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done! Saved {len(players_list)} players to players.json")


if __name__ == "__main__":
    scrape_players()