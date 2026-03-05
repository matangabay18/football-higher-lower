import streamlit as st
import json
import random
import os
from datetime import datetime

st.set_page_config(page_title="Higher or Lower: Football", page_icon="⚽", layout="wide")

# ══════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f; color: #f0f0f0;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stHeader"] { background: transparent; }
.main .block-container { padding: 1.5rem 2.5rem 4rem; max-width: 1300px; }

/* Title */
.game-title {
    font-family: 'Bebas Neue', cursive;
    font-size: clamp(2.5rem, 6vw, 5rem);
    letter-spacing: 0.05em; line-height: 1;
    text-align: center; margin-bottom: 0.1em;
    background: linear-gradient(135deg, #fff 0%, #a8ff78 50%, #78ffd6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.game-subtitle {
    text-align: center; font-size: 0.8rem; color: #555;
    letter-spacing: 0.35em; text-transform: uppercase; margin-bottom: 0.3rem;
}

/* Stats bar */
.stats-bar {
    display: flex; justify-content: center; align-items: center;
    gap: 0; margin: 1rem auto 0;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 50px; max-width: 620px; overflow: hidden;
}
.stat-item {
    flex: 1; padding: 0.7rem 1rem; text-align: center;
    border-right: 1px solid rgba(255,255,255,0.06);
}
.stat-item:last-child { border-right: none; }
.stat-label { font-size: 0.6rem; letter-spacing: 0.2em; text-transform: uppercase; color: #555; margin-bottom: 0.1rem; }
.stat-val {
    font-family: 'Bebas Neue', cursive; font-size: 2rem; line-height: 1;
    background: linear-gradient(135deg, #a8ff78, #78ffd6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.stat-val.streak { background: linear-gradient(135deg, #ff9a3c, #ff6b6b);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.stat-val.best { background: linear-gradient(135deg, #ffd700, #ffaa00);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }

/* Filters */
.filter-bar {
    display: flex; justify-content: center; gap: 0.5rem;
    flex-wrap: wrap; margin: 0.8rem auto; max-width: 900px;
}

/* VS */
.vs-wrap { display: flex; align-items: center; justify-content: center; height: 100%; min-height: 480px; }
.vs-badge {
    font-family: 'Bebas Neue', cursive; font-size: 1.3rem;
    width: 52px; height: 52px; border-radius: 50%;
    background: linear-gradient(135deg, #a8ff78, #78ffd6); color: #0a0a0f;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 32px rgba(168,255,120,0.55);
}

/* Player card */
.pcard {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; overflow: hidden; transition: box-shadow 0.3s;
}
.pcard:hover { box-shadow: 0 0 0 1px rgba(168,255,120,0.2), 0 16px 48px rgba(0,0,0,0.5); }
.pcard-img { width: 100%; aspect-ratio: 3/4; overflow: hidden; background: #111; position: relative; }
.pcard-img img {
    width: 100%; height: 100%; object-fit: cover;
    object-position: center top; display: block;
    transition: opacity 0.5s ease;
}
.pcard-body { padding: 1rem 1.4rem 1.4rem; text-align: center; border-top: 1px solid rgba(255,255,255,0.05); }
.pcard-name { font-family: 'Bebas Neue', cursive; font-size: 1.8rem; letter-spacing: 0.04em; color: #fff; margin-bottom: 0.2rem; line-height: 1.1; }
.pcard-meta { font-size: 0.75rem; color: #555; margin-bottom: 0.3rem; letter-spacing: 0.05em; }
.pcard-value { font-size: 1.4rem; font-weight: 700; color: #a8ff78; }
.pcard-hidden { font-size: 0.8rem; color: #444; letter-spacing: 0.18em; text-transform: uppercase; margin-top: 0.2rem; }
.pcard-revealed { font-size: 1.3rem; font-weight: 700; color: #78ffd6; animation: popIn 0.4s ease; }
@keyframes popIn { 0%{transform:scale(0.5);opacity:0} 70%{transform:scale(1.1)} 100%{transform:scale(1);opacity:1} }

/* Hint badge */
.hint-box {
    background: rgba(255,200,60,0.1); border: 1px solid rgba(255,200,60,0.3);
    border-radius: 10px; padding: 0.4rem 1rem; text-align: center;
    color: #ffc83c; font-size: 0.85rem; margin-top: 0.5rem;
    animation: fadeIn 0.3s ease;
}
@keyframes fadeIn { from{opacity:0;transform:translateY(-5px)} to{opacity:1;transform:translateY(0)} }

/* Difficulty badge */
.diff-easy { color: #a8ff78; }
.diff-medium { color: #ffc83c; }
.diff-hard { color: #ff6b6b; }

/* Buttons */
div[data-testid="stButton"] button {
    font-family: 'DM Sans', sans-serif !important; font-weight: 700 !important;
    letter-spacing: 0.08em !important; text-transform: uppercase !important;
    height: 52px !important; border-radius: 12px !important; font-size: 0.9rem !important;
}
.btn-higher div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #a8ff78, #78ffd6) !important;
    color: #0a0a0f !important; border: none !important;
    box-shadow: 0 4px 20px rgba(168,255,120,0.3) !important;
}
.btn-lower div[data-testid="stButton"] button {
    background: rgba(255,255,255,0.05) !important; color: #ddd !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
}
.btn-same div[data-testid="stButton"] button {
    background: rgba(255,200,60,0.08) !important; color: #ffc83c !important;
    border: 1px solid rgba(255,200,60,0.25) !important;
}
.btn-hint div[data-testid="stButton"] button {
    background: rgba(255,200,60,0.06) !important; color: #ffc83c !important;
    border: 1px solid rgba(255,200,60,0.2) !important;
    height: 40px !important; font-size: 0.8rem !important;
}
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #a8ff78, #78ffd6) !important;
    color: #0a0a0f !important; border: none !important;
    height: 58px !important; font-size: 1rem !important;
    box-shadow: 0 6px 28px rgba(168,255,120,0.35) !important;
}

/* Feedback */
.flash-correct {
    background: rgba(168,255,120,0.07); border: 1px solid rgba(168,255,120,0.25);
    border-radius: 10px; padding: 0.5rem 1rem; text-align: center;
    color: #a8ff78; font-weight: 600; letter-spacing: 0.1em;
    margin-bottom: 0.8rem; font-size: 0.9rem;
}
.flash-streak {
    background: rgba(255,154,60,0.1); border: 1px solid rgba(255,154,60,0.3);
    border-radius: 10px; padding: 0.4rem 1rem; text-align: center;
    color: #ff9a3c; font-weight: 700; font-size: 1rem; margin-bottom: 0.5rem;
    animation: popIn 0.4s ease;
}

/* Game over */
.gameover-box {
    text-align: center; padding: 2.5rem 2rem 1.5rem;
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 24px; max-width: 500px; margin: 1.5rem auto;
}
.gameover-title {
    font-family: 'Bebas Neue', cursive; font-size: 3rem;
    background: linear-gradient(135deg, #ff6b6b, #ffc3a0);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.gameover-score {
    font-family: 'Bebas Neue', cursive; font-size: 6rem; line-height: 1;
    background: linear-gradient(135deg, #a8ff78, #78ffd6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.gameover-label { font-size: 0.75rem; color: #555; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.5rem; }
.pb-badge {
    display: inline-block; background: rgba(255,215,0,0.1);
    border: 1px solid rgba(255,215,0,0.3); border-radius: 20px;
    padding: 0.3rem 1rem; color: #ffd700; font-size: 0.85rem;
    font-weight: 700; margin-bottom: 1rem;
}

/* Share box */
.share-box {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 1rem 1.5rem; text-align: center;
    margin: 0.8rem auto; max-width: 500px;
}
.share-text { font-size: 0.9rem; color: #888; margin-bottom: 0.5rem; }
.share-msg {
    font-family: 'Bebas Neue', cursive; font-size: 1.1rem;
    color: #fff; letter-spacing: 0.05em;
    background: rgba(255,255,255,0.05); border-radius: 8px;
    padding: 0.5rem 1rem; margin-bottom: 0.5rem;
}

/* Leaderboard */
.lb-title {
    font-family: 'Bebas Neue', cursive; font-size: 1.8rem;
    letter-spacing: 0.08em; text-align: center; margin: 1.5rem 0 0.8rem; color: #fff;
}
.lb-table { width: 100%; border-collapse: collapse; margin: 0 auto; max-width: 600px; }
.lb-table th { font-size: 0.65rem; letter-spacing: 0.2em; text-transform: uppercase; color: #444; padding: 0.4rem 1rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.06); }
.lb-table td { padding: 0.6rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.9rem; color: #aaa; }
.lb-table tr:nth-child(1) td { color: #ffd700; font-weight: 700; }
.lb-table tr:nth-child(2) td { color: #c0c0c0; font-weight: 600; }
.lb-table tr:nth-child(3) td { color: #cd7f32; font-weight: 600; }
.lb-rank { font-family: 'Bebas Neue', cursive; font-size: 1.1rem; color: #444; }
.lb-score-val { font-family: 'Bebas Neue', cursive; font-size: 1.3rem; color: #a8ff78; }
.lb-highlight td { background: rgba(168,255,120,0.05); color: #a8ff78 !important; }

/* Input */
div[data-testid="stTextInput"] input {
    background: #ffffff !important; border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important; color: #000000 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 1rem !important;
    padding: 0.6rem 1rem !important; text-align: center !important;
}

/* Selectbox */
div[data-testid="stSelectbox"] > div { background: rgba(255,255,255,0.05) !important; border-radius: 10px !important; }

#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
hr { border-color: rgba(255,255,255,0.05) !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════
#  LEADERBOARD
# ══════════════════════════════════════════
LEADERBOARD_FILE = "leaderboard.json"

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_to_leaderboard(name, score, difficulty):
    lb = load_leaderboard()
    lb.append({"name": name.strip(), "score": score, "difficulty": difficulty,
                "date": datetime.now().strftime("%d/%m/%Y")})
    lb = sorted(lb, key=lambda x: x['score'], reverse=True)[:100]
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(lb, f, indent=2)
    return lb


# ══════════════════════════════════════════
#  LOAD PLAYERS
# ══════════════════════════════════════════
@st.cache_data
def load_data():
    with open('players.json', 'r', encoding='utf-8') as f:
        return json.load(f)

ALL_PLAYERS = load_data()

# Build filter options from data
ALL_LEAGUES = sorted(set(p.get('league', 'Unknown') for p in ALL_PLAYERS if p.get('league') and p.get('league') != 'Unknown'))
ALL_POSITIONS = sorted(set(p.get('position', 'Unknown') for p in ALL_PLAYERS if p.get('position') and p.get('position') != 'Unknown'))


# ══════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════
defaults = {
    'score': 0, 'streak': 0, 'max_streak': 0,
    'personal_best': 0, 'game_over': False,
    'last_result': None, 'score_saved': False,
    'hint_used': False, 'show_hint': False,
    'revealing': False, 'p1': None, 'p2': None,
    'difficulty': 'Medium', 'filter_league': 'All',
    'filter_position': 'All', 'new_pb': False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════
#  PLAYER POOL
# ══════════════════════════════════════════
def get_pool():
    pool = ALL_PLAYERS.copy()
    if st.session_state.filter_league != 'All':
        pool = [p for p in pool if p.get('league') == st.session_state.filter_league]
    if st.session_state.filter_position != 'All':
        pool = [p for p in pool if p.get('position') == st.session_state.filter_position]
    return pool if len(pool) >= 2 else ALL_PLAYERS

def get_random_player(exclude_name=None, difficulty='Medium'):
    pool = get_pool()
    if exclude_name:
        pool = [p for p in pool if p['name'] != exclude_name]
    if not pool:
        pool = ALL_PLAYERS

    if difficulty == 'Easy' and st.session_state.p1:
        # Pick player with noticeably different value (>20% difference)
        base_val = st.session_state.p1['value']
        easy_pool = [p for p in pool if abs(p['value'] - base_val) > base_val * 0.2]
        if len(easy_pool) >= 1:
            return random.choice(easy_pool)

    if difficulty == 'Hard' and st.session_state.p1:
        # Pick player with very similar value (<15% difference)
        base_val = st.session_state.p1['value']
        hard_pool = [p for p in pool if p['name'] != (exclude_name or '') and abs(p['value'] - base_val) < base_val * 0.15]
        if len(hard_pool) >= 1:
            return random.choice(hard_pool)

    return random.choice(pool)

# Init players if needed
if st.session_state.p1 is None:
    st.session_state.p1 = get_random_player()
if st.session_state.p2 is None:
    st.session_state.p2 = get_random_player(st.session_state.p1['name'])


# ══════════════════════════════════════════
#  GAME LOGIC
# ══════════════════════════════════════════
def check_guess(guess):
    v1, v2 = st.session_state.p1['value'], st.session_state.p2['value']
    correct = (
        (guess == 'higher' and v2 >= v1) or
        (guess == 'lower'  and v2 <= v1) or
        (guess == 'same'   and v1 == v2)
    )
    if correct:
        st.session_state.score += 1
        st.session_state.streak += 1
        st.session_state.max_streak = max(st.session_state.streak, st.session_state.max_streak)
        st.session_state.last_result = 'correct'
        st.session_state.revealing = True
        st.session_state.hint_used = False
        st.session_state.show_hint = False
    else:
        st.session_state.streak = 0
        st.session_state.last_result = 'wrong'
        st.session_state.revealing = True

def advance_game():
    if st.session_state.last_result == 'correct':
        st.session_state.p1 = st.session_state.p2
        st.session_state.p2 = get_random_player(st.session_state.p1['name'], st.session_state.difficulty)
    else:
        # Check personal best
        if st.session_state.score > st.session_state.personal_best:
            st.session_state.personal_best = st.session_state.score
            st.session_state.new_pb = True
        else:
            st.session_state.new_pb = False
        st.session_state.game_over = True
    st.session_state.revealing = False

def restart_game():
    pool = get_pool()
    p1 = random.choice(pool)
    p2 = get_random_player(p1['name'], st.session_state.difficulty)
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.game_over = False
    st.session_state.last_result = None
    st.session_state.score_saved = False
    st.session_state.hint_used = False
    st.session_state.show_hint = False
    st.session_state.revealing = False
    st.session_state.new_pb = False
    st.session_state.p1 = p1
    st.session_state.p2 = p2


# ══════════════════════════════════════════
#  HTML HELPERS
# ══════════════════════════════════════════
def player_card_html(player, show_value, revealed_value=None):
    image = player.get('image', '').strip()
    img_block = (
        f'<div class="pcard-img"><img src="{image}" alt="{player["name"]}" referrerpolicy="no-referrer" crossorigin="anonymous"></div>'
        if image else '<div class="pcard-placeholder">⚽</div>'
    )
    club = player.get('club', '')
    league = player.get('league', '')
    meta = " · ".join(filter(None, [club, league]))
    meta_html = f'<div class="pcard-meta">{meta}</div>' if meta and meta != "Unknown · Unknown" else ""

    if revealed_value is not None:
        value_html = f'<div class="pcard-revealed">{player["display_value"]}</div>'
    elif show_value:
        value_html = f'<div class="pcard-value">{player["display_value"]}</div>'
    else:
        value_html = '<div class="pcard-hidden">??? · Make your guess</div>'

    return f"""<div class="pcard">{img_block}
        <div class="pcard-body">
            <div class="pcard-name">{player['name']}</div>
            {meta_html}{value_html}
        </div></div>"""

def leaderboard_html(entries, highlight_name=None):
    if not entries:
        return "<p style='text-align:center;color:#444;padding:1rem'>No scores yet — be the first!</p>"
    medals = {1:"🥇",2:"🥈",3:"🥉"}
    rows = ""
    for i, e in enumerate(entries[:20], 1):
        rank = medals.get(i, f'<span class="lb-rank">{i}</span>')
        hl = "lb-highlight" if (highlight_name and e['name'].lower() == highlight_name.lower()) else ""
        diff_label = e.get('difficulty', '')
        diff_col = {'Easy':'#a8ff78','Medium':'#ffc83c','Hard':'#ff6b6b'}.get(diff_label, '#888')
        rows += f"""<tr class="{hl}">
            <td>{rank}</td><td>{e['name']}</td>
            <td><span class="lb-score-val">{e['score']}</span></td>
            <td style="color:{diff_col};font-size:0.75rem">{diff_label}</td>
            <td style="color:#444;font-size:0.75rem">{e['date']}</td>
        </tr>"""
    return f"""<table class="lb-table"><thead><tr>
        <th>#</th><th>Name</th><th>Score</th><th>Difficulty</th><th>Date</th>
        </tr></thead><tbody>{rows}</tbody></table>"""


# ══════════════════════════════════════════
#  RENDER
# ══════════════════════════════════════════

# Header
st.markdown("<p class='game-subtitle'>⚽ The Football Value Game</p>", unsafe_allow_html=True)
st.markdown("<h1 class='game-title'>Higher or Lower</h1>", unsafe_allow_html=True)

# Stats bar
streak_emoji = "🔥" if st.session_state.streak >= 3 else ""
st.markdown(f"""
<div class='stats-bar'>
    <div class='stat-item'><div class='stat-label'>Score</div><div class='stat-val'>{st.session_state.score}</div></div>
    <div class='stat-item'><div class='stat-label'>Streak {streak_emoji}</div><div class='stat-val streak'>{st.session_state.streak}</div></div>
    <div class='stat-item'><div class='stat-label'>Best</div><div class='stat-val best'>{st.session_state.personal_best}</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── GAME OVER ──
if st.session_state.game_over:
    final_score = st.session_state.score

    pb_html = '<div class="pb-badge">🏆 New Personal Best!</div>' if st.session_state.new_pb else ""
    st.markdown(f"""
    <div class='gameover-box'>
        <div class='gameover-title'>Game Over</div>
        <div class='gameover-score'>{final_score}</div>
        <div class='gameover-label'>Final Score · Best Streak: {st.session_state.max_streak}</div>
        {pb_html}
    </div>
    """, unsafe_allow_html=True)

    # Share button
    share_text = f"⚽ I scored {final_score} on Football Higher or Lower! ({st.session_state.difficulty} mode) Can you beat me? 🔥"
    st.markdown(f"""
    <div class='share-box'>
        <div class='share-text'>Share your score:</div>
        <div class='share-msg'>{share_text}</div>
    </div>
    """, unsafe_allow_html=True)
    _, sc, _ = st.columns([1,3,1])
    with sc:
        if st.button("📋 Copy Share Message", use_container_width=True):
            st.write(f'<script>navigator.clipboard.writeText("{share_text}")</script>', unsafe_allow_html=True)
            st.success("Copied! Paste it anywhere 🎉")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Save score
    if not st.session_state.score_saved:
        st.markdown("<p style='text-align:center;color:#888;margin:0.5rem 0 0.3rem;font-size:0.9rem'>Save your score to the leaderboard:</p>", unsafe_allow_html=True)
        _, inp, _ = st.columns([1,2,1])
        with inp:
            pname = st.text_input("", placeholder="Your name...", label_visibility="collapsed", key="name_input")
            s1, s2 = st.columns(2)
            with s1:
                if st.button("💾 Save Score", use_container_width=True, type="primary"):
                    if pname.strip():
                        save_to_leaderboard(pname, final_score, st.session_state.difficulty)
                        st.session_state.score_saved = True
                        st.session_state.saved_name = pname.strip()
                        st.rerun()
                    else:
                        st.warning("Enter your name!")
            with s2:
                st.button("🔄 Play Again", on_click=restart_game, use_container_width=True)
    else:
        st.markdown("<p style='text-align:center;color:#a8ff78;font-weight:600;margin:0.3rem 0 1rem'>✓ Score saved!</p>", unsafe_allow_html=True)
        _, mid, _ = st.columns([1,2,1])
        with mid:
            st.button("🔄 Play Again", on_click=restart_game, type="primary", use_container_width=True)

    # Leaderboard
    st.markdown("<div class='lb-title'>🏆 All-Time Leaderboard</div>", unsafe_allow_html=True)
    st.markdown(leaderboard_html(load_leaderboard(), st.session_state.get('saved_name')), unsafe_allow_html=True)

# ── REVEAL SCREEN ──
elif st.session_state.revealing:
    result_color = "#a8ff78" if st.session_state.last_result == 'correct' else "#ff6b6b"
    result_text = "✓ Correct!" if st.session_state.last_result == 'correct' else "✗ Wrong!"
    st.markdown(f"<div style='text-align:center;font-size:1.5rem;font-weight:700;color:{result_color};margin-bottom:0.8rem'>{result_text}</div>", unsafe_allow_html=True)

    p1, p2 = st.session_state.p1, st.session_state.p2
    left, mid, right = st.columns([11, 1, 11])
    with left:
        st.markdown(player_card_html(p1, show_value=True), unsafe_allow_html=True)
    with mid:
        st.markdown("<div class='vs-wrap'><div class='vs-badge'>VS</div></div>", unsafe_allow_html=True)
    with right:
        st.markdown(player_card_html(p2, show_value=False, revealed_value=p2['value']), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, cc, _ = st.columns([1,2,1])
    with cc:
        label = "➡️ Next Player" if st.session_state.last_result == 'correct' else "See Results"
        st.button(label, on_click=advance_game, type="primary", use_container_width=True)

# ── ACTIVE GAME ──
else:
    # Filters row
    fc1, fc2, fc3 = st.columns([2, 2, 2])
    with fc1:
        diff = st.selectbox("⚡ Difficulty", ["Easy", "Medium", "Hard"],
                            index=["Easy","Medium","Hard"].index(st.session_state.difficulty),
                            key="diff_select", label_visibility="collapsed")
        if diff != st.session_state.difficulty:
            st.session_state.difficulty = diff
    with fc2:
        leagues = ['All'] + ALL_LEAGUES
        league = st.selectbox("🏆 League", leagues,
                              index=leagues.index(st.session_state.filter_league) if st.session_state.filter_league in leagues else 0,
                              key="league_select", label_visibility="collapsed")
        if league != st.session_state.filter_league:
            st.session_state.filter_league = league
            restart_game()
            st.rerun()
    with fc3:
        positions = ['All'] + ALL_POSITIONS
        position = st.selectbox("👟 Position", positions,
                                index=positions.index(st.session_state.filter_position) if st.session_state.filter_position in positions else 0,
                                key="pos_select", label_visibility="collapsed")
        if position != st.session_state.filter_position:
            st.session_state.filter_position = position
            restart_game()
            st.rerun()

    # Streak notification
    if st.session_state.last_result == 'correct':
        if st.session_state.streak >= 5:
            st.markdown(f"<div class='flash-streak'>🔥 {st.session_state.streak} IN A ROW! ON FIRE!</div>", unsafe_allow_html=True)
        elif st.session_state.streak >= 3:
            st.markdown(f"<div class='flash-streak'>🔥 {st.session_state.streak} streak!</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='flash-correct'>✓ Correct! Keep going!</div>", unsafe_allow_html=True)

    p1, p2 = st.session_state.p1, st.session_state.p2

    # Cards
    left, mid, right = st.columns([11, 1, 11])
    with left:
        st.markdown(player_card_html(p1, show_value=True), unsafe_allow_html=True)
    with mid:
        st.markdown("<div class='vs-wrap'><div class='vs-badge'>VS</div></div>", unsafe_allow_html=True)
    with right:
        st.markdown(player_card_html(p2, show_value=False), unsafe_allow_html=True)
        # Hint
        if not st.session_state.hint_used:
            st.markdown("<div class='btn-hint'>", unsafe_allow_html=True)
            if st.button("💡 Use Hint", use_container_width=True, key="hint_btn"):
                st.session_state.hint_used = True
                st.session_state.show_hint = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        if st.session_state.show_hint:
            nat = p2.get('nationality', '')
            pos = p2.get('position', '')
            hint_parts = [x for x in [nat, pos] if x and x != 'Unknown']
            hint = " · ".join(hint_parts) if hint_parts else "No hint available"
            st.markdown(f"<div class='hint-box'>💡 {hint}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;color:#555;letter-spacing:0.2em;font-size:0.78rem;text-transform:uppercase;margin-bottom:0.8rem;'>"
        "Is their market value higher, lower, or the same?</p>", unsafe_allow_html=True)

    _, c1, _g, c2, _ = st.columns([1, 4, 1, 4, 1])
    with c1:
        st.markdown("<div class='btn-higher'>", unsafe_allow_html=True)
        st.button("⬆️  Higher", on_click=check_guess, args=("higher",), use_container_width=True, key="higher")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='btn-lower'>", unsafe_allow_html=True)
        st.button("⬇️  Lower", on_click=check_guess, args=("lower",), use_container_width=True, key="lower")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, sc, _ = st.columns([2, 3, 2])
    with sc:
        st.markdown("<div class='btn-same'>", unsafe_allow_html=True)
        st.button("🟰  Same Value", on_click=check_guess, args=("same",), use_container_width=True, key="same")
        st.markdown("</div>", unsafe_allow_html=True)