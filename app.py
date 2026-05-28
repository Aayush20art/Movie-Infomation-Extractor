import streamlit as st

from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.output_parsers import PydanticOutputParser

# Load .env
import os

os.environ["MISTRAL_API_KEY"] = st.secrets["MISTRAL_API_KEY"]

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Movie JSON Extractor",
    page_icon="🎬",
    layout="centered"
)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>

/* Main Background */
.stApp {
    background: linear-gradient(135deg, #0f0f0f, #1a001f, #2b0033);
    color: white;
}

/* Title */
h1 {
    color: #d946ef !important;
    text-align: center;
    font-weight: bold;
}

/* Subheader */
h3 {
    color: #c084fc !important;
}

/* Text Area Label */
label {
    color: #ffffff !important;
    font-size: 18px !important;
    font-weight: 600 !important;
}

/* Text Area Box */
textarea {
    background-color: #111111 !important;
    color: #ffffff !important;
    border: 2px solid #a855f7 !important;
    border-radius: 12px !important;
    font-size: 16px !important;
}

/* Placeholder text */
textarea::placeholder {
    color: #cccccc !important;
}

/* Button Styling */
.stButton > button {
    background: linear-gradient(90deg, #7e22ce, #c026d3);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 25px;
    font-size: 16px;
    font-weight: bold;
    transition: 0.3s;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #9333ea, #e879f9);
    transform: scale(1.03);
}

/* JSON Output Box */
.stJson {
    background-color: #111111 !important;
    border: 2px solid #9333ea !important;
    border-radius: 12px !important;
    padding: 10px !important;
}

/* Warning Message */
.stAlert {
    border-radius: 10px;
}

/* Spinner Text */
.stSpinner > div {
    color: #ffffff !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------- TITLE --------------------
st.title("🎬 Movie Information Extractor")

# -------------------- MODEL --------------------
model = ChatMistralAI(model="mistral-small-2506")

# -------------------- PYDANTIC SCHEMA --------------------
class Movie(BaseModel):
    title: str
    release_year: Optional[int]
    genre: List[str]
    director: Optional[str]
    cast: List[str]
    rating: Optional[float]
    summary: str

# -------------------- PARSER --------------------
parser = PydanticOutputParser(pydantic_object=Movie)

# -------------------- PROMPT --------------------
prompt = ChatPromptTemplate.from_messages([
    
    ('system', """
Extract movie information from the paragraph.

{format_instructions}
"""),

    ('human', "{paragraph}")
])

# -------------------- INPUT BOX --------------------
paragraph = st.text_area(
    "Enter Movie Paragraph",
    placeholder="Paste movie description here...",
    height=250
)

# -------------------- BUTTON --------------------
if st.button("✨ Extract Information"):

    if paragraph.strip() == "":
        st.warning("Please enter a paragraph.")

    else:
        with st.spinner("Extracting Information..."):

            # Final Prompt
            final_prompt = prompt.invoke({
                "paragraph": paragraph,
                "format_instructions": parser.get_format_instructions()
            })

            # Model Response
            response = model.invoke(final_prompt)

            # Parse Output
            parsed_output = parser.parse(response.content)

            # JSON Output
            st.subheader("📦 Extracted JSON")

            st.json(parsed_output.model_dump())
