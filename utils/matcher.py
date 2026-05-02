"""
utils/matcher.py
Matching engine: TF-IDF + cosine similarity + skill gap analysis
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.text_processor import (clean_text, tokenize_and_lemmatize,
                                   extract_skills)


def tfidf_match_score(resume_text: str, jd_text: str) -> float:
    """Return cosine similarity (0-1) between resume and JD using TF-IDF."""
    corpus = [
        " ".join(tokenize_and_lemmatize(resume_text)),
        " ".join(tokenize_and_lemmatize(jd_text)),
    ]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return float(score)


def skill_match_analysis(resume_text: str, jd_text: str) -> dict:
    """
    Returns:
        matched_skills  : skills in both resume and JD
        missing_skills  : skills in JD but NOT in resume
        extra_skills    : skills in resume but NOT in JD
        skill_score     : matched / total_jd_skills
    """
    resume_skills = extract_skills(resume_text)
    jd_skills     = extract_skills(jd_text)

    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    extra   = resume_skills - jd_skills

    score = len(matched) / max(len(jd_skills), 1)

    return {
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "extra_skills":   sorted(extra),
        "resume_skills":  sorted(resume_skills),
        "jd_skills":      sorted(jd_skills),
        "skill_score":    score,
    }


def compute_section_scores(resume_text: str, jd_text: str) -> dict:
    """
    Heuristic section-level scores:
        skills_score    : from skill_match_analysis
        content_score   : TF-IDF cosine
        experience_score: rough keyword density for experience terms
        overall         : weighted combination
    """
    tfidf  = tfidf_match_score(resume_text, jd_text)
    skills = skill_match_analysis(resume_text, jd_text)

    # Experience heuristic
    exp_keywords = ["year", "experience", "worked", "developed", "built",
                    "led", "managed", "designed", "implemented", "deployed"]
    resume_lower = resume_text.lower()
    exp_hits = sum(resume_lower.count(kw) for kw in exp_keywords)
    exp_score = min(exp_hits / 20, 1.0)  # cap at 1.0

    overall = (
        0.40 * skills["skill_score"]
        + 0.40 * tfidf
        + 0.20 * exp_score
    )

    return {
        "skills_score":     round(skills["skill_score"] * 100, 1),
        "content_score":    round(tfidf * 100, 1),
        "experience_score": round(exp_score * 100, 1),
        "overall_score":    round(overall * 100, 1),
        **{k: v for k, v in skills.items() if k != "skill_score"},
    }


def ats_keyword_density(resume_text: str, jd_text: str) -> list[dict]:
    """
    Find important JD keywords and their frequency in the resume.
    Useful for ATS optimization advice.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english",
                                 max_features=30)
    vectorizer.fit([jd_text])
    jd_keywords = vectorizer.get_feature_names_out()

    resume_lower = resume_text.lower()
    results = []
    for kw in jd_keywords:
        count = len([m for m in __import__("re").finditer(
            r"\b" + __import__("re").escape(kw) + r"\b", resume_lower)])
        results.append({"keyword": kw, "in_jd": True, "in_resume_count": count})

    return sorted(results, key=lambda x: x["in_resume_count"])
