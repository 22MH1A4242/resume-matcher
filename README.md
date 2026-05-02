https://resume-matcher-anjalidevimedapati.streamlit.app/

# 🎯 AI Resume ↔ Job Description Matcher

> **Skills demonstrated:** NLP · TF-IDF · Cosine Similarity · NLTK · Streamlit · ATS Optimisation · PDF parsing

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Download spaCy model
python -m spacy download en_core_web_sm

# 3. Launch the app
streamlit run app.py
```

## Project Structure

```
project2_resume_matcher/
├── app.py                  ← Streamlit app (main)
├── requirements.txt
├── utils/
│   ├── text_processor.py   ← PDF/DOCX extraction, skill detection, cleaning
│   └── matcher.py          ← TF-IDF scoring, skill gap, ATS keyword analysis
└── uploads/                ← Temp folder for uploaded files
```

## Features

| Feature | Description |
|---|---|
| Resume upload | PDF, DOCX, or paste text |
| Overall match score | Weighted combo of skill + content + experience scores |
| Skill gap analysis | Shows matched, missing, and bonus skills |
| ATS keyword analysis | Lists JD keywords missing from resume |
| Personalised tips | Actionable recommendations to improve the resume |
| Contact extraction | Auto-detects email and phone number |

## Resume Bullet Points (copy these!)

- Built NLP-powered resume-JD matching system using TF-IDF and cosine similarity achieving skill detection across 80+ technical keywords
- Implemented ATS keyword density analysis to identify resume gaps and optimise keyword placement
- Deployed as a Streamlit web app supporting PDF, DOCX, and text input with real-time match scoring
- Created a modular NLP pipeline with lemmatisation, stopword removal, and n-gram vectorisation
