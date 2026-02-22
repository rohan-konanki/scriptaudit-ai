# ScriptAudit AI: Agentic Data Integrity for Film Analysis
Recursive Agentic Validation for the Film Industry. Developed for Hacklytics 2026.

High-integrity analysis tool designed to bridge the gap between creative script ideation and factual database grounding. Utilizes a multi-layered agentic pipeline, to ensure that AI-generated script reports are strictly validated against a verified movie database, eliminating narrative hallucinations and ensuring architectural schema compliance.

## Pipeline Flow
**Vector Search (Actian VectorAI DB):** The system takes a user's script concept and generates a 3072-dimensional embedding. It then performs a similarity search against a 200-movie TMDB vector database.

**Report Generation (Gemini 3 Flash):** Using the retrieved "ground truth" metadata (titles and plot premises), the system utilizes Gemini 3 Flash on the v1alpha endpoint to construct a structured audit report.

**Agentic Verification (Sphinx AI):** A Sphinx Agent audits the generated report against the source code (ingest.py) and the Actian payload to ensure factual alignment and format compliance.

## Tech Stack
**Vector Database:** Actian VectorAI DB (Local Docker Cluster)

**LLM (Reasoning & Generation):** Gemini 3 Flash (Preview)

**LLM (Embeddings):** gemini-embedding-001

**Agentic Auditor:** Sphinx AI Agent

**Frontend:** Streamlit

## Installation & Setup
### Note: These steps are only verified on Windows, and may fail on macOS or Linux.
#### 1. Clone the Repository
```
git clone https://github.com/rohan-konanki/scriptaudit-ai.git
cd scriptaudit-ai
```
#### 2. Install Dependencies
Ensure you have a Python 3.10+ environment. Note that the Actian client is installed via a local wheel file included in the repository. Highly recommended to use a virtual environment to ensure proper functionality.
```
pip install -r requirements.txt
```
Authenticate Sphinx using `sphinx-cli login`, otherwise the app will not function as intended. If `sphinx-cli` is not recognized as a command, try:
```
python -c "from sphinx_cli.runner import main; import sys; sys.exit(main())" login
```
#### 3. Environment Variables
Create a .env file in the root directory and Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
```
#### 4. Launch Actian VectorAI DB
Ensure that Docker Desktop is running, and start the local vector database cluster using Docker Compose:

```
docker-compose up -d
```
#### 5. Ingest Movie Data
Run the ingestion script to populate the Actian database with 200 [TMDB movie records](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata):

```
python src/ingest.py
```
#### 6. Run the Dashboard
Launch the Streamlit application:

```
streamlit run src/app.py
```
## Key Features
#### Agentic "Strict Audit" Mode
When enabled, the Sphinx Agent performs a high-stakes cross-reference of the report against the Actian source payload. Specifically instructed to identify "narrative hallucinations" in which the AI adds plot details not found in the source data.

#### Real-Time Reasoning Logs
Users can monitor the Sphinx Agent's "Thinking Phase" in real time via the Sphinx Audit tab.

#### Traceable Metadata
Every report includes [SCHEMA_VALIDATION] blocks that map generated content directly to specific database keys like title and plot, ensuring technical traceability.

## Project Structure
`src/app.py`: Streamlit UI and agent orchestration.

`src/audit_engine.py`: Core logic for embeddings, Actian search, and report generation.

`src/ingest.py`: Data pipeline for indexing TMDB data into Actian.

`docs/source/reports/`: Permanent storage for validated audit reports.

`audit_logs/`: Archive for agentic reasoning traces and Sphinx log notebooks. Generated at runtime
