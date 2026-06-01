import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.output_parsers import PydanticOutputParser
import os

os.environ["MISTRAL_API_KEY"] = st.secrets["MISTRAL_API_KEY"]

st.set_page_config(
    page_title="CineExtract — Film Intelligence",
    page_icon="🎞️",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Mono:wght@300;400&display=swap');

/* ── Root Variables ── */
:root {
    --noir-black:    #0a0905;
    --noir-dark:     #111009;
    --noir-charcoal: #1c1a12;
    --noir-brown:    #2a2318;
    --gold-deep:     #b8860b;
    --gold-mid:      #d4a017;
    --gold-bright:   #f0c040;
    --gold-pale:     #f7dfa0;
    --cream:         #f5f0e8;
    --cream-dim:     #d4cbb8;
    --red-accent:    #8b1a1a;
    --red-bright:    #c0392b;
    --sepia:         #6b5a3e;
}

/* ── App Shell ── */
.stApp {
    background-color: var(--noir-black);
    background-image:
        radial-gradient(ellipse at 20% 0%, #1a1408 0%, transparent 60%),
        radial-gradient(ellipse at 80% 100%, #120c04 0%, transparent 60%);
    color: var(--cream);
    font-family: 'Crimson Pro', Georgia, serif;
}

/* Film grain overlay */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 9999;
    opacity: 0.6;
}

/* ── Hero ── */
.noir-hero {
    text-align: center;
    padding: 3.5rem 1rem 2rem;
    position: relative;
}

.noir-hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 1px;
    height: 3rem;
    background: linear-gradient(to bottom, transparent, var(--gold-mid));
    animation: drop-line 1.2s ease-out both;
}

.film-strip {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0;
    margin-bottom: 1.8rem;
}

.film-hole {
    width: 10px; height: 10px;
    border: 1.5px solid var(--gold-deep);
    border-radius: 2px;
    margin: 0 4px;
    opacity: 0.7;
    animation: filmhole-blink 4s ease-in-out infinite;
}

.film-hole:nth-child(2) { animation-delay: 0.4s; }
.film-hole:nth-child(4) { animation-delay: 0.8s; }
.film-hole:nth-child(5) { animation-delay: 1.2s; }

.film-frame {
    background: var(--noir-charcoal);
    border: 1.5px solid var(--gold-deep);
    padding: 6px 16px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--gold-mid);
    letter-spacing: 3px;
    text-transform: uppercase;
}

.noir-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 4.2rem;
    font-weight: 900;
    font-style: italic;
    color: var(--cream);
    line-height: 1;
    letter-spacing: -1px;
    margin: 0;
    animation: title-glow 4s ease-in-out infinite;
}

.noir-title span {
    color: var(--gold-mid);
}

.noir-subtitle {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: var(--sepia);
    margin-top: 0.6rem;
}

.noir-rule {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 2rem auto;
    max-width: 500px;
}

.noir-rule-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, transparent, var(--gold-deep), transparent);
    animation: rule-line-pulse 3s ease-in-out infinite;
}

.noir-rule-diamond {
    width: 6px; height: 6px;
    background: var(--gold-mid);
    transform: rotate(45deg);
    animation: diamond-spin 6s linear infinite;
}

/* ── Input Label ── */
label {
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 4px !important;
    text-transform: uppercase !important;
    color: var(--sepia) !important;
    font-weight: 400 !important;
    display: block !important;
    margin-bottom: 10px !important;
}

/* ── Text Area ── */
.stTextArea textarea {
    background-color: var(--noir-charcoal) !important;
    color: var(--cream-dim) !important;
    border: 1px solid var(--sepia) !important;
    border-radius: 0 !important;
    font-family: 'Crimson Pro', Georgia, serif !important;
    font-size: 17px !important;
    line-height: 1.7 !important;
    padding: 18px 20px !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
}

.stTextArea textarea:focus {
    border-color: var(--gold-mid) !important;
    box-shadow: 0 0 0 1px var(--gold-deep), inset 0 0 30px rgba(0,0,0,0.3) !important;
    outline: none !important;
}

.stTextArea textarea::placeholder {
    color: var(--sepia) !important;
    font-style: italic !important;
}

/* ── Keyframe Animations ── */
@keyframes shimmer {
    0%   { left: -100%; }
    60%  { left: 100%; }
    100% { left: 100%; }
}

@keyframes pulse-border {
    0%, 100% { border-color: var(--gold-deep); box-shadow: 0 0 0px rgba(212,160,23,0); }
    50%       { border-color: var(--gold-bright); box-shadow: 0 0 18px rgba(212,160,23,0.18); }
}

@keyframes diamond-spin {
    0%   { transform: rotate(45deg) scale(1); }
    50%  { transform: rotate(225deg) scale(1.4); opacity: 0.5; }
    100% { transform: rotate(405deg) scale(1); }
}

@keyframes filmhole-blink {
    0%, 90%, 100% { opacity: 0.7; }
    95%            { opacity: 0.15; }
}

@keyframes title-glow {
    0%, 100% { text-shadow: 0 0 40px rgba(212,160,23,0.08); }
    50%       { text-shadow: 0 0 100px rgba(212,160,23,0.22), 0 0 20px rgba(212,160,23,0.10); }
}

@keyframes rule-line-pulse {
    0%, 100% { opacity: 0.4; }
    50%       { opacity: 1; }
}

@keyframes drop-line {
    0%   { height: 0; opacity: 0; }
    100% { height: 3rem; opacity: 1; }
}

/* ── Button Wrapper — centered ── */
div[data-testid="stButton"] {
    display: flex !important;
    justify-content: center !important;
}

/* ── Button ── */
.stButton > button {
    width: 320px !important;
    height: 56px !important;
    background: transparent !important;
    border: 1px solid var(--gold-deep) !important;
    border-radius: 0 !important;
    color: var(--gold-bright) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 6px !important;
    text-transform: uppercase !important;
    font-weight: 400 !important;
    transition: all 0.35s ease !important;
    position: relative !important;
    overflow: hidden !important;
    animation: pulse-border 3.5s ease-in-out infinite !important;
}

/* Infinite shimmer sweep */
.stButton > button::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 60%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(240,192,64,0.12), transparent);
    animation: shimmer 3.5s ease-in-out infinite;
}

/* Corner accents on button */
.stButton > button::after {
    content: '';
    position: absolute;
    top: 4px; right: 4px;
    width: 8px; height: 8px;
    border-top: 1px solid var(--gold-mid);
    border-right: 1px solid var(--gold-mid);
    pointer-events: none;
}

.stButton > button:hover {
    background: rgba(212, 160, 23, 0.07) !important;
    border-color: var(--gold-bright) !important;
    box-shadow: 0 0 40px rgba(212,160,23,0.15), inset 0 0 40px rgba(212,160,23,0.04) !important;
    letter-spacing: 8px !important;
    animation: none !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: var(--gold-mid) !important;
}

/* ── Result Card ── */
.result-card {
    background: var(--noir-charcoal);
    border: 1px solid var(--sepia);
    margin-top: 2.5rem;
    position: relative;
    overflow: hidden;
}

/* corner ornaments */
.result-card::before,
.result-card::after {
    content: '';
    position: absolute;
    width: 20px; height: 20px;
}

.result-card::before {
    top: -1px; left: -1px;
    border-top: 2px solid var(--gold-mid);
    border-left: 2px solid var(--gold-mid);
}

.result-card::after {
    bottom: -1px; right: -1px;
    border-bottom: 2px solid var(--gold-mid);
    border-right: 2px solid var(--gold-mid);
}

.card-poster-strip {
    height: 5px;
    background: repeating-linear-gradient(
        90deg,
        var(--gold-deep) 0px, var(--gold-deep) 8px,
        var(--noir-black) 8px, var(--noir-black) 12px
    );
}

.card-header {
    padding: 2rem 2.5rem 1.5rem;
    border-bottom: 1px solid var(--noir-brown);
    position: relative;
}

.card-year-badge {
    position: absolute;
    top: 2rem; right: 2.5rem;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    color: var(--gold-deep);
    border: 1px solid var(--noir-brown);
    padding: 4px 10px;
}

.card-movie-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.4rem;
    font-weight: 700;
    font-style: italic;
    color: var(--cream);
    line-height: 1.1;
    margin: 0 0 0.5rem;
    padding-right: 5rem;
}

.card-director {
    font-family: 'Crimson Pro', Georgia, serif;
    font-size: 14px;
    color: var(--sepia);
    letter-spacing: 1px;
    font-style: italic;
}

.card-director span {
    color: var(--gold-pale);
    font-style: normal;
}

.card-body {
    padding: 1.8rem 2.5rem;
}

/* Genre tags */
.genre-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 1.8rem;
}

.genre-tag {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--gold-mid);
    border: 1px solid var(--gold-deep);
    padding: 4px 10px;
    background: rgba(184, 134, 11, 0.06);
}

/* Rating */
.rating-section {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 1.8rem;
    padding-bottom: 1.8rem;
    border-bottom: 1px solid var(--noir-brown);
}

.rating-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--sepia);
}

.stars {
    display: flex;
    gap: 3px;
}

.star-filled {
    color: var(--gold-mid);
    font-size: 18px;
}

.star-empty {
    color: var(--noir-brown);
    font-size: 18px;
}

.rating-num {
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    font-weight: 700;
    color: var(--gold-pale);
}

.rating-denom {
    font-family: 'Crimson Pro', serif;
    font-size: 13px;
    color: var(--sepia);
}

/* Cast */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: var(--sepia);
    margin-bottom: 10px;
    display: block;
}

.cast-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 1.8rem;
}

.cast-chip {
    font-family: 'Crimson Pro', serif;
    font-size: 15px;
    color: var(--cream-dim);
    background: var(--noir-brown);
    padding: 5px 14px;
    border-left: 2px solid var(--gold-deep);
    font-style: italic;
}

/* Synopsis */
.synopsis-box {
    background: var(--noir-dark);
    border-left: 2px solid var(--red-accent);
    padding: 1.2rem 1.5rem;
}

.synopsis-text {
    font-family: 'Crimson Pro', serif;
    font-size: 17px;
    line-height: 1.75;
    color: var(--cream-dim);
    font-style: italic;
}

/* ── Expander ── */
.stExpander {
    background: var(--noir-charcoal) !important;
    border: 1px solid var(--noir-brown) !important;
    border-radius: 0 !important;
    margin-top: 1.2rem !important;
}

.stExpander summary {
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 3px !important;
    color: var(--sepia) !important;
    text-transform: uppercase !important;
}

/* ── Warning / Alert ── */
.stAlert {
    background: rgba(139, 26, 26, 0.12) !important;
    border: 1px solid var(--red-accent) !important;
    border-radius: 0 !important;
    color: var(--cream-dim) !important;
}

/* ── JSON block ── */
[data-testid="stJson"] {
    background-color: var(--noir-dark) !important;
    border: 1px solid var(--noir-brown) !important;
    border-radius: 0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--noir-dark); }
::-webkit-scrollbar-thumb { background: var(--sepia); }

/* ── Hide chrome ── */
footer, #MainMenu, header { visibility: hidden; }

</style>
""", unsafe_allow_html=True)


# ── Hero ──
st.markdown("""
<div class="noir-hero">
    <div class="film-strip">
        <div class="film-hole"></div>
        <div class="film-hole"></div>
        <div class="film-frame">REEL 001</div>
        <div class="film-hole"></div>
        <div class="film-hole"></div>
    </div>
    <div class="noir-title">Cine<span>Extract</span></div>
    <div class="noir-subtitle">Film Intelligence System · Est. MMXXV</div>
    <div class="noir-rule">
        <div class="noir-rule-line"></div>
        <div class="noir-rule-diamond"></div>
        <div class="noir-rule-line"></div>
    </div>
</div>
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
    placeholder="Drop a synopsis, review, or description into the reel…",
    height=180
)

st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

# ── Extract Button ──
if st.button("◈  DEVELOP THE REEL"):
    if paragraph.strip() == "":
        st.warning("No transmission detected. Feed the machine a description.")
    else:
        with st.spinner("Developing the negative…"):
            final_prompt = prompt.invoke({
                "paragraph": paragraph,
                "format_instructions": parser.get_format_instructions()
            })
            response = model.invoke(final_prompt)
            parsed = parser.parse(response.content)
            data = parsed.model_dump()

        # ── Genre tags ──
        genre_html = "".join(
            f'<span class="genre-tag">{g}</span>'
            for g in data["genre"]
        )

        # ── Star rating ──
        if data["rating"] is not None:
            filled = round(data["rating"] / 2)
            stars_html = "".join(
                f'<span class="star-{"filled" if i <= filled else "empty"}">★</span>'
                for i in range(1, 6)
            )
            rating_display = f'''
            <div class="rating-section">
                <span class="rating-label">Rating</span>
                <div class="stars">{stars_html}</div>
                <span class="rating-num">{data["rating"]:.1f}</span>
                <span class="rating-denom">/10</span>
            </div>'''
        else:
            rating_display = f'''
            <div class="rating-section">
                <span class="rating-label">Rating</span>
                <span style="font-family:'DM Mono',monospace;font-size:11px;color:#6b5a3e;letter-spacing:2px;">UNRATED</span>
            </div>'''

        # ── Cast chips ──
        cast_html = "".join(
            f'<span class="cast-chip">{c}</span>'
            for c in data["cast"]
        )

        # ── Director ──
        director_html = (
            f'Directed by <span>{data["director"]}</span>'
            if data["director"]
            else '<span style="opacity:0.35;font-style:italic">Director unknown</span>'
        )

        # ── Year badge ──
        year_html = str(data["release_year"]) if data["release_year"] else "——"

        st.markdown(f"""
        <div class="result-card">
            <div class="card-poster-strip"></div>
            <div class="card-header">
                <div class="card-year-badge">{year_html}</div>
                <div class="card-movie-title">{data["title"]}</div>
                <div class="card-director">{director_html}</div>
            </div>
            <div class="card-body">
                <div class="genre-row">{genre_html}</div>
                {rating_display}
                <span class="section-label">Starring</span>
                <div class="cast-row">{cast_html}</div>
                <span class="section-label">Synopsis</span>
                <div class="synopsis-box">
                    <div class="synopsis-text">{data["summary"]}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("◈  RAW DISPATCH — JSON FEED"):
            st.json(data)
