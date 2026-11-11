"""Custom CSS design system and SaaS styling for the Social Network Analyzer."""

import streamlit as st


def inject_custom_css() -> None:
    """Inject global custom CSS for the dark-slate SaaS dashboard theme."""
    st.markdown(
        """
        <style>
        /* ── Typography & Web Fonts ── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"], [class*="st-"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }
        code, pre, .stCode, [data-testid="stCodeBlock"] {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* ── Minimal Chrome ── */
        #MainMenu, header[data-testid="stHeader"], footer {
            visibility: hidden;
            height: 0;
        }
        div.block-container {
            padding-top: 1.5rem;
            max-width: 96%;
        }

        /* ── Dark-Slate Sidebar ── */
        section[data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            font-size: 0.9rem;
            color: #94A3B8;
        }

        /* ── Pill-Style Navigation Tabs ── */
        div[data-baseweb="tab-list"] {
            gap: 0.5rem !important;
            border-bottom: none !important;
            background: transparent !important;
            padding-bottom: 0.75rem !important;
        }
        button[data-baseweb="tab"] {
            background: rgba(17, 24, 39, 0.75) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 9999px !important;
            color: #94A3B8 !important;
            padding: 0.45rem 1.25rem !important;
            margin-right: 0.35rem !important;
            font-weight: 500 !important;
            font-size: 0.88rem !important;
            transition: all 0.2s ease !important;
        }
        button[data-baseweb="tab"]:hover {
            background: rgba(30, 41, 59, 0.85) !important;
            color: #F8FAFC !important;
            border-color: rgba(99, 102, 241, 0.4) !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
            border-color: #6366F1 !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
        }
        div[data-baseweb="tab-highlight"],
        div[data-baseweb="tab-border"] {
            display: none !important;
        }

        /* ── Glassmorphic KPI Cards ── */
        .kpi-card {
            background: rgba(17, 24, 39, 0.65);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 1.15rem 1.2rem;
            text-align: left;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -2px rgba(0, 0, 0, 0.2);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .kpi-card:hover {
            border-color: rgba(99, 102, 241, 0.6);
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.25), 0 6px 14px rgba(0, 0, 0, 0.35);
            transform: translateY(-2px);
        }
        .kpi-label {
            font-size: 0.72rem;
            font-weight: 600;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.35rem;
        }
        .kpi-value {
            font-size: 1.65rem;
            font-weight: 700;
            color: #F8FAFC;
            letter-spacing: -0.02em;
            line-height: 1.2;
        }
        .kpi-subtitle {
            font-size: 0.78rem;
            color: #64748B;
            margin-top: 0.35rem;
        }

        /* ── IFrame Embeds (e.g. PyVis) ── */
        iframe {
            border-radius: 14px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            overflow: hidden !important;
        }
        div[data-testid="stCustomComponentV1"] {
            border-radius: 14px !important;
            overflow: hidden !important;
        }

        /* ── DataFrames & Tables ── */
        .stDataFrame, [data-testid="stDataFrame"] {
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            overflow: hidden;
        }

        /* ── Primary & Download Buttons ── */
        .stButton > button[kind="primary"],
        .stButton > button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #6366F1, #4F46E5) !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button[kind="primary"]:hover,
        .stButton > button[data-testid="baseButton-primary"]:hover {
            box-shadow: 0 6px 18px rgba(99, 102, 241, 0.45) !important;
            transform: translateY(-1px) !important;
            opacity: 0.95 !important;
        }
        .stDownloadButton > button {
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 8px !important;
            background: #111827 !important;
            color: #F8FAFC !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        .stDownloadButton > button:hover {
            background: #1F2937 !important;
            border-color: #6366F1 !important;
            color: #FFFFFF !important;
        }

        /* ── Expanders ── */
        details[data-testid="stExpander"] {
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 10px !important;
            background: #111827 !important;
        }

        /* ── Alerts ── */
        .stAlert {
            border-radius: 10px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, subtitle: str = "") -> None:
    """Render a styled glassmorphic KPI metric card."""
    sub_html = f'<div class="kpi-subtitle">{subtitle}</div>' if subtitle else ""
    html = f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

