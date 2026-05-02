"""
app.py — AI Resume to Job Description Matcher
Run: streamlit run app.py
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.text_processor import extract_text, extract_contact_info
from utils.matcher import compute_section_scores, ats_keyword_density

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Matcher",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.score-card {
    background: linear-gradient(135deg, #1a237e, #283593);
    border-radius: 16px; padding: 1.5rem; text-align: center; color: white;
}
.score-big { font-size: 3rem; font-weight: 800; }
.tag-green  { background:#e8f5e9; color:#1b5e20; border-radius:99px;
              padding:3px 12px; font-size:0.8rem; display:inline-block; margin:3px; }
.tag-red    { background:#ffebee; color:#b71c1c; border-radius:99px;
              padding:3px 12px; font-size:0.8rem; display:inline-block; margin:3px; }
.tag-blue   { background:#e3f2fd; color:#0d47a1; border-radius:99px;
              padding:3px 12px; font-size:0.8rem; display:inline-block; margin:3px; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎯 AI Resume ↔ Job Description Matcher")
st.markdown("Upload your resume and paste a job description to get your **match score**, **skill gap analysis**, and **ATS optimisation tips**.")

# ── Inputs ────────────────────────────────────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("📄 Your Resume")
    upload_mode = st.radio("Input method", ["Upload File (PDF / DOCX)", "Paste Text"], horizontal=True)
    resume_text = ""
    if upload_mode == "Upload File (PDF / DOCX)":
        uploaded = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])
        if uploaded:
            resume_text = extract_text(uploaded, uploaded.name)
            st.success(f"✅ Loaded {len(resume_text.split()):,} words from {uploaded.name}")
    else:
        resume_text = st.text_area("Paste your resume text here", height=250,
                                   placeholder="Copy-paste your full resume...")

with col_r:
    st.subheader("💼 Job Description")
    jd_text = st.text_area(
        "Paste the job description here", height=300,
        placeholder="Paste the full job description you are applying for...",
    )

# ── Analyse Button ────────────────────────────────────────────────────────────
st.markdown("---")
run = st.button("🚀 Analyse Match", type="primary", use_container_width=True)

if run:
    if not resume_text.strip():
        st.error("Please upload or paste your resume.")
        st.stop()
    if not jd_text.strip():
        st.error("Please paste the job description.")
        st.stop()

    with st.spinner("Analysing your resume against the job description..."):
        results = compute_section_scores(resume_text, jd_text)
        ats     = ats_keyword_density(resume_text, jd_text)
        contact = extract_contact_info(resume_text)

    overall = results["overall_score"]
    verdict = ("🟢 Strong Match" if overall >= 70
               else "🟠 Moderate Match" if overall >= 50
               else "🔴 Needs Work")

    # ── Overall score ─────────────────────────────────────────────────────────
    st.markdown("## 📊 Results")
    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        ("Overall Match",   overall,                     "blue"),
        ("Skill Match",     results["skills_score"],     "green"),
        ("Content Match",   results["content_score"],    "orange"),
        ("Experience Score",results["experience_score"], "purple"),
    ]
    colors = {"blue": "#1565C0", "green": "#2E7D32", "orange": "#E65100", "purple": "#6A1B9A"}
    for col, (label, val, color) in zip([c1, c2, c3, c4], metrics):
        with col:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=val,
                title={"text": label, "font": {"size": 13}},
                number={"suffix": "%", "font": {"size": 22}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar":  {"color": colors[color]},
                    "steps": [{"range": [0, 50], "color": "#f5f5f5"},
                              {"range": [50, 75], "color": "#fffde7"},
                              {"range": [75, 100], "color": "#e8f5e9"}],
                }
            ))
            fig.update_layout(height=200, margin=dict(t=30, b=0, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"### Verdict: {verdict} — **{overall:.0f}%**")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🧠 Skill Gap", "🔍 ATS Keywords", "👤 Resume Info", "💡 Recommendations"])

    # Tab 1: Skill gap
    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader(f"✅ Matched Skills ({len(results['matched_skills'])})")
            if results["matched_skills"]:
                st.markdown(" ".join([f"<span class='tag-green'>{s}</span>"
                                      for s in results["matched_skills"]]),
                            unsafe_allow_html=True)
            else:
                st.info("No common skill keywords found.")

        with col_b:
            st.subheader(f"❌ Missing Skills ({len(results['missing_skills'])})")
            if results["missing_skills"]:
                st.markdown(" ".join([f"<span class='tag-red'>{s}</span>"
                                      for s in results["missing_skills"]]),
                            unsafe_allow_html=True)
                st.caption("Add these to your resume if you have experience with them!")
            else:
                st.success("Great! Your resume mentions all skill keywords from the JD.")

        st.markdown("---")
        st.subheader("📈 Skills Radar")
        cats = ["Matched", "Missing", "Extra (bonus)"]
        vals = [len(results["matched_skills"]),
                len(results["missing_skills"]),
                len(results["extra_skills"])]
        fig_bar = px.bar(x=cats, y=vals,
                         color=cats,
                         color_discrete_map={"Matched": "#388e3c", "Missing": "#d32f2f", "Extra (bonus)": "#1565C0"},
                         labels={"x": "Category", "y": "Count"},
                         title="Skill Distribution")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Tab 2: ATS
    with tab2:
        st.subheader("🔍 ATS Keyword Frequency Analysis")
        st.markdown("These are the **most important keywords** from the JD and how often they appear in your resume.")
        ats_df = pd.DataFrame(ats).rename(columns={"keyword": "JD Keyword", "in_resume_count": "Times in Resume"})
        ats_df["Status"] = ats_df["Times in Resume"].apply(
            lambda x: "✅ Present" if x > 0 else "❌ Missing")
        ats_df = ats_df.sort_values("Times in Resume", ascending=False)
        st.dataframe(ats_df[["JD Keyword", "Times in Resume", "Status"]],
                     use_container_width=True, height=400)

        missing_kw = ats_df[ats_df["Times in Resume"] == 0]["JD Keyword"].tolist()
        if missing_kw:
            st.warning(f"⚠️ **{len(missing_kw)} ATS keywords missing** from your resume: "
                       + ", ".join(f"`{k}`" for k in missing_kw[:10]))

    # Tab 3: Resume info
    with tab3:
        st.subheader("👤 Detected Contact Info")
        st.json(contact)
        st.subheader("📝 Resume Text Preview")
        st.text_area("Full extracted text", resume_text, height=300, disabled=True)

    # Tab 4: Recommendations
    with tab4:
        st.subheader("💡 Personalised Recommendations")
        tips = []

        if overall < 50:
            tips.append("🔴 **Low match score.** Tailor your resume heavily — use exact phrases from the JD.")
        elif overall < 70:
            tips.append("🟠 **Moderate match.** Add the missing skills to your resume if applicable.")
        else:
            tips.append("🟢 **Strong match!** Minor tweaks to keyword density should get you through ATS.")

        if results["missing_skills"]:
            top3 = results["missing_skills"][:3]
            tips.append(f"📌 **Priority skills to add:** {', '.join(top3)}. Even a single project using these helps.")

        if len(missing_kw := ats_df[ats_df["Times in Resume"] == 0]["JD Keyword"].tolist()) > 5:
            tips.append(f"📋 **ATS risk:** {len(missing_kw)} JD keywords missing. Add them naturally in your summary or skills section.")

        tips.append("📝 **Quantify achievements** — numbers make recruiters stop scrolling. E.g., 'improved accuracy by 15%'")
        tips.append("🔗 **Add GitHub links** for every project mentioned — recruiters want to see working code.")
        tips.append("🎯 **Customise your summary** for each application — 3-4 sentences matching the JD's language exactly.")

        for tip in tips:
            st.markdown(f"- {tip}")

else:
    st.markdown("""
    <div style='text-align:center; padding: 3rem; opacity:0.6;'>
        <h3>Upload your resume + paste a job description → click Analyse Match</h3>
        <p>Supports PDF, DOCX, and plain text resumes</p>
    </div>
    """, unsafe_allow_html=True)
