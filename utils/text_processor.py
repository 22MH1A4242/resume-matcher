"""
utils/text_processor.py
Text extraction + cleaning utilities
"""
import re
import PyPDF2
import docx
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)

STOP_WORDS = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

SKILL_KEYWORDS = {
    "python", "r", "sql", "java", "scala", "julia", "bash",
    "machine learning", "deep learning", "neural network", "nlp",
    "natural language processing", "computer vision", "reinforcement learning",
    "scikit-learn", "sklearn", "tensorflow", "keras", "pytorch", "xgboost",
    "lightgbm", "catboost", "transformers", "bert", "gpt", "llm",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    "tableau", "power bi", "looker", "excel", "google data studio",
    "aws", "azure", "gcp", "google cloud", "bigquery", "redshift", "s3",
    "mlflow", "airflow", "docker", "kubernetes", "git", "github", "ci/cd",
    "streamlit", "flask", "fastapi", "spark", "hadoop", "kafka", "dbt",
    "statistics", "probability", "hypothesis testing", "a/b testing",
    "regression", "classification", "clustering", "time series", "forecasting",
    "feature engineering", "feature selection", "eda", "data wrangling",
    "mysql", "postgresql", "mongodb", "sqlite", "snowflake", "databricks",
    "communication", "teamwork", "problem solving", "leadership",
}


def extract_text_from_pdf(file) -> str:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def extract_text_from_docx(file) -> str:
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


def extract_text(file, filename: str) -> str:
    fname = filename.lower()
    if fname.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif fname.endswith(".docx"):
        return extract_text_from_docx(file)
    else:
        return file.read().decode("utf-8", errors="ignore")


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_and_lemmatize(text: str) -> list:
    tokens = re.findall(r'\b[a-z]{3,}\b', clean_text(text))
    return [lemmatizer.lemmatize(t) for t in tokens if t not in STOP_WORDS]


def extract_skills(text: str) -> set:
    text_lower = text.lower()
    found = set()
    for skill in SKILL_KEYWORDS:
        if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
            found.add(skill)
    return found


def extract_contact_info(text: str) -> dict:
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", text)
    phone_match = re.search(r"[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{4,9}", text)
    return {
        "email": email_match.group() if email_match else "Not found",
        "phone": phone_match.group() if phone_match else "Not found",
    }