"""Job Recommendations page — match resume skills to job profiles."""

from __future__ import annotations

import streamlit as st

from config import MAX_FILE_SIZE, PROJECT_NAME, THEME_COLORS
from utils.recommendation import JobMatch, JobRecommender
from utils.resume_parser import ResumeParser
from utils.skill_extractor import SkillExtractor
from utils.styles import (
    inject_global_styles,
    page_header,
    render_sidebar,
    section_heading,
    site_footer,
    summary_bar,
)

# ---------------------------------------------------------------------------
# Page config — must be the very first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title=f"Job Recommendations | {PROJECT_NAME}",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_UPLOADER_EXTENSIONS = ["pdf", "docx", "txt"]
_P   = THEME_COLORS["primary"]
_SEC = THEME_COLORS["secondary"]
_ACC = THEME_COLORS["accent"]
_MUT = THEME_COLORS["text_muted"]
_SUR = THEME_COLORS["surface"]
_TXT = THEME_COLORS["text"]
_SUC = THEME_COLORS["success"]
_WRN = THEME_COLORS["warning"]
_ERR = THEME_COLORS["error"]


# ---------------------------------------------------------------------------
# Page-specific CSS (job card styles not in the global design system)
# ---------------------------------------------------------------------------

def _inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        /* ── Job card ── */
        .job-card {{
            background: {_SUR}; border: 1px solid #e4e8ed;
            border-radius: 16px; padding: 1.5rem 1.4rem;
            height: 100%; position: relative; overflow: hidden;
            box-shadow: 0 2px 12px rgba(0,0,0,0.04);
            transition: box-shadow 0.2s, transform 0.2s, border-color 0.2s;
        }}
        .job-card:hover {{
            box-shadow: 0 10px 32px rgba(30,58,95,0.12);
            transform: translateY(-2px); border-color: #b8c8d8;
        }}
        .job-card.top-match {{
            border-color: {_SEC};
            box-shadow: 0 4px 20px rgba(61,126,166,0.18);
        }}
        .job-card.top-match::before {{
            content: '★ Top Match';
            position: absolute; top: 0; right: 0;
            background: {_SEC}; color: #fff;
            font-size: 0.68rem; font-weight: 700;
            padding: 0.25rem 0.75rem;
            border-radius: 0 16px 0 10px;
            letter-spacing: 0.04em;
        }}
        .card-header {{
            display: flex; align-items: flex-start;
            gap: 0.75rem; margin-bottom: 0.9rem;
        }}
        .card-icon {{ font-size: 2rem; line-height: 1; flex-shrink: 0; }}
        .card-title {{
            font-size: 1.05rem; font-weight: 700; color: {_P};
            margin: 0 0 0.2rem 0; letter-spacing: -0.01em;
        }}
        .card-desc {{ font-size: 0.8rem; color: {_MUT}; margin: 0; line-height: 1.5; }}
        .conf-row {{
            display: flex; align-items: center;
            justify-content: space-between; margin-bottom: 0.3rem;
        }}
        .conf-label {{
            font-size: 0.75rem; font-weight: 600; color: {_MUT};
            text-transform: uppercase; letter-spacing: 0.05em;
        }}
        .conf-pct {{ font-size: 1.1rem; font-weight: 800; color: {_P}; }}
        .conf-bar-bg {{
            background: #eef1f4; border-radius: 99px;
            height: 8px; width: 100%; margin-bottom: 0.35rem; overflow: hidden;
        }}
        .conf-bar-fill {{ height: 100%; border-radius: 99px; transition: width 0.4s ease; }}
        .conf-badge {{
            display: inline-block; border-radius: 20px;
            font-size: 0.7rem; font-weight: 700;
            padding: 0.18rem 0.6rem; margin-bottom: 0.9rem;
        }}
        .meta-row {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.9rem; }}
        .meta-chip {{
            display: inline-flex; align-items: center; gap: 0.25rem;
            background: #f0f4f8; border-radius: 6px;
            font-size: 0.72rem; font-weight: 500; color: {_TXT};
            padding: 0.2rem 0.55rem;
        }}
        .skill-section-label {{
            font-size: 0.72rem; font-weight: 600; color: {_MUT};
            text-transform: uppercase; letter-spacing: 0.05em;
            margin: 0.6rem 0 0.35rem 0;
        }}
        .skill-chips {{ display: flex; flex-wrap: wrap; gap: 0.3rem; }}
        .chip-matched {{
            background: rgba(42,157,143,0.1); color: #1e7a6e;
            border: 1px solid rgba(42,157,143,0.3);
            border-radius: 6px; font-size: 0.7rem; font-weight: 500;
            padding: 0.15rem 0.5rem;
        }}
        .chip-missing {{
            background: rgba(231,111,81,0.08); color: #c0442a;
            border: 1px solid rgba(231,111,81,0.25);
            border-radius: 6px; font-size: 0.7rem; font-weight: 500;
            padding: 0.15rem 0.5rem;
        }}
        .chip-nice {{
            background: rgba(61,126,166,0.08); color: #2a5f8a;
            border: 1px solid rgba(61,126,166,0.22);
            border-radius: 6px; font-size: 0.7rem; font-weight: 500;
            padding: 0.15rem 0.5rem;
        }}
        .detected-strip {{
            background: {_SUR}; border: 1px solid #e4e8ed;
            border-radius: 12px; padding: 1rem 1.25rem;
            margin-bottom: 1.75rem;
        }}
        .detected-strip-title {{
            font-size: 0.78rem; font-weight: 600; color: {_MUT};
            text-transform: uppercase; letter-spacing: 0.05em;
            margin: 0 0 0.6rem 0;
        }}
        @media (prefers-color-scheme: dark) {{
            .job-card {{ background: #1a2535; border-color: #263347; }}
            .job-card:hover {{ border-color: #3a5070; }}
            .card-title {{ color: #a8c4de; }}
            .card-desc  {{ color: #8a9db5; }}
            .meta-chip  {{ background: #1e2e42; color: #c0d4e8; }}
            .detected-strip {{ background: #1a2535; border-color: #263347; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1_048_576:
        return f"{n/1024:.1f} KB"
    return f"{n/1_048_576:.2f} MB"


def _growth_color(growth: str) -> str:
    return {"High": _SUC, "Medium": _WRN, "Stable": _MUT}.get(growth, _MUT)


# ---------------------------------------------------------------------------
# UI components
# ---------------------------------------------------------------------------

def _render_uploader():
    st.markdown(
        f"""
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
        help="Upload a PDF, DOCX, or TXT resume to generate job recommendations.",
    )


def _render_detected_skills(skills: list[str]) -> None:
    if not skills:
        return
    chips = "".join(f'<span class="chip-nice">{s}</span>' for s in skills[:40])
    overflow = (
        f'<span style="font-size:0.72rem;color:{_MUT}"> +{len(skills)-40} more</span>'
        if len(skills) > 40 else ""
    )
    st.markdown(
        f"""
        <div class="detected-strip">
            <p class="detected-strip-title">{len(skills)} skills detected from your resume</p>
            <div class="skill-chips">{chips}{overflow}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_job_card(match: JobMatch, is_top: bool) -> None:
    top_cls   = "top-match" if is_top else ""
    bar_color = match.confidence_color
    badge_bg  = bar_color

    matched_chips = "".join(f'<span class="chip-matched">{s}</span>' for s in match.matched)
    missing_chips = "".join(f'<span class="chip-missing">{s}</span>' for s in match.missing[:6])
    nice_chips    = "".join(f'<span class="chip-nice">{s}</span>'    for s in match.nice_matched[:5])

    matched_block = (
        f'<p class="skill-section-label">Matched Skills</p>'
        f'<div class="skill-chips">{matched_chips}</div>'
    ) if match.matched else ""

    missing_block = (
        f'<p class="skill-section-label">Skills to Add</p>'
        f'<div class="skill-chips">{missing_chips}</div>'
    ) if match.missing else ""

    nice_block = (
        f'<p class="skill-section-label">Bonus Skills You Have</p>'
        f'<div class="skill-chips">{nice_chips}</div>'
    ) if match.nice_matched else ""

    growth_color = _growth_color(match.growth)

    st.markdown(
        f"""
        <div class="job-card {top_cls}">
            <div class="card-header">
                <span class="card-icon">{match.icon}</span>
                <div>
                    <p class="card-title">{match.title}</p>
                    <p class="card-desc">{match.description}</p>
                </div>
            </div>
            <div class="conf-row">
                <span class="conf-label">Confidence</span>
                <span class="conf-pct">{match.confidence:.1f}%</span>
            </div>
            <div class="conf-bar-bg">
                <div class="conf-bar-fill"
                     style="width:{match.confidence}%; background:{bar_color};"></div>
            </div>
            <span class="conf-badge"
                  style="background:{badge_bg}20; color:{badge_bg};
                         border:1px solid {badge_bg}40;">
                {match.confidence_label}
            </span>
            <div class="meta-row">
                <span class="meta-chip">{match.salary_range}</span>
                <span class="meta-chip"
                      style="color:{growth_color}; background:{growth_color}15;">
                    {match.growth} Growth
                </span>
            </div>
            {matched_block}
            {missing_block}
            {nice_block}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_cards(matches: list[JobMatch]) -> None:
    section_heading("Matched Roles", "Ranked by confidence — based on skills extracted from your resume.")
    for row_start in range(0, len(matches), 2):
        row = matches[row_start: row_start + 2]
        cols = st.columns(len(row), gap="medium")
        for col, match in zip(cols, row):
            with col:
                _render_job_card(match, is_top=(row_start == 0 and match == matches[0]))
        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    inject_global_styles()
    _inject_styles()
    render_sidebar()
    page_header(
        "Career Matching",
        "Job Recommendations",
        "Upload your resume and instantly see which roles best match your skill set — "
        "ranked by confidence score computed from your detected skills.",
    )

    uploaded = _render_uploader()

    if uploaded is None:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ara-empty">
                <p class="ara-empty-title">No resume uploaded yet</p>
                <p class="ara-empty-sub">
                    Upload a PDF, DOCX, or TXT resume above.<br>
                    Skills will be extracted automatically and matched against 8 job profiles.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        site_footer()
        return

    if uploaded.size > MAX_FILE_SIZE:
        st.error(f"File exceeds the 5 MB limit ({_fmt_size(uploaded.size)} uploaded).")
        site_footer()
        return

    cache_key = f"job_rec_{uploaded.name}_{uploaded.size}"
    if cache_key not in st.session_state:
        with st.spinner("Parsing resume and extracting skills…"):
            try:
                parser = ResumeParser(uploaded, filename=uploaded.name)
                resume_data = parser.parse()
                extractor = SkillExtractor()
                skills = extractor.extract_skills(resume_data.raw_text)
                st.session_state[cache_key] = (resume_data, skills)
            except Exception as exc:
                st.error(f"Could not parse resume: {exc}")
                site_footer()
                return

    resume_data, skills = st.session_state[cache_key]

    if not skills:
        st.warning(
            "No recognisable skills were detected in this resume. "
            "Ensure the document contains plain text (not a scanned image)."
        )
        site_footer()
        return

    recommender = JobRecommender()
    matches = recommender.recommend(skills)

    summary_bar([
        ("File",           uploaded.name),
        ("Skills Detected", str(len(skills))),
        ("Top Match",      f"{matches[0].title}"),
        ("Top Confidence", f"{matches[0].confidence:.1f}%"),
    ])

    _render_detected_skills(skills)
    _render_cards(matches)
    site_footer()


main()
