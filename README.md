# 🎬 Movie Information Extractor

A Streamlit web app that extracts structured movie information from unstructured text paragraphs using **Mistral AI** and **LangChain** — and returns clean, validated JSON output.

🔗 **Live Demo**: [movie-infomation-extractor.streamlit.app](https://movie-infomation-extractor-kf7eydfr6v468vymieyvrp.streamlit.app/)

---

## 📌 Features

- Paste any movie-related paragraph and extract structured data instantly
- Uses `mistral-small-2506` via LangChain's `ChatMistralAI` integration
- Pydantic schema validation ensures clean, typed JSON output
- Extracts: **Title**, **Release Year**, **Genre**, **Director**, **Cast**, **Rating**, and **Summary**
- Simple and clean Streamlit UI

---

## 🧱 Tech Stack

| Layer        | Technology                          |
|--------------|--------------------------------------|
| Frontend     | Streamlit                            |
| LLM          | Mistral AI (`mistral-small-2506`)    |
| Orchestration| LangChain Core                       |
| Parsing      | Pydantic + `PydanticOutputParser`    |
| Secrets      | Streamlit Secrets (`st.secrets`)     |

---

## 📁 Project Structure

```
movie-information-extractor/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── secrets.toml        # API key (not committed to Git)
└── README.md
```

---

## ⚙️ Setup & Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/your-username/movie-information-extractor.git
cd movie-information-extractor
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Mistral API key

Create a `.streamlit/secrets.toml` file:

```toml
MISTRAL_API_KEY = "your_mistral_api_key_here"
```

> ⚠️ Never commit `secrets.toml` to GitHub. Add it to `.gitignore`.

### 4. Run the app

```bash
streamlit run app.py
```

---

## 📦 Requirements

```
streamlit
langchain-core
langchain-mistralai
pydantic
```

> Add these to your `requirements.txt`.

---

## 🧠 How It Works

1. User pastes a paragraph describing a movie
2. A `ChatPromptTemplate` formats the input with Pydantic format instructions
3. `ChatMistralAI` sends the prompt to the Mistral API
4. `PydanticOutputParser` validates and parses the response into a typed `Movie` object
5. The result is displayed as structured JSON using `st.json()`

### Pydantic Schema

```python
class Movie(BaseModel):
    title: str
    release_year: Optional[int]
    genre: List[str]
    director: Optional[str]
    cast: List[str]
    rating: Optional[float]
    summary: str
```

---

## 📸 Demo

> Paste a paragraph like:

```
The Dark Knight, released in 2008, is a superhero film directed by Christopher Nolan.
Starring Christian Bale, Heath Ledger, and Aaron Eckhart, it holds an IMDb rating of 9.0.
The film explores themes of chaos and morality in Gotham City.
```

> And get back:

```json
{
  "title": "The Dark Knight",
  "release_year": 2008,
  "genre": ["Superhero", "Action", "Thriller"],
  "director": "Christopher Nolan",
  "cast": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"],
  "rating": 9.0,
  "summary": "A superhero film exploring themes of chaos and morality in Gotham City."
}
```

---

## 🚀 Deploy on Streamlit Cloud

1. Push your code to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and connect your repo
3. Add `MISTRAL_API_KEY` under **App Settings → Secrets**
4. Deploy!

---


## 🙋‍♂️ Author

**Aayush** — B.Tech Information Technology  
📍 Chandigarh Engineering College, Landran  
🔗 [LinkedIn](www.linkedin.com/in/aayush-sharma-b108a93b0) • [GitHub](https://github.com/Aayush20art)
