import streamlit as st
import sys
import os
import logging
from datetime import datetime

# Add the project root to Python path to enable imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(project_root, 'config', '.env'))

from src.llm_handler import get_llm_response
from src.code_parser import extract_python_code
from src.analysis.static_analyzer.static_analyzer import run_pylint, run_bandit, run_mypy
from src.analysis.dynamic_analyzer.dynamic_analyzer_main import run_dynamic_analysis

from src.context_handler import parse_files_to_context_string, create_initial_prompt, create_feedback_prompt

MAX_ATTEMPTS = 5
MAX_FILES = 4 # we can adjust this later if more files are needed

# --- Setup File Logging  ---
LOG_DIR = "app_logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
log_file_name = f"pycode_bot_run_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.log"
LOG_FILE_PATH = os.path.join(LOG_DIR, log_file_name)
file_logger = logging.getLogger("PyCodeBotFileLogger")
file_logger.setLevel(logging.INFO)
if not file_logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE_PATH)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    file_logger.addHandler(file_handler)

# --- Session State Initialization ---
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = ""
if 'analysis_issues' not in st.session_state:
    st.session_state.analysis_issues = []
if 'error_attempt_info' not in st.session_state:
    st.session_state.error_attempt_info = {}
if 'user_query' not in st.session_state:
    st.session_state.user_query = ""
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "gpt-4o-mini"
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")
if 'google_api_key' not in st.session_state:
    st.session_state.google_api_key = os.getenv("GOOGLE_API_KEY", "")

# --- Helper Functions  ---
def add_log(message: str, level: str = "info"):
    ui_log_message = f"[{level.upper()}] {message}" if level != "info" else message
    st.session_state.log_messages.append(ui_log_message)
    log_method = getattr(file_logger, level.lower(), file_logger.info)
    log_method(message)

# --- Sidebar for Configuration  ---
with st.sidebar:
    st.header("Configuration")
    st.session_state.selected_model = st.selectbox(
        "Choose LLM Model:",
        ("gpt-4o-mini", "gpt-3.5-turbo", "gemini-1.5-flash-latest", "gemini-2.0-flash"),
        index=["gpt-4o-mini", "gpt-3.5-turbo", "gemini-1.5-flash-latest", "gemini-2.0-flash"].index(st.session_state.selected_model)
    )
    st.subheader("API Keys")
    if not st.session_state.openai_api_key:
        st.session_state.openai_api_key = st.text_input("OpenAI API Key:", type="password", value=st.session_state.openai_api_key)
    else:
        st.success("OpenAI API Key loaded.")
        if st.button("Clear OpenAI Key"):
            st.session_state.openai_api_key = ""
            st.rerun()

    if not st.session_state.google_api_key:
        st.session_state.google_api_key = st.text_input("Google API Key (for Gemini):", type="password", value=st.session_state.google_api_key)
    else:
        st.success("Google API Key loaded.")
        if st.button("Clear Google Key"):
            st.session_state.google_api_key = ""
            st.rerun()
            
    st.markdown("---")
    st.markdown("This app generates Python code and performs static analysis. Retries up to 2 times if issues are found.")
    st.markdown(f"ℹ️ Detailed logs for this session are being saved to: `{LOG_FILE_PATH}`")


# --- Main Application Area ---
st.title("🐍 PyCode Bot Assistant")
st.write("Enter your request, attach optional files for context, and the assistant will generate and analyze Python code.")

current_user_query = st.text_area(
    "Your code request:", 
    value=st.session_state.user_query, 
    height=100,
    key="user_query_input"
)

# --- NEWWWW: FILE UPLOADER ---
uploaded_files = st.file_uploader(
    f"Attach up to {MAX_FILES} files for context (CSV, XLSX, TXT, PY)",
    type=['csv', 'xlsx', 'txt', 'py'],
    accept_multiple_files=True,
    key="file_uploader"
)

if st.button("✨ Generate Code"):
    st.session_state.user_query = current_user_query
    
    # Reset state
    st.session_state.generated_code = ""
    st.session_state.analysis_issues = []
    st.session_state.error_attempt_info = {}
    st.session_state.log_messages = [] 

    add_log("--- New Code Generation Request ---")
    add_log(f"User Query: {st.session_state.user_query}")
    add_log(f"Selected Model: {st.session_state.selected_model}")

    # --- MODIFIED: VALIDATION AND CONTEXT PREPARATION ---
    if len(uploaded_files) > MAX_FILES:
        st.error(f"You can upload a maximum of {MAX_FILES} files.")
        add_log(f"Error: User tried to upload {len(uploaded_files)} files.", level="error")
    elif not st.session_state.user_query.strip():
        st.warning("Please enter a code request.")
        add_log("Warning: Empty code request.", level="warning")
    elif st.session_state.selected_model in ("gpt-4o-mini", "gpt-3.5-turbo") and not st.session_state.openai_api_key:
        st.error(f"OpenAI API Key is required for {st.session_state.selected_model}.")
        add_log(f"OpenAI API Key missing for {st.session_state.selected_model}.", level="error")
    elif st.session_state.selected_model in ("gemini-1.5-flash-latest", "gemini-2.0-flash") and not st.session_state.google_api_key:
        st.error(f"Google API Key is required for {st.session_state.selected_model}.")
        add_log(f"Google API Key missing for {st.session_state.selected_model}.", level="error")
    else:
        # --- MODIFIED: USE OFTHE NEW CONTEXT HANDLER ---
        file_context = parse_files_to_context_string(uploaded_files)
        if uploaded_files:
            file_names = [f.name for f in uploaded_files]
            add_log(f"Attached files for context: {', '.join(file_names)}")
        
        current_llm_input = create_initial_prompt(st.session_state.user_query, file_context)
        
        with st.spinner("👩‍💻 Generating and analyzing code... This may take a few moments."):
            for attempt in range(1, MAX_ATTEMPTS + 1):
                add_log(f"\n--- Attempt {attempt} of {MAX_ATTEMPTS} ---")
                st.write(f"Attempt {attempt} of {MAX_ATTEMPTS}...")
                
                add_log(f"Prompt to LLM (Attempt {attempt}):\n{current_llm_input}")

                llm_response_content = get_llm_response(
                    user_query=current_llm_input,
                    model_name=st.session_state.selected_model,
                    openai_api_key=st.session_state.openai_api_key,
                    google_api_key=st.session_state.google_api_key
                )
                add_log(f"LLM Raw Response (Attempt {attempt}):\n{llm_response_content}")

                if llm_response_content.startswith("Error:"):
                    st.session_state.analysis_issues = [llm_response_content]
                    st.session_state.generated_code = "" 
                    st.session_state.error_attempt_info = {"attempt": attempt, "max_attempts": MAX_ATTEMPTS}
                    add_log(f"LLM call failed: {llm_response_content}", level="error")
                    break 

                extracted_code = extract_python_code(llm_response_content)
                st.session_state.generated_code = extracted_code 
                
                if extracted_code:
                    add_log(f"Extracted Code (Attempt {attempt}):\n{extracted_code}")
                else:
                    add_log(f"No Python code block extracted from LLM response (Attempt {attempt}).", level="warning")

                if not extracted_code:
                    st.session_state.analysis_issues = ["LLM did not return a recognizable Python code block."]
                    st.session_state.error_attempt_info = {"attempt": attempt, "max_attempts": MAX_ATTEMPTS}
                    if attempt < MAX_ATTEMPTS:
                        # --- MODIFIED: USE THE NEW FEEDBACK PROMPT ---
                        # We don't need a special prompt here, the standard feedback prompt works.
                        # We will just pass an appropriate error message.
                        current_llm_input = create_feedback_prompt(
                            original_user_query=st.session_state.user_query,
                            file_context=file_context,
                            failed_code="N/A - No code was returned.",
                            analysis_issues=["Your response did not contain a valid Python code block. Please provide ONLY a Python code block enclosed in ```python ... ```."]
                        )
                        add_log("No code block found. Preparing retry with feedback.", level="warning")
                        st.write("No code block found, retrying...")
                        continue
                    else:
                        add_log("Failed to get code block after multiple attempts.", level="error")
                        st.write("Failed to get code block after multiple attempts.")
                        break 
                
                # --- ANALYSIS ---
                pylint_issues = run_pylint(extracted_code)
                bandit_issues = run_bandit(extracted_code)
                mypy_issues = run_mypy(extracted_code)  
                dynamic_issues = run_dynamic_analysis(extracted_code,"dynapyt", "comprehensive") 

                add_log(f"Pylint Issues (Attempt {attempt}): " + ('\n- '.join(pylint_issues) if pylint_issues else "No issues found."))
                add_log(f"Bandit Issues (Attempt {attempt}): " + ('\n- '.join(bandit_issues) if bandit_issues else "No issues found."))
                add_log(f"MyPy Issues (Attempt {attempt}): " + ('\n- '.join(mypy_issues) if mypy_issues else "No issues found."))
                add_log(f"Dynamic Analysis Issues (Attempt {attempt}): " + ('\n- '.join(dynamic_issues) if dynamic_issues else "No issues (placeholder)."))

                all_issues = pylint_issues + bandit_issues + mypy_issues + dynamic_issues
                st.session_state.analysis_issues = all_issues
                st.session_state.error_attempt_info = {"attempt": attempt, "max_attempts": MAX_ATTEMPTS}

                if not all_issues:
                    add_log("Code generated successfully with no static analysis issues found!")
                    st.write("Code generated successfully with no static analysis issues found!")
                    break 
                else:
                    add_log(f"Found {len(all_issues)} issues. Details logged.", level="warning")
                    st.write(f"Found {len(all_issues)} issues. Details below.")
                    if attempt < MAX_ATTEMPTS:
                        # --- MODIFIED: THE NEW FEEDBACK PROMPT ---
                        current_llm_input = create_feedback_prompt(
                            original_user_query=st.session_state.user_query,
                            file_context=file_context,
                            failed_code=extracted_code,
                            analysis_issues=all_issues
                        )
                        add_log("Attempting to fix issues. New prompt prepared for LLM.")
                        st.write("Attempting to fix issues...")
                    else:
                        add_log("Max retries reached. Displaying last attempt with issues.", level="warning")
                        st.write("Max retries reached. Displaying last attempt with issues.")
                        break 
        st.rerun() 

# --- Display Results ---
if st.session_state.generated_code:
    st.subheader("Generated Code")
    st.code(st.session_state.generated_code, language="python")
    if st.button("📋 Copy Code", key="manual_copy_toast_button"):
        st.toast("Copied to clipboard!", icon="✅")

if st.session_state.analysis_issues:
    attempt_info = st.session_state.error_attempt_info
    expander_title = "⚠️ Analysis Issues"
    if attempt_info:
        expander_title += f" (Last Attempt: {attempt_info.get('attempt', '?')} of {attempt_info.get('max_attempts', MAX_ATTEMPTS)})"
    
    with st.expander(expander_title, expanded=True):
        for issue in st.session_state.analysis_issues:
            st.warning(issue)
elif st.session_state.generated_code and not st.session_state.analysis_issues and st.session_state.user_query:
    st.success("✅ No static analysis issues found in the generated code!")

if st.session_state.log_messages:
    with st.expander("📜 View Process Log (In-Memory)", expanded=False):
        for log_entry in st.session_state.log_messages:
            st.text(log_entry)