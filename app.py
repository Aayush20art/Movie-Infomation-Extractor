import streamlit as st

from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.output_parsers import PydanticOutputParser

# Load .env
import os

os.environ["MISTRAL_API_KEY"] = st.secrets["MISTRAL_API_KEY"]

# Streamlit Config
st.set_page_config(
    page_title="Movie JSON Extractor",
    page_icon="🎬"
)

# Title
st.title("🎬 Movie Information Extractor")

# Model
model = ChatMistralAI(model="mistral-small-2506")

# Pydantic Schema
class Movie(BaseModel):
    title: str
    release_year: Optional[int]
    genre: List[str]
    director: Optional[str]
    cast: List[str]
    rating: Optional[float]
    summary: str

# Parser
parser = PydanticOutputParser(pydantic_object=Movie)

# Prompt
prompt = ChatPromptTemplate.from_messages([
    
    ('system', """
Extract movie information from the paragraph.

{format_instructions}
"""),

    ('human', "{paragraph}")
])

# Input Box
paragraph = st.text_area(
    "Enter Movie Paragraph",
    height=250
)

# Button
if st.button("Extract Information"):

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