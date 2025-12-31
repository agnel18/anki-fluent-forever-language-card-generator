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
            --gradient-primary: {'linear-gradient(135deg, #238636 0%, #2ea043 100%)' if is_dark else 'linear-gradient(135deg, #0969da 0%, #218bff 100%)'};
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
                    background-color: {'#161b22' if is_dark else '#f6f8fa'} !important;
                    color: {'#e6edf3' if is_dark else '#0c0c0c'} !important;
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

                /* Tab styling for better visibility */
                .stTabs [data-baseweb="tab-list"] {{
                    background-color: var(--secondary-bg) !important;
                    border-bottom: 1px solid var(--card-border) !important;
                }}

                .stTabs [data-baseweb="tab"] {{
                    background-color: transparent !important;
                    color: var(--text-color) !important;
                    border: none !important;
                    padding: 8px 16px !important;
                    margin: 0 2px !important;
                    border-radius: 4px 4px 0 0 !important;
                }}

                .stTabs [data-baseweb="tab"]:hover {{
                    background-color: var(--hover-bg) !important;
                    color: var(--text-color) !important;
                }}

                .stTabs [data-baseweb="tab"][aria-selected="true"] {{
                    background-color: var(--bg-color) !important;
                    color: var(--primary-color) !important;
                    border-bottom: 2px solid var(--primary-color) !important;
                    font-weight: 600 !important;
                }}

                .stTabs [data-baseweb="tab"] button {{
                    color: var(--text-color) !important;
                    background: transparent !important;
                    border: none !important;
                    font-weight: inherit !important;
                }}

                .stTabs [data-baseweb="tab"][aria-selected="true"] button {{
                    color: var(--primary-color) !important;
                    font-weight: 600 !important;
                }}

                /* Number input styling for better visibility */
                .stNumberInput input {{
                    color: var(--text-color) !important;
                    background-color: var(--secondary-bg) !important;
                    border: 1px solid var(--card-border) !important;
                    border-radius: 4px !important;
                }}

                .stNumberInput input:focus {{
                    border-color: var(--primary-color) !important;
                    box-shadow: 0 0 0 1px var(--primary-color) !important;
                }}

                /* Checkbox styling for better visibility */
                .stCheckbox {{
                    color: var(--text-color) !important;
                }}

                .stCheckbox input[type="checkbox"] {{
                    accent-color: var(--primary-color) !important;
                    border: 1px solid var(--card-border) !important;
                }}

                /* Log/console output styling for better readability */
                .stCodeBlock, .stCodeBlock * {{
                    background-color: var(--secondary-bg) !important;
                    color: var(--text-color) !important;
                    border: 1px solid var(--card-border) !important;
                }}

                /* Button prominence improvements - Professional solid colors */
                .stButton > button {{
                    font-weight: 600 !important;
                    border-radius: 6px !important;
                    transition: all 0.2s ease !important;
                    border: 1px solid transparent !important;
                }}

                .stButton > button:hover {{
                    transform: translateY(-1px) !important;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
                }}

                button[kind="primary"] {{
                    background-color: {'#238636' if is_dark else '#0969da'} !important;
                    color: white !important;
                    border-color: {'#2ea043' if is_dark else '#218bff'} !important;
                    font-weight: 700 !important;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
                }}

                button[kind="primary"]:hover {{
                    background-color: {'#2ea043' if is_dark else '#218bff'} !important;
                    border-color: {'#3fb950' if is_dark else '#79c0ff'} !important;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
                    transform: translateY(-1px) !important;
                }}

                /* Enhanced primary action button styling */
                .primary-action-button button[kind="primary"] {{
                    font-size: 1.2rem !important;
                    padding: 1rem 2rem !important;
                    height: auto !important;
                    min-height: 3.5rem !important;
                    font-weight: 700 !important;
                    letter-spacing: 0.5px !important;
                    text-transform: none !important;
                    border-radius: 8px !important;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                    background: {'linear-gradient(135deg, #238636 0%, #2ea043 100%)' if is_dark else 'linear-gradient(135deg, #0969da 0%, #218bff 100%)'} !important;
                }}

                .primary-action-button button[kind="primary"]:hover {{
                    transform: translateY(-2px) !important;
                    box-shadow: 0 8px 20px rgba(0,0,0,0.25) !important;
                    background: {'linear-gradient(135deg, #2ea043 0%, #3fb950 100%)' if is_dark else 'linear-gradient(135deg, #218bff 0%, #79c0ff 100%)'} !important;
                }}

                .primary-action-button button[kind="primary"]:active {{
                    transform: translateY(0px) !important;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
                }}

                /* Authentication button enhancements */
                .auth-button-primary button {{
                    font-size: 1.1rem !important;
                    padding: 0.8rem 1.5rem !important;
                    height: auto !important;
                    min-height: 3rem !important;
                    font-weight: 600 !important;
                    border-radius: 6px !important;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
                    transition: all 0.2s ease !important;
                }}

                .auth-button-primary button:hover {{
                    transform: translateY(-1px) !important;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
                }}

                .auth-button-secondary button {{
                    font-size: 1rem !important;
                    padding: 0.7rem 1.2rem !important;
                    height: auto !important;
                    min-height: 2.8rem !important;
                    font-weight: 500 !important;
                    border-radius: 6px !important;
                    border: 2px solid var(--primary-color) !important;
                    background-color: transparent !important;
                    color: var(--primary-color) !important;
                    transition: all 0.2s ease !important;
                }}

                .auth-button-secondary button:hover {{
                    background-color: var(--primary-color) !important;
                    color: white !important;
                    transform: translateY(-1px) !important;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
                }}
            </style>
            """, unsafe_allow_html=True)