from __future__ import annotations

from pathlib import Path

import streamlit as st

from config import PROJECT_NAME, THEME_COLORS, VERSION
from utils.styles import inject_global_styles, render_sidebar, site_footer

_HERE = Path(__file__).resolve().parent

st.set_page_config(
    page_title=PROJECT_NAME,
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

FEATURES = [
    (
        "Resume Analysis",
        "pages/Resume_Analysis.py",
        "Extract structured data from PDF or DOCX resumes — contact info, skills, "
        "education, and work experience — with NLP-powered parsing.",
    ),
    (
        "Dashboard",
        "pages/Dashboard.py",
        "Track your resume score, skill coverage, and job-fit metrics in one "
        "consolidated view that updates with every upload.",
    ),
    (
        "Skill Gap Analysis",
        "pages/Skill_Gap.py",
        "Compare your current skill set against target job requirements and receive "
        "a prioritised list of areas to develop.",
    ),
    (
        "Job Recommendations",
        "pages/Job_Recommendation.py",
        "Discover roles that align with your experience and strengths, ranked by "
        "compatibility score computed from your resume.",
    ),
]

HOW_IT_WORKS = [
    ("01", "Upload",  "Drop your PDF or DOCX resume into the analyzer."),
    ("02", "Parse",   "NLP extracts text, skills, education, and experience."),
    ("03", "Score",   "Algorithms evaluate completeness, clarity, and fit."),
    ("04", "Act",     "Review gaps, explore roles, and iterate your resume."),
]

TECH_STACK = [
    "Python 3.11",
    "Streamlit",
    "spaCy NLP",
    "scikit-learn",
    "Plotly",
    "SQLite",
]

_P   = THEME_COLORS["primary"]
_SEC = THEME_COLORS["secondary"]
_ACC = THEME_COLORS["accent"]
_MUT = THEME_COLORS["text_muted"]
_TXT = THEME_COLORS["text"]
_SUR = THEME_COLORS["surface"]


def _inject_home_styles() -> None:
    st.markdown(
        f"""
        <style>
        .home-hero {{
            background: linear-gradient(135deg, {_P} 0%, {_SEC} 60%, #2a5f8a 100%);
            border-radius: 20px;
            padding: 3rem 2.75rem;
            margin-bottom: 2.25rem;
            color: #ffffff;
            box-shadow: 0 16px 48px rgba(30,58,95,0.28);
            position: relative; overflow: hidden;
        }}
        .home-hero::before {{
            content: '';
            position: absolute; top: -60px; right: -60px;
            width: 280px; height: 280px; border-radius: 50%;
            background: rgba(255,255,255,0.04); pointer-events: none;
        }}
        .home-hero::after {{
            content: '';
            position: absolute; bottom: -80px; right: 80px;
            width: 200px; height: 200px; border-radius: 50%;
            background: rgba(244,162,97,0.08); pointer-events: none;
        }}
        .home-hero-eyebrow {{
            display: inline-block;
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.25);
            border-radius: 20px; font-size: 0.75rem;
            font-weight: 600; letter-spacing: 0.07em;
            text-transform: uppercase;
            padding: 0.28rem 0.85rem; margin-bottom: 1rem;
            color: rgba(255,255,255,0.92);
        }}
        .home-hero h1 {{
            font-size: 2.5rem; font-weight: 800;
            margin: 0 0 1rem 0; letter-spacing: -0.04em;
            line-height: 1.15; color: #ffffff;
        }}
        .home-hero-sub {{
            font-size: 1rem; line-height: 1.65;
            opacity: 0.88; max-width: 560px; margin: 0;
        }}
        .home-logo-box {{
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 20px; padding: 2.25rem 1.75rem;
            text-align: center;
            box-shadow: 0 16px 48px rgba(30,58,95,0.28);
        }}
        .home-logo-title {{
            font-size: 0.95rem; font-weight: 700;
            color: #ffffff; margin: 0 0 0.25rem 0;
        }}
        .home-logo-sub {{
            font-size: 0.75rem; color: rgba(255,255,255,0.58); margin: 0;
        }}
        .home-logo-pill {{
            display: inline-block;
            background: rgba(42,157,143,0.25);
            border: 1px solid rgba(42,157,143,0.5);
            color: #7ee8de; border-radius: 20px;
            font-size: 0.7rem; font-weight: 600;
            padding: 0.2rem 0.65rem; margin-top: 0.85rem;
        }}
        .home-feat {{
            background: {_SUR};
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.6rem 1.4rem;
            height: 100%;
            box-shadow: 0 1px 8px rgba(0,0,0,0.05);
            transition: box-shadow 0.22s ease, transform 0.22s ease, border-color 0.22s ease;
            position: relative; overflow: hidden;
        }}
        .home-feat::before {{
            content: '';
            position: absolute; top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, {_SEC}, {_ACC});
            opacity: 0; transition: opacity 0.22s ease;
        }}
        .home-feat:hover {{
            box-shadow: 0 10px 32px rgba(30,58,95,0.12);
            transform: translateY(-3px); border-color: #c8d6e5;
        }}
        .home-feat:hover::before {{ opacity: 1; }}
        .home-feat h3 {{
            color: {_P}; font-size: 0.98rem; font-weight: 700;
            margin: 0 0 0.45rem 0; letter-spacing: -0.01em;
        }}
        .home-feat p {{
            color: {_MUT}; font-size: 0.85rem;
            line-height: 1.6; margin: 0;
        }}
        .home-hiw {{
            background: linear-gradient(135deg, #f0f4f8 0%, #e8eef5 100%);
            border-radius: 14px; padding: 1.75rem 1.5rem;
        }}
        .home-hiw-num {{
            font-size: 1.5rem; font-weight: 800;
            color: {_SEC}; opacity: 0.35; line-height: 1;
            flex-shrink: 0; min-width: 2rem;
        }}
        .home-hiw-title {{
            font-size: 0.92rem; font-weight: 700;
            color: {_P}; margin: 0 0 0.2rem 0;
        }}
        .home-hiw-desc {{
            font-size: 0.8rem; color: {_MUT}; margin: 0; line-height: 1.5;
        }}
        .home-tech-strip {{ display: flex; flex-wrap: wrap; gap: 0.55rem; margin-top: 0.5rem; }}
        .home-tech-chip {{
            display: inline-flex; align-items: center; gap: 0.35rem;
            background: {_SUR}; border: 1px solid #e2e8f0;
            border-radius: 8px; padding: 0.32rem 0.7rem;
            font-size: 0.78rem; font-weight: 500; color: {_TXT};
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }}
        @media (prefers-color-scheme: dark) {{
            .home-feat {{ background: #1a2535; border-color: #263347; }}
            .home-feat:hover {{ border-color: #3a5070; }}
            .home-feat h3 {{ color: #a8c4de; }}
            .home-feat p  {{ color: #8a9db5; }}
            .home-hiw     {{ background: linear-gradient(135deg, #1a2535 0%, #1e2d40 100%); }}
            .home-hiw-title {{ color: #a8c4de; }}
            .home-hiw-desc  {{ color: #8a9db5; }}
            .home-tech-chip {{ background: #1a2535; border-color: #263347; color: #c0d4e8; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_hero() -> None:
    left, right = st.columns([1.65, 1], gap="large")

    with left:
        st.markdown(
            f"""
            <div class="home-hero">
                <span class="home-hero-eyebrow">AI-Powered Career Tool</span>
                <h1>{PROJECT_NAME}</h1>
                <p class="home-hero-sub">
                    Upload your resume, uncover strengths and skill gaps, and receive
                    actionable recommendations tailored to your target roles — all in
                    one intelligent workspace.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
            <div style="padding-top:0.25rem;">
                <div class="home-logo-box"
                     style="background:linear-gradient(135deg,{_P} 0%,#0d1f35 100%);
                            border:1px solid rgba(255,255,255,0.12);">
                    <p class="home-logo-title">{PROJECT_NAME}</p>
                    <p class="home-logo-sub">Resume · Skills · Careers</p>
                    <span class="home-logo-pill">NLP-Powered Analysis</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    btn1, btn2, _ = st.columns([1, 1, 2], gap="small")
    with btn1:
        st.page_link(str(_HERE / "pages" / "Resume_Analysis.py"), label="Analyze My Resume", use_container_width=True)
    with btn2:
        st.page_link(str(_HERE / "pages" / "Dashboard.py"), label="View Dashboard", use_container_width=True)


def _render_features() -> None:
    st.markdown(
        '<p class="ara-section-title">What you can do</p>'
        '<p class="ara-section-sub">Four integrated tools that take your resume from raw document to career clarity.</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(4, gap="medium")
    for col, (title, page, desc) in zip(cols, FEATURES):
        with col:
            st.markdown(
                f"""
                <div class="home-feat">
                    <h3>{title}</h3>
                    <p>{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_how_it_works() -> None:
    st.markdown(
        '<p class="ara-section-title">How it works</p>'
        '<p class="ara-section-sub">Four steps from upload to actionable insight.</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(4, gap="medium")
    for col, (num, title, desc) in zip(cols, HOW_IT_WORKS):
        with col:
            st.markdown(
                f"""
                <div class="home-hiw">
                    <div style="display:flex;align-items:flex-start;gap:0.9rem;">
                        <span class="home-hiw-num">{num}</span>
                        <div>
                            <p class="home-hiw-title">{title}</p>
                            <p class="home-hiw-desc">{desc}</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_tech_stack() -> None:
    st.markdown(
        '<p class="ara-section-title">Built with</p>'
        '<p class="ara-section-sub">Open-source tools powering every layer of the analysis pipeline.</p>',
        unsafe_allow_html=True,
    )
    chips = "".join(
        f'<span class="home-tech-chip">{name}</span>'
        for name in TECH_STACK
    )
    st.markdown(f'<div class="home-tech-strip">{chips}</div>', unsafe_allow_html=True)


inject_global_styles()
_inject_home_styles()
render_sidebar()
_render_hero()

st.markdown("<br>", unsafe_allow_html=True)
_render_features()

st.markdown("<br>", unsafe_allow_html=True)
_render_how_it_works()

st.markdown("<br>", unsafe_allow_html=True)
_render_tech_stack()

site_footer()
