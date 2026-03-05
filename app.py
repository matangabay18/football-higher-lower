import streamlit as st
import json
import random
import os
from datetime import datetime

# --- 1. Page Configuration ---
st.set_page_config(page_title="Higher or Lower: Football", page_icon="⚽", layout="wide")

# --- 2. Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f;
    color: #f0f0f0;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stHeader"] { background: transparent; }
.main .block-container { padding: 2rem 3rem 4rem; max-width: 1300px; }

.game-title {
    font-family: 'Bebas Neue', cursive;
    font-size: clamp(3rem, 7vw, 5.5rem);
    letter-spacing: 0.05em;
    line-height: 1;
    text-align: center;
    margin-bottom: 0.1em;
    background: linear-gradient(135deg, #ffffff 0%, #a8ff78 50%, #78ffd6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.game-subtitle {
    text-align: center;
    font-size: 0.85rem;
    color: #555;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.score-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1.5rem;
    margin: 1.2rem auto 0;
    padding: 0.8rem 2.5rem;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 50px;
    max-width: 360px;
}
.score-label { font-size: 0.7rem; letter-spacing: 0.25em; text-transform: uppercase; color: #666; }
.score-value {
    font-family: 'Bebas Neue', cursive;
    font-size: 2.8rem;
    line-height: 1;
    background: linear-gradient(135deg, #a8ff78, #78ffd6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.vs-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 500px;
}
.vs-badge {
    font-family: 'Bebas Neue', cursive;
    font-size: 1.3rem;
    width: 52px; height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, #a8ff78, #78ffd6);
    color: #0a0a0f;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 32px rgba(168,255,120,0.55);
}
.pcard {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    overflow: hidden;
    transition: box-shadow 0.3s;
}
.pcard:hover {
    box-shadow: 0 0 0 1px rgba(168,255,120,0.2), 0 16px 48px rgba(0,0,0,0.5);
}
.pcard-img {
    width: 100%;
    aspect-ratio: 3 / 4;
    overflow: hidden;
    background: #111;
}
.pcard-img img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center top;
    display: block;
}
.pcard-placeholder {
    width: 100%;
    aspect-ratio: 3 / 4;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255,255,255,0.04);
    font-size: 5rem;
}
.pcard-body {
    padding: 1.1rem 1.4rem 1.5rem;
    text-align: center;
    border-top: 1px solid rgba(255,255,255,0.05);
}
.pcard-name {
    font-family: 'Bebas Neue', cursive;
    font-size: 1.9rem;
    letter-spacing: 0.04em;
    color: #fff;
    margin-bottom: 0.3rem;
    line-height: 1.1;
}
.pcard-value { font-size: 1.4rem; font-weight: 700; color: #a8ff78; }
.pcard-hidden { font-size: 0.8rem; color: #444; letter-spacing: 0.18em; text-transform: uppercase; margin-top: 0.2rem; }

div[data-testid="stButton"] button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    height: 52px !important;
    border-radius: 12px !important;
    font-size: 0.9rem !important;
}
.btn-higher div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #a8ff78, #78ffd6) !important;
    color: #0a0a0f !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(168,255,120,0.3) !important;
}
.btn-lower div[data-testid="stButton"] button {
    background: rgba(255,255,255,0.05) !important;
    color: #ddd !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
}
.btn-same div[data-testid="stButton"] button {
    background: rgba(255,200,60,0.08) !important;
    color: #ffc83c !important;
    border: 1px solid rgba(255,200,60,0.25) !important;
}
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #a8ff78, #78ffd6) !important;
    color: #0a0a0f !important;
    border: none !important;
    height: 58px !important;
    font-size: 1rem !important;
    box-shadow: 0 6px 28px rgba(168,255,120,0.35) !important;
}
.flash-correct {
    background: rgba(168,255,120,0.07);
    border: 1px solid rgba(168,255,120,0.25);
    border-radius: 10px;
    padding: 0.5rem 1rem;
    text-align: center;
    color: #a8ff78;
    font-weight: 600;
    letter-spacing: 0.1em;
    margin-bottom: 1rem;
    font-size: 0.9rem;
}
.gameover-box {
    text-align: center;
    padding: 2.5rem 2rem 1.5rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 24px;
    max-width: 500px;
    margin: 2rem auto;
}
.gameover-title {
    font-family: 'Bebas Neue', cursive;
    font-size: 3.5rem;
    background: linear-gradient(135deg, #ff6b6b, #ffc3a0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.gameover-score {
    font-family: 'Bebas Neue', cursive;
    font-size: 7rem;
    line-height: 1;
    background: linear-gradient(135deg, #a8ff78, #78ffd6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.gameover-label { font-size: 0.8rem; color: #555; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 1.5rem; }

/* Leaderboard */
.lb-title {
    font-family: 'Bebas Neue', cursive;
    font-size: 2rem;
    letter-spacing: 0.08em;
    text-align: center;
    margin: 2rem 0 1rem;
    color: #fff;
}
.lb-table {
    width: 100%;
    border-collapse: collapse;
    margin: 0 auto;
    max-width: 600px;
}
.lb-table th {
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #555;
    padding: 0.5rem 1rem;
    text-align: left;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.lb-table td {
    padding: 0.7rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.95rem;
    color: #ccc;
}
.lb-table tr:first-child td { color: #ffd700; font-weight: 700; }
.lb-table tr:nth-child(2) td { color: #c0c0c0; font-weight: 600; }
.lb-table tr:nth-child(3) td { color: #cd7f32; font-weight: 600; }
.lb-rank { font-family: 'Bebas Neue', cursive; font-size: 1.2rem; color: #444; }
.lb-score-val { font-family: 'Bebas Neue', cursive; font-size: 1.4rem; color: #a8ff78; }
.lb-highlight td { background: rgba(168,255,120,0.05); color: #a8ff78 !important; }

/* Input styling */
div[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.6rem 1rem !important;
    text-align: center !important;
}

#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
hr { border-color: rgba(255,255,255,0.05) !important; }
</style>
""", unsafe_allow_html=True)


# --- 3. Leaderboard helpers ---
LEADERBOARD_FILE = "leaderboard.json"

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_leaderboard(data):
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_score(name, score):
    lb = load_leaderboard()
    lb.append({
        "name": name.strip(),
        "score": score,
        "date": datetime.now().strftime("%d/%m/%Y")
    })
    # Keep top 100, sorted by score desc
    lb = sorted(lb, key=lambda x: x['score'], reverse=True)[:100]
    save_leaderboard(lb)
    return lb


# --- 4. Load Players ---
@st.cache_data
def load_data():
    with open('players.json', 'r', encoding='utf-8') as f:
        return json.load(f)

players = load_data()


# --- 5. Session State ---
def get_random_player(exclude_name=None):
    pool = [p for p in players if p['name'] != exclude_name] if exclude_name else players
    return random.choice(pool)

if 'score'          not in st.session_state: st.session_state.score = 0
if 'game_over'      not in st.session_state: st.session_state.game_over = False
if 'last_result'    not in st.session_state: st.session_state.last_result = None
if 'score_saved'    not in st.session_state: st.session_state.score_saved = False
if 'p1'             not in st.session_state: st.session_state.p1 = get_random_player()
if 'p2'             not in st.session_state: st.session_state.p2 = get_random_player(st.session_state.p1['name'])


# --- 6. Game Logic ---
def check_guess(guess):
    v1, v2 = st.session_state.p1['value'], st.session_state.p2['value']
    correct = (
        (guess == 'higher' and v2 >= v1) or
        (guess == 'lower'  and v2 <= v1) or
        (guess == 'same'   and v1 == v2)
    )
    if correct:
        st.session_state.score += 1
        st.session_state.last_result = 'correct'
        st.session_state.p1 = st.session_state.p2
        st.session_state.p2 = get_random_player(st.session_state.p1['name'])
    else:
        st.session_state.last_result = 'wrong'
        st.session_state.game_over = True

def restart_game():
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.last_result = None
    st.session_state.score_saved = False
    st.session_state.p1 = get_random_player()
    st.session_state.p2 = get_random_player(st.session_state.p1['name'])


# --- 7. Card HTML ---
def player_card_html(player, show_value: bool) -> str:
    image = player.get('image', '').strip()
    if image:
        img_block = f'<div class="pcard-img"><img src="{image}" alt="{player["name"]}" referrerpolicy="no-referrer" crossorigin="anonymous"></div>'
    else:
        img_block = '<div class="pcard-placeholder">⚽</div>'

    value_html = (
        f'<div class="pcard-value">{player["display_value"]}</div>'
        if show_value else
        '<div class="pcard-hidden">??? · Make your guess</div>'
    )
    return f"""
    <div class="pcard">
        {img_block}
        <div class="pcard-body">
            <div class="pcard-name">{player['name']}</div>
            {value_html}
        </div>
    </div>
    """


# --- 8. Leaderboard HTML ---
def leaderboard_html(entries, highlight_name=None):
    if not entries:
        return "<p style='text-align:center;color:#444;'>No scores yet. Be the first!</p>"

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    rows = ""
    for i, entry in enumerate(entries[:20], 1):
        rank = medals.get(i, f'<span class="lb-rank">{i}</span>')
        highlight = "lb-highlight" if (highlight_name and entry['name'].lower() == highlight_name.lower()) else ""
        rows += f"""
        <tr class="{highlight}">
            <td>{rank}</td>
            <td>{entry['name']}</td>
            <td><span class="lb-score-val">{entry['score']}</span></td>
            <td style="color:#444;font-size:0.8rem">{entry['date']}</td>
        </tr>
        """

    return f"""
    <table class="lb-table">
        <thead>
            <tr>
                <th>#</th>
                <th>Player</th>
                <th>Score</th>
                <th>Date</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    """


# ══════════════════════════════════════════
#  RENDER
# ══════════════════════════════════════════

st.markdown("<p class='game-subtitle'>⚽ The Football Value Game</p>", unsafe_allow_html=True)
st.markdown("<h1 class='game-title'>Higher or Lower</h1>", unsafe_allow_html=True)
st.markdown(f"""
<div class='score-bar'>
    <span class='score-label'>Score</span>
    <span class='score-value'>{st.session_state.score}</span>
    <span class='score-label'>Points</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Game Over Screen ──
if st.session_state.game_over:
    final_score = st.session_state.score

    st.markdown(f"""
    <div class='gameover-box'>
        <div class='gameover-title'>Game Over</div>
        <div class='gameover-score'>{final_score}</div>
        <div class='gameover-label'>Final Score</div>
    </div>
    """, unsafe_allow_html=True)

    # Save score section
    if not st.session_state.score_saved:
        st.markdown("<p style='text-align:center;color:#888;margin:1rem 0 0.3rem;'>Enter your name to save your score:</p>", unsafe_allow_html=True)
        _, inp_col, _ = st.columns([1, 2, 1])
        with inp_col:
            player_name = st.text_input("", placeholder="Your name...", label_visibility="collapsed", key="name_input")
            save_col, play_col = st.columns(2)
            with save_col:
                if st.button("💾 Save Score", use_container_width=True, type="primary"):
                    if player_name.strip():
                        lb = add_score(player_name, final_score)
                        st.session_state.score_saved = True
                        st.session_state.saved_name = player_name.strip()
                        st.rerun()
                    else:
                        st.warning("Please enter your name!")
            with play_col:
                st.button("🔄 Play Again", on_click=restart_game, use_container_width=True)
    else:
        st.markdown(f"<p style='text-align:center;color:#a8ff78;font-weight:600;margin:0.5rem 0 1.5rem;'>✓ Score saved!</p>", unsafe_allow_html=True)
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            st.button("🔄 Play Again", on_click=restart_game, type="primary", use_container_width=True)

    # Leaderboard
    st.markdown("<div class='lb-title'>🏆 All-Time Leaderboard</div>", unsafe_allow_html=True)
    lb_data = load_leaderboard()
    highlight = st.session_state.get('saved_name', None)
    st.markdown(leaderboard_html(lb_data, highlight), unsafe_allow_html=True)

# ── Active Game ──
else:
    if st.session_state.last_result == 'correct':
        st.markdown("<div class='flash-correct'>✓ Correct! Keep going!</div>", unsafe_allow_html=True)

    p1, p2 = st.session_state.p1, st.session_state.p2

    left, mid, right = st.columns([11, 1, 11])
    with left:
        st.markdown(player_card_html(p1, show_value=True), unsafe_allow_html=True)
    with mid:
        st.markdown("<div class='vs-wrap'><div class='vs-badge'>VS</div></div>", unsafe_allow_html=True)
    with right:
        st.markdown(player_card_html(p2, show_value=False), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;color:#555;letter-spacing:0.2em;"
        "font-size:0.78rem;text-transform:uppercase;margin-bottom:0.8rem;'>"
        "Is their market value higher, lower, or the same?</p>",
        unsafe_allow_html=True
    )

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