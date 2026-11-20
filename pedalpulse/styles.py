"""Bright, high-contrast PedalPulse interface and Plotly styling."""
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --teal:#0F6265; --teal-dark:#0A484C; --coral:#E85E53; --paper:#F5F7FA; --white:#FFFFFF; --ink:#172B3A; --muted:#586B79; --line:#E2E8EE; --mint:#E9F5F2; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:var(--paper); color:var(--ink); }
[data-testid="stHeader"], #MainMenu, footer { visibility:hidden; }
.block-container { max-width:1200px; padding-top:1.15rem; padding-bottom:3.5rem; }
h1,h2,h3,h4,.brand,.kpi strong { font-family:'Space Grotesk',sans-serif !important; color:var(--ink); }
h1 { font-size:clamp(2.35rem,4.8vw,4rem) !important; letter-spacing:-.055em; line-height:1.04 !important; }
h2 { letter-spacing:-.035em; }
p, label, [data-testid="stMarkdownContainer"] { color:var(--ink); }
.brand { display:flex; align-items:center; gap:.72rem; padding:.2rem 0 1.55rem; font-size:1.16rem; font-weight:700; }
.brand-mark { display:grid; place-items:center; width:39px; height:39px; border-radius:13px; background:var(--teal); color:#fff; font:700 .82rem 'Space Grotesk',sans-serif; box-shadow:0 5px 14px #0f626528; }
.badge { border:1px solid #cfe5df; border-radius:999px; background:#eff8f5; color:#14585A; padding:.4rem .72rem; font:700 .7rem 'DM Sans',sans-serif; }
.hero-panel { position:relative; display:flex; align-items:center; justify-content:space-between; min-height:340px; overflow:hidden; padding:3.35rem 4rem; border:1px solid var(--line); border-radius:28px; background:#fff; box-shadow:0 15px 45px #2437480b; }
.hero-panel:before { content:''; position:absolute; width:400px; height:400px; right:-70px; top:-175px; border:1px solid #0f62651e; border-radius:50%; box-shadow:0 0 0 42px #0f626508,0 0 0 84px #0f626506; }
.hero-copy { position:relative; z-index:1; max-width:620px; }
.hero-panel h1 { color:var(--ink) !important; margin:.75rem 0 .7rem; }
.hero-panel p { max-width:490px; margin:0; color:var(--muted); font-size:1.1rem; line-height:1.7; }
.hero-art { position:relative; width:225px; height:200px; margin-right:30px; flex:0 0 225px; }
.orbit { position:absolute; inset:5px 16px; border:1px solid #0f62654a; border-radius:50%; transform:rotate(-25deg); }
.orbit.two { inset:24px 0; transform:rotate(25deg); border-color:#e85e5340; }
.pulse-dot { position:absolute; top:32px; right:16px; width:16px; height:16px; border-radius:50%; background:var(--coral); box-shadow:0 0 0 8px #e85e531a; }
.hero-stat { position:absolute; right:18px; bottom:27px; padding:.9rem 1.1rem; border:1px solid var(--line); border-radius:16px; background:#fff; box-shadow:0 8px 24px #24374813; }
.hero-stat strong { display:block; color:var(--teal); font:700 1.45rem 'Space Grotesk',sans-serif; }
.hero-stat span { color:var(--muted); font-size:.74rem; white-space:nowrap; }
.eyebrow { color:var(--coral); font-size:.72rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; }
.section-intro { padding:2.55rem 0 1rem; }
.section-intro h2 { margin:.35rem 0 .25rem; color:var(--ink); font-size:1.6rem; }
.section-intro p,.page-title p { margin:0; color:var(--muted); }
.feature { height:100%; min-height:175px; padding:1.45rem; border:1px solid var(--line); border-radius:19px; background:#fff; box-shadow:0 8px 26px #24374808; transition:transform .18s ease,box-shadow .18s ease; }
.feature:hover { transform:translateY(-3px); box-shadow:0 14px 30px #24374812; }
.feature-icon { display:grid; place-items:center; width:42px; height:42px; border:1px solid #cfe5df; border-radius:13px; background:var(--mint); color:var(--teal); font:700 .72rem 'Space Grotesk',sans-serif; }
.feature h3 { margin:1rem 0 .4rem; color:var(--ink); font-size:1.06rem; }
.feature p { margin:0; color:var(--muted); font-size:.9rem; line-height:1.55; }
.architecture { display:flex; justify-content:space-around; align-items:center; gap:1rem; margin:1.7rem 0 1rem; padding:1.05rem 1.25rem; border:1px solid var(--line); border-radius:17px; background:#fff; color:#263F4B; font-size:.87rem; font-weight:700; }
.architecture span { display:flex; align-items:center; }
.architecture .step { color:var(--coral); font-size:1.1rem; }
.footer { padding:2.2rem 0 .3rem; color:var(--muted); text-align:center; font-size:.82rem; }
.page-title { padding:.3rem 0 1.15rem; }
.page-title h1 { margin:.45rem 0 .5rem; font-size:clamp(2.1rem,4vw,3.2rem) !important; }
.section-label { display:flex; align-items:center; gap:.75rem; margin:1.8rem 0 1rem; color:var(--ink); font:700 1.12rem 'Space Grotesk',sans-serif; }
.section-num { display:grid; place-items:center; width:30px; height:30px; border-radius:10px; background:var(--teal); color:white; font:700 .8rem 'DM Sans',sans-serif; }
.kpi { min-height:110px; padding:1.1rem 1.15rem; border:1px solid var(--line); border-top:3px solid var(--teal); border-radius:16px; background:#fff; box-shadow:0 8px 24px #24374808; }
.kpi small { display:block; margin-bottom:.65rem; color:var(--muted); font-size:.75rem; font-weight:700; }
.kpi strong { display:block; overflow-wrap:anywhere; color:var(--teal-dark); font:700 clamp(.95rem,1.35vw,1.25rem) 'Space Grotesk',sans-serif; }
[data-testid="stFileUploader"] section { border:1.5px dashed #91bcb6; border-radius:18px; background:#fff; }
[data-testid="stFileUploader"] section:hover { border-color:var(--teal); background:#f7fcfa; }
[data-testid="stFileUploader"] small, [data-testid="stFileUploader"] span { color:var(--muted); }
div.stButton > button, [data-testid="stFormSubmitButton"] button { min-height:43px; padding:.58rem 1.25rem; border:1px solid var(--teal); border-radius:999px; background:var(--teal); color:#fff; font-weight:700; transition:all .18s ease; }
div.stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover { transform:translateY(-1px); border-color:var(--teal-dark); background:var(--teal-dark); color:#fff; box-shadow:0 7px 17px #0f626528; }
div.stButton > button:focus, [data-testid="stFormSubmitButton"] button:focus { box-shadow:0 0 0 3px #e85e5344; }
[data-testid="stCheckbox"] label { padding:.4rem .7rem; border:1px solid var(--line); border-radius:999px; background:#fff; color:#344957; font-weight:600; transition:all .15s ease; }
[data-testid="stCheckbox"]:has(input:checked) label { border-color:var(--teal); background:var(--teal); color:#fff; }
[data-testid="stRadio"] label { color:#344957; font-weight:600; }
[data-testid="stTabs"] [role="tablist"] { gap:.45rem; }
[data-testid="stTabs"] button[role="tab"] { border-radius:12px 12px 0 0; color:#4b5e6a; }
[data-testid="stTabs"] button[aria-selected="true"] { color:var(--teal); border-bottom-color:var(--coral); }
[data-testid="stForm"] { margin-top:.65rem; padding:1.05rem; border:1px solid var(--line); border-radius:17px; background:#fff; }
[data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--line) !important; border-radius:19px !important; background:#fff; box-shadow:0 10px 28px #24374808; padding:.35rem .65rem; }
[data-testid="stVerticalBlockBorderWrapper"] h4 { margin-top:.4rem; color:var(--ink); }
.graph-heading { display:flex; align-items:center; justify-content:space-between; gap:.7rem; padding:.1rem 0 .45rem; }
.graph-heading h3 { margin:.15rem 0; color:var(--ink); font:700 1.12rem 'Space Grotesk',sans-serif; }
.graph-heading span { flex:none; padding:.32rem .62rem; border:1px solid #cfe5df; border-radius:999px; background:#eff8f5; color:#14585A; font-size:.72rem; font-weight:700; }
[data-testid="stAlert"] { border-radius:14px; }
[data-testid="stCaptionContainer"] { color:var(--muted); }
.auth-aside { min-height:390px; padding:2rem; border-radius:24px; background:linear-gradient(145deg,#EAF6F3,#F7FBFA); border:1px solid #d8eae5; }
.auth-aside h2 { margin:.75rem 0; color:var(--ink); font:700 1.8rem 'Space Grotesk',sans-serif; }
.auth-aside p { color:var(--muted); line-height:1.65; }
.auth-point { display:flex; gap:.7rem; align-items:center; margin-top:1rem; color:#294551; font-size:.9rem; font-weight:600; }
.auth-check { display:grid; place-items:center; width:25px; height:25px; flex:none; border-radius:9px; background:#fff; color:var(--teal); font-size:.8rem; }
.upload-note { padding:.8rem 1rem; border:1px solid #d8eae5; border-radius:13px; background:#f3faf8; color:#34545a; font-size:.88rem; }
.loaded-pill { display:inline-block; padding:.45rem .75rem; border:1px solid #b9ddd3; border-radius:999px; background:#eff9f5; color:#185957; font-size:.83rem; font-weight:700; }
@media (max-width:760px) {
 .block-container { padding-left:1rem; padding-right:1rem; }
 .hero-panel { min-height:310px; padding:2.15rem 1.5rem; }
 .hero-art { position:absolute; right:-95px; opacity:.35; }
 .hero-copy { max-width:100%; }
 .architecture { flex-wrap:wrap; justify-content:center; }
 .architecture .step { display:none; }
 .brand { padding-bottom:1.1rem; }
 .auth-aside { min-height:auto; margin-bottom:1rem; }
}
</style>
"""


def chart_layout():
    """Return shared high-contrast Plotly styling options."""
    return {"template": "plotly_white", "paper_bgcolor": "#FFFFFF",
            "plot_bgcolor": "#FFFFFF", "colorway": ["#0F6265", "#E85E53", "#6FA3A0", "#D89C3C"],
            "margin": {"l": 16, "r": 16, "t": 24, "b": 16},
            "font": {"family": "DM Sans, sans-serif", "color": "#172B3A"}}
