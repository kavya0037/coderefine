import streamlit as st
import os
from dotenv import load_dotenv

# Try to load environment variables from .env file if it exists
load_dotenv()

from analyzer import analyze_code

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Code Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main-title {
        background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #a0aab2;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stTextArea textarea {
        font-family: 'Courier New', Courier, monospace;
        font-size: 14px;
        background-color: #1e1e1e;
        color: #d4d4d4;
    }
    .success-text {
        color: #00C851;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("Configure your AI Code Assistant here.")
    
    api_key_input = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API Key. Overrides the environment variable if provided.")
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
        
    analysis_type = st.selectbox(
        "Analysis Type",
        options=[
            "Comprehensive Review",
            "Bug Detection",
            "Optimization",
            "Best Practices & Simplicity"
        ],
        help="Select the specific type of feedback you need."
    )
    
    language = st.selectbox(
        "Programming Language",
        options=["Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "Other"],
        help="Specify the language to help the AI format its code snippets correctly."
    )
    
    st.markdown("---")
    st.markdown("### How to use")
    st.markdown("1. Paste your code into the editor.")
    st.markdown("2. Select your language and analysis goal.")
    st.markdown("3. Click **Analyze Code** and wait for the magic.")

# --- Main App Area ---
st.markdown('<h1 class="main-title">✨ AI Code Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Detect bugs, optimize performance, and rewrite cleaner code instantly.</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Your Code")
    code_input = st.text_area("Paste your source code here", height=400, placeholder="# Paste your buggy or unoptimized code here...")
    
    analyze_btn = st.button("🚀 Analyze Code", type="primary", use_container_width=True)

with col2:
    st.subheader("💡 Analysis & Rewrites")
    output_area = st.empty()
    output_area.info("Your analysis report will appear here.")

# --- Analysis Logic ---
if analyze_btn:
    if not code_input.strip():
        st.warning("Please enter some code to analyze.")
    elif not os.environ.get("GEMINI_API_KEY"):
         st.error("Missing Gemini API Key. Please provide it in the sidebar or via a .env file.")
    else:
        with st.spinner(f"Running {analysis_type} on your {language} code..."):
            try:
                result = analyze_code(code=code_input, analysis_type=analysis_type, language=language)
                st.snow() # Fun little micro-interaction on success
                with col2:
                    st.markdown("### Results")
                    st.markdown(result)
            except Exception as e:
                st.error(f"Failed to generate analysis: {e}")

