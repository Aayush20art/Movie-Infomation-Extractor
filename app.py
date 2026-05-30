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

/* ---------- Main App ---------- */
.stApp {
    background: linear-gradient(135deg, #050505 0%, #120018 50%, #220033 100%);
    color: white;
}

/* ---------- Header ---------- */
h1 {
    text-align: center;
    color: #d946ef !important;
    font-size: 3rem !important;
    font-weight: 800 !important;
}

/* ---------- Subheaders ---------- */
h3, .stSubheader {
    color: #c084fc !important;
}

/* ---------- Text Area ---------- */
.stTextArea textarea {
    background-color: #121212 !important;
    color: white !important;
    border: 2px solid #9333ea !important;
    border-radius: 15px !important;
    font-size: 16px !important;
    padding: 15px !important;
}

.stTextArea textarea:focus {
    border: 2px solid #d946ef !important;
    box-shadow: 0 0 15px rgba(217,70,239,0.6) !important;
}

/* Placeholder */
.stTextArea textarea::placeholder {
    color: #aaaaaa !important;
}

/* ---------- Labels ---------- */
label {
    color: white !important;
    font-weight: 600 !important;
    font-size: 17px !important;
}

/* ---------- Button ---------- */
.stButton > button {
    width: 100%;
    height: 55px;
    background: linear-gradient(90deg,#7e22ce,#d946ef);
    color: white !important;
    font-size: 18px;
    font-weight: 700;
    border: none;
    border-radius: 15px;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 25px rgba(217,70,239,0.5);
    background: linear-gradient(90deg,#9333ea,#e879f9);
}

/* ---------- JSON Output ---------- */
[data-testid="stJson"] {
    background-color: #111111 !important;
    border: 2px solid #9333ea !important;
    border-radius: 15px !important;
    padding: 15px !important;
}

/* ---------- Success / Warning ---------- */
.stAlert {
    border-radius: 15px !important;
}

/* ---------- Spinner ---------- */
.stSpinner {
    color: #d946ef !important;
}

/* ---------- Container Cards ---------- */
div[data-testid="stVerticalBlock"] > div {
    border-radius: 15px;
}

/* ---------- Hide Streamlit Footer ---------- */
footer {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}

header {
    visibility: hidden;
}

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
