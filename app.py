import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.output_parsers import PydanticOutputParser
import os

os.environ["MISTRAL_API_KEY"] = st.secrets["MISTRAL_API_KEY"]

st.set_page_config(
    page_title="Movie Extractor — Galaxy Edition",
    page_icon="🎬",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:ital,wght@0,300;0,400;0,500;1,300&family=Share+Tech+Mono&display=swap');

/* ── Base ── */
.stApp {
    background: #06040F;
    color: #E8E0FF;
}

/* ── Nebula background ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 60% 40% at 80% 20%, rgba(120,40,200,0.18) 0%, transparent 70%),
        radial-gradient(ellipse 50% 35% at 10% 70%, rgba(60,0,160,0.15) 0%, transparent 70%),
        radial-gradient(ellipse 40% 30% at 50% 90%, rgba(180,60,255,0.10) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* ── Typography ── */
h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    color: #ffffff !important;
    text-transform: uppercase;
    letter-spacing: 3px;
}

/* ── Blinking icon + title block ── */
.galaxy-hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.blink-icon {
    font-size: 3rem;
    display: block;
    margin-bottom: 1rem;
    animation: blink-fade 1.5s ease-in-out infinite;
    filter: drop-shadow(0 0 12px #A855F7);
}
@keyframes blink-fade {
    0%, 100% { opacity: 1;    transform: scale(1);    }
    50%       { opacity: 0.15; transform: scale(0.92); }
}
.galaxy-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: 3px;
    color: #ffffff;
    text-transform: uppercase;
    line-height: 1.1;
    margin: 0;
}
.galaxy-subtitle {
    font-family: 'Orbitron', monospace;
    font-size: 1rem;
    font-weight: 400;
    color: #A855F7;
    letter-spacing: 8px;
    margin-top: 6px;
}
.galaxy-tagline {
    font-family: 'Exo 2', sans-serif;
    font-size: 0.9rem;
    font-weight: 300;
    color: #9D8FCF;
    font-style: italic;
    margin-top: 10px;
    letter-spacing: 0.5px;
}

/* ── Divider ── */
.galaxy-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 1rem 0 1.8rem;
}
.galaxy-divider::before,
.galaxy-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(168,85,247,0.5), transparent);
}
.divider-dot {
    width: 6px; height: 6px;
    background: #A855F7;
    border-radius: 50%;
    box-shadow: 0 0 8px #A855F7;
}

/* ── Labels ── */
label, .stTextArea label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: #7C5FBF !important;
    font-weight: 400 !important;
}

/* ── Textarea ── */
textarea {
    background: rgba(20, 8, 45, 0.8) !important;
    border: 1px solid rgba(168, 85, 247, 0.3) !important;
    border-left: 3px solid #A855F7 !important;
    color: #E8E0FF !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.97rem !important;
    font-weight: 300 !important;
    line-height: 1.8 !important;
    border-radius: 0 8px 8px 0 !important;
    caret-color: #A855F7;
}
textarea::placeholder {
    color: #4A3870 !important;
    font-style: italic;
}
textarea:focus {
    border-color: rgba(168, 85, 247, 0.7) !important;
    border-left-color: #C084FC !important;
    background: rgba(30, 12, 60, 0.9) !important;
    box-shadow: none !important;
}

/* ── Button ── */
.stButton { width: 100% !important; }
.stButton > button {
    width: 100% !important;
    background: rgba(168, 85, 247, 0.15) !important;
    border: 1px solid rgba(168, 85, 247, 0.6) !important;
    border-radius: 8px !important;
    color: #C084FC !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    padding: 0.9rem !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover {
    background: rgba(168, 85, 247, 0.3) !important;
    border-color: #A855F7 !important;
    color: #E9D5FF !important;
    transform: scale(1.01);
}
.stButton > button:active {
    transform: scale(0.99) !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #A855F7 !important;
}

/* ── Warning / Error ── */
.stAlert {
    background: rgba(180, 30, 60, 0.15) !important;
    border-left: 3px solid #E05070 !important;
    border-radius: 0 8px 8px 0 !important;
    color: #F4A0B0 !important;
    font-style: italic;
}

/* ── Result card ── */
.result-card {
    background: rgba(15, 6, 35, 0.85);
    border: 1px solid rgba(168, 85, 247, 0.25);
    border-radius: 12px;
    overflow: hidden;
    margin-top: 2rem;
}
.card-header {
    background: rgba(80, 20, 140, 0.35);
    padding: 1.4rem 1.6rem 1.2rem;
    border-bottom: 1px solid rgba(168, 85, 247, 0.2);
}
.movie-name {
    font-family: 'Orbitron', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 1px;
    margin-bottom: 5px;
}
.movie-dir {
    font-family: 'Exo 2', sans-serif;
    font-size: 0.88rem;
    color: #9D8FCF;
    font-style: italic;
}
.movie-dir span { color: #C084FC; font-style: normal; font-weight: 500; }

.card-body { padding: 1.4rem 1.6rem; }

.genre-wrap { display: flex; flex-wrap: wrap; gap: 7px; margin-bottom: 1.4rem; }
.genre-tag {
    background: rgba(168, 85, 247, 0.15);
    border: 1px solid rgba(168, 85, 247, 0.35);
    color: #C084FC;
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
}

.meta-grid { display: flex; gap: 12px; margin-bottom: 1.4rem; flex-wrap: wrap; }
.meta-box {
    background: rgba(30, 10, 60, 0.6);
    border: 1px solid rgba(168, 85, 247, 0.2);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    min-width: 130px;
}
.mlbl {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px; letter-spacing: 2px;
    color: #6B4FA0; text-transform: uppercase;
    display: block; margin-bottom: 5px;
}
.mval { font-family: 'Exo 2', sans-serif; font-size: 1rem; font-weight: 500; color: #E8E0FF; }
.star-filled { color: #A855F7; text-shadow: 0 0 6px #A855F7; }
.star-empty  { color: #2D1B50; }
.rating-num  { font-family: 'Share Tech Mono', monospace; font-size: 11px; color: #7C5FBF; margin-left: 6px; }

.cast-lbl {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px; letter-spacing: 2px;
    color: #6B4FA0; text-transform: uppercase;
    display: block; margin-bottom: 8px;
}
.cast-wrap { display: flex; flex-wrap: wrap; gap: 7px; margin-bottom: 1.4rem; }
.cast-chip {
    background: rgba(20, 8, 45, 0.8);
    border: 1px solid rgba(100, 60, 180, 0.35);
    border-radius: 6px;
    padding: 5px 12px;
    font-family: 'Exo 2', sans-serif;
    font-size: 0.88rem;
    color: #C4B8E8;
}

.synopsis-box {
    background: rgba(25, 10, 55, 0.7);
    border: 1px solid rgba(168, 85, 247, 0.15);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}
.synopsis-text {
    font-family: 'Exo 2', sans-serif;
    font-size: 0.95rem;
    line-height: 1.85;
    color: #B0A0D8;
    font-weight: 300;
    font-style: italic;
}

/* ── JSON block ── */
.stJson {
    background: #030108 !important;
    border: 1px solid rgba(168, 85, 247, 0.2) !important;
    border-radius: 8px !important;
    font-family: 'Share Tech Mono', monospace !important;
    color: #9D7FEF !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #06040F; }
::-webkit-scrollbar-thumb { background: #4A2870; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Hero Section ──
st.markdown("""
<div class="galaxy-hero">
    <span class="blink-icon">🎬</span>
    <div class="galaxy-title">Movie Extractor</div>
    <div class="galaxy-subtitle">Galaxy Edition</div>
    <div class="galaxy-tagline">Powered by AI · Deep Space Intelligence</div>
</div>
<div class="galaxy-divider"><div class="divider-dot"></div></div>
""", unsafe_allow_html=True)


# ── Model ──
model = ChatMistralAI(model="mistral-small-2506")


# ── Pydantic Schema ──
class Movie(BaseModel):
    title: str
    release_year: Optional[int]
    genre: List[str]
    director: Optional[str]
    cast: List[str]
    rating: Optional[float]
    summary: str


# ── Parser & Prompt ──
parser = PydanticOutputParser(pydantic_object=Movie)

prompt = ChatPromptTemplate.from_messages([
    ('system', "Extract movie information from the paragraph.\n{format_instructions}"),
    ('human', "{paragraph}")
])


# ── Input ──
paragraph = st.text_area(
    "TRANSMISSION INPUT",
    placeholder="Paste any movie description, review, or synopsis into the void…",
    height=200
)


# ── Extract Button ──
if st.button("🚀 LAUNCH EXTRACTION"):
    if paragraph.strip() == "":
        st.warning("Please enter a movie description first.")
    else:
        with st.spinner("Scanning the cosmos…"):
            final_prompt = prompt.invoke({
                "paragraph": paragraph,
                "format_instructions": parser.get_format_instructions()
            })
            response = model.invoke(final_prompt)
            parsed = parser.parse(response.content)
            data = parsed.model_dump()

        # ── Genre tags ──
        genre_html = "".join(f'<span class="genre-tag">{g}</span>' for g in data["genre"])

        # ── Star rating ──
        if data["rating"] is not None:
            filled = round(data["rating"] / 2)
            stars_html = "".join(
                f'<span class="star-{"filled" if i <= filled else "empty"}">★</span>'
                for i in range(1, 6)
            )
            stars_html += f'<span class="rating-num">{data["rating"]:.1f}/10</span>'
        else:
            stars_html = '<span style="color:#4A3870;font-size:0.88rem;">N/A</span>'

        # ── Cast chips ──
        cast_html = "".join(f'<span class="cast-chip">{c}</span>' for c in data["cast"])

        director_html = (
            f'Directed by <span>{data["director"]}</span>'
            if data["director"]
            else '<span style="opacity:0.4">Unknown commander</span>'
        )

        st.markdown(f"""
        <div class="result-card">
            <div class="card-header">
                <div class="movie-name">{data["title"]}</div>
                <div class="movie-dir">{director_html}</div>
            </div>
            <div class="card-body">
                <div class="genre-wrap">{genre_html}</div>
                <div class="meta-grid">
                    <div class="meta-box">
                        <span class="mlbl">Year</span>
                        <span class="mval">{data["release_year"] or "—"}</span>
                    </div>
                    <div class="meta-box">
                        <span class="mlbl">Rating</span>
                        <div style="display:flex;align-items:center;gap:3px;">{stars_html}</div>
                    </div>
                </div>
                <span class="cast-lbl">Cast</span>
                <div class="cast-wrap">{cast_html}</div>
                <div class="synopsis-box">
                    <div class="synopsis-text">{data["summary"]}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📡 Raw JSON Output"):
            st.json(data)
