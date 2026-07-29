from __future__ import annotations

import streamlit as st

from config import PROJECT_NAME
from utils.database import DatabaseManager
from utils.styles import (
    inject_global_styles,
    page_header,
    render_sidebar,
    section_heading,
    site_footer,
    stat_card,
)
from utils.visualization import score_trend, skills_by_category, top_skills_bar

st.set_page_config(
    page_title=f"Dashboard | {PROJECT_NAME}",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=60, show_spinner=False)
def _load_dashboard_data() -> dict:
    db = DatabaseManager()
    stats = db.get_dashboard_stats()

    all_resumes = db.resumes.get_all(limit=1)
    trend: list[dict] = []
    categorized: dict[str, list[str]] = {}

    if all_resumes:
        latest_id = all_resumes[0]["id"]
        trend = db.scores.get_score_trend(latest_id)
        categorized = db.skills.get_for_resume(latest_id)

    return {"stats": stats, "trend": trend, "categorized": categorized}


def _render_kpi_row(stats: dict) -> None:
    score_stats   = stats.get("score_stats", {})
    total_resumes = stats.get("total_resumes", 0)
    top_skills    = stats.get("top_skills", [])

    avg_score   = score_stats.get("avg_total")
    avg_ats     = score_stats.get("avg_ats")
    score_count = score_stats.get("count", 0)

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        stat_card(
            "", "Avg Resume Score",
            f"{avg_score:.0f}" if avg_score is not None else "—",
            f"Across {score_count} scoring run{'s' if score_count != 1 else ''}",
        )
    with c2:
        stat_card(
            "", "Avg ATS Score",
            f"{avg_ats:.0f}" if avg_ats is not None else "—",
            "ATS-friendliness estimate",
        )
    with c3:
        stat_card(
            "", "Resumes Uploaded",
            str(total_resumes),
            "Total stored in database",
        )
    with c4:
        stat_card(
            "", "Unique Skills Tracked",
            str(len(top_skills)),
            "Most common across all resumes",
        )


def _render_charts(data: dict) -> None:
    section_heading("Analytics", "Charts update automatically as you upload more resumes.")

    col_left, col_right = st.columns(2, gap="medium")

    with col_left:
        with st.container(border=True):
            categorized = data["categorized"]
            if categorized:
                st.plotly_chart(skills_by_category(categorized), use_container_width=True)
            else:
                st.caption("Skills by category — upload a resume to populate.")

    with col_right:
        with st.container(border=True):
            trend = data["trend"]
            if trend:
                st.plotly_chart(score_trend(trend), use_container_width=True)
            else:
                st.caption("Score trend — upload a resume to populate.")


def _render_top_skills(stats: dict) -> None:
    top = stats.get("top_skills", [])
    if not top:
        return
    section_heading("Top Skills", "Most frequently detected skills across all uploaded resumes.")
    with st.container(border=True):
        st.plotly_chart(top_skills_bar(top), use_container_width=True)


def main() -> None:
    inject_global_styles()
    render_sidebar()
    page_header(
        "Analytics",
        "Dashboard",
        "Monitor resume scores, skill coverage, and upload history at a glance.",
    )

    data  = _load_dashboard_data()
    stats = data["stats"]

    if stats["total_resumes"] == 0:
        st.info(
            "No resumes analysed yet. "
            "Head to **Resume Analysis** to upload your first resume.",
        )
    else:
        _render_kpi_row(stats)
        st.markdown("<br>", unsafe_allow_html=True)
        _render_charts(data)
        st.markdown("<br>", unsafe_allow_html=True)
        _render_top_skills(stats)

    site_footer()


main()
