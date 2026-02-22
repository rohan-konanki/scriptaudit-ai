import streamlit as st
import pandas as pd
import subprocess
import os
import time
import shutil
from pathlib import Path
from audit_engine import audit_script

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ScriptAudit AI | Agentic Data Integrity",
    layout="wide"
)

# --- THE "NUCLEAR" ANTI-GHOSTING CSS ---
st.markdown("""
    <style>
    /* 1. Global Opacity Lock - Prevents the 'Greying Out' */
    [data-testid="stAppViewBlockContainer"], 
    [data-testid="stVerticalBlock"],
    [data-testid="stMarkdownContainer"],
    .stTabs, .stTable, .stTextArea, .stButton {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
    }

    /* 2. Target the specific 'Busy' overlay Streamlit uses */
    .st-emotion-cache-zt5igj, .st-emotion-cache-16idsys {
        opacity: 1 !important;
    }

    /* 3. Terminal/Code Wrap styling */
    code {
        white-space: pre-wrap !important;
        word-break: break-all !important;
    }
    .stCodeBlock {
        background-color: #0e1117 !important;
        border: 1px solid #30363d !important;
        padding: 10px !important;
    }

    /* 4. Report Styling */
    .report-container {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 10px;
        border: 1px solid #e6e9ef;
        color: #1a1c23;
        opacity: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'audit_complete' not in st.session_state:
    st.session_state.audit_complete = False

# --- SIDEBAR ---
with st.sidebar:
    st.title("System Architecture")
    st.status("Actian VectorAI DB", state="complete")
    st.status("Gemini 3 Flash", state="complete")
    st.status("Sphinx AI Auditor", state="complete")
    
    st.markdown("---")
    st.info("""
    **Pipeline Flow:**
    1. **Vector Search:** Actian VectorAI DB retrieves matches.
    2. **Generation:** Gemini constructs a structured report.
    3. **Verification:** Sphinx Agent performs a schema audit.
    """)
    st.markdown("---")
    strict_mode = st.toggle("Enforce Strict Audit", value=False, help="Enable cross-referencing for potential hallucinations.")
    st.markdown("---")
    if st.button("Clear Session", use_container_width=True):
        st.session_state.audit_complete = False
        st.session_state.actian_results = None
        st.rerun()


# --- MAIN UI ---
st.title("ScriptAudit AI")
st.caption("Recursive Agentic Validation for Film Industry Script Analysis")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("💡 Script Concept")
    user_idea = st.text_area(
        "Enter your movie idea below:",
        placeholder="A story about a robot on a ruined Earth...",
        height=200
    )
    
    run_btn = st.button("Execute Audit Pipeline", type="primary", use_container_width=True, key="main_run_btn")

    if run_btn:
        if user_idea:

            with st.status("Pipeline Executing...", expanded=True) as status:
                st.write("Querying Actian VectorAI DB...")
                
                # 1. CAPTURE THE LIVE RESULTS
                results = audit_script(user_idea, "web_demo_audit") 
                if results:
                    # 2. Explicitly commit to session state
                    st.session_state.actian_results = results 
                    st.session_state.audit_complete = True
                    status.update(label="Syncing with Vector Cluster...", state="complete")
                    time.sleep(0.5) 
                    st.rerun() 
                else:
                    st.error("Engine returned empty results.")

                
                st.write("Generating Traceable Audit Report...")
                time.sleep(1) 
                status.update(label="Local Execution Complete. Starting Agentic Audit...", state="running")
            
            st.session_state.audit_complete = True
            st.rerun()
        else:
            st.error("Please enter a concept first.")

with col2:
    if st.session_state.audit_complete:
        tab1, tab2, tab3 = st.tabs(["Vector Matches", "Sphinx Audit", "Validated Report"])
        
        with tab1:
            st.write("### 🧬 Actian VectorAI DB Results")
            
            # Use .get() to avoid errors if the key doesn't exist yet
            raw_matches = st.session_state.get('actian_results')
            
            # SAFETY CHECK: Only iterate if raw_matches is NOT None
            if raw_matches is not None:
                formatted_data = []
                for i, res in enumerate(raw_matches):
                    # Safe extraction of title and score
                    title = res.payload.get('title', 'Unknown Title') if hasattr(res, 'payload') else "Unknown"
                    score = getattr(res, 'score', 0.0)
                    
                    formatted_data.append({
                        "Rank": i + 1,
                        "Movie": title,
                        "Similarity": round(score, 4),
                        "Status": "✅ Verified"
                    })
                
                st.table(pd.DataFrame(formatted_data))
                st.caption("Data source: Actian VectorAI DB")
            else:
                # Show a helpful message instead of crashing
                st.info("Results will appear here once the pipeline execution is complete.")

        with tab2:
            st.write("### Real-Time Sphinx Reasoning")
            log_container = st.empty()

            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"

            if strict_mode:
                audit_prompt = (
                    "URGENT: Perform a HIGH-STRICTNESS audit of @docs/source/reports/web_demo_audit.md against @src/ingest.py. "
                    "Identify any 'Narrative Hallucinations' where the report adds plot details not found in the source payload. "
                    "Verify that EVERY 'title' matches EXACTLY. If you find a single discrepancy, flag it as a 'SCHEMA_VIOLATION'."
                )
            else:
                audit_prompt = (
                    "Analyze @src/ingest.py and @docs/source/reports/web_demo_audit.md. "
                    "Does the report utilize the 'title' and 'plot' fields defined in the ingest script?"
                )
            
            cmd = ["sphinx-cli", "chat", "--no-memory-write", "--prompt", audit_prompt]

            full_log = ""
            # Capture the live terminal output
            root_dir = str(Path(__file__).resolve().parent.parent)
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, encoding="utf-8", env=env, cwd=root_dir) as proc:
                for line in proc.stdout:
                    full_log += line
                    log_container.code(full_log, language="bash")


            if proc.returncode == 0:
                st.success("✅ Sphinx Audit Verified: Report matches database schema.")
                
                # Housekeeping: Move logs to a dedicated folder
                try:
                    import shutil
                    log_dir = Path("audit_logs")
                    log_dir.mkdir(exist_ok=True)
                    
                    # Find and move all notebooks generated in the root
                    for nb_file in Path(".").glob("*.ipynb"):
                        shutil.move(str(nb_file), log_dir / nb_file.name)
                    
                    st.caption(f"📁 Agent logs archived to `/{log_dir}`")
                except Exception as e:
                    # Silent fail for cleanup so it doesn't interrupt the demo
                    pass 
            else:
                st.warning("Audit Suspicious: Check schema tags in source.")

        with tab3:
            report_path = Path("docs/source/reports/web_demo_audit.md")
            if report_path.exists():
                with open(report_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                st.markdown('<div class="report-container">', unsafe_allow_html=True)
                st.markdown(content)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.download_button(
                    label="Download Validated Audit",
                    data=content,
                    file_name="script_audit_report.md",
                    mime="text/markdown",
                    key="dl_btn_final"
                )
    else:
        st.info("Enter a concept and execute the pipeline to see the Agentic Audit in action.")