import os
import requests
from dotenv import load_dotenv
from cortex import CortexClient # Assuming this is your Actian client
import json
from pathlib import Path

# 1. BULLETPROOF ENV LOADING
# This finds the .env file in the root even if you run from /src
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Ensure we use the correct variable name from your .env
api_key = os.getenv("GEMINI_API_KEY")

def audit_script(script_idea, output_filename):
    if not api_key:
        print(f"❌ Error: GEMINI_API_KEY not found. Checked: {env_path}")
        return

    print(f"Auditing script idea: '{script_idea}'...\n")
    
    # 2. EMBEDDING CALL (REST)
    embed_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={api_key}"
    embed_payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": script_idea}]}
    }
    
    response = requests.post(embed_url, json=embed_payload)
    embed_response = response.json()
    
    if 'error' in embed_response:
        print(f"❌ Embedding Error: {embed_response['error']['message']}")
        return

    query_vector = embed_response['embedding']['values']
    
    # 3. ACTIAN SEARCH
    # Using with_payload=True to ensure Sphinx has data to audit
    with CortexClient("localhost:50051") as db_client:
        results = db_client.search(
            "movies", 
            query=query_vector, 
            top_k=3,
            with_payload=True
        )
    
    if not results:
        print("No similar movies found.")
        return

    # 4. CONSTRUCT CONTEXT
    context = ""
    for r in results:
        t = r.payload.get('title', 'Unknown')
        p = r.payload.get('plot', 'No plot available')
        context += f"MATCHED TITLE: {t}\nMATCHED PLOT: {p}\n---\n"

    # 5. OPTIMIZED PROMPT (Fixed f-string escaping)
    # Note the double {{ }} to prevent Python from trying to fill them
    # 5. POLISHED DASHBOARD PROMPT
    prompt_text = f"""
    SYSTEM ROLE: 
    Technical Auditor & Film Analyst.

    TASK:
    Generate a visually structured audit report for the ScriptAudit AI Dashboard.
    
    DATA:
    {context}

    FORMATTING RULES:
    1. Use '---' (horizontal rules) between films.
    2. Put the [SCHEMA_VALIDATION] blocks inside a Markdown code block or blockquote to make them stand out.
    3. Use Bold headers for clarity.

    OUTPUT STRUCTURE:

    # Script Audit Report
    **Analysis of input:** _{script_idea}_

    ---

    ## Match: [Movie Title]
    
    > **Technical Metadata Traceability**
    > [SCHEMA_VALIDATION_START]
    > - **KEY:** `title` | **VALUE:** [Insert Title]
    > - **KEY:** `plot`  | **VALUE:** [Insert Plot]
    > [SCHEMA_VALIDATION_END]

    ### Narrative Analysis
    [Insert analysis here. Focus on how it relates to the user's idea.]

    ---
    (Repeat for each match)

    ## Metadata Integrity
    - **Source:** Actian VectorAI
    - **Validation:** Sphinx Agentic Audit Ready
    """
    
    # 6. GENERATE REPORT
    # Using v1beta for the latest 2026 models
    generate_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    generate_payload = {
        "contents": [{"parts": [{"text": prompt_text}]}]
    }
    
    print("Generating report...")
    gen_response = requests.post(generate_url, json=generate_payload).json()
    
    if 'candidates' not in gen_response:
        print("❌ Generation Error:", gen_response)
        return

    report_text = gen_response['candidates'][0]['content']['parts'][0]['text']

    # 7. SAVE OUTPUTS
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, "..", "docs", "source", "reports", f"{output_filename}.md")
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # ADD A TIMESTAMP TO THE CONTENT (To prove it's new!)
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"\n"
    
    print(f"Attempting to save report to: {os.path.abspath(filepath)}")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header + report_text)
        f.flush() # Force the OS to write the buffer immediately
        os.fsync(f.fileno()) # Deep flush to disk
        
    print(f"✅ Success! File updated at {timestamp}")

if __name__ == "__main__":
    test_idea = "A lonely garbage collector robot on a ruined Earth discovers a tiny plant, sparking a journey across the galaxy."
    audit_script(test_idea, "robot_earth_audit")