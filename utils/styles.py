from __future__ import annotations

import os as _os

import streamlit as st

from config import PROJECT_NAME, THEME_COLORS, VERSION

_P   = THEME_COLORS["primary"]
_SEC = THEME_COLORS["secondary"]
_ACC = THEME_COLORS["accent"]
_SUR = THEME_COLORS["surface"]
_TXT = THEME_COLORS["text"]
_MUT = THEME_COLORS["text_muted"]
_SUC = THEME_COLORS["success"]
_WRN = THEME_COLORS["warning"]
_ERR = THEME_COLORS["error"]

NAV_PAGES = [
    ("app.py",                      "Home",               None),
    ("pages/Dashboard.py",          "Dashboard",          None),
    ("pages/Resume_Analysis.py",    "Resume Analysis",    None),
    ("pages/Skill_Gap.py",          "Skill Gap",          None),
    ("pages/Job_Recommendation.py", "Job Recommendations",None),
    ("pages/About.py",              "About",              None),
]

_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_NAV_PAGES_ABS = [
    (_os.path.join(_ROOT, path), label, icon)
    for path, label, icon in NAV_PAGES
]


def inject_global_styles() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            -webkit-font-smoothing: antialiased;
        }}

        .block-container {{
            padding-top: 2rem !important;
            padding-bottom: 5rem !important;
            max-width: 1180px !important;
        }}

        [data-testid="stSidebarNav"] {{ display: none !important; }}
        #MainMenu  {{ visibility: hidden; }}
        footer     {{ visibility: hidden; }}
        header     {{ visibility: hidden; }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {_P} 0%, #0d1f35 100%) !important;
            border-right: none !important;
        }}

        [data-testid="stSidebar"] > div:first-child {{
            padding: 1.5rem 1.25rem 2rem 1.25rem;
        }}

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] li,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {{
            color: rgba(255,255,255,0.82) !important;
        }}

        [data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,0.10) !important;
            margin: 1rem 0 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stPageLink"] a {{
            border-radius: 8px !important;
            padding: 0.45rem 0.75rem !important;
            margin-bottom: 0.15rem !important;
            transition: background 0.18s ease !important;
            color: rgba(255,255,255,0.80) !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {{
            background: rgba(255,255,255,0.10) !important;
            color: #ffffff !important;
        }}

        .ara-sb-brand {{
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin-bottom: 0.25rem;
        }}
        .ara-sb-name {{
            font-size: 1rem; font-weight: 700;
            color: #ffffff !important;
            letter-spacing: -0.02em; line-height: 1.2;
        }}
        .ara-sb-tagline {{
            font-size: 0.75rem;
            color: rgba(255,255,255,0.50) !important;
            margin: 0.3rem 0 1.25rem 0;
            line-height: 1.45;
        }}
        .ara-sb-section {{
            font-size: 0.68rem; font-weight: 700;
            letter-spacing: 0.09em; text-transform: uppercase;
            color: rgba(255,255,255,0.38) !important;
            margin: 0.75rem 0 0.4rem 0;
        }}
        .ara-sb-formats {{
            display: flex; gap: 0.35rem; flex-wrap: wrap;
            margin-top: 0.5rem;
        }}
        .ara-sb-fmt {{
            background: rgba(255,255,255,0.08);
            color: rgba(255,255,255,0.60) !important;
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 5px; font-size: 0.68rem;
            font-weight: 600; padding: 0.18rem 0.5rem;
        }}
        .ara-sb-badge {{
            display: inline-flex; align-items: center; gap: 0.3rem;
            background: rgba(42,157,143,0.18);
            color: #7ee8de !important;
            border: 1px solid rgba(42,157,143,0.35);
            border-radius: 20px; font-size: 0.7rem; font-weight: 600;
            padding: 0.22rem 0.7rem; margin-top: 0.6rem;
        }}
        .ara-sb-version {{
            font-size: 0.68rem;
            color: rgba(255,255,255,0.28) !important;
            margin-top: 1.75rem;
        }}

        .ara-page-header {{
            background: linear-gradient(135deg, {_P} 0%, {_SEC} 100%);
            border-radius: 18px;
            padding: 2rem 2.25rem;
            margin-bottom: 2rem;
            color: #ffffff;
            box-shadow: 0 12px 40px rgba(30,58,95,0.22);
            position: relative; overflow: hidden;
        }}
        .ara-page-header::after {{
            content: '';
            position: absolute; bottom: -60px; right: -40px;
            width: 200px; height: 200px; border-radius: 50%;
            background: rgba(255,255,255,0.04); pointer-events: none;
        }}
        .ara-page-header h1 {{
            font-size: 1.85rem; font-weight: 800;
            margin: 0 0 0.45rem 0; letter-spacing: -0.03em;
            color: #ffffff;
        }}
        .ara-page-header p {{
            font-size: 0.92rem; opacity: 0.85;
            margin: 0; line-height: 1.6; max-width: 640px;
        }}
        .ara-page-eyebrow {{
            display: inline-block;
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.22);
            border-radius: 20px; font-size: 0.72rem;
            font-weight: 600; letter-spacing: 0.07em;
            text-transform: uppercase;
            padding: 0.25rem 0.8rem; margin-bottom: 0.75rem;
            color: rgba(255,255,255,0.90);
        }}

        .ara-section-title {{
            font-size: 1.15rem; font-weight: 700;
            color: {_TXT}; margin: 0 0 0.25rem 0;
            letter-spacing: -0.02em;
        }}
        .ara-section-sub {{
            font-size: 0.875rem; color: {_MUT};
            margin: 0 0 1.25rem 0; line-height: 1.55;
        }}

        .ara-card {{
            background: {_SUR};
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.5rem 1.4rem;
            height: 100%;
            box-shadow: 0 1px 8px rgba(0,0,0,0.05);
            transition: box-shadow 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
            position: relative; overflow: hidden;
        }}
        .ara-card:hover {{
            box-shadow: 0 8px 28px rgba(30,58,95,0.11);
            transform: translateY(-2px);
            border-color: #c8d6e5;
        }}
        .ara-card-accent {{
            position: absolute; top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, {_SEC}, {_ACC});
        }}

        .ara-stat {{
            background: {_SUR};
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.35rem 1.4rem;
            box-shadow: 0 1px 8px rgba(0,0,0,0.05);
            position: relative; overflow: hidden;
        }}
        .ara-stat-icon {{ font-size: 1.6rem; margin-bottom: 0.5rem; display: block; }}
        .ara-stat-label {{
            font-size: 0.72rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.07em;
            color: {_MUT}; margin: 0 0 0.2rem 0;
        }}
        .ara-stat-value {{
            font-size: 2.1rem; font-weight: 800;
            color: {_P}; line-height: 1; margin: 0 0 0.35rem 0;
            letter-spacing: -0.03em;
        }}
        .ara-stat-delta {{ font-size: 0.78rem; color: {_MUT}; margin: 0; }}
        .ara-stat-bar {{
            position: absolute; bottom: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, {_SEC}, {_ACC});
            opacity: 0.6;
        }}

        .ara-chips {{ display: flex; flex-wrap: wrap; gap: 0.35rem; }}
        .ara-chip {{
            display: inline-block;
            background: #f0f4f8;
            color: {_TXT};
            border: 1px solid #dde4ed;
            border-radius: 6px;
            font-size: 0.72rem; font-weight: 500;
            padding: 0.2rem 0.55rem;
        }}
        .ara-chip-green {{
            background: rgba(42,157,143,0.10); color: #1a7a6e;
            border: 1px solid rgba(42,157,143,0.28);
        }}
        .ara-chip-red {{
            background: rgba(231,111,81,0.08); color: #b83a22;
            border: 1px solid rgba(231,111,81,0.25);
        }}
        .ara-chip-blue {{
            background: rgba(61,126,166,0.09); color: #245f8a;
            border: 1px solid rgba(61,126,166,0.22);
        }}
        .ara-chip-orange {{
            background: rgba(244,162,97,0.12); color: #a05a10;
            border: 1px solid rgba(244,162,97,0.30);
        }}

        .ara-banner {{
            background: {_SUR};
            border: 1px solid #e2e8f0;
            border-left: 4px solid {_SEC};
            border-radius: 12px;
            padding: 1.1rem 1.4rem;
            margin-bottom: 1.5rem;
        }}
        .ara-banner-title {{
            font-size: 0.95rem; font-weight: 600;
            color: {_P}; margin: 0 0 0.2rem 0;
        }}
        .ara-banner-body {{
            font-size: 0.875rem; color: {_MUT};
            margin: 0; line-height: 1.55;
        }}

        .ara-upload-zone {{
            background: {_SUR};
            border: 2px dashed #c8d6e5;
            border-radius: 14px;
            padding: 1.75rem 1.5rem;
            text-align: center;
            margin-bottom: 1.25rem;
            transition: border-color 0.2s;
        }}
        .ara-upload-zone:hover {{ border-color: {_SEC}; }}
        .ara-upload-title {{
            font-size: 1rem; font-weight: 600;
            color: {_P}; margin: 0 0 0.3rem 0;
        }}
        .ara-upload-sub {{ font-size: 0.82rem; color: {_MUT}; margin: 0; }}

        .ara-summary {{
            background: {_SUR};
            border: 1px solid #e2e8f0;
            border-left: 4px solid {_SEC};
            border-radius: 12px;
            padding: 1rem 1.4rem;
            margin-bottom: 1.75rem;
            display: flex; align-items: center;
            gap: 1.25rem; flex-wrap: wrap;
        }}
        .ara-summary-item {{ min-width: 80px; }}
        .ara-summary-label {{
            font-size: 0.68rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.07em;
            color: {_MUT}; margin: 0 0 0.15rem 0;
        }}
        .ara-summary-value {{
            font-size: 0.95rem; font-weight: 700; color: {_P}; margin: 0;
        }}
        .ara-summary-divider {{
            width: 1px; height: 32px;
            background: #e2e8f0; flex-shrink: 0;
        }}

        .ara-progress-wrap {{ margin-bottom: 0.75rem; }}
        .ara-progress-row {{
            display: flex; justify-content: space-between;
            align-items: center; margin-bottom: 0.3rem;
        }}
        .ara-progress-label {{ font-size: 0.78rem; font-weight: 600; color: {_MUT}; }}
        .ara-progress-pct {{ font-size: 0.88rem; font-weight: 700; color: {_P}; }}
        .ara-progress-bg {{
            background: #eef1f4; border-radius: 99px;
            height: 7px; overflow: hidden;
        }}
        .ara-progress-fill {{
            height: 100%; border-radius: 99px;
            transition: width 0.4s ease;
        }}

        .ara-empty {{
            background: {_SUR};
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 3.5rem 2rem;
            text-align: center;
        }}
        .ara-empty-icon {{ font-size: 3rem; margin-bottom: 0.75rem; }}
        .ara-empty-title {{
            font-size: 1.1rem; font-weight: 700;
            color: {_P}; margin: 0 0 0.4rem 0;
        }}
        .ara-empty-sub {{
            font-size: 0.875rem; color: {_MUT};
            margin: 0; line-height: 1.6; max-width: 420px;
            margin-left: auto; margin-right: auto;
        }}

        .ara-footer {{
            margin-top: 4rem;
            padding-top: 1.5rem;
            border-top: 1px solid #e2e8f0;
            display: flex; align-items: center;
            justify-content: space-between; flex-wrap: wrap; gap: 0.75rem;
        }}
        .ara-footer-left {{
            font-size: 0.8rem; color: {_MUT}; line-height: 1.55;
        }}
        .ara-footer-left strong {{ color: {_P}; font-weight: 600; }}

        @media (prefers-color-scheme: dark) {{
            .ara-card, .ara-stat, .ara-banner,
            .ara-upload-zone, .ara-summary, .ara-empty {{
                background: #1a2535 !important;
                border-color: #263347 !important;
            }}
            .ara-card:hover {{ border-color: #3a5070 !important; }}
            .ara-section-title {{ color: #c0d4e8 !important; }}
            .ara-section-sub, .ara-stat-delta,
            .ara-banner-body, .ara-upload-sub,
            .ara-empty-sub {{ color: #8a9db5 !important; }}
            .ara-stat-value, .ara-banner-title,
            .ara-summary-value, .ara-empty-title {{ color: #a8c4de !important; }}
            .ara-chip {{ background: #1e2e42; border-color: #2e4260; color: #c0d4e8; }}
            .ara-progress-bg {{ background: #263347; }}
            .ara-footer {{ border-color: #263347; }}
            .ara-footer-left {{ color: #8a9db5; }}
            .ara-footer-left strong {{ color: #a8c4de; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div class="ara-sb-brand">
                <span class="ara-sb-name">{PROJECT_NAME}</span>
            </div>
            <p class="ara-sb-tagline">NLP-powered resume insights &amp; career tools.</p>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        st.markdown('<p class="ara-sb-section">Navigation</p>', unsafe_allow_html=True)
        for path, label, icon in _NAV_PAGES_ABS:
            try:
                st.page_link(path, label=label)
            except Exception:
                pass

        st.divider()

        st.markdown('<p class="ara-sb-section">Supported formats</p>', unsafe_allow_html=True)
        st.markdown(
            '<div class="ara-sb-formats">'
            '<span class="ara-sb-fmt">PDF</span>'
            '<span class="ara-sb-fmt">DOCX</span>'
            '<span class="ara-sb-fmt">TXT</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="margin-top:0.75rem;">'
            '<span class="ara-sb-badge">Active</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<p class="ara-sb-version">v{VERSION} · AI Resume Analyzer</p>',
            unsafe_allow_html=True,
        )


def page_header(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="ara-page-header">
            <span class="ara-page-eyebrow">{eyebrow}</span>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title: str, subtitle: str = "") -> None:
    sub = f'<p class="ara-section-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<p class="ara-section-title">{title}</p>{sub}',
        unsafe_allow_html=True,
    )


def empty_state(icon: str, title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="ara-empty">
            <div class="ara-empty-icon">{icon}</div>
            <p class="ara-empty-title">{title}</p>
            <p class="ara-empty-sub">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_card(icon: str, label: str, value: str, delta: str) -> None:
    st.markdown(
        f"""
        <div class="ara-stat">
            <div class="ara-stat-bar"></div>
            <span class="ara-stat-icon">{icon}</span>
            <p class="ara-stat-label">{label}</p>
            <p class="ara-stat-value">{value}</p>
            <p class="ara-stat-delta">{delta}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def summary_bar(items: list[tuple[str, str]]) -> None:
    parts: list[str] = []
    for i, (label, value) in enumerate(items):
        if i:
            parts.append('<div class="ara-summary-divider"></div>')
        parts.append(
            f'<div class="ara-summary-item">'
            f'<p class="ara-summary-label">{label}</p>'
            f'<p class="ara-summary-value">{value}</p>'
            f'</div>'
        )
    st.markdown(
        f'<div class="ara-summary">{"".join(parts)}</div>',
        unsafe_allow_html=True,
    )


def skill_chips(skills: list[str], variant: str = "default") -> None:
    cls = {
        "green":  "ara-chip ara-chip-green",
        "red":    "ara-chip ara-chip-red",
        "blue":   "ara-chip ara-chip-blue",
        "orange": "ara-chip ara-chip-orange",
    }.get(variant, "ara-chip")
    chips = "".join(f'<span class="{cls}">{s}</span>' for s in skills)
    st.markdown(f'<div class="ara-chips">{chips}</div>', unsafe_allow_html=True)


def progress_bar(label: str, pct: float, color: str) -> None:
    st.markdown(
        f"""
        <div class="ara-progress-wrap">
            <div class="ara-progress-row">
                <span class="ara-progress-label">{label}</span>
                <span class="ara-progress-pct">{pct:.0f}%</span>
            </div>
            <div class="ara-progress-bg">
                <div class="ara-progress-fill"
                     style="width:{pct}%; background:{color};"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def site_footer() -> None:
    st.markdown(
        f"""
        <div class="ara-footer">
            <div class="ara-footer-left">
                <strong>{PROJECT_NAME}</strong> · v{VERSION}<br>
                Built with Streamlit · Python · spaCy · scikit-learn
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
