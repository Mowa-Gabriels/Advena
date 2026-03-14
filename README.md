# Advena ✈️
**AI-Powered U.S. Visa Eligibility Advisor** — Built on Agno v2 + Claude

## Architecture

```
Agno v2: Pure Sequential Pipeline (5 Agents, no Workflow class)
────────────────────────────────────────────────────────────────
Plain Python orchestration — no coordinator LLM, full control

  Step 1  ProfileParser Agent        Claude Sonnet
          Extracts structured profile JSON

  Step 2  VisaResearcher Agent       Claude Sonnet + ExaTools
          Searches USCIS.gov & travel.state.gov (cached per visa)

  Step 3  ScoringEngine Agent        Claude Sonnet
          Scores profile 0–100 per requirement

  Step 4  RecommendationAgent        Claude Sonnet
          Strategic advice + alternative pathways JSON

  Step 5  ReportGenerator Agent      Claude Opus (streamed)
          Final Markdown → PDF report
```

## Key v1 → v2 Changes

| v1 | v2 |
|---|---|
| `Team(mode="coordinate")` | Plain sequential agent calls in Python |
| `RunResponse` | Deprecated — removed entirely |
| `AgentMemory` / `AgentKnowledge` | Removed — replaced by `SqliteDb` |
| `enable_agentic_context=True` | `enable_agentic_state=True` |
| `team.run(query).content` | `agent.run(input=...)` → `.content` |
| `response_model=` | `output_schema=` |
| `context=` | `dependencies=` |
| Google Gemini | Anthropic Claude |
| `.md` report download | Styled `.pdf` via reportlab |
| No streaming in Streamlit | `st.status()` + `st.write_stream()` |

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
echo "ANTHROPIC_API_KEY=your_anthropic_api_key" >> .env
echo "EXA_API_KEY=your_exa_api_key"             >> .env

# 3. Run
streamlit run app.py
```

## Files

```
advena/
├── app.py                  # Streamlit UI — navy/gold theme
├── immisense_workflow.py   # 5-agent pipeline: build_agents, run_pipeline_steps, stream_report
├── visa_data.py            # VISA_DESCRIPTIONS, GOAL_TO_VISA_MAPPING, ASSESSMENT_QUESTIONS
├── pdf_report.py           # markdown_to_pdf() — reportlab PDF generator
├── debug_pipeline.py       # CLI runner — test agents without Streamlit
├── requirements.txt
└── README.md
```

## API Keys Required

- **ANTHROPIC_API_KEY** — [Anthropic Console](https://console.anthropic.com/)
- **EXA_API_KEY** — [Exa](https://exa.ai/) for live USCIS web search

## Roadmap

| Sprint | Features |
|--------|----------|
| **1 — Foundation** | Persistent case file (SqliteDb), assessment history, multi-pathway ranker |
| **2 — Intelligence** | Document upload + extraction, prevailing wage checker, policy change flag |
| **3 — Engagement** | Deadline tracker, H-1B lottery simulator, shareable score card |
| **4 — B2B** | Employer checklist generator, cohort benchmarking |