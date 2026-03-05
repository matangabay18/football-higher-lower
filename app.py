import streamlit as st
import json
import random
import os
from datetime import datetime

st.set_page_config(page_title="Higher or Lower: Football", page_icon="⚽", layout="wide")

# ══════════════════════════════════════════
#  CSS + ANIMATIONS + SOUND
# ══════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;700&display=swap');

/* Hide the sidebar to store our invisible routing buttons */
[data-testid="stSidebar"] { display: none !important; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f; color: #f0f0f0;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stHeader"] { background: transparent; }
.main .block-container { padding: 1.5rem 2.5rem 4rem; max-width: 1300px; }

/* ── TITLE ── */
.game-title {
    font-family: 'Bebas Neue', cursive;
    font-size: clamp(3rem, 8vw, 6rem);
    letter-spacing: 0.05em; line-height: 1;
    text-align: center; margin-bottom: 0.1em;
    background: linear-gradient(135deg, #fff 0%, #a8ff78 50%, #78ffd6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.game-subtitle {
    text-align: center; font-size: 0.85rem; color: #555;
    letter-spacing: 0.35em; text-transform: uppercase; margin-bottom: 0.5rem;
}

/* ── LOBBY ── */
.lobby-intro {
    text-align: center; max-width: 520px; margin: 0.5rem auto 1.5rem;
    color: #888; font-size: 0.95rem; line-height: 1.6;
}
.lobby-step {
    display: flex; align-items: center; justify-content: center;
    gap: 0.5rem; font-size: 0.72rem; letter-spacing: 0.2em;
    text-transform: uppercase; color: #444; margin-bottom: 0.6rem;
}
.lobby-step-num {
    width: 22px; height: 22px; border-radius: 50%;
    background: rgba(168,255,120,0.15); border: 1px solid rgba(168,255,120,0.3);
    color: #a8ff78; font-size: 0.7rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
}

.option-card {
    padding: 1.1rem 0.8rem; border-radius: 16px; text-align: center;
    cursor: pointer; border: 2px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.03);
    transition: all 0.2s ease; position: relative;
}
.option-card:hover { border-color: rgba(168,255,120,0.3); background: rgba(168,255,120,0.05); transform: translateY(-2px); }
.option-card.sel-green  { border-color: #a8ff78 !important; background: rgba(168,255,120,0.12) !important; box-shadow: 0 0 24px rgba(168,255,120,0.25); }
.option-card.sel-orange { border-color: #ff9a3c !important; background: rgba(255,154,60,0.12) !important; box-shadow: 0 0 24px rgba(255,154,60,0.25); }
.option-card.sel-red    { border-color: #ff6b6b !important; background: rgba(255,107,107,0.12) !important; box-shadow: 0 0 24px rgba(255,107,107,0.25); }
.option-card.sel-blue   { border-color: #78b4ff !important; background: rgba(120,180,255,0.12) !important; box-shadow: 0 0 24px rgba(120,180,255,0.25); }
.check-badge {
    position: absolute; top: 8px; right: 10px;
    font-size: 0.8rem; color: #a8ff78;
}
.option-emoji { font-size: 1.8rem; margin-bottom: 0.3rem; }
.option-label { font-family: 'Bebas Neue', cursive; font-size: 1.15rem; letter-spacing: 0.04em; color: #fff; }
.option-desc  { font-size: 0.68rem; color: #666; margin-top: 0.15rem; line-height: 1.3; }

.lobby-divider { border: none; border-top: 1px solid rgba(255,255,255,0.05); margin: 1.5rem 0; }

.selected-summary {
    text-align: center; padding: 0.8rem 1.5rem;
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 50px; max-width: 480px; margin: 0 auto 1rem;
    font-size: 0.9rem; color: #888;
}

/* ── STATS BAR ── */
.stats-bar {
    display: flex; justify-content: center; align-items: center;
    gap: 0; margin: 1rem auto 0;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 50px; max-width: 700px; overflow: hidden;
}
.stat-item { flex: 1; padding: 0.6rem 1rem; text-align: center; border-right: 1px solid rgba(255,255,255,0.06); }
.stat-item:last-child { border-right: none; }
.stat-label { font-size: 0.58rem; letter-spacing: 0.2em; text-transform: uppercase; color: #555; margin-bottom: 0.1rem; }
.stat-val { font-family: 'Bebas Neue', cursive; font-size: 1.9rem; line-height: 1; background: linear-gradient(135deg, #a8ff78, #78ffd6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.stat-val.streak { background: linear-gradient(135deg, #ff9a3c, #ff6b6b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.stat-val.best   { background: linear-gradient(135deg, #ffd700, #ffaa00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }

/* ── VS ── */
.vs-wrap { display: flex; align-items: center; justify-content: center; height: 100%; min-height: 480px; }
.vs-badge { font-family: 'Bebas Neue', cursive; font-size: 1.3rem; width: 52px; height: 52px; border-radius: 50%; background: linear-gradient(135deg, #a8ff78, #78ffd6); color: #0a0a0f; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 32px rgba(168,255,120,0.55); }

/* ── PLAYER CARD ── */
.pcard { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; overflow: hidden; transition: box-shadow 0.3s; }
.pcard:hover { box-shadow: 0 0 0 1px rgba(168,255,120,0.2), 0 16px 48px rgba(0,0,0,0.5); }
.pcard-img { width: 100%; aspect-ratio: 3/4; overflow: hidden; background: #111; }
.pcard-img img { width: 100%; height: 100%; object-fit: cover; object-position: center top; display: block; }
.pcard-placeholder { width: 100%; aspect-ratio: 3/4; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.04); font-size: 5rem; }
.pcard-body { padding: 1rem 1.4rem 1.4rem; text-align: center; border-top: 1px solid rgba(255,255,255,0.05); }
.pcard-name { font-family: 'Bebas Neue', cursive; font-size: 1.8rem; letter-spacing: 0.04em; color: #fff; margin-bottom: 0.2rem; line-height: 1.1; }
.pcard-meta { font-size: 0.72rem; color: #555; margin-bottom: 0.3rem; }
.pcard-value  { font-size: 1.4rem; font-weight: 700; color: #a8ff78; }
.pcard-hidden { font-size: 0.8rem; color: #444; letter-spacing: 0.18em; text-transform: uppercase; margin-top: 0.2rem; }
.pcard-revealed { font-size: 1.3rem; font-weight: 700; color: #78ffd6; animation: popIn 0.4s ease; }

/* ── TRIVIA BOX ── */
.trivia-box {
    background: rgba(120,180,255,0.07); border: 1px solid rgba(120,180,255,0.25);
    border-radius: 12px; padding: 0.7rem 1.2rem; text-align: center;
    color: #a0c8ff; font-size: 0.85rem; margin-top: 0.8rem;
    animation: slideUp 0.4s ease;
}
.trivia-label { font-size: 0.6rem; letter-spacing: 0.2em; text-transform: uppercase; color: #5a8aaa; margin-bottom: 0.2rem; }

/* ── ANIMATIONS ── */
@keyframes popIn    { 0%{transform:scale(0.5);opacity:0} 70%{transform:scale(1.1)} 100%{transform:scale(1);opacity:1} }
@keyframes slideUp  { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
@keyframes slideIn  { from{opacity:0;transform:translateX(60px)} to{opacity:1;transform:translateX(0)} }
@keyframes fadeIn   { from{opacity:0} to{opacity:1} }
@keyframes shakeX   { 0%,100%{transform:translateX(0)} 20%{transform:translateX(-8px)} 40%{transform:translateX(8px)} 60%{transform:translateX(-5px)} 80%{transform:translateX(5px)} }

.anim-slide-in  { animation: slideIn 0.45s cubic-bezier(0.22,1,0.36,1); }
.anim-fade-in   { animation: fadeIn 0.35s ease; }
.anim-shake     { animation: shakeX 0.5s ease; }

/* ── HINT ── */
.hint-box { background: rgba(255,200,60,0.1); border: 1px solid rgba(255,200,60,0.3); border-radius: 10px; padding: 0.4rem 1rem; text-align: center; color: #ffc83c; font-size: 0.85rem; margin-top: 0.5rem; animation: slideUp 0.3s ease; }

/* ── BUTTONS ── */
div[data-testid="stButton"] button { font-family: 'DM Sans', sans-serif !important; font-weight: 700 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; height: 52px !important; border-radius: 12px !important; font-size: 0.9rem !important; }
.btn-higher div[data-testid="stButton"] button { background: linear-gradient(135deg, #a8ff78, #78ffd6) !important; color: #0a0a0f !important; border: none !important; box-shadow: 0 4px 20px rgba(168,255,120,0.3) !important; }
.btn-lower  div[data-testid="stButton"] button { background: rgba(255,255,255,0.05) !important; color: #ddd !important; border: 1px solid rgba(255,255,255,0.12) !important; }
.btn-same   div[data-testid="stButton"] button { background: rgba(255,200,60,0.08) !important; color: #ffc83c !important; border: 1px solid rgba(255,200,60,0.25) !important; }
.btn-hint   div[data-testid="stButton"] button { background: rgba(255,200,60,0.06) !important; color: #ffc83c !important; border: 1px solid rgba(255,200,60,0.2) !important; height: 40px !important; font-size: 0.78rem !important; }
div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(135deg, #a8ff78, #78ffd6) !important; color: #0a0a0f !important; border: none !important; height: 58px !important; font-size: 1rem !important; box-shadow: 0 6px 28px rgba(168,255,120,0.35) !important; }

/* ── FEEDBACK ── */
.flash-correct { background: rgba(168,255,120,0.07); border: 1px solid rgba(168,255,120,0.25); border-radius: 10px; padding: 0.5rem 1rem; text-align: center; color: #a8ff78; font-weight: 600; letter-spacing: 0.1em; margin-bottom: 0.8rem; font-size: 0.9rem; }
.flash-streak  { background: rgba(255,154,60,0.1); border: 1px solid rgba(255,154,60,0.3); border-radius: 10px; padding: 0.4rem 1rem; text-align: center; color: #ff9a3c; font-weight: 700; font-size: 1rem; margin-bottom: 0.5rem; animation: popIn 0.4s ease; }
.flash-wrong   { background: rgba(255,107,107,0.08); border: 1px solid rgba(255,107,107,0.25); border-radius: 10px; padding: 0.5rem 1rem; text-align: center; color: #ff6b6b; font-weight: 600; margin-bottom: 0.8rem; animation: shakeX 0.5s ease; }

/* ── GAME OVER ── */
.gameover-box { text-align: center; padding: 2.5rem 2rem 1.5rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 24px; max-width: 500px; margin: 1.5rem auto; }
.gameover-title { font-family: 'Bebas Neue', cursive; font-size: 3rem; background: linear-gradient(135deg, #ff6b6b, #ffc3a0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.gameover-score { font-family: 'Bebas Neue', cursive; font-size: 6rem; line-height: 1; background: linear-gradient(135deg, #a8ff78, #78ffd6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.gameover-label { font-size: 0.75rem; color: #555; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.5rem; }
.pb-badge { display: inline-block; background: rgba(255,215,0,0.1); border: 1px solid rgba(255,215,0,0.3); border-radius: 20px; padding: 0.3rem 1rem; color: #ffd700; font-size: 0.85rem; font-weight: 700; margin-bottom: 1rem; }

/* ── SHARE ── */
.share-box { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 1rem 1.5rem; text-align: center; margin: 0.8rem auto; max-width: 500px; }
.share-msg { font-size: 0.9rem; color: #ccc; background: rgba(255,255,255,0.05); border-radius: 8px; padding: 0.5rem 1rem; margin-bottom: 0.5rem; }

/* ── LEADERBOARD ── */
.lb-wrap { max-width: 680px; margin: 0 auto; }
.lb-title    { font-family: 'Bebas Neue', cursive; font-size: 1.6rem; letter-spacing: 0.08em; text-align: center; margin: 1.5rem 0 0.3rem; color: #fff; }
.lb-subtitle { text-align: center; font-size: 0.72rem; color: #555; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 0.8rem; }
.lb-table { width: 100%; border-collapse: collapse; }
.lb-table th { font-size: 0.62rem; letter-spacing: 0.2em; text-transform: uppercase; color: #444; padding: 0.4rem 0.8rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.06); }
.lb-table td { padding: 0.55rem 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.88rem; color: #aaa; }
.lb-table tr:nth-child(1) td { color: #ffd700; font-weight: 700; }
.lb-table tr:nth-child(2) td { color: #c0c0c0; font-weight: 600; }
.lb-table tr:nth-child(3) td { color: #cd7f32; font-weight: 600; }
.lb-rank { font-family: 'Bebas Neue', cursive; font-size: 1.1rem; color: #444; }
.lb-score-val { font-family: 'Bebas Neue', cursive; font-size: 1.2rem; color: #a8ff78; }
.lb-highlight td { background: rgba(168,255,120,0.05); color: #a8ff78 !important; }

/* ── INPUTS — black text ── */
div[data-testid="stTextInput"] input {
    background: #ffffff !important; border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important; color: #000000 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 1rem !important;
    padding: 0.6rem 1rem !important; text-align: center !important;
}
/* ALL selectbox / dropdown text → black */
div[data-testid="stSelectbox"] div[data-baseweb="select"] * { color: #000000 !important; }
div[data-baseweb="select"] { background: #ffffff !important; border-radius: 10px !important; }
div[data-baseweb="popover"] * { color: #000000 !important; background: #ffffff !important; }
div[data-baseweb="menu"]    * { color: #000000 !important; }

/* ALL regular buttons in lobby → black text so it's readable */
div[data-testid="stButton"] button {
    color: #000000 !important;
    background: #ffffff !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
}
/* Override back for game buttons that need their own colors */
.btn-higher div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #a8ff78, #78ffd6) !important;
    color: #0a0a0f !important; border: none !important;
    box-shadow: 0 4px 20px rgba(168,255,120,0.3) !important;
}
.btn-lower div[data-testid="stButton"] button {
    background: rgba(30,30,40,0.8) !important;
    color: #dddddd !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
}
.btn-same div[data-testid="stButton"] button {
    background: rgba(40,35,10,0.8) !important;
    color: #ffc83c !important;
    border: 1px solid rgba(255,200,60,0.3) !important;
}
.btn-hint div[data-testid="stButton"] button {
    background: rgba(40,35,10,0.6) !important;
    color: #ffc83c !important;
    border: 1px solid rgba(255,200,60,0.25) !important;
    height: 40px !important; font-size: 0.78rem !important;
}
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #a8ff78, #78ffd6) !important;
    color: #0a0a0f !important; border: none !important;
    height: 58px !important; font-size: 1rem !important;
    box-shadow: 0 6px 28px rgba(168,255,120,0.35) !important;
}

#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
hr { border-color: rgba(255,255,255,0.05) !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════
#  SOUND ENGINE  (Web Audio API via JS)
# ══════════════════════════════════════════
def play_sound(sound_type):
    """Play sound using st.components.v1.html — the only way JS reliably runs in Streamlit."""
    import streamlit.components.v1 as components

    scripts = {
        'correct': """
            var a=new(window.AudioContext||window.webkitAudioContext)();
            var o=a.createOscillator(),g=a.createGain();
            o.connect(g);g.connect(a.destination);o.type='sine';
            o.frequency.setValueAtTime(523,a.currentTime);
            o.frequency.setValueAtTime(659,a.currentTime+0.12);
            o.frequency.setValueAtTime(784,a.currentTime+0.24);
            g.gain.setValueAtTime(0.25,a.currentTime);
            g.gain.exponentialRampToValueAtTime(0.001,a.currentTime+0.6);
            o.start();o.stop(a.currentTime+0.6);
        """,
        'wrong': """
            var a=new(window.AudioContext||window.webkitAudioContext)();
            var o=a.createOscillator(),g=a.createGain();
            o.connect(g);g.connect(a.destination);o.type='sawtooth';
            o.frequency.setValueAtTime(280,a.currentTime);
            o.frequency.exponentialRampToValueAtTime(80,a.currentTime+0.4);
            g.gain.setValueAtTime(0.3,a.currentTime);
            g.gain.exponentialRampToValueAtTime(0.001,a.currentTime+0.45);
            o.start();o.stop(a.currentTime+0.45);
        """,
        'streak': """
            var freqs=[523,659,784,1047];
            freqs.forEach(function(f,i){
                setTimeout(function(){
                    var a=new(window.AudioContext||window.webkitAudioContext)();
                    var o=a.createOscillator(),g=a.createGain();
                    o.connect(g);g.connect(a.destination);o.type='sine';
                    o.frequency.value=f;
                    g.gain.setValueAtTime(0.2,a.currentTime);
                    g.gain.exponentialRampToValueAtTime(0.001,a.currentTime+0.25);
                    o.start();o.stop(a.currentTime+0.25);
                }, i*100);
            });
        """,
        'pb': """
            var freqs=[784,988,1175,1568,2093];
            freqs.forEach(function(f,i){
                setTimeout(function(){
                    var a=new(window.AudioContext||window.webkitAudioContext)();
                    var o=a.createOscillator(),g=a.createGain();
                    o.connect(g);g.connect(a.destination);o.type='sine';
                    o.frequency.value=f;
                    g.gain.setValueAtTime(0.15,a.currentTime);
                    g.gain.exponentialRampToValueAtTime(0.001,a.currentTime+0.3);
                    o.start();o.stop(a.currentTime+0.3);
                }, i*110);
            });
        """,
        'click': """
            var a=new(window.AudioContext||window.webkitAudioContext)();
            var o=a.createOscillator(),g=a.createGain();
            o.connect(g);g.connect(a.destination);o.type='sine';
            o.frequency.value=900;
            g.gain.setValueAtTime(0.08,a.currentTime);
            g.gain.exponentialRampToValueAtTime(0.001,a.currentTime+0.08);
            o.start();o.stop(a.currentTime+0.08);
        """,
    }

    js = scripts.get(sound_type, '')
    if not js:
        return

    components.html(f"""
    <!DOCTYPE html><html><body>
    <script>
        (function() {{
            try {{
                {js}
            }} catch(e) {{ console.log('Sound error:', e); }}
        }})();
    </script>
    </body></html>
    """, height=0, width=0)


# ══════════════════════════════════════════
#  TRIVIA DATABASE
# ══════════════════════════════════════════
TRIVIA = {
    "Lamine Yamal": "Became the youngest player to score at a European Championship at age 16.",
    "Erling Haaland": "Scored 36 Premier League goals in his debut season — a new record.",
    "Kylian Mbappé": "Won the World Cup with France at just 19 years old in 2018.",
    "Jude Bellingham": "Scored a bicycle kick to win El Clásico on his first attempt.",
    "Vinicius Junior": "Won the Ballon d'Or in 2024 — the first Brazilian to do so.",
    "Pedri": "Won the Golden Boy award in 2021 after a stunning debut season.",
    "Jamal Musiala": "Born in Germany, raised in England, chose to play for Germany.",
    "Bukayo Saka": "Arsenal's most important player — voted Player of the Season twice.",
    "Cole Palmer": "Scored 4 goals in a single Premier League match for Chelsea.",
    "Declan Rice": "Became Arsenal's record signing at £105m in 2023.",
    "Florian Wirtz": "Scored the fastest goal in Bundesliga history at age 17.",
    "Rodri": "Won Euro 2024 and the Champions League in the same season.",
    "Mohamed Salah": "Holds the record for most Premier League goals in a 38-game season (32).",
    "Harry Kane": "England's all-time leading scorer with over 60 international goals.",
    "Trent Alexander-Arnold": "Has more assists than any other defender in Premier League history.",
}


def get_trivia(player_name):
    # Exact match first
    if player_name in TRIVIA:
        return TRIVIA[player_name]
    # Partial match
    for key, val in TRIVIA.items():
        if key.lower() in player_name.lower() or player_name.lower() in key.lower():
            return val
    # Generic facts based on position/league
    return None


# ══════════════════════════════════════════
#  LOAD PLAYERS
# ══════════════════════════════════════════
@st.cache_data
def load_data():
    with open('players.json', 'r', encoding='utf-8') as f:
        return json.load(f)


ALL_PLAYERS = load_data()
ALL_LEAGUES = sorted(set(
    p.get('league', '') for p in ALL_PLAYERS
    if p.get('league') and p.get('league') not in ('Unknown', '')
))


# ══════════════════════════════════════════
#  LEADERBOARD
# ══════════════════════════════════════════
def lb_key(difficulty, league):
    safe = league.replace(' ', '_').replace('/', '_')
    return f"leaderboard_{difficulty}_{safe}.json"


def load_lb(difficulty, league):
    path = lb_key(difficulty, league)
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except:
            return []
    return []


def save_lb(difficulty, league, name, score):
    path = lb_key(difficulty, league)
    data = load_lb(difficulty, league)
    data.append({"name": name.strip(), "score": score, "date": datetime.now().strftime("%d/%m/%Y")})
    data = sorted(data, key=lambda x: x['score'], reverse=True)[:100]
    with open(path, 'w') as f: json.dump(data, f, indent=2)
    return data


# ══════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════
DEFAULTS = {
    'screen': 'lobby',
    'difficulty': None, 'league': None,
    'score': 0, 'streak': 0, 'max_streak': 0, 'personal_best': 0,
    'new_pb': False, 'score_saved': False, 'saved_name': None,
    'hint_used': False, 'show_hint': False,
    'last_result': None, 'p1': None, 'p2': None,
    'lobby_diff': 'Medium', 'lobby_league': 'All Leagues',
    'pending_sound': None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════
#  PLAYER POOL
# ══════════════════════════════════════════
def get_pool():
    pool = ALL_PLAYERS
    if st.session_state.league and st.session_state.league != 'All Leagues':
        pool = [p for p in pool if p.get('league') == st.session_state.league]
    return pool if len(pool) >= 2 else ALL_PLAYERS


def pick_player(exclude_name=None):
    pool = get_pool()
    if exclude_name:
        pool = [p for p in pool if p['name'] != exclude_name]
    if not pool: pool = ALL_PLAYERS
    diff = st.session_state.difficulty
    base = st.session_state.p1
    if diff == 'Easy' and base:
        easy = [p for p in pool if abs(p['value'] - base['value']) > base['value'] * 0.25]
        if easy: return random.choice(easy)
    elif diff == 'Hard' and base:
        hard = [p for p in pool if abs(p['value'] - base['value']) < base['value'] * 0.12]
        if hard: return random.choice(hard)
    return random.choice(pool)


# ══════════════════════════════════════════
#  GAME ACTIONS
# ══════════════════════════════════════════
def start_game():
    pool = get_pool()
    p1 = random.choice(pool)
    st.session_state.p1 = p1
    st.session_state.p2 = pick_player(p1['name'])
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.max_streak = 0
    st.session_state.new_pb = False
    st.session_state.score_saved = False
    st.session_state.saved_name = None
    st.session_state.hint_used = False
    st.session_state.show_hint = False
    st.session_state.last_result = None
    st.session_state.screen = 'game'
    st.session_state.pending_sound = 'click'


def check_guess(guess):
    v1, v2 = st.session_state.p1['value'], st.session_state.p2['value']
    correct = (
            (guess == 'higher' and v2 >= v1) or
            (guess == 'lower' and v2 <= v1) or
            (guess == 'same' and v1 == v2)
    )
    if correct:
        st.session_state.score += 1
        st.session_state.streak += 1
        st.session_state.max_streak = max(st.session_state.streak, st.session_state.max_streak)
        st.session_state.last_result = 'correct'
        st.session_state.pending_sound = 'streak' if st.session_state.streak >= 3 else 'correct'
    else:
        st.session_state.streak = 0
        st.session_state.last_result = 'wrong'
        st.session_state.pending_sound = 'wrong'
    st.session_state.screen = 'reveal'


def advance():
    if st.session_state.last_result == 'correct':
        st.session_state.p1 = st.session_state.p2
        st.session_state.p2 = pick_player(st.session_state.p1['name'])
        st.session_state.hint_used = False
        st.session_state.show_hint = False
        st.session_state.screen = 'game'
        st.session_state.pending_sound = 'click'
    else:
        if st.session_state.score > st.session_state.personal_best:
            st.session_state.personal_best = st.session_state.score
            st.session_state.new_pb = True
            st.session_state.pending_sound = 'pb'
        st.session_state.screen = 'gameover'


def go_lobby():
    st.session_state.screen = 'lobby'
    st.session_state.difficulty = None
    st.session_state.league = None


# ══════════════════════════════════════════
#  HTML HELPERS
# ══════════════════════════════════════════
def card_html(player, show_value, reveal=False, animate=False):
    img = player.get('image', '').strip()
    anim = 'anim-slide-in' if animate else ''
    img_block = (
        f'<div class="pcard-img"><img src="{img}" alt="{player["name"]}" referrerpolicy="no-referrer" crossorigin="anonymous"></div>'
        if img else '<div class="pcard-placeholder">⚽</div>'
    )
    club = player.get('club', '')
    league = player.get('league', '')
    meta_parts = [x for x in [club, league] if x and x != 'Unknown']
    meta = f'<div class="pcard-meta">{" · ".join(meta_parts)}</div>' if meta_parts else ''

    if reveal:
        val_html = f'<div class="pcard-revealed">{player["display_value"]}</div>'
    elif show_value:
        val_html = f'<div class="pcard-value">{player["display_value"]}</div>'
    else:
        val_html = '<div class="pcard-hidden">??? · Make your guess</div>'

    return f'<div class="pcard {anim}">{img_block}<div class="pcard-body"><div class="pcard-name">{player["name"]}</div>{meta}{val_html}</div></div>'


def lb_html(entries, highlight=None):
    if not entries:
        return "<p style='text-align:center;color:#444;padding:1rem'>No scores yet — be the first!</p>"
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    rows = ""
    for i, e in enumerate(entries[:15], 1):
        rank = medals.get(i, f'<span class="lb-rank">{i}</span>')
        hl = "lb-highlight" if (highlight and e['name'].lower() == highlight.lower()) else ""
        rows += f'<tr class="{hl}"><td>{rank}</td><td>{e["name"]}</td><td><span class="lb-score-val">{e["score"]}</span></td><td style="color:#444;font-size:0.72rem">{e["date"]}</td></tr>'
    return f'<table class="lb-table"><thead><tr><th>#</th><th>Name</th><th>Score</th><th>Date</th></tr></thead><tbody>{rows}</tbody></table>'


# ══════════════════════════════════════════
#  HEADER (always shown)
# ══════════════════════════════════════════
st.markdown("<p class='game-subtitle'>⚽ The Football Value Game</p>", unsafe_allow_html=True)
st.markdown("<h1 class='game-title'>Higher or Lower</h1>", unsafe_allow_html=True)

# Fire pending sounds
if st.session_state.pending_sound:
    play_sound(st.session_state.pending_sound)
    st.session_state.pending_sound = None

# ══════════════════════════════════════════
#  LOBBY
# ══════════════════════════════════════════
if st.session_state.screen == 'lobby':

    import streamlit.components.v1 as components

    # ── HIDDEN ROUTING BUTTONS (For smooth JS transitions) ──
    with st.sidebar:
        for diff in ["Easy", "Medium", "Hard"]:
            if st.button(f"set_diff_{diff}"):
                st.session_state.lobby_diff = diff
        for league in ["All Leagues"] + ALL_LEAGUES:
            if st.button(f"set_league_{league}"):
                st.session_state.lobby_league = league

    st.markdown(
        "<p class='lobby-intro'>Guess which footballer has a higher market value.<br>Pick your settings below and challenge the leaderboard!</p>",
        unsafe_allow_html=True)

    # ── STEP 1: Difficulty ──
    st.markdown("""<div class='lobby-step'>
        <div class='lobby-step-num'>1</div>
        <span>Choose your difficulty</span>
    </div>""", unsafe_allow_html=True)

    diff_meta = {
        "Easy": ("🟢", "Players far apart in value", "#a8ff78", "rgba(168,255,120,0.12)", "rgba(168,255,120,0.2)"),
        "Medium": ("🟡", "Standard game, balanced pairs", "#ff9a3c", "rgba(255,154,60,0.12)", "rgba(255,154,60,0.2)"),
        "Hard": (
        "🔴", "Very similar values, hard to tell", "#ff6b6b", "rgba(255,107,107,0.12)", "rgba(255,107,107,0.2)"),
    }

    diff_cols = st.columns(3)
    for col, label in zip(diff_cols, ["Easy", "Medium", "Hard"]):
        with col:
            is_sel = st.session_state.lobby_diff == label
            emoji, desc, c1, c2, c3 = diff_meta[label]
            style = f"border:2px solid {c1};background:{c2};box-shadow:0 0 24px {c3};" if is_sel else "border:2px solid rgba(255,255,255,0.07);background:rgba(255,255,255,0.03);"
            check = f'<span style="position:absolute;top:8px;right:10px;color:{c1};font-size:1rem">✓</span>' if is_sel else ""

            # Increased padding and height to prevent shadow clipping
            components.html(f"""<!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap" rel="stylesheet">
            <style>body{{margin:0;padding:12px;background:transparent;overflow:hidden}}
            .card{{cursor:pointer;border-radius:16px;padding:1.1rem 0.7rem;text-align:center;position:relative;{style}transition:all 0.2s;user-select:none;width:100%;box-sizing:border-box}}
            .card:active{{filter:brightness(1.2)}}
            </style></head><body>
            <div class="card" onclick="
                window.parent.postMessage({{key:'diff',val:'{label}'}}, '*');
                this.style.filter='brightness(1.3)';
            ">
                {check}
                <div style="font-size:1.8rem;margin-bottom:4px">{emoji}</div>
                <div style="font-family:Bebas Neue,cursive;font-size:1.3rem;color:#fff;letter-spacing:0.05em">{label}</div>
                <div style="font-size:0.7rem;color:#888;margin-top:3px">{desc}</div>
            </div>
            </body></html>""", height=145)

    # Catch postMessage and click the hidden sidebar buttons for a smooth, no-reload update
    components.html("""<!DOCTYPE html><html><body style="margin:0;padding:0;background:transparent">
    <script>
    if (!window.parent._st_lobby_listener) {
        window.parent.addEventListener('message', function(e) {
            let doc = window.parent.document;
            let btns = Array.from(doc.querySelectorAll('[data-testid="stSidebar"] button'));

            if (e.data && e.data.key === 'diff') {
                let target = btns.find(b => b.textContent.trim() === 'set_diff_' + e.data.val);
                if (target) target.click();
            }
            if (e.data && e.data.key === 'league') {
                let target = btns.find(b => b.textContent.trim() === 'set_league_' + e.data.val.replace(/_/g, ' '));
                if (target) target.click();
            }
        });
        window.parent._st_lobby_listener = true;
    }
    </script>
    </body></html>""", height=0)

    st.markdown("<hr class='lobby-divider'>", unsafe_allow_html=True)

    # ── STEP 2: League ──
    st.markdown("""<div class='lobby-step'>
        <div class='lobby-step-num'>2</div>
        <span>Choose a league (or play all)</span>
    </div>""", unsafe_allow_html=True)

    league_logo = {
        "All Leagues": "",
        "Premier League": "https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg",
        "La Liga": "https://upload.wikimedia.org/wikipedia/commons/5/54/LaLiga_logo_2023.svg",
        "Bundesliga": "https://upload.wikimedia.org/wikipedia/en/d/df/Bundesliga_logo_%282017%29.svg",
        "Serie A": "https://upload.wikimedia.org/wikipedia/en/e/e1/Serie_A_logo_%282019%29.svg",
        "Ligue 1": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Ligue1_Uber_Eats_2020.svg",
        "Primeira Liga": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Liga_Portugal_logo.svg",
        "Eredivisie": "https://upload.wikimedia.org/wikipedia/commons/0/0f/Eredivisie_nieuw_logo_2017-.svg",
    }
    league_opts = ["All Leagues"] + ALL_LEAGUES

    for row_start in range(0, len(league_opts), 4):
        chunk = league_opts[row_start:row_start + 4]
        while len(chunk) < 4:
            chunk.append(None)
        cols = st.columns(4)
        for col, label in zip(cols, chunk):
            with col:
                if label is None:
                    st.markdown("<div style='height:100px'></div>", unsafe_allow_html=True)
                    continue
                is_sel = st.session_state.lobby_league == label
                style = "border:2px solid #78b4ff;background:rgba(120,180,255,0.12);box-shadow:0 0 20px rgba(120,180,255,0.2);" if is_sel else "border:2px solid rgba(255,255,255,0.07);background:rgba(255,255,255,0.03);"
                check = '<span style="position:absolute;top:6px;right:8px;color:#78b4ff;font-size:0.9rem">✓</span>' if is_sel else ""
                logo_url = league_logo.get(label, "")
                logo_html = f'<img src="{logo_url}" style="width:44px;height:44px;object-fit:contain;margin-bottom:4px;display:block;margin-left:auto;margin-right:auto" referrerpolicy="no-referrer">' if logo_url else '<div style="font-size:1.8rem;margin-bottom:4px">&#127757;</div>'
                safe = label.replace(" ", "_")

                # Increased padding and height to prevent shadow clipping
                components.html(f"""<!DOCTYPE html><html><head>
                <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap" rel="stylesheet">
                <style>body{{margin:0;padding:12px;background:transparent;overflow:hidden}}
                .card{{cursor:pointer;border-radius:16px;padding:0.85rem 0.5rem;text-align:center;position:relative;{style}transition:all 0.2s;user-select:none;width:100%;box-sizing:border-box;min-height:90px}}
                .card:active{{filter:brightness(1.2)}}
                </style></head><body>
                <div class="card" onclick="window.parent.postMessage({{key:'league',val:'{safe}'}},'*');this.style.filter='brightness(1.3)'">
                    {check}{logo_html}
                    <div style="font-family:Bebas Neue,cursive;font-size:0.85rem;color:#fff;letter-spacing:0.03em">{label}</div>
                </div>
                </body></html>""", height=130)
        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

    st.markdown("<hr class='lobby-divider'>", unsafe_allow_html=True)

    diff_colors = {"Easy": "#a8ff78", "Medium": "#ffc83c", "Hard": "#ff6b6b"}
    dc = diff_colors.get(st.session_state.lobby_diff, "#fff")
    st.markdown(f"""<div class='selected-summary'>
        Playing: <strong style='color:{dc}'>{st.session_state.lobby_diff}</strong>
        &nbsp;&middot;&nbsp;
        <strong style='color:#a8ff78'>{st.session_state.lobby_league}</strong>
    </div>""", unsafe_allow_html=True)

    _, pc, _ = st.columns([1, 2, 1])
    with pc:
        if st.button("⚽  Play Now", type="primary", use_container_width=True, key="play_now"):
            st.session_state.difficulty = st.session_state.lobby_diff
            st.session_state.league = st.session_state.lobby_league
            start_game()
            st.rerun()

    st.markdown(f"<div class='lb-title'>🏆 Top Scores</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='lb-subtitle'>{st.session_state.lobby_diff} &middot; {st.session_state.lobby_league}</div>",
        unsafe_allow_html=True)
    st.markdown(
        f"<div class='lb-wrap'>{lb_html(load_lb(st.session_state.lobby_diff, st.session_state.lobby_league))}</div>",
        unsafe_allow_html=True)


# ══════════════════════════════════════════
#  GAME SCREEN
# ══════════════════════════════════════════
elif st.session_state.screen == 'game':

    streak_emoji = "🔥" if st.session_state.streak >= 3 else ""
    diff_colors = {"Easy": "#a8ff78", "Medium": "#ffc83c", "Hard": "#ff6b6b"}
    dc = diff_colors.get(st.session_state.difficulty, "#fff")
    st.markdown(f"""
    <div class='stats-bar'>
        <div class='stat-item'><div class='stat-label'>Score</div><div class='stat-val'>{st.session_state.score}</div></div>
        <div class='stat-item'><div class='stat-label'>Streak {streak_emoji}</div><div class='stat-val streak'>{st.session_state.streak}</div></div>
        <div class='stat-item'><div class='stat-label'>Best</div><div class='stat-val best'>{st.session_state.personal_best}</div></div>
        <div class='stat-item'><div class='stat-label'>Mode</div><div class='stat-val' style='font-size:1rem;color:{dc}'>{st.session_state.difficulty}</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Feedback
    if st.session_state.last_result == 'correct':
        if st.session_state.streak >= 5:
            st.markdown(f"<div class='flash-streak'>🔥 {st.session_state.streak} IN A ROW! ON FIRE!</div>",
                        unsafe_allow_html=True)
        elif st.session_state.streak >= 3:
            st.markdown(f"<div class='flash-streak'>🔥 {st.session_state.streak} streak!</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='flash-correct'>✓ Correct! Keep going!</div>", unsafe_allow_html=True)

    p1, p2 = st.session_state.p1, st.session_state.p2
    left, mid, right = st.columns([11, 1, 11])
    with left:
        st.markdown(card_html(p1, show_value=True), unsafe_allow_html=True)
    with mid:
        st.markdown("<div class='vs-wrap'><div class='vs-badge'>VS</div></div>", unsafe_allow_html=True)
    with right:
        # Animate p2 card sliding in
        st.markdown(card_html(p2, show_value=False, animate=True), unsafe_allow_html=True)
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
        "<p style='text-align:center;color:#555;letter-spacing:0.2em;font-size:0.78rem;text-transform:uppercase;margin-bottom:0.8rem'>Is their market value higher, lower, or the same?</p>",
        unsafe_allow_html=True)

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

    st.markdown("<br>", unsafe_allow_html=True)
    _, bc, _ = st.columns([2, 1, 2])
    with bc:
        if st.button("← Change Mode", use_container_width=True):
            go_lobby();
            st.rerun()


# ══════════════════════════════════════════
#  REVEAL SCREEN
# ══════════════════════════════════════════
elif st.session_state.screen == 'reveal':

    result_color = "#a8ff78" if st.session_state.last_result == 'correct' else "#ff6b6b"
    result_text = "✓ Correct!" if st.session_state.last_result == 'correct' else "✗ Wrong!"
    anim_cls = "anim-fade-in" if st.session_state.last_result == 'correct' else "anim-shake"

    st.markdown(
        f"<div class='{anim_cls}' style='text-align:center;font-size:1.5rem;font-weight:700;color:{result_color};margin-bottom:0.8rem'>{result_text}</div>",
        unsafe_allow_html=True)

    p1, p2 = st.session_state.p1, st.session_state.p2
    left, mid, right = st.columns([11, 1, 11])
    with left:
        st.markdown(card_html(p1, show_value=True), unsafe_allow_html=True)
    with mid:
        st.markdown("<div class='vs-wrap'><div class='vs-badge'>VS</div></div>", unsafe_allow_html=True)
    with right:
        st.markdown(card_html(p2, show_value=False, reveal=True), unsafe_allow_html=True)

        # Trivia box
        trivia = get_trivia(p2['name'])
        if not trivia:
            trivia = get_trivia(p1['name'])
            trivia_player = p1['name'] if trivia else None
        else:
            trivia_player = p2['name']

        if trivia:
            st.markdown(f"""<div class='trivia-box'>
                <div class='trivia-label'>⚡ Did you know · {trivia_player}</div>
                {trivia}
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, cc, _ = st.columns([1, 2, 1])
    with cc:
        label = "➡️ Next Player" if st.session_state.last_result == 'correct' else "📊 See Results"
        st.button(label, on_click=advance, type="primary", use_container_width=True)


# ══════════════════════════════════════════
#  GAME OVER SCREEN
# ══════════════════════════════════════════
elif st.session_state.screen == 'gameover':

    final = st.session_state.score
    pb_html = '<div class="pb-badge">🏆 New Personal Best!</div>' if st.session_state.new_pb else ""

    st.markdown(f"""<div class='gameover-box'>
        <div class='gameover-title'>Game Over</div>
        <div class='gameover-score'>{final}</div>
        <div class='gameover-label'>Best Streak: {st.session_state.max_streak} · {st.session_state.difficulty} · {st.session_state.league}</div>
        {pb_html}
    </div>""", unsafe_allow_html=True)

    share_text = f"⚽ I scored {final} on Football Higher or Lower! ({st.session_state.difficulty} · {st.session_state.league}) Can you beat me? 🔥"
    st.markdown(f"""<div class='share-box'>
        <div style='font-size:0.8rem;color:#666;margin-bottom:0.4rem'>Share your score:</div>
        <div class='share-msg'>{share_text}</div>
    </div>""", unsafe_allow_html=True)
    _, sc2, _ = st.columns([1, 2, 1])
    with sc2:
        if st.button("📋 Copy Share Message", use_container_width=True):
            st.success(f'Copy this: {share_text}')

    st.markdown("<hr>", unsafe_allow_html=True)

    if not st.session_state.score_saved:
        st.markdown(
            "<p style='text-align:center;color:#888;font-size:0.9rem;margin:0.5rem 0 0.3rem'>Save your score to the leaderboard:</p>",
            unsafe_allow_html=True)
        _, inp, _ = st.columns([1, 2, 1])
        with inp:
            pname = st.text_input("", placeholder="Your name...", key="name_input")
            s1, s2 = st.columns(2)
            with s1:
                if st.button("💾 Save Score", use_container_width=True, type="primary"):
                    if pname.strip():
                        save_lb(st.session_state.difficulty, st.session_state.league, pname, final)
                        st.session_state.score_saved = True
                        st.session_state.saved_name = pname.strip()
                        st.rerun()
                    else:
                        st.warning("Enter your name!")
            with s2:
                if st.button("🔄 Play Again", use_container_width=True):
                    start_game();
                    st.rerun()
    else:
        st.markdown(
            "<p style='text-align:center;color:#a8ff78;font-weight:600;margin:0.3rem 0 1rem'>✓ Score saved!</p>",
            unsafe_allow_html=True)
        r1, r2, _ = st.columns([1, 1, 1])
        with r1:
            if st.button("🔄 Play Again", use_container_width=True, type="primary"):
                start_game();
                st.rerun()
        with r2:
            if st.button("⚡ Change Mode", use_container_width=True):
                go_lobby();
                st.rerun()

    st.markdown(f"<div class='lb-title'>🏆 Leaderboard</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='lb-subtitle'>{st.session_state.difficulty} · {st.session_state.league}</div>",
                unsafe_allow_html=True)
    st.markdown(
        f"<div class='lb-wrap'>{lb_html(load_lb(st.session_state.difficulty, st.session_state.league), st.session_state.saved_name)}</div>",
        unsafe_allow_html=True)