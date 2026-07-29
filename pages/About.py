"""About page — project information, tech stack, and architecture overview."""

from __future__ import annotations

import streamlit as st

from config import PROJECT_NAME, THEME_COLORS, VERSION
from utils.styles import (
    inject_global_styles,
    page_header,
    render_sidebar,
    section_heading,
    site_footer,
    skill_chips,
)

# ---------------------------------------------------------------------------
# Page config — must be the very first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title=f"About | {PROJECT_NAME}",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Content constants
# ---------------------------------------------------------------------------

_TECH_STACK = [
    ("Streamlit 1.41",    "UI framework — multi-page app with reactive widgets."),
    ("spaCy 3.8",         "NLP — named-entity recognition and tokenisation."),
    ("scikit-learn 1.5",  "ML utilities — TF-IDF, cosine similarity helpers."),
    ("Pandas 2.2",        "Tabular data manipulation and aggregation."),
    ("Plotly 5.24",       "Interactive charts — gauge, bar, radar, line."),
    ("pdfplumber 0.11",   "Primary PDF text extraction with layout awareness."),
    ("PyPDF2 3.0",        "Fallback PDF extraction for encrypted/scanned files."),
    ("python-docx 1.1",   "DOCX paragraph and table text extraction."),
    ("SQLite 3",          "Embedded database — resumes, skills, scores."),
    ("fpdf2 2.8",         "Reserved for PDF report export (future feature)."),
]

_FEATURES = [
    ("Resume Parsing",       "Extracts name, email, phone, GitHub, LinkedIn, and six content sections from PDF, DOCX, and TXT files using dual-engine extraction and spaCy NER."),
    ("Skill Extraction",     "Greedy left-to-right scan against a 550+ skill taxonomy across 10 categories, with alias normalisation and canonical display names."),
    ("Resume Scoring",       "Weighted section scoring (contact, skills, experience, education, projects, extras) plus a separate ATS-friendliness estimate."),
    ("Skill Gap Analysis",   "Radar chart and per-category progress bars comparing your skills against any of 8 curated job profiles."),
    ("Job Recommendations",  "Weighted Jaccard scoring ranks 8 job profiles by confidence, showing matched skills, missing skills, salary range, and market growth."),
    ("Persistent Storage",   "SQLite with WAL mode and foreign-key cascades stores every upload, skill set, and score for dashboard aggregation."),
]

_ARCHITECTURE = [
    ("app.py",                   "Streamlit entry point — Home page with hero, features, how-it-works, and tech strip."),
    ("config.py",                "Project-wide constants: paths, upload limits, theme colours."),
    ("pages/Dashboard.py",       "Live KPI cards, skills-by-category bar chart, score trend line chart."),
    ("pages/Resume_Analysis.py", "Upload → parse → score → display across five tabs."),
    ("pages/Skill_Gap.py",       "Role selector → radar chart → missing/matched skills → category progress bars."),
    ("pages/Job_Recommendation.py", "Upload → extract → rank 8 profiles → job cards with confidence bars."),
    ("utils/styles.py",          "Single CSS design system + sidebar renderer shared by every page."),
    ("utils/resume_parser.py",   "TextExtractor, ContactExtractor, NameExtractor, SectionExtractor, ResumeParser."),
    ("utils/skill_extractor.py", "SKILL_TAXONOMY, _AliasIndex, SkillExtractor — extract, normalise, categorise."),
    ("utils/score_calculator.py","ResumeScorer — section scores + ATS score → ScoreResult dataclass."),
    ("utils/recommendation.py",  "JOB_PROFILES, JobRecommender — weighted Jaccard → ranked JobMatch list."),
    ("utils/visualization.py",   "Plotly chart builders: score_gauge, section_scores_bar, skills_by_category, score_trend, skill_gap_radar, top_skills_bar."),
    ("utils/database.py",        "DatabaseManager façade over ResumeRepository, SkillRepository, ScoreRepository."),
    ("utils/text_processing.py", "clean_text, normalize_whitespace, split_into_lines, section slicing."),
]

_P   = THEME_COLORS["primary"]
_SEC = THEME_COLORS["secondary"]
_MUT = THEME_COLORS["text_muted"]
_SUR = THEME_COLORS["surface"]


# ---------------------------------------------------------------------------
# Page-specific CSS
# ---------------------------------------------------------------------------

def _inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        .about-tech-row {{
            display: flex; align-items: flex-start; gap: 0.75rem;
            padding: 0.85rem 1rem;
            background: {_SUR}; border: 1px solid #e2e8f0;
            border-radius: 10px; margin-bottom: 0.5rem;
        }}
        .about-tech-icon {{ font-size: 1.4rem; flex-shrink: 0; line-height: 1.3; }}
        .about-tech-name {{
            font-size: 0.88rem; font-weight: 700; color: {_P};
            margin: 0 0 0.15rem 0;
        }}
        .about-tech-desc {{ font-size: 0.8rem; color: {_MUT}; margin: 0; line-height: 1.45; }}
        .about-feat-row {{
            display: flex; align-items: flex-start; gap: 0.75rem;
            padding: 0.9rem 1rem;
            background: {_SUR}; border: 1px solid #e2e8f0;
            border-radius: 10px; margin-bottom: 0.5rem;
        }}
        .about-feat-icon {{ font-size: 1.4rem; flex-shrink: 0; line-height: 1.3; }}
        .about-feat-title {{
            font-size: 0.9rem; font-weight: 700; color: {_P};
            margin: 0 0 0.2rem 0;
        }}
        .about-feat-desc {{ font-size: 0.8rem; color: {_MUT}; margin: 0; line-height: 1.5; }}
        .about-arch-row {{
            display: flex; gap: 0.75rem; padding: 0.65rem 1rem;
            border-bottom: 1px solid #f0f4f8;
        }}
        .about-arch-row:last-child {{ border-bottom: none; }}
        .about-arch-file {{
            font-size: 0.78rem; font-weight: 600; color: {_SEC};
            font-family: 'Courier New', monospace; min-width: 220px; flex-shrink: 0;
        }}
        .about-arch-desc {{ font-size: 0.8rem; color: {_MUT}; line-height: 1.45; }}
        @media (prefers-color-scheme: dark) {{
            .about-tech-row, .about-feat-row {{
                background: #1a2535; border-color: #263347;
            }}
            .about-tech-name, .about-feat-title {{ color: #a8c4de; }}
            .about-tech-desc, .about-feat-desc  {{ color: #8a9db5; }}
            .about-arch-row {{ border-color: #1e2d40; }}
            .about-arch-file {{ color: #7eb8d8; }}
            .about-arch-desc {{ color: #8a9db5; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

def _render_overview() -> None:
    section_heading("Overview")
    st.markdown(
        f"""
        **{PROJECT_NAME}** (v{VERSION}) is a fully local, privacy-first web application
        that transforms a raw PDF, DOCX, or TXT resume into structured career intelligence.

        It extracts contact details, skills, education, and work experience using NLP,
        scores the resume against ATS criteria, identifies skill gaps relative to target
        job roles, and ranks 8 job profiles by match confidence — all without sending
        your data to any external service.

        Built with **Streamlit** for the UI, **spaCy** for NLP, **scikit-learn** for ML
        utilities, and **SQLite** for persistent storage, the entire stack runs on a
        single machine with no cloud dependency.
        """
    )


def _render_features() -> None:
    section_heading("Features")
    for title, desc in _FEATURES:
        st.markdown(
            f"""
            <div class="about-feat-row">
                <div>
                    <p class="about-feat-title">{title}</p>
                    <p class="about-feat-desc">{desc}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_tech_stack() -> None:
    section_heading("Tech Stack")
    col_a, col_b = st.columns(2, gap="medium")
    half = len(_TECH_STACK) // 2 + len(_TECH_STACK) % 2
    for col, items in ((col_a, _TECH_STACK[:half]), (col_b, _TECH_STACK[half:])):
        with col:
            for name, desc in items:
                st.markdown(
                    f"""
                    <div class="about-tech-row">
                        <div>
                            <p class="about-tech-name">{name}</p>
                            <p class="about-tech-desc">{desc}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def _render_architecture() -> None:
    section_heading("Project Architecture")
    rows = "".join(
        f'<div class="about-arch-row">'
        f'<span class="about-arch-file">{f}</span>'
        f'<span class="about-arch-desc">{d}</span>'
        f'</div>'
        for f, d in _ARCHITECTURE
    )
    st.markdown(
        f'<div style="background:{_SUR};border:1px solid #e2e8f0;border-radius:12px;'
        f'padding:0.25rem 0;">{rows}</div>',
        unsafe_allow_html=True,
    )


def _render_links() -> None:
    section_heading("Links & Resources")
    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        st.page_link("pages/Resume_Analysis.py", label="Analyse a Resume", use_container_width=True)
    with col2:
        st.page_link("pages/Skill_Gap.py", label="Skill Gap Analysis", use_container_width=True)
    with col3:
        st.page_link("pages/Job_Recommendation.py", label="Job Recommendations", use_container_width=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    inject_global_styles()
    _inject_styles()
    render_sidebar()
    page_header(
        "Project Info",
        f"About {PROJECT_NAME}",
        f"v{VERSION} · NLP-powered resume analysis, skill gap detection, and job matching — fully local.",
    )

    _render_overview()
    st.markdown("<br>", unsafe_allow_html=True)
    _render_features()
    st.markdown("<br>", unsafe_allow_html=True)
    _render_tech_stack()
    st.markdown("<br>", unsafe_allow_html=True)
    _render_architecture()
    st.markdown("<br>", unsafe_allow_html=True)
    _render_links()
    site_footer()


main()
