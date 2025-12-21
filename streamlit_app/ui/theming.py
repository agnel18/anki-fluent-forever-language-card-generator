import streamlit as st

def apply_theme_css():
    """Apply theme-aware CSS with CSS variables."""
    # Theme-aware CSS with CSS variables (applied after theme selection)
    is_dark = st.session_state.get("theme", "dark") == "dark"
    st.markdown(f"""
    <style>
        /* Force summary cards and alert containers to use the same font for balance */
        .stAlert, .stAlert * {{
            font-family: var(--font-family) !important;
            font-size: 0.92rem !important;
            font-weight: 500 !important;
            letter-spacing: normal !important;
        }}
        /* Make summary cards more visually balanced */
        .stAlertContainer {{
            border-radius: 12px !important;
            box-shadow: none !important;
            margin-bottom: 0.5rem !important;
        }}
        /* Remove extra padding/margin from summary cards */
        .stAlertContentInfo, .stAlertContentInfo * {{
            padding: 0.15rem 0.5rem !important;
            margin: 0 !important;
        }}

        :root {{
            --bg-color: {'#0e1117' if is_dark else '#ffffff'};
            --bg-color-rgb: {'14, 17, 23' if is_dark else '255, 255, 255'};
            --secondary-bg: {'#161b22' if is_dark else '#f6f8fa'};
            --text-color: {'#e6edf3' if is_dark else '#0c0c0c'};
            --subtle-text: {'#8b949e' if is_dark else '#24292f'};
            --primary-color: {'#58a6ff' if is_dark else '#0969da'};
            --secondary-color: {'#79c0ff' if is_dark else '#218bff'};
            --tertiary-color: {'#a5d6ff' if is_dark else '#79c0ff'};
            --accent-color: {'#ff6b6b' if is_dark else '#d73a49'};
            --accent-secondary: {'#4ecdc4' if is_dark else '#218bff'};
            --button-primary-bg: {'#238636' if is_dark else '#1a7f37'};
            --button-primary-border: {'#3fb950' if is_dark else '#1f883d'};
            --button-primary-hover-bg: {'#2ea043' if is_dark else '#218838'};
            --button-secondary-bg: {'#30363d' if is_dark else '#f6f8fa'};
            --button-secondary-border: {'#8b949e' if is_dark else '#d0d7de'};
            --button-secondary-hover-bg: {'#484f58' if is_dark else '#f3f4f6'};
            --button-text: {'white' if is_dark else 'black'};
            --button-secondary-text: {'#e6edf3' if is_dark else '#24292f'};
            --hover-bg: {'#30363d' if is_dark else '#f3f4f6'};
            --info-bg: {'#0550ae' if is_dark else '#ddf4ff'};
            --info-border: {'#79c0ff' if is_dark else '#218bff'};
            --success-bg: {'#1f6feb' if is_dark else '#ddf4ff'};
            --success-border: {'#58a6ff' if is_dark else '#0969da'};
            --warning-bg: {'#8b4513' if is_dark else '#fff3cd'};
            --warning-border: {'#d9a040' if is_dark else '#bf8700'};
            --error-bg: {'#da3633' if is_dark else '#ffebe9'};
            --error-border: {'#f85149' if is_dark else '#cf222e'};
            --card-bg: {'#161b22' if is_dark else '#f6f8fa'};
            --card-border: {'#30363d' if is_dark else '#d0d7de'};
            --gradient-primary: {'linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%)' if is_dark else 'linear-gradient(135deg, #0969da 0%, #218bff 100%)'};
            --box-shadow: {'0 8px 25px rgba(0,0,0,0.2)' if is_dark else '0 8px 25px rgba(0,0,0,0.1)'};
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --base-font-size: 16px;
            --link-color: var(--primary-color);
            --usage-green: #238636;
            --usage-yellow: #eab308;
                    --usage-red: #ef4444;
                }}

                /* Apply theme variables to Streamlit components */
                .stApp {{
                    background-color: var(--bg-color) !important;
                    color: var(--text-color) !important;
                }}

                .main .block-container {{
                    background-color: var(--bg-color) !important;
                    color: var(--text-color) !important;
                }}

                .stSidebar {{
                    background-color: var(--secondary-bg) !important;
                }}

                .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {{
                    color: var(--text-color) !important;
                }}

                .stMarkdown, h3 {{
                    font-size: 1.2rem !important;
                }}

                .stButton > button {{
                    background-color: var(--button-secondary-bg) !important;
                    color: var(--button-secondary-text) !important;
                    border-color: var(--button-secondary-border) !important;
                }}

                .stButton > button:hover {{
                    background-color: var(--button-secondary-hover-bg) !important;
                }}

                .stSelectbox > div > div {{
                    background-color: var(--secondary-bg) !important;
                    color: var(--text-color) !important;
                    border-color: var(--card-border) !important;
                }}

                /* Additional theme rules for light mode */
                .stMetric, .stMetric * {{
                    color: var(--text-color) !important;
                }}

                .stSidebar .stMetric, .stSidebar .stMetric * {{
                    color: var(--text-color) !important;
                }}

                .stTextInput input {{
                    color: var(--text-color) !important;
                    background-color: var(--secondary-bg) !important;
                }}

                button[kind="primary"] {{
                    background-color: var(--button-primary-bg) !important;
                    color: var(--button-text) !important;
                    border-color: var(--button-primary-border) !important;
                }}

                button[kind="secondary"] {{
                    background-color: var(--button-secondary-bg) !important;
                    color: var(--button-secondary-text) !important;
                    border-color: var(--button-secondary-border) !important;
                }}

                .stSelectbox select, .stSelectbox input, .stSelectbox div {{
                    color: var(--text-color) !important;
                    background-color: var(--secondary-bg) !important;
                    border: none !important;
                    outline: none !important;
                }}

                li[role="option"], li[role="option"] * {{
                    color: var(--text-color) !important;
                    background-color: var(--secondary-bg) !important;
                }}

                /* File uploader theming */
                .stFileUploader {{
                    background-color: var(--secondary-bg) !important;
                    color: var(--text-color) !important;
                }}
                .stFileUploader * {{
                    color: var(--text-color) !important;
                }}
                .stFileUploader button {{
                    background-color: var(--button-secondary-bg) !important;
                    color: var(--button-secondary-text) !important;
                    border-color: var(--button-secondary-border) !important;
                }}
                /* File uploader dropzone */
                [data-testid="stFileUploaderDropzone"] {{
                    background-color: var(--secondary-bg) !important;
                    color: var(--text-color) !important;
                }}
                [data-testid="stFileUploaderDropzone"] * {{
                    color: var(--text-color) !important;
                }}

                /* Tooltip icons */
                .stTooltipIcon svg {{
                    color: var(--text-color) !important;
                    stroke: var(--text-color) !important;
                }}

                /* Tooltip popups */
                .stTooltipContent {{
                    background-color: var(--secondary-bg) !important;
                    color: var(--text-color) !important;
                    border-color: var(--card-border) !important;
                }}

                /* Widget labels */
                [data-testid="stWidgetLabel"] {{
                    background: transparent !important;
                    background-color: transparent !important;
                    color: var(--text-color) !important;
                }}
                [data-testid="stWidgetLabel"] .stMarkdownContainer,
                [data-testid="stWidgetLabel"] .stMarkdownContainer p,
                [data-testid="stWidgetLabel"] p {{
                    color: var(--text-color) !important;
                }}

                /* Aggressively remove selectbox and label borders/backgrounds */
                .stSelectbox, .stSelectbox *, [data-baseweb="select"], [data-baseweb="select"] *, [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] * {{
                    border: none !important;
                    outline: none !important;
                    box-shadow: none !important;
                    background: transparent !important;
                    background-color: transparent !important;
                }}
                /* Keep text color and background for content */
                .stSelectbox, .stSelectbox * {{
                    color: var(--text-color) !important;
                }}
                [data-testid="stWidgetLabel"] {{
                    color: var(--text-color) !important;
                }}
                /* ...existing CSS rules... */
            </style>
            """, unsafe_allow_html=True)