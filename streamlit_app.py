import streamlit as st
import sys, os
import pandas as pd
import plotly.graph_objects as go

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.selector import select_team, generate_insights, get_stat, VENUES, COUNTRIES

# ── Fix flat VENUES ────────────────────────────────────────────────────────
_s = next(iter(VENUES.values()), {})
if isinstance(_s, str):
    _FM = {"pace":{"pitch":"pace","country":"—","avg_score":280,"dew":False,"desc":""},
           "spin":{"pitch":"spin","country":"—","avg_score":260,"dew":False,"desc":""},
           "balanced":{"pitch":"balanced","country":"—","avg_score":270,"dew":False,"desc":""}}
    VENUES = {k:_FM.get(v,{"pitch":v,"country":"—","avg_score":270,"dew":False,"desc":""}) for k,v in VENUES.items()}

st.set_page_config(page_title="ODI XI Selector", page_icon="🏏",
                   layout="wide", initial_sidebar_state="expanded")

# ── Load full player dataset ───────────────────────────────────────────────
@st.cache_data
def load_full_data():
    base = os.path.dirname(os.path.abspath(__file__))
    paths = [
        os.path.join(base, "..", "backend", "data", "merged_odi_stats.csv"),
        os.path.join(base, "..", "data", "merged_odi_stats.csv"),
        os.path.join(os.getcwd(), "data", "merged_odi_stats.csv"),
        os.path.join(os.getcwd(), "backend", "data", "merged_odi_stats.csv"),
    ]
    for p in paths:
        n = os.path.normpath(p)
        if os.path.exists(n):
            df = pd.read_csv(n)
            df.columns = df.columns.str.strip()
            return df
    return pd.DataFrame()

FULL_DATA = load_full_data()

def get_player_full(name):
    if FULL_DATA.empty: return {}
    row = FULL_DATA[FULL_DATA["Player Name"] == name]
    if row.empty: return {}
    return row.iloc[0].to_dict()

# ══════════════════════════════════════════════════════════════════════════
# THEMES
# ══════════════════════════════════════════════════════════════════════════
THEMES = {
    "India":        {"bg":"#0C1830","surface":"#142040","surface2":"#1C2A52","border":"#2A4080",
                     "accent1":"#FF7A00","accent2":"#4A9EFF","text":"#C8DCFF","muted":"#4A6898",
                     "flag":"🇮🇳","glow":"rgba(255,122,0,0.25)","c1":"#FF9933","c2":"#FFFFFF","c3":"#138808",
                     "sw_strengths":["World-class top 3 — deep run-scoring ability","Bumrah + Shami = elite death bowling globally","3 allrounders extend batting to No.8","Spin variety: wrist-spin + left-arm orthodox"],
                     "sw_weaknesses":["Middle-order collapses if top 3 fail cheaply","Over-reliance on Virat Kohli in pressure chases","Only 1 genuine WK — no backup option","Pace-only attack struggles on flat spin tracks"]},
    "Australia":    {"bg":"#081A08","surface":"#102010","surface2":"#183018","border":"#264826",
                     "accent1":"#FFD700","accent2":"#5CBF5C","text":"#C8F0C8","muted":"#4A7A4A",
                     "flag":"🇦🇺","glow":"rgba(255,215,0,0.25)","c1":"#00008B","c2":"#FFD700","c3":"#CC0000",
                     "sw_strengths":["Dominant top-order with consistent 50+ partnerships","World-class pace trio","Aggressive batting from No.1 to No.8","Excellent record chasing under pressure"],
                     "sw_weaknesses":["Vulnerable vs quality spin on sub-continent","Middle order collapses in low-scoring games","Limited spin bowling options","Over-aggressive on slow tracks"]},
    "England":      {"bg":"#160A28","surface":"#1E1035","surface2":"#281442","border":"#3C2260",
                     "accent1":"#E53935","accent2":"#B39DDB","text":"#E8D8FF","muted":"#6A4A8A",
                     "flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","glow":"rgba(229,57,53,0.25)","c1":"#CC0000","c2":"#FFFFFF","c3":"#003087",
                     "sw_strengths":["Fearless Bazball batting philosophy","Quality swing bowling in overcast conditions","Deep batting order to No.9","Strong T20 crossover players"],
                     "sw_weaknesses":["Struggles on spinning sub-continent tracks","Top order brittle vs quality seam early","Dependent on overcast swing conditions","Inconsistent spin bowling"]},
    "Pakistan":     {"bg":"#001810","surface":"#002218","surface2":"#002E20","border":"#004830",
                     "accent1":"#00E676","accent2":"#A5D6A7","text":"#C0F5D8","muted":"#2A8A5A",
                     "flag":"🇵🇰","glow":"rgba(0,230,118,0.25)","c1":"#01411C","c2":"#FFFFFF","c3":"#01411C",
                     "sw_strengths":["Mercurial batting capable of 350+ any day","Natural reverse swing exponents at death","Leg-spin adds 4th bowling dimension","Strong in home spin conditions"],
                     "sw_weaknesses":["Inconsistency — can collapse under 150","Top-order technique questioned vs quality pace","Lower order very tail-heavy","Fielding below par vs top nations"]},
    "Bangladesh":   {"bg":"#180C00","surface":"#221400","surface2":"#2E1C00","border":"#483000",
                     "accent1":"#FF6D00","accent2":"#4CAF50","text":"#FFE5C8","muted":"#7A4A20",
                     "flag":"🇧🇩","glow":"rgba(255,109,0,0.25)","c1":"#006A4E","c2":"#F42A41","c3":"#006A4E",
                     "sw_strengths":["Spin trio world-class on home tracks","Shakib Al Hasan — most impactful allrounder","Excellent home record — genuine fortress","Liton Das provides explosive starts"],
                     "sw_weaknesses":["Away record significantly weaker","Pace bowling lacks penetration on fast tracks","Middle order collapses vs quality spin away","Fielding standard below top-8 nations"]},
    "South Africa": {"bg":"#0C1400","surface":"#141E00","surface2":"#1E2E00","border":"#304800",
                     "accent1":"#FFB300","accent2":"#76FF03","text":"#ECF5A8","muted":"#5A7A18",
                     "flag":"🇿🇦","glow":"rgba(255,179,0,0.25)","c1":"#007A4D","c2":"#FFB81C","c3":"#001489",
                     "sw_strengths":["Pace attack among most hostile globally","De Kock — one of best WK-batters ever","Excellent fielding saves 20+ runs per match","Rabada + Nortje = elite death bowling pair"],
                     "sw_weaknesses":["Historically struggle at ICC tournaments","Spin options thin outside Keshav Maharaj","Middle-order depth questioned","Away record on sub-continent poor"]},
    "Sri Lanka":    {"bg":"#050D1E","surface":"#0A1530","surface2":"#0E1E40","border":"#1A3060",
                     "accent1":"#F5A623","accent2":"#4A90D9","text":"#D8E8FF","muted":"#3A6090",
                     "flag":"🇱🇰","glow":"rgba(245,166,35,0.25)","c1":"#00247D","c2":"#F5A623","c3":"#8D153A",
                     "sw_strengths":["Home spin pitches unplayable for most teams","Mathews / Mendis veteran leadership","Hasaranga — elite wrist-spin worldwide","Home fortress: Premadasa historically dominant"],
                     "sw_weaknesses":["Away batting brittle vs high-quality pace","Pace bowling lacks consistent second option","Over-reliance on Hasaranga in spin conditions","Top order inconsistency in must-win games"]},
    "New Zealand":  {"bg":"#000E20","surface":"#001630","surface2":"#001E40","border":"#003060",
                     "accent1":"#00E5FF","accent2":"#FFFFFF","text":"#B8EEFF","muted":"#2A6080",
                     "flag":"🇳🇿","glow":"rgba(0,229,255,0.25)","c1":"#00247D","c2":"#CC142B","c3":"#FFFFFF",
                     "sw_strengths":["Disciplined team ethic — no weak link","Conway + Williamson = elite ODI partnership","Boult swings ball both ways in seam conditions","Consistent ICC tournament semi-finalists"],
                     "sw_weaknesses":["Smaller population — squad depth thinner","Spin bowling limited on sub-continent","Lower-order struggles vs quality death bowling","Home conditions may not replicate away"]},
    "_default":     {"bg":"#080E1A","surface":"#0E1826","surface2":"#162030","border":"#1E2E40",
                     "accent1":"#3B82F6","accent2":"#FFFFFF","text":"#C0D4EC","muted":"#304A64",
                     "flag":"🏏","glow":"rgba(59,130,246,0.2)","c1":"#3B82F6","c2":"#FFFFFF","c3":"#1D4ED8",
                     "sw_strengths":["Select a country to see analysis"],
                     "sw_weaknesses":["Select a country to see analysis"]},
}

def T(c=""): return THEMES.get(c, THEMES["_default"])
def pl(p): return {"pace":"Pace","spin":"Spin","balanced":"Balanced"}.get(p, p.title())
def rl(r): return {"wicketkeeper":"WK","allrounder":"All-Rounder","bowler":"Bowler","batter":"Batter"}.get(r, r.title())
def initials(n):
    p = n.split(); return (p[0][0]+p[-1][0]).upper() if len(p)>=2 else n[:2].upper()

# ══════════════════════════════════════════════════════════════════════════
# FLAG SVG BACKGROUND
# ══════════════════════════════════════════════════════════════════════════
def flag_svg_bg(country):
    th = T(country)
    c1, c2, c3, a1 = th["c1"], th["c2"], th["c3"], th["accent1"]
    return (
        '<div style="position:absolute;top:0;left:0;right:0;bottom:0;overflow:hidden;'
        'border-radius:inherit;pointer-events:none;z-index:0">'
        '<svg viewBox="0 0 1200 120" xmlns="http://www.w3.org/2000/svg" '
        'preserveAspectRatio="xMidYMid slice" style="width:100%;height:100%">'
        '<defs><filter id="sf"><feGaussianBlur stdDeviation="2.5"/></filter></defs>'
        f'<rect width="1200" height="40" fill="{c1}" opacity="0.15">'
        '<animate attributeName="height" values="40;48;40" dur="5s" repeatCount="indefinite"/></rect>'
        f'<rect y="40" width="1200" height="40" fill="{c2}" opacity="0.07">'
        '<animate attributeName="y" values="40;36;40" dur="5s" repeatCount="indefinite"/></rect>'
        f'<rect y="80" width="1200" height="40" fill="{c3}" opacity="0.15">'
        '<animate attributeName="y" values="80;76;80" dur="5s" repeatCount="indefinite"/></rect>'
        f'<path d="M0,25 Q300,10 600,25 Q900,40 1200,25" stroke="{c1}" stroke-width="1.5" '
        'fill="none" opacity="0.3" filter="url(#sf)">'
        '<animate attributeName="d" '
        'values="M0,25 Q300,10 600,25 Q900,40 1200,25;M0,25 Q300,40 600,25 Q900,10 1200,25;M0,25 Q300,10 600,25 Q900,40 1200,25" '
        'dur="4s" repeatCount="indefinite"/></path>'
        f'<circle cx="60" cy="60" r="50" fill="{a1}" opacity="0.07">'
        '<animate attributeName="r" values="50;65;50" dur="7s" repeatCount="indefinite"/></circle>'
        '</svg></div>'
    )

# ══════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════
def inject_css(country=""):
    th = T(country)
    a1 = th["accent1"]
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');
*,[class*="css"]{{font-family:'Outfit',sans-serif!important;box-sizing:border-box;}}
.mono{{font-family:'Fira Code',monospace!important;}}
.stApp,.main{{background:{th["bg"]}!important;}}
.block-container{{padding:0 2rem 4rem!important;max-width:1600px!important;}}
section[data-testid="stSidebar"]{{background:{th["surface"]}!important;border-right:1px solid {th["border"]}!important;}}
section[data-testid="stSidebar"] *{{color:{th["text"]}!important;}}
section[data-testid="stSidebar"] label{{color:{th["muted"]}!important;font-size:.63rem!important;text-transform:uppercase!important;letter-spacing:.16em!important;font-weight:600!important;}}
section[data-testid="stSidebar"] .stButton>button{{background:{a1}!important;color:#000!important;border:none!important;border-radius:8px!important;font-weight:700!important;font-size:.76rem!important;letter-spacing:.1em!important;text-transform:uppercase!important;padding:.65rem 1rem!important;box-shadow:0 4px 24px {th["glow"]}!important;}}
section[data-testid="stSidebar"] .stButton>button:hover{{opacity:.85!important;}}
hr{{border-color:{th["border"]}!important;margin:.6rem 0!important;}}
button[data-baseweb="tab"]{{font-size:.6rem!important;color:{th["muted"]}!important;text-transform:uppercase!important;letter-spacing:.14em!important;font-weight:600!important;}}
button[data-baseweb="tab"][aria-selected="true"]{{color:{a1}!important;border-bottom-color:{a1}!important;}}
header[data-testid="stHeader"]{{background:transparent!important;}}

/* Banner */
.ctry-banner{{position:relative;background:{th["surface"]};border-bottom:1px solid {th["border"]};padding:20px 2rem 18px;overflow:hidden;margin:0 -2rem 20px;}}
.ctry-inner{{position:relative;z-index:1;display:flex;align-items:center;gap:18px;}}
.ctry-flag{{font-size:2.8rem;line-height:1;filter:drop-shadow(0 0 16px {a1}88);}}
.ctry-name{{font-size:1.7rem;font-weight:700;color:{th["text"]};letter-spacing:-.02em;}}
.ctry-sub{{font-size:.56rem;color:{th["muted"]};text-transform:uppercase;letter-spacing:.22em;margin-top:3px;}}
.ctry-cap{{margin-left:auto;text-align:right;}}
.ctry-cap-name{{font-family:'Fira Code',monospace;font-size:1.05rem;color:{a1};text-shadow:0 0 20px {a1}88;}}
.ctry-cap-lbl{{font-size:.5rem;color:{th["muted"]};text-transform:uppercase;letter-spacing:.2em;margin-top:2px;}}

/* Metrics */
.mc{{background:{th["surface"]};border:1px solid {th["border"]};border-radius:10px;padding:11px 12px;text-align:center;}}
.mc:hover{{border-color:{a1}55;box-shadow:0 0 18px {th["glow"]};}}
.mv{{font-family:'Fira Code',monospace;font-size:.82rem;font-weight:500;color:{th["text"]};display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.ml{{font-size:.5rem;color:{th["muted"]};text-transform:uppercase;letter-spacing:.16em;margin-top:4px;}}

/* Section divider */
.sdiv{{display:flex;align-items:center;gap:10px;margin:10px 0 6px;}}
.sdiv-line{{flex:1;height:1px;background:{th["border"]};}}
.sdiv-text{{font-size:.52rem;font-weight:700;color:{a1}99;text-transform:uppercase;letter-spacing:.26em;white-space:nowrap;}}

/* ═══════════════════════════════════════════════════════════════
   PLAYER CARD WRAPPER
   The card HTML is rendered first (position:relative).
   The st.button is then made position:absolute, covering the
   entire card area — fully transparent so you see the card,
   but clicking anywhere fires the button.
   ═══════════════════════════════════════════════════════════════ */
.pc-wrap {{
  position: relative;
  margin-bottom: 4px;
}}
/* The visible card */
.pc {{
  display: flex;
  align-items: center;
  gap: 10px;
  background: {th["surface"]}CC;
  border: 1px solid {th["border"]};
  border-radius: 10px;
  padding: 9px 12px 9px 0;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  transition: border-color .2s, box-shadow .2s, background .2s, transform .15s;
  pointer-events: none;   /* card itself doesn't intercept — the button does */
}}
.pc-wrap:hover .pc {{
  border-color: {a1}66;
  background: {th["surface2"]}EE;
  box-shadow: 0 2px 22px {th["glow"]};
  transform: translateX(2px);
}}
/* The invisible full-coverage button */
.pc-wrap > div[data-testid="stButton"] {{
  position: absolute !important;
  top: 0 !important; left: 0 !important;
  right: 0 !important; bottom: 0 !important;
  z-index: 10 !important;
  margin: 0 !important;
}}
.pc-wrap > div[data-testid="stButton"] > button {{
  position: absolute !important;
  top: 0 !important; left: 0 !important;
  width: 100% !important; height: 100% !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  cursor: pointer !important;
  padding: 0 !important;
  border-radius: 10px !important;
  color: transparent !important;
  font-size: 0 !important;
}}
.pc-wrap > div[data-testid="stButton"] > button:hover,
.pc-wrap > div[data-testid="stButton"] > button:focus {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
}}

.stripe{{position:absolute;left:0;top:0;bottom:0;width:4px;background:{a1};opacity:.65;}}
.stripe-cap{{opacity:1;box-shadow:0 0 10px {a1};}}
.pnum{{font-family:'Fira Code',monospace;font-size:.63rem;color:{th["muted"]};min-width:28px;text-align:center;flex-shrink:0;}}
.av{{width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Fira Code',monospace;font-size:.72rem;font-weight:700;flex-shrink:0;border:2px solid {a1}44;background:{th["surface2"]};color:{a1}CC;}}
.av-cap{{border-color:{a1};box-shadow:0 0 14px {th["glow"]};}}
.pname{{font-size:.84rem;font-weight:600;color:{th["text"]};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.2;}}
.pname-cap{{color:{a1};}}
.ppos{{font-size:.56rem;color:{th["muted"]};text-transform:uppercase;letter-spacing:.1em;margin-top:2px;}}
.pstats{{display:flex;gap:12px;flex-shrink:0;margin-left:auto;padding-right:8px;}}
.sv{{font-family:'Fira Code',monospace;font-size:.76rem;font-weight:500;color:{th["text"]};text-align:right;display:block;white-space:nowrap;}}
.sl{{font-size:.48rem;color:{th["muted"]};text-transform:uppercase;letter-spacing:.1em;text-align:right;display:block;margin-top:1px;}}
.badge{{font-size:.49rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;padding:2px 6px;border-radius:4px;flex-shrink:0;white-space:nowrap;}}
.b-cap{{background:{a1}22;color:{a1};border:1px solid {a1}55;}}
.b-bat{{background:#1D4ED818;color:#60A5FA;border:1px solid #3B82F640;}}
.b-ar{{background:#15803D18;color:#4ADE80;border:1px solid #22C55E40;}}
.b-bow{{background:#B91C1C18;color:#F87171;border:1px solid #EF444440;}}
.b-wk{{background:#7C3AED18;color:#C084FC;border:1px solid #A855F740;}}

/* Insights */
.ic{{background:{th["surface"]};border:1px solid {th["border"]};border-left:3px solid {a1}66;border-radius:8px;padding:10px 13px;margin-bottom:5px;font-size:.77rem;color:{th["text"]}AA;line-height:1.8;}}
.ic b{{color:{th["text"]}DD;font-weight:600;}}
.vbox{{background:{th["bg"]};border:1px solid {th["border"]};border-left:3px solid {a1};border-radius:8px;padding:9px 12px;margin:6px 0;font-size:.7rem;color:{th["muted"]};line-height:1.7;}}
.vbox b{{color:{th["text"]}CC;font-weight:600;}}
.chart-card{{background:{th["surface"]};border:1px solid {th["border"]};border-radius:12px;padding:16px 18px;margin-bottom:4px;}}
.chart-title{{font-size:.56rem;font-weight:700;color:{th["muted"]};text-transform:uppercase;letter-spacing:.22em;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid {th["border"]};}}
.slabel{{font-size:.56rem;font-weight:700;color:{th["muted"]};text-transform:uppercase;letter-spacing:.22em;border-bottom:1px solid {th["border"]};padding-bottom:6px;margin-bottom:12px;}}
.sw-wrap{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px;}}
.sw-box{{border-radius:10px;padding:12px 14px;}}
.sw-box-s{{background:{th["surface"]};border:1px solid #22C55E30;border-top:3px solid #22C55E;}}
.sw-box-w{{background:{th["surface"]};border:1px solid #EF444430;border-top:3px solid #EF4444;}}
.sw-head{{font-size:.52rem;font-weight:700;text-transform:uppercase;letter-spacing:.22em;margin-bottom:8px;}}
.sw-head-s{{color:#4ADE80;}}.sw-head-w{{color:#F87171;}}
.sw-item{{font-size:.73rem;color:{th["text"]}99;line-height:1.7;padding:4px 0;border-bottom:1px solid {th["border"]}55;}}
.sw-item:last-child{{border-bottom:none;}}
.sw-dot-s{{color:#4ADE80;margin-right:5px;}}.sw-dot-w{{color:#F87171;margin-right:5px;}}

/* Profile page */
.profile-wrap{{background:{th["surface"]};border:1px solid {th["border"]};border-radius:14px;overflow:hidden;}}
.profile-hdr{{background:{th["surface2"]};border-bottom:1px solid {th["border"]};padding:18px 20px;display:flex;align-items:center;gap:16px;position:relative;overflow:hidden;}}
.profile-av{{width:64px;height:64px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Fira Code',monospace;font-size:1.3rem;font-weight:700;background:{th["surface"]};border:3px solid {a1};color:{a1};box-shadow:0 0 24px {th["glow"]};flex-shrink:0;position:relative;z-index:1;}}
.profile-name{{font-size:1.3rem;font-weight:700;color:{th["text"]};position:relative;z-index:1;}}
.profile-country{{font-size:.6rem;color:{th["muted"]};text-transform:uppercase;letter-spacing:.2em;margin-top:3px;position:relative;z-index:1;}}
.stat-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:{th["border"]};}}
.stat-cell{{background:{th["surface"]};padding:14px 10px;text-align:center;}}
.stat-cell-val{{font-family:'Fira Code',monospace;font-size:1.1rem;font-weight:500;color:{th["text"]};display:block;}}
.stat-cell-lbl{{font-size:.5rem;color:{th["muted"]};text-transform:uppercase;letter-spacing:.14em;margin-top:4px;}}
.stat-cell-accent{{color:{a1};}}

/* Venues */
.venue-card{{background:{th["surface"]};border:1px solid {th["border"]};border-radius:12px;padding:16px 18px;transition:all .2s;}}
.venue-card:hover{{border-color:{a1}55;box-shadow:0 4px 24px {th["glow"]};transform:translateY(-2px);}}
.vc-name{{font-size:.88rem;font-weight:600;color:{th["text"]};margin-bottom:4px;}}
.vc-country{{font-size:.58rem;color:{th["muted"]};text-transform:uppercase;letter-spacing:.14em;margin-bottom:10px;}}
.vc-pills{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;}}
.vc-pill{{font-size:.54rem;font-weight:700;padding:2px 8px;border-radius:4px;letter-spacing:.1em;text-transform:uppercase;}}
.vc-pill-pace{{background:#1D4ED820;color:#60A5FA;border:1px solid #3B82F640;}}
.vc-pill-spin{{background:#15803D20;color:#4ADE80;border:1px solid #22C55E40;}}
.vc-pill-balanced{{background:#78350F20;color:#FCD34D;border:1px solid #F59E0B40;}}
.vc-pill-dew{{background:#1E3A5F20;color:#93C5FD;border:1px solid #3B82F640;}}
.vc-score{{font-family:'Fira Code',monospace;font-size:1.4rem;font-weight:500;color:{a1};}}
.vc-score-lbl{{font-size:.5rem;color:{th["muted"]};text-transform:uppercase;letter-spacing:.14em;}}
.vc-desc{{font-size:.72rem;color:{th["muted"]};line-height:1.6;margin-top:8px;border-top:1px solid {th["border"]};padding-top:8px;}}

/* Back button */
.back-btn > div[data-testid="stButton"] > button {{
  background: {th["surface2"]} !important;
  border: 1px solid {a1}66 !important;
  color: {a1} !important;
  font-size: .7rem !important; font-weight: 700 !important;
  letter-spacing: .1em !important; text-transform: uppercase !important;
  padding: .45rem 1.2rem !important; border-radius: 8px !important;
  margin-bottom: 16px !important;
  box-shadow: 0 0 12px {th["glow"]} !important;
}}
.back-btn > div[data-testid="stButton"] > button:hover {{
  background: {a1}22 !important;
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# PLAYER PROFILE VIEW
# ══════════════════════════════════════════════════════════════════════════
def render_profile(name, row, country):
    th   = T(country)
    a1   = th["accent1"]
    pf   = get_player_full(name)
    role = str(row.get("role","batter")).lower()
    ini  = initials(name)

    runs     = int(get_stat(row, ["runs"]))
    bat_avg  = get_stat(row, ["bat_avg"])
    bat_sr   = get_stat(row, ["bat_sr"])
    innings  = int(pf.get("Innings Played", 0) or 0)
    matches  = int(get_stat(row, ["total_matches"]))
    wickets  = int(get_stat(row, ["wickets"]))
    bowl_avg = get_stat(row, ["bowl_avg"])
    bowl_sr  = get_stat(row, ["bowl_sr"])
    runs_con = int(pf.get("Runs Conceded", 0) or 0)
    pos      = str(pf.get("Batting Position", row.get("position",""))).title()

    rpi = f"{runs/innings:.1f}" if innings else "—"
    rpm = f"{runs/matches:.1f}" if matches else "—"

    st.markdown(f"""
<div class="profile-wrap">
  <div class="profile-hdr">
    {flag_svg_bg(country)}
    <div class="profile-av">{ini}</div>
    <div style="position:relative;z-index:1">
      <div class="profile-name">{name}</div>
      <div class="profile-country">{th['flag']} {country} &nbsp;·&nbsp; {pos} &nbsp;·&nbsp; {rl(role)}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="margin-top:2px">
  <div style="font-size:.52rem;font-weight:700;color:{th['muted']};text-transform:uppercase;letter-spacing:.22em;padding:12px 0 8px">Batting</div>
  <div class="stat-grid">
    <div class="stat-cell"><span class="stat-cell-val stat-cell-accent">{runs:,}</span><span class="stat-cell-lbl">ODI Runs</span></div>
    <div class="stat-cell"><span class="stat-cell-val">{bat_avg:.2f}</span><span class="stat-cell-lbl">Bat Average</span></div>
    <div class="stat-cell"><span class="stat-cell-val">{bat_sr:.2f}</span><span class="stat-cell-lbl">Strike Rate</span></div>
    <div class="stat-cell"><span class="stat-cell-val">{innings}</span><span class="stat-cell-lbl">Innings</span></div>
    <div class="stat-cell"><span class="stat-cell-val">{matches}</span><span class="stat-cell-lbl">Matches</span></div>
    <div class="stat-cell"><span class="stat-cell-val">{rpi}</span><span class="stat-cell-lbl">Runs/Inn</span></div>
    <div class="stat-cell"><span class="stat-cell-val">{rpm}</span><span class="stat-cell-lbl">Runs/Match</span></div>
    <div class="stat-cell"><span class="stat-cell-val">{pos}</span><span class="stat-cell-lbl">Position</span></div>
  </div>
</div>""", unsafe_allow_html=True)

    if wickets > 0 or role in ("bowler","allrounder"):
        st.markdown(f"""
<div style="margin-top:2px">
  <div style="font-size:.52rem;font-weight:700;color:{th['muted']};text-transform:uppercase;letter-spacing:.22em;padding:12px 0 8px">Bowling</div>
  <div class="stat-grid">
    <div class="stat-cell"><span class="stat-cell-val stat-cell-accent">{wickets}</span><span class="stat-cell-lbl">Wickets</span></div>
    <div class="stat-cell"><span class="stat-cell-val">{f"{bowl_avg:.2f}" if bowl_avg else "—"}</span><span class="stat-cell-lbl">Bowl Avg</span></div>
    <div class="stat-cell"><span class="stat-cell-val">{f"{bowl_sr:.2f}" if bowl_sr else "—"}</span><span class="stat-cell-lbl">Bowl SR</span></div>
    <div class="stat-cell"><span class="stat-cell-val">{runs_con:,}</span><span class="stat-cell-lbl">Runs Conceded</span></div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown(f'<div style="padding:14px 0 4px;font-size:.52rem;font-weight:700;color:{th["muted"]};text-transform:uppercase;letter-spacing:.22em">Performance Index</div>', unsafe_allow_html=True)
    items = [("Batting Avg", bat_avg, 60, "%"), ("Strike Rate", bat_sr, 140, ""), ("Matches", float(matches), 300, "")]
    if wickets > 0: items.append(("Wickets", float(wickets), 350, ""))
    for lbl, val, mx, sfx in items:
        pct = min(int(val/mx*100), 100) if mx else 0
        st.markdown(f"""
<div style="margin-bottom:10px">
  <div style="display:flex;justify-content:space-between;margin-bottom:4px">
    <span style="font-size:.68rem;color:{th['muted']};text-transform:uppercase;letter-spacing:.1em">{lbl}</span>
    <span style="font-family:'Fira Code',monospace;font-size:.72rem;color:{th['text']}">{val:.1f}{sfx}</span>
  </div>
  <div style="background:{th['border']};border-radius:3px;height:4px">
    <div style="width:{pct}%;height:100%;background:{a1};border-radius:3px;box-shadow:0 0 8px {th['glow']}"></div>
  </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# CHART HELPERS
# ══════════════════════════════════════════════════════════════════════════
_CFG = {"displayModeBar": False, "staticPlot": True}

def _base(th, h=280):
    return dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Outfit", size=10, color=th["muted"]),
                height=h, margin=dict(l=0, r=55, t=8, b=8))

def chart_hbar(df, col, country, hi_is_low=False):
    th = T(country); df = df[df[col]>0].sort_values(col, ascending=True).copy()
    if df.empty: return None
    hi = df[col].min() if hi_is_low else df[col].max()
    clr = [th["accent1"] if v==hi else th["surface2"] for v in df[col]]
    fig = go.Figure(go.Bar(x=df[col].round(1), y=df["player_name"], orientation="h",
        marker=dict(color=clr, line=dict(width=0)),
        text=df[col].apply(lambda v: str(int(v)) if v==int(v) else f"{v:.1f}"),
        textposition="outside", textfont=dict(size=9, color=th["muted"])))
    fig.update_layout(**_base(th),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=9, color=th["text"]), linecolor=th["border"]))
    return fig

def chart_donut(team, country):
    th = T(country); rc = team["role"].value_counts()
    clr_map = {"batter":"#3B82F6","allrounder":"#22C55E","bowler":"#EF4444","wicketkeeper":"#A855F7"}
    fig = go.Figure(go.Pie(labels=[rl(r) for r in rc.index], values=rc.values, hole=0.62,
        marker=dict(colors=[clr_map.get(r,"#1A3050") for r in rc.index], line=dict(color=th["bg"], width=3)),
        textfont=dict(size=9, color=th["muted"])))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit", size=9, color=th["muted"]), height=260,
        margin=dict(l=0,r=0,t=8,b=8), legend=dict(font=dict(size=9,color=th["muted"]),bgcolor="rgba(0,0,0,0)"))
    return fig

def chart_radar(team, country):
    th = T(country); top6 = team.sort_values("runs", ascending=False).head(6)
    cats = ["Runs","Bat Avg","Bat SR","Wickets","Bowl SR"]
    mx = {"runs":team["runs"].max() or 1,"bat_avg":80,"bat_sr":160,"wickets":team["wickets"].max() or 1,"bowl_sr":60}
    fig = go.Figure()
    pal = [th["accent1"],th["accent2"],"#60A5FA","#4ADE80","#F87171","#C084FC"]
    for idx,(_, r) in enumerate(top6.iterrows()):
        vals = [r["runs"]/mx["runs"]*100, min(r["bat_avg"]/mx["bat_avg"]*100,100),
                min(r["bat_sr"]/mx["bat_sr"]*100,100), r["wickets"]/mx["wickets"]*100,
                max(0,(60-r["bowl_sr"])/60*100) if r["bowl_sr"]>0 else 0]
        fig.add_trace(go.Scatterpolar(r=vals+[vals[0]], theta=cats+[cats[0]],
            fill="toself", name=r["player_name"].split()[-1],
            line=dict(width=1.5,color=pal[idx%len(pal)]), fillcolor="rgba(59,130,246,0.04)"))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit",size=9,color=th["muted"]), height=280, margin=dict(l=20,r=20,t=8,b=8),
        polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=False,range=[0,100]),
                   angularaxis=dict(tickfont=dict(size=9,color=th["muted"]),linecolor=th["border"])),
        legend=dict(font=dict(size=8,color=th["muted"]),bgcolor="rgba(0,0,0,0)"))
    return fig


# ══════════════════════════════════════════════════════════════════════════
# PLAYER CARD  ← card renders as HTML first, then a transparent
#               full-size button is overlaid so clicking anywhere works
# ══════════════════════════════════════════════════════════════════════════
def render_player(i, row, captain, country):
    th    = T(country)
    a1    = th["accent1"]
    role  = str(row.get("role","batter")).lower()
    name  = str(row.get("player_name", f"Player {i+1}"))
    is_cap = (name == captain)
    ini   = initials(name)
    pos   = str(row.get("position","")).replace("order","").strip().title()

    runs  = int(get_stat(row,["runs"]))
    avg_  = get_stat(row,["bat_avg"])
    sr_   = get_stat(row,["bat_sr"])
    wkts  = int(get_stat(row,["wickets"]))
    bavg  = get_stat(row,["bowl_avg"])
    bsr   = get_stat(row,["bowl_sr"])
    mat   = int(get_stat(row,["total_matches"]))

    if is_cap:                 badge = '<span class="badge b-cap">Captain</span>'
    elif role=="wicketkeeper": badge = '<span class="badge b-wk">WK</span>'
    elif role=="allrounder":   badge = '<span class="badge b-ar">AR</span>'
    elif role=="bowler":       badge = '<span class="badge b-bow">Bowl</span>'
    else:                      badge = '<span class="badge b-bat">Bat</span>'

    if role == "bowler":
        s = (f'<div><div class="sv">{wkts}</div><div class="sl">Wkts</div></div>'
             f'<div><div class="sv">{f"{bavg:.1f}" if bavg else "—"}</div><div class="sl">Avg</div></div>'
             f'<div><div class="sv">{f"{bsr:.1f}" if bsr else "—"}</div><div class="sl">SR</div></div>'
             f'<div><div class="sv">{mat}</div><div class="sl">Mat</div></div>')
    elif role == "allrounder":
        s = (f'<div><div class="sv">{runs}</div><div class="sl">Runs</div></div>'
             f'<div><div class="sv">{sr_:.1f}</div><div class="sl">SR</div></div>'
             f'<div><div class="sv">{wkts}</div><div class="sl">Wkts</div></div>'
             f'<div><div class="sv">{mat}</div><div class="sl">Mat</div></div>')
    else:
        s = (f'<div><div class="sv">{runs}</div><div class="sl">Runs</div></div>'
             f'<div><div class="sv">{avg_:.1f}</div><div class="sl">Avg</div></div>'
             f'<div><div class="sv">{sr_:.1f}</div><div class="sl">SR</div></div>'
             f'<div><div class="sv">{mat}</div><div class="sl">Mat</div></div>')

    av_cls = "av av-cap" if is_cap else "av"
    st_cls = "stripe stripe-cap" if is_cap else "stripe"
    nm_cls = "pname pname-cap" if is_cap else "pname"

    # 1) Open the wrapper (position:relative)
    st.markdown('<div class="pc-wrap">', unsafe_allow_html=True)

    # 2) Render the VISIBLE card (pointer-events:none so it doesn't block button)
    st.markdown(f"""
<div class="pc">
  <div class="{st_cls}"></div>
  <div class="pnum">{i+1:02d}</div>
  <div class="{av_cls}">{ini}</div>
  <div style="flex:1;min-width:0;padding-left:2px">
    <div class="{nm_cls}">{name} <span style="font-size:.5rem;opacity:.3;vertical-align:middle">↗</span></div>
    <div class="ppos">{pos}</div>
  </div>
  <div class="pstats">{s}</div>
  {badge}
</div>""", unsafe_allow_html=True)

    # 3) Render the INVISIBLE button overlaid on top via CSS absolute positioning
    #    It has no visible label — just an empty string
    clicked = st.button(" ", key=f"pclick_{i}", help=f"View {name}'s profile")

    # 4) Close the wrapper
    st.markdown('</div>', unsafe_allow_html=True)

    if clicked:
        st.session_state["profile_player"] = name
        st.session_state["profile_row"]    = row if isinstance(row, dict) else row
        st.session_state["show_profile"]   = True
        st.rerun()


def render_sw_panel(country):
    th = T(country)
    s = "".join(f'<div class="sw-item"><span class="sw-dot-s">●</span>{x}</div>' for x in th.get("sw_strengths",[]))
    w = "".join(f'<div class="sw-item"><span class="sw-dot-w">●</span>{x}</div>' for x in th.get("sw_weaknesses",[]))
    st.markdown(f"""<div style="margin-top:14px">
      <div class="slabel">Strengths &amp; Weaknesses</div>
      <div class="sw-wrap">
        <div class="sw-box sw-box-s"><div class="sw-head sw-head-s">● Strengths</div>{s}</div>
        <div class="sw-box sw-box-w"><div class="sw-head sw-head-w">● Weaknesses</div>{w}</div>
      </div></div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""<div style="padding:4px 0 10px">
      <div style="font-size:1.05rem;font-weight:700;letter-spacing:-.01em">ODI XI</div>
      <div style="font-size:.56rem;text-transform:uppercase;letter-spacing:.2em;opacity:.4;margin-top:2px">Squad Selector</div>
    </div>""", unsafe_allow_html=True)
    page = st.radio("View", ["XI & Insights","Analytics","Venues"], label_visibility="collapsed")
    st.divider()
    country = st.selectbox("Country", [""]+COUNTRIES,
        format_func=lambda x: f"{THEMES.get(x,THEMES['_default'])['flag']}  {x}" if x else "Select country…")
    venue_opts = ["— No venue —"] + sorted(VENUES.keys())
    sel_v = st.selectbox("Venue", venue_opts)
    venue = "" if sel_v.startswith("—") else sel_v
    auto_pitch = ""
    if venue and venue in VENUES:
        v = VENUES[venue]; auto_pitch = v.get("pitch","pace")
        dc = "#FFB300" if v.get("dew") else "inherit"
        st.markdown(f"""<div class="vbox"><b>{venue.split(",")[0]}</b><br>
          Pitch <b>{pl(auto_pitch)}</b> · Avg <b>{v.get("avg_score","—")}</b> ·
          Dew <b style="color:{dc}">{"Yes" if v.get("dew") else "No"}</b><br>
          <span style="font-size:.66rem;opacity:.7">{v.get("desc","")}</span></div>""", unsafe_allow_html=True)
    ovr = st.radio("Pitch override", ["Auto","Pace","Spin","Balanced"], horizontal=True)
    pitch = (auto_pitch or "pace") if ovr=="Auto" else ovr.lower()
    st.divider()
    go_btn = st.button("Generate Best XI", use_container_width=True, type="primary")

inject_css(country)

# ══════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════
for k, v in [("team",None),("captain",None),("meta",{}),("sel_cty",""),
             ("show_profile",False),("profile_player",""),("profile_row",None)]:
    if k not in st.session_state: st.session_state[k] = v

if go_btn:
    if not country:
        st.warning("Please select a country first."); st.stop()
    with st.spinner(f"Selecting Best XI for {country}…"):
        try:
            res = select_team(country, venue=venue, pitch=pitch)
            if len(res)==3: t,c,m = res
            else: t,c = res; m = {"pitch":pitch,"avg_score":275,"dew":False,"venue_desc":""}
        except Exception as e:
            st.error(f"Error: {e}"); st.stop()
    if t is None or t.empty:
        st.error(f"No players found for '{country}'."); st.stop()
    st.session_state.update({"team":t,"captain":c,"meta":m or {},"sel_cty":country,
                              "show_profile":False,"profile_player":""})

team=st.session_state.team; captain=st.session_state.captain
meta=st.session_state.meta or {}; sel_cty=st.session_state.sel_cty
th=T(sel_cty)

# ══════════════════════════════════════════════════════════════════════════
# VENUES PAGE
# ══════════════════════════════════════════════════════════════════════════
if page == "Venues":
    th2 = T(country or "_default")
    st.markdown(f"""<div class="ctry-banner">
      {flag_svg_bg(country or "_default")}
      <div class="ctry-inner">
        <div style="position:relative;z-index:1">
          <div class="ctry-name">International Venues</div>
          <div class="ctry-sub">{len(VENUES)} grounds · pitch profiles · scoring data</div>
        </div>
      </div></div>""", unsafe_allow_html=True)
    fc1,fc2,fc3 = st.columns([2,2,1])
    with fc1: filt_country = st.selectbox("Filter by country", ["All"]+sorted(set(v.get("country","—") for v in VENUES.values())))
    with fc2: filt_pitch   = st.selectbox("Filter by pitch",   ["All","Pace","Spin","Balanced"])
    with fc3: filt_dew     = st.selectbox("Dew factor",        ["All","Yes","No"])
    filtered = {vn:vi for vn,vi in VENUES.items()
                if (filt_country=="All" or vi.get("country","—")==filt_country)
                and (filt_pitch=="All" or vi.get("pitch","").title()==filt_pitch)
                and (filt_dew=="All" or ("Yes" if vi.get("dew") else "No")==filt_dew)}
    st.markdown(f'<div style="font-size:.6rem;color:{th2["muted"]};margin:8px 0 14px;text-transform:uppercase;letter-spacing:.14em">Showing {len(filtered)} of {len(VENUES)} venues</div>', unsafe_allow_html=True)
    items = list(sorted(filtered.items()))
    for row_start in range(0, len(items), 3):
        cols = st.columns(3, gap="medium")
        for col,(vname,vinfo) in zip(cols, items[row_start:row_start+3]):
            pt = vinfo.get("pitch","")
            dew_pill = '<span class="vc-pill vc-pill-dew">Dew</span>' if vinfo.get("dew") else ""
            vshort = vname.split(",")[0]
            vcity  = ", ".join(vname.split(",")[1:]).strip() or vshort
            with col:
                st.markdown(
                    f'<div class="venue-card"><div class="vc-name">{vshort}</div>'
                    f'<div class="vc-country">{vinfo.get("country","—")} &nbsp;·&nbsp; {vcity}</div>'
                    f'<div class="vc-pills"><span class="vc-pill vc-pill-{pt}">{pt.title()}</span>{dew_pill}</div>'
                    f'<div><span class="vc-score">{vinfo.get("avg_score","—")}</span></div>'
                    f'<div class="vc-score-lbl">Avg 1st innings</div>'
                    f'<div class="vc-desc">{str(vinfo.get("desc","")).replace(chr(39),"&#39;")}</div>'
                    f'</div>', unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════
# PLAYER PROFILE PAGE
# ══════════════════════════════════════════════════════════════════════════
if st.session_state.get("show_profile") and st.session_state.get("profile_player"):
    pname = st.session_state["profile_player"]
    prow  = st.session_state["profile_row"]
    prow_dict = prow if isinstance(prow, dict) else (prow.to_dict() if prow is not None else {})

    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back to XI", key="close_profile"):
        st.session_state.update({"show_profile":False,"profile_player":"","profile_row":None})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    render_profile(pname, prow_dict, sel_cty)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════
# LANDING
# ══════════════════════════════════════════════════════════════════════════
if team is None:
    st.markdown("""<div style="padding:60px 0 0;max-width:480px">
      <div style="font-size:1.7rem;font-weight:700;letter-spacing:-.02em;margin-bottom:6px">ODI AI Team Selector</div>
      <div style="font-size:.58rem;text-transform:uppercase;letter-spacing:.22em;opacity:.3;margin-bottom:28px">Pitch-aware · Venue-intelligent · Role-balanced</div>
      <div style="font-size:.78rem;line-height:2.3;opacity:.45">
        ① Select a country → pick a venue<br>② Override pitch type if needed<br>
        ③ Click Generate Best XI<br>④ Click any player card to view full stats<br>
        ⑤ Switch to Analytics or Venues
      </div></div>""", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════
# BANNER + METRICS
# ══════════════════════════════════════════════════════════════════════════
st.markdown(f"""<div class="ctry-banner">
  {flag_svg_bg(sel_cty)}
  <div class="ctry-inner">
    <div class="ctry-flag">{th["flag"]}</div>
    <div><div class="ctry-name">{sel_cty}</div>
      <div class="ctry-sub">Best XI · {pl(pitch)} conditions · {venue.split(",")[0] if venue else "Any venue"}</div></div>
    <div class="ctry-cap">
      <div class="ctry-cap-name">{captain or "—"}</div>
      <div class="ctry-cap-lbl">Captain</div>
    </div>
  </div></div>""", unsafe_allow_html=True)

cols = st.columns(5)
for col,(lbl,val) in zip(cols,[("Avg Score",str(meta.get("avg_score","—"))),
    ("Pitch",pl(pitch)),("Venue",venue.split(",")[0][:16] if venue else "Open"),
    ("Dew","Yes" if meta.get("dew") else "No"),("Country",sel_cty[:14])]):
    col.markdown(f'<div class="mc"><span class="mv mono">{val}</span><div class="ml">{lbl}</div></div>', unsafe_allow_html=True)
st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 1 — XI & Insights
# ══════════════════════════════════════════════════════════════════════════
if page == "XI & Insights":
    left, right = st.columns([5,6], gap="large")
    with left:
        GL = {"opener":"Openers","middle order":"Middle Order",
              "lower order":"Lower Order / All-Rounders","bowler":"Bowlers"}
        last_g = None; wk_shown = False
        for i, row in team.iterrows():
            pos  = str(row.get("position","")).strip().lower()
            role = str(row.get("role","")).strip().lower()
            if role=="wicketkeeper" and not wk_shown:
                st.markdown('<div class="sdiv"><div class="sdiv-line"></div><div class="sdiv-text">Wicketkeeper</div><div class="sdiv-line"></div></div>', unsafe_allow_html=True)
                wk_shown = True
            elif pos!=last_g and pos in GL and role!="wicketkeeper":
                st.markdown(f'<div class="sdiv"><div class="sdiv-line"></div><div class="sdiv-text">{GL[pos]}</div><div class="sdiv-line"></div></div>', unsafe_allow_html=True)
                last_g = pos
            render_player(i, row.to_dict(), captain, sel_cty)
    with right:
        st.markdown('<div class="slabel">Insights</div>', unsafe_allow_html=True)
        try: ins = generate_insights(team, venue=venue, pitch=pitch, meta=meta)
        except TypeError: ins = generate_insights(team, venue=venue, pitch=pitch)
        for tab, key in zip(st.tabs(["Batting","Bowling","Team","Venue","Strategy"]),
                            ["batting","bowling","team","venue","strategy"]):
            with tab:
                for item in ins.get(key,["No data."]):
                    if item: st.markdown(f'<div class="ic">{item}</div>', unsafe_allow_html=True)
        render_sw_panel(sel_cty)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 2 — Analytics
# ══════════════════════════════════════════════════════════════════════════
elif page == "Analytics":
    st.markdown('<div class="slabel">Analytics Dashboard</div>', unsafe_allow_html=True)
    def cc(title, fig, msg="No data."):
        st.markdown(f'<div class="chart-card"><div class="chart-title">{title}</div>', unsafe_allow_html=True)
        if fig: st.plotly_chart(fig, use_container_width=True, config=_CFG)
        else: st.markdown(f'<div style="font-size:.72rem;color:{th["muted"]};padding:18px 0">{msg}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    r1a,r1b = st.columns(2, gap="medium")
    with r1a: cc("Batting — ODI Runs", chart_hbar(team[team["role"].isin(["batter","wicketkeeper","allrounder"])],"runs",sel_cty))
    with r1b: cc("Bowling — ODI Wickets", chart_hbar(team[team["wickets"]>0],"wickets",sel_cty))
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    r2a,r2b = st.columns(2, gap="medium")
    with r2a: cc("Batting Average",     chart_hbar(team,"bat_avg",sel_cty))
    with r2b: cc("Batting Strike Rate", chart_hbar(team,"bat_sr", sel_cty))
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    r3a,r3b,r3c = st.columns([2,2,1], gap="medium")
    with r3a:
        bdf = team[(team["bowl_sr"]>0)&(team["wickets"]>5)]
        cc("Bowling SR (lower = better)", chart_hbar(bdf,"bowl_sr",sel_cty,hi_is_low=True), "Not enough bowling data.")
    with r3b: cc("Player Radar — Top 6", chart_radar(team,sel_cty))
    with r3c: cc("Squad Mix", chart_donut(team,sel_cty))
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="slabel">Key Numbers</div>', unsafe_allow_html=True)
    bp = team[team["wickets"]>0]
    kv = [("Total Runs",f"{int(team['runs'].sum()):,}"),("Total Wickets",f"{int(team['wickets'].sum())}"),
          ("Best Bat Avg",f"{team['bat_avg'].max():.1f}"),("Best Bat SR",f"{team['bat_sr'].max():.1f}"),
          ("Best Bowl SR",f"{bp['bowl_sr'].min():.1f}" if not bp.empty else "—"),
          ("Avg 25+ Count",str(len(team[team["bat_avg"]>25])))]
    for col,(lbl,val) in zip(st.columns(6), kv):
        col.markdown(f'<div class="mc"><span class="mv mono">{val}</span><div class="ml">{lbl}</div></div>', unsafe_allow_html=True)