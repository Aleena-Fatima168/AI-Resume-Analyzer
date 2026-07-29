from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go

from config import THEME_COLORS

_P   = THEME_COLORS["primary"]
_SEC = THEME_COLORS["secondary"]
_ACC = THEME_COLORS["accent"]
_MUT = THEME_COLORS["text_muted"]
_TXT = THEME_COLORS["text"]
_SUC = THEME_COLORS["success"]
_WRN = THEME_COLORS["warning"]
_ERR = THEME_COLORS["error"]

_BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=24, r=24, t=48, b=24),
    font=dict(family="Inter, sans-serif", color=_TXT),
    title_font=dict(size=14, color=_P),
)


def score_gauge(score: float, title: str = "Resume Score") -> go.Figure:
    color = _SUC if score >= 70 else (_WRN if score >= 50 else _ERR)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": title, "font": {"size": 14, "color": _P}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": _MUT},
            "bar":  {"color": color},
            "bgcolor": "#eef1f4",
            "steps": [
                {"range": [0,  50], "color": "#fde8e4"},
                {"range": [50, 70], "color": "#fef9e7"},
                {"range": [70, 100],"color": "#e4f5f3"},
            ],
            "threshold": {
                "line": {"color": _P, "width": 2},
                "thickness": 0.75,
                "value": score,
            },
        },
        number={"suffix": "%", "font": {"size": 28, "color": _P}},
    ))
    fig.update_layout(**_BASE_LAYOUT, height=260)
    return fig


def section_scores_bar(section_scores: dict[str, float]) -> go.Figure:
    labels = [k.capitalize() for k in section_scores]
    values = list(section_scores.values())
    colors = [_SUC if v >= 70 else (_WRN if v >= 50 else _ERR) for v in values]

    fig = go.Figure(go.Bar(
        x=values, y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{v:.0f}%" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        **_BASE_LAYOUT,
        title="Section Scores",
        xaxis=dict(range=[0, 115], showgrid=False, visible=False),
        yaxis=dict(showgrid=False),
        height=280,
    )
    return fig


def skills_by_category(categorized: dict[str, list[str]]) -> go.Figure:
    cats   = list(categorized.keys())
    counts = [len(v) for v in categorized.values()]
    fig = px.bar(
        x=cats, y=counts,
        title="Skills by Category",
        color_discrete_sequence=[_SEC],
        labels={"x": "Category", "y": "Count"},
    )
    fig.update_layout(**_BASE_LAYOUT)
    fig.update_xaxes(showgrid=False, tickangle=-20)
    fig.update_yaxes(gridcolor="#eef1f4")
    return fig


def score_trend(trend_data: list[dict]) -> go.Figure:
    if not trend_data:
        fig = go.Figure()
        fig.update_layout(**_BASE_LAYOUT, title="Score Trend")
        return fig

    labels = [f"Upload {i+1}" for i in range(len(trend_data))]
    totals = [r["total_score"] for r in trend_data]
    ats    = [r["ats_score"]   for r in trend_data]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=totals, name="Total Score",
        mode="lines+markers",
        line=dict(color=_ACC, width=2),
        marker=dict(size=7),
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=ats, name="ATS Score",
        mode="lines+markers",
        line=dict(color=_SEC, width=2, dash="dot"),
        marker=dict(size=7),
    ))
    fig.update_layout(
        **_BASE_LAYOUT,
        title="Score Trend",
        yaxis=dict(range=[0, 100], gridcolor="#eef1f4"),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", y=-0.2),
    )
    return fig


def skill_gap_radar(
    categories: list[str],
    candidate_counts: list[int],
    required_counts: list[int],
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=candidate_counts + [candidate_counts[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name="Your Skills",
        line_color=_SEC,
        fillcolor="rgba(61,126,166,0.2)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=required_counts + [required_counts[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name="Required",
        line_color=_ACC,
        fillcolor="rgba(244,162,97,0.15)",
    ))
    fig.update_layout(
        **_BASE_LAYOUT,
        title="Skill Coverage vs. Job Requirements",
        polar=dict(radialaxis=dict(visible=True, range=[0, max(required_counts or [1]) + 1])),
        legend=dict(orientation="h", y=-0.15),
        height=380,
    )
    return fig


def top_skills_bar(top_skills: list[dict]) -> go.Figure:
    if not top_skills:
        fig = go.Figure()
        fig.update_layout(**_BASE_LAYOUT, title="Top Skills Across Resumes")
        return fig

    skills = [r["skill"]  for r in top_skills]
    counts = [r["count"]  for r in top_skills]
    fig = go.Figure(go.Bar(
        x=counts, y=skills,
        orientation="h",
        marker_color=_SEC,
        text=counts,
        textposition="outside",
    ))
    fig.update_layout(
        **_BASE_LAYOUT,
        title="Top Skills Across Resumes",
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(autorange="reversed"),
        height=360,
    )
    return fig
