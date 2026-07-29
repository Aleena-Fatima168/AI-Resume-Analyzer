from __future__ import annotations

import streamlit as st

from config import MAX_FILE_SIZE, PROJECT_NAME, THEME_COLORS
from utils.recommendation import JOB_PROFILES
from utils.resume_parser import ResumeParser
from utils.skill_extractor import SKILL_TAXONOMY, SkillExtractor
from utils.styles import (
    empty_state,
    inject_global_styles,
    page_header,
    progress_bar,
    render_sidebar,
    section_heading,
    site_footer,
    skill_chips,
    summary_bar,
)
from utils.visualization import skill_gap_radar

st.set_page_config(
    page_title=f"Skill Gap | {PROJECT_NAME}",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

_UPLOADER_EXTENSIONS = ["pdf", "docx", "txt"]
_SUC = THEME_COLORS["success"]
_WRN = THEME_COLORS["warning"]
_ERR = THEME_COLORS["error"]
_SEC = THEME_COLORS["secondary"]
_MUT = THEME_COLORS["text_muted"]


def _fmt_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1_048_576:
        return f"{n / 1024:.1f} KB"
    return f"{n / 1_048_576:.2f} MB"


def _cache_key(uploaded) -> str:
    return f"skill_gap_{uploaded.name}_{uploaded.size}"


def _extract_skills(uploaded) -> list[str] | None:
    key = _cache_key(uploaded)
    if key in st.session_state:
        return st.session_state[key]
    with st.spinner("Parsing resume and extracting skills…"):
        try:
            parser = ResumeParser(uploaded, filename=uploaded.name)
            resume_data = parser.parse()
            extractor = SkillExtractor()
            skills = extractor.extract_skills(resume_data.raw_text)
            st.session_state[key] = skills
            return skills
        except Exception as exc:
            st.error(f"Could not parse resume: {exc}")
            return None


def _build_gap_data(candidate_skills: list[str], profile_name: str) -> dict:
    profile          = JOB_PROFILES[profile_name]
    required_skills  = set(profile["required"].keys())
    nice_skills      = set(profile["nice_to_have"])
    candidate_set    = {s.lower() for s in candidate_skills}

    matched      = [s for s in required_skills if s.lower() in candidate_set]
    missing      = [s for s in required_skills if s.lower() not in candidate_set]
    nice_matched = [s for s in nice_skills     if s.lower() in candidate_set]

    coverage_pct = (len(matched) / len(required_skills) * 100) if required_skills else 0.0

    categories = list(SKILL_TAXONOMY.keys())
    extractor  = SkillExtractor()
    candidate_cat = extractor.categorize_skills(candidate_skills)
    profile_cat   = extractor.categorize_skills(list(required_skills | nice_skills))

    candidate_counts = [len(candidate_cat.get(c, [])) for c in categories]
    required_counts  = [len(profile_cat.get(c, []))   for c in categories]

    active = [
        i for i, (cc, rc) in enumerate(zip(candidate_counts, required_counts))
        if cc > 0 or rc > 0
    ]
    if active:
        categories       = [categories[i]       for i in active]
        candidate_counts = [candidate_counts[i] for i in active]
        required_counts  = [required_counts[i]  for i in active]

    return {
        "categories":       categories,
        "candidate_counts": candidate_counts,
        "required_counts":  required_counts,
        "matched":          sorted(matched),
        "missing":          sorted(missing),
        "nice_matched":     sorted(nice_matched),
        "coverage_pct":     round(coverage_pct, 1),
    }


def _render_uploader():
    st.markdown(
        """
        <div class="ara-upload-zone">
            <p class="ara-upload-title">Upload your resume</p>
            <p class="ara-upload-sub">PDF, DOCX, or TXT · max 5 MB · drag &amp; drop supported</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return st.file_uploader(
        "Resume file",
        type=_UPLOADER_EXTENSIONS,
        label_visibility="collapsed",
        help="Upload a PDF, DOCX, or TXT resume to analyse skill gaps.",
    )


def _render_radar(gap: dict) -> None:
    if not gap["categories"]:
        st.info("Not enough skill data to render the radar chart for this profile.")
        return
    with st.container(border=True):
        st.plotly_chart(
            skill_gap_radar(gap["categories"], gap["candidate_counts"], gap["required_counts"]),
            use_container_width=True,
        )


def _render_missing_skills(gap: dict) -> None:
    section_heading(
        "Missing Required Skills",
        f"{len(gap['missing'])} required skills not detected in your resume.",
    )
    if not gap["missing"]:
        st.success("You have all required skills for this role.")
        return
    skill_chips(gap["missing"], variant="red")


def _render_matched_skills(gap: dict) -> None:
    section_heading(
        "Skills You Already Have",
        f"{len(gap['matched'])} of {len(gap['matched']) + len(gap['missing'])} required skills matched.",
    )
    if gap["matched"]:
        skill_chips(gap["matched"], variant="green")
    else:
        st.info("No required skills matched yet.")

    if gap["nice_matched"]:
        st.markdown("")
        section_heading("Bonus Skills", "Nice-to-have skills you already possess.")
        skill_chips(gap["nice_matched"], variant="blue")


def _render_section_progress(gap: dict) -> None:
    section_heading("Coverage by Category", "How well your skills cover each category required for this role.")
    for cat, have, need in zip(gap["categories"], gap["candidate_counts"], gap["required_counts"]):
        if need == 0:
            continue
        pct   = min(have / need * 100, 100.0)
        color = _SUC if pct >= 70 else (_WRN if pct >= 40 else _ERR)
        progress_bar(f"{cat}  ({have}/{need})", pct, color)


def main() -> None:
    inject_global_styles()
    render_sidebar()
    page_header(
        "Gap Analysis",
        "Skill Gap Analysis",
        "Compare your current skill set against a target job role and get a prioritised list of skills to develop.",
    )

    uploaded = _render_uploader()

    if uploaded is None:
        st.markdown("<br>", unsafe_allow_html=True)
        empty_state(
            "",
            "No resume uploaded yet",
            "Upload a PDF, DOCX, or TXT file above, then select a target role to see your skill gap.",
        )
        site_footer()
        return

    if uploaded.size > MAX_FILE_SIZE:
        st.error(f"File exceeds the 5 MB limit ({_fmt_size(uploaded.size)} uploaded).")
        site_footer()
        return

    skills = _extract_skills(uploaded)
    if skills is None:
        site_footer()
        return

    if not skills:
        st.warning(
            "No recognisable skills were detected. "
            "Ensure the document contains plain text (not a scanned image)."
        )
        site_footer()
        return

    st.markdown("<br>", unsafe_allow_html=True)
    profile_name = st.selectbox(
        "Select a target job role",
        options=list(JOB_PROFILES.keys()),
        help="Choose the role you are targeting to see your skill gap.",
    )

    gap = _build_gap_data(skills, profile_name)

    summary_bar([
        ("File",              uploaded.name),
        ("Skills Detected",   str(len(skills))),
        ("Target Role",       profile_name),
        ("Required Coverage", f"{gap['coverage_pct']:.0f}%"),
        ("Missing Skills",    str(len(gap["missing"]))),
    ])

    st.markdown("<br>", unsafe_allow_html=True)
    _render_radar(gap)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2, gap="large")
    with col_left:
        _render_missing_skills(gap)
    with col_right:
        _render_matched_skills(gap)

    st.markdown("<br>", unsafe_allow_html=True)
    _render_section_progress(gap)

    site_footer()


main()
