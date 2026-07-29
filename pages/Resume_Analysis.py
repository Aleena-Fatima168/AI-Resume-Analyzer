from __future__ import annotations

import streamlit as st

from config import MAX_FILE_SIZE, PROJECT_NAME
from utils.database import DatabaseManager
from utils.resume_parser import ResumeParser
from utils.score_calculator import ResumeScorer
from utils.skill_extractor import SkillExtractor
from utils.styles import (
    empty_state,
    inject_global_styles,
    page_header,
    progress_bar,
    render_sidebar,
    section_heading,
    site_footer,
    skill_chips,
    stat_card,
    summary_bar,
)
from utils.visualization import score_gauge, section_scores_bar

st.set_page_config(
    page_title=f"Resume Analysis | {PROJECT_NAME}",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

_UPLOADER_EXTENSIONS = ["pdf", "docx", "txt"]
_MAX_LABEL = (
    f"{MAX_FILE_SIZE // (1024 * 1024)} MB"
    if MAX_FILE_SIZE >= 1024 * 1024
    else f"{MAX_FILE_SIZE // 1024} KB"
)


def _fmt_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1_048_576:
        return f"{n / 1024:.1f} KB"
    return f"{n / 1_048_576:.2f} MB"


def _cache_key(uploaded) -> str:
    return f"analysis_{uploaded.name}_{uploaded.size}"


def _run_analysis(uploaded) -> dict | None:
    key = _cache_key(uploaded)
    if key in st.session_state:
        return st.session_state[key]

    with st.spinner("Parsing resume…"):
        try:
            parser = ResumeParser(uploaded, filename=uploaded.name)
            resume_data = parser.parse()
        except Exception as exc:
            st.error(f"Could not parse resume: {exc}")
            return None

    with st.spinner("Extracting skills…"):
        extractor = SkillExtractor()
        skills = extractor.extract_skills(resume_data.raw_text)
        categorized = extractor.categorize_skills(skills)

    with st.spinner("Scoring resume…"):
        scorer = ResumeScorer()
        result = scorer.score(resume_data, skills)

    with st.spinner("Saving to database…"):
        try:
            db = DatabaseManager()
            resume_id = db.save_analysis(
                resume_data=resume_data,
                filename=uploaded.name,
                file_type=uploaded.name.rsplit(".", 1)[-1].lower(),
                categorized_skills=categorized,
                total_score=result.total_score,
                ats_score=result.ats_score,
                section_scores=result.section_scores,
                feedback=result.feedback,
            )
        except Exception:
            resume_id = None

    payload = {
        "resume_data": resume_data,
        "skills":      skills,
        "categorized": categorized,
        "result":      result,
        "resume_id":   resume_id,
        "filename":    uploaded.name,
        "filesize":    uploaded.size,
    }
    st.session_state[key] = payload
    return payload


def _render_uploader():
    st.markdown(
        f"""
        <div class="ara-upload-zone">
            <p class="ara-upload-title">Upload your resume</p>
            <p class="ara-upload-sub">PDF, DOCX, or TXT · max {_MAX_LABEL} · drag &amp; drop supported</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return st.file_uploader(
        "Resume file",
        type=_UPLOADER_EXTENSIONS,
        label_visibility="collapsed",
        help="Upload a PDF, DOCX, or TXT resume to analyse.",
    )


def _render_scores(payload: dict) -> None:
    result = payload["result"]
    section_heading("Resume Score", "Overall quality and ATS-friendliness of your resume.")

    g1, g2 = st.columns(2, gap="medium")
    with g1:
        with st.container(border=True):
            st.plotly_chart(score_gauge(result.total_score, "Overall Score"), use_container_width=True)
    with g2:
        with st.container(border=True):
            st.plotly_chart(score_gauge(result.ats_score, "ATS Score"), use_container_width=True)

    with st.container(border=True):
        st.plotly_chart(section_scores_bar(result.section_scores), use_container_width=True)

    if result.feedback:
        section_heading("Feedback", "Actionable suggestions to improve your resume.")
        for tip in result.feedback:
            st.markdown(f"- {tip}")


def _render_summary(payload: dict) -> None:
    summary_bar([
        ("File",  payload["filename"]),
        ("Size",  _fmt_size(payload["filesize"])),
        ("Skills", str(len(payload["skills"]))),
        ("Score", f"{payload['result'].total_score:.0f} / 100"),
        ("Grade", payload["result"].grade),
    ])


def _render_tabs(payload: dict) -> None:
    rd          = payload["resume_data"]
    categorized = payload["categorized"]

    tab_text, tab_contact, tab_skills, tab_edu, tab_exp = st.tabs([
        "Extracted Text", "Contact Info", "Skills", "Education", "Experience",
    ])

    with tab_text:
        section_heading("Raw Extracted Text")
        st.text_area(
            "text",
            value=rd.raw_text or "(no text extracted)",
            height=320,
            disabled=True,
            label_visibility="collapsed",
        )

    with tab_contact:
        section_heading("Contact Information")
        for label, value in [
            ("Name",     rd.name     or "—"),
            ("Email",    rd.email    or "—"),
            ("Phone",    rd.phone    or "—"),
            ("GitHub",   rd.github   or "—"),
            ("LinkedIn", rd.linkedin or "—"),
        ]:
            c1, c2 = st.columns([1, 3])
            c1.markdown(f"**{label}**")
            c2.markdown(value)

    with tab_skills:
        section_heading(
            "Detected Skills",
            f"{len(payload['skills'])} skills found across {len(categorized)} categories.",
        )
        if categorized:
            for category, skills_list in categorized.items():
                st.markdown(f"**{category}**")
                skill_chips(skills_list, variant="blue")
                st.markdown("")
        else:
            empty_state("", "No skills detected", "Ensure the resume contains plain text and lists skills explicitly.")

    with tab_edu:
        section_heading("Education")
        if rd.education:
            for line in rd.education:
                st.markdown(f"- {line}")
        else:
            empty_state("", "No education section found", "Add an education section with degree, institution, and year.")

    with tab_exp:
        section_heading("Experience")
        if rd.experience:
            for line in rd.experience:
                st.markdown(f"- {line}")
        else:
            empty_state("", "No experience section found", "Add a work experience section with job titles and responsibilities.")


def main() -> None:
    inject_global_styles()
    render_sidebar()
    page_header(
        "NLP Analysis",
        "Resume Analysis",
        "Upload a PDF, DOCX, or TXT resume to extract skills, score completeness, and get actionable feedback.",
    )

    uploaded = _render_uploader()

    if uploaded is None:
        st.markdown("<br>", unsafe_allow_html=True)
        empty_state(
            "",
            "No resume uploaded yet",
            "Upload a PDF, DOCX, or TXT file above to begin analysis.",
        )
        site_footer()
        return

    if uploaded.size > MAX_FILE_SIZE:
        st.error(f"File exceeds the {_MAX_LABEL} limit ({_fmt_size(uploaded.size)} uploaded).")
        site_footer()
        return

    payload = _run_analysis(uploaded)
    if payload is None:
        site_footer()
        return

    st.markdown("<br>", unsafe_allow_html=True)
    _render_summary(payload)
    _render_scores(payload)
    st.markdown("<br>", unsafe_allow_html=True)
    _render_tabs(payload)
    site_footer()


main()
