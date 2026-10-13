import requests
import os
import streamlit as st

# =============================
# CONFIG
# =============================
API_BASE = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =============================
# STYLES (cinema night theme)
# Palette: midnight #0f0e1a · surface #1a1830 · raised #25223f
#          text #ece9f6 · muted #9a96b5 · accent saffron #f5b94a · rose #e8647c
# Type:    Fraunces (display) + Manrope (UI)
# =============================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Manrope:wght@400;500;600;700&display=swap');

:root {
    --bg: #0f0e1a;
    --surface: #1a1830;
    --raised: #25223f;
    --line: rgba(255,255,255,0.08);
    --text: #ece9f6;
    --muted: #9a96b5;
    --accent: #f5b94a;
    --accent-2: #e8647c;
    --radius: 14px;
}

html, body, [class*="css"], .stApp, .stMarkdown, button, input, select, textarea {
    font-family: 'Manrope', system-ui, -apple-system, 'Segoe UI', sans-serif !important;
}

/* ---------- App shell ---------- */
.stApp {
    background:
        radial-gradient(900px 500px at 85% -10%, rgba(232,100,124,0.14), transparent 60%),
        radial-gradient(800px 500px at 0% 0%, rgba(245,185,74,0.08), transparent 55%),
        var(--bg);
    color: var(--text);
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px; }

/* ---------- Headings ---------- */
h1, h2, h3, h4 {
    font-family: 'Fraunces', Georgia, serif !important;
    color: var(--text) !important;
    letter-spacing: -0.01em;
}
h1 { font-weight: 700 !important; }
h3 { font-weight: 500 !important; margin-top: 0.5rem; }
h4 { font-weight: 500 !important; color: var(--muted) !important; }

/* ---------- Hero ---------- */
.hero { padding: 0.5rem 0 0.25rem 0; }
.hero-title {
    font-family: 'Fraunces', Georgia, serif;
    font-size: clamp(2.2rem, 4vw, 3.4rem);
    font-weight: 700;
    line-height: 1.05;
    color: var(--text);
    margin: 0;
}
.hero-title span { color: var(--accent); }
.small-muted { color: var(--muted); font-size: 0.95rem; line-height: 1.5; }
.hero .small-muted { margin-top: 0.6rem; max-width: 640px; }

hr, [data-testid="stDivider"] { border-color: var(--line) !important; }

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { font-size: 1.15rem; }
section[data-testid="stSidebar"] label p { color: var(--muted) !important; font-size: 0.85rem; }

/* ---------- Inputs ---------- */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    transition: border-color .15s ease, box-shadow .15s ease;
}
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(245,185,74,0.18) !important;
}
input { color: var(--text) !important; }
input::placeholder { color: var(--muted) !important; opacity: .8; }
label p { color: var(--text) !important; font-weight: 600; }
.stTextInput input { padding: 0.75rem 0.9rem; font-size: 1rem; }

/* ---------- Buttons ---------- */
.stButton > button {
    width: 100%;
    background: var(--raised);
    color: var(--text);
    border: 1px solid var(--line);
    border-radius: 10px;
    font-weight: 600;
    padding: 0.4rem 0.8rem;
    transition: background .15s ease, color .15s ease, border-color .15s ease;
}
.stButton > button:hover {
    background: var(--accent);
    color: #1a1226;
    border-color: var(--accent);
}
.stButton > button:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
}

/* ---------- Posters ---------- */
[data-testid="stImage"] img {
    border-radius: var(--radius);
    border: 1px solid var(--line);
    box-shadow: 0 10px 24px rgba(0,0,0,0.35);
    transition: transform .2s ease, box-shadow .2s ease;
}
[data-testid="stImage"] img:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 30px rgba(0,0,0,0.5);
}
.movie-title {
    font-size: 0.9rem;
    font-weight: 600;
    line-height: 1.15rem;
    height: 2.3rem;
    overflow: hidden;
    color: var(--text);
    margin-top: 0.1rem;
}
.no-poster {
    aspect-ratio: 2 / 3;
    display: flex; align-items: center; justify-content: center;
    background: var(--surface);
    border: 1px dashed var(--line);
    border-radius: var(--radius);
    color: var(--muted);
    font-size: 0.9rem;
}

/* ---------- Cards (bordered containers) ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface);
    border: 1px solid var(--line) !important;
    border-radius: 18px !important;
}

/* ---------- Details ---------- */
.detail-title {
    font-family: 'Fraunces', Georgia, serif;
    font-size: clamp(1.8rem, 3vw, 2.6rem);
    font-weight: 700;
    line-height: 1.1;
    margin: 0 0 0.6rem 0;
    color: var(--text);
}
.meta-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 0.4rem 0; align-items: center; }
.meta-label { color: var(--muted); font-size: 0.85rem; margin-right: 4px; }
.chip {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    border: 1px solid rgba(245,185,74,0.35);
    background: rgba(245,185,74,0.08);
    color: var(--accent);
    font-size: 0.82rem;
    font-weight: 600;
}
.chip-muted {
    border-color: var(--line);
    background: var(--raised);
    color: var(--text);
}
.overview-text { color: var(--text); line-height: 1.7; font-size: 1rem; max-width: 70ch; }

/* ---------- Alerts ---------- */
[data-testid="stAlert"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 12px;
    color: var(--text);
}

/* ---------- Motion preference ---------- */
@media (prefers-reduced-motion: reduce) {
    * { transition: none !important; }
    [data-testid="stImage"] img:hover { transform: none; }
}
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# STATE + ROUTING (single-file pages)
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"  # home | details
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except:
        pass


def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=30)  # short cache for autocomplete
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols, gap="medium")
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")

            with colset[c]:
                if poster:
                    st.image(poster, width="stretch")
                else:
                    st.markdown(
                        "<div class='no-poster'>🖼️ No poster</div>",
                        unsafe_allow_html=True,
                    )

                if st.button("Open", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)

                st.markdown(
                    f"<div class='movie-title'>{title}</div>", unsafe_allow_html=True
                )


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                }
            )
    return cards


# =============================
# IMPORTANT: Robust TMDB search parsing
# Supports BOTH API shapes:
# 1) raw TMDB: {"results":[{id,title,poster_path,...}]}
# 2) list cards: [{tmdb_id,title,poster_url,...}]
# =============================
def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    """
    Returns:
      suggestions: list[(label, tmdb_id)]
      cards: list[{tmdb_id,title,poster_url}]
    """
    keyword_l = keyword.strip().lower()

    # A) If API returns dict with 'results'
    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        raw_items = []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": m.get("release_date", ""),
                }
            )

    # B) If API returns already as list
    elif isinstance(data, list):
        raw_items = []
        for m in data:
            # might be {tmdb_id,title,poster_url}
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": poster_url,
                    "release_date": m.get("release_date", ""),
                }
            )
    else:
        return [], []

    # Word-match filtering (contains)
    matched = [x for x in raw_items if keyword_l in x["title"].lower()]

    # If nothing matched, fallback to raw list (so never blank)
    final_list = matched if matched else raw_items

    # Suggestions = top 10 labels
    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    # Cards = top N
    cards = [
        {"tmdb_id": x["tmdb_id"], "title": x["title"], "poster_url": x["poster_url"]}
        for x in final_list[:limit]
    ]
    return suggestions, cards


# =============================
# SIDEBAR (clean)
# =============================
with st.sidebar:
    st.markdown("## 🎬 Menu")
    if st.button("🏠 Home"):
        goto_home()

    st.markdown("---")
    st.markdown("### 🏠 Home Feed (only home)")
    home_category = st.selectbox(
        "Category",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
    )
    grid_cols = st.slider("Grid columns", 4, 8, 6)

# =============================
# HEADER
# =============================
st.markdown(
    """
<div class='hero'>
    <div class='hero-title'>🎬 Movie <span>Recommender</span></div>
    <div class='small-muted'>Type keyword → dropdown suggestions + matching results → open → details + recommendations</div>
</div>
""",
    unsafe_allow_html=True,
)
st.divider()

# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":
    typed = st.text_input(
        "Search by movie title (keyword)", placeholder="Type: avenger, batman, love..."
    )

    st.divider()

    # SEARCH MODE (Autocomplete + word-match results)
    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for suggestions.")
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})

            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(
                    data, typed.strip(), limit=24
                )

                # Dropdown
                if suggestions:
                    labels = ["-- Select a movie --"] + [s[0] for s in suggestions]
                    selected = st.selectbox("Suggestions", labels, index=0)

                    if selected != "-- Select a movie --":
                        # map label -> id
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No suggestions found. Try another keyword.")

                st.markdown("### Results")
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")

        st.stop()

    # HOME FEED MODE
    st.markdown(f"### 🏠 Home — {home_category.replace('_',' ').title()}")

    home_cards, err = api_get_json(
        "/home", params={"category": home_category, "limit": 24}
    )
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")

# ==========================================================
# VIEW: DETAILS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("← Back to Home"):
            goto_home()
        st.stop()

    # Top bar
    a, b = st.columns([3, 1])
    with a:
        st.markdown("### 📄 Movie Details")
    with b:
        if st.button("← Back to Home"):
            goto_home()

    # Details (your FastAPI safe route)
    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    # Layout: Poster LEFT, Details RIGHT
    left, right = st.columns([1, 2.4], gap="large")

    with left:
        with st.container(border=True):
            if data.get("poster_url"):
                st.image(data["poster_url"], width="stretch")
            else:
                st.markdown(
                    "<div class='no-poster'>🖼️ No poster</div>", unsafe_allow_html=True
                )

    with right:
        with st.container(border=True):
            st.markdown(
                f"<div class='detail-title'>{data.get('title','')}</div>",
                unsafe_allow_html=True,
            )
            release = data.get("release_date") or "-"
            genre_names = [g["name"] for g in data.get("genres", [])]
            genre_chips = (
                "".join(f"<span class='chip'>{g}</span>" for g in genre_names)
                if genre_names
                else "<span class='small-muted'>-</span>"
            )
            st.markdown(
                f"<div class='meta-row'><span class='meta-label'>Release</span>"
                f"<span class='chip chip-muted'>{release}</span></div>"
                f"<div class='meta-row'><span class='meta-label'>Genres</span>{genre_chips}</div>",
                unsafe_allow_html=True,
            )
            st.markdown("---")
            st.markdown("### Overview")
            st.markdown(
                f"<div class='overview-text'>{data.get('overview') or 'No overview available.'}</div>",
                unsafe_allow_html=True,
            )

    if data.get("backdrop_url"):
        st.markdown("#### Backdrop")
        st.image(data["backdrop_url"], width="stretch")

    st.divider()
    st.markdown("### ✅ Recommendations")

    # Recommendations (TF-IDF + Genre) via your bundle endpoint
    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.markdown("#### 🔎 Similar Movies (TF-IDF)")
            poster_grid(
                to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")),
                cols=grid_cols,
                key_prefix="details_tfidf",
            )

            st.markdown("#### 🎭 More Like This (Genre)")
            poster_grid(
                bundle.get("genre_recommendations", []),
                cols=grid_cols,
                key_prefix="details_genre",
            )
        else:
            st.info("Showing Genre recommendations (fallback).")
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                poster_grid(
                    genre_only, cols=grid_cols, key_prefix="details_genre_fallback"
                )
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")