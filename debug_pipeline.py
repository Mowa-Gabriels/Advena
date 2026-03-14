"""
ImmiSense — CLI Debug Runner
============================
Runs the full 5-agent pipeline in the terminal.
No Streamlit. Prints raw agent output at every step.

Usage:
    python debug_pipeline.py
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.exa import ExaTools

# ── Hardcoded test profile (edit as needed) ──────────────────────────────────

VISA_CATEGORY = "H-1B"

USER_QUERY = """
## Applicant Profile:
- Full Name: Mowa Test
- Age: 32
- Nationality: Nigerian
- Country of Birth: Nigeria
- Highest Degree: Master's Degree
- Field of Study: Computer Science
- Years of Experience: 6
- Annual Income (USD): 75000
- Liquid Assets (USD): 30000
- Sponsorship Status: Have a job offer / sponsorship
- Current Residence: Nigeria
- Current U.S. Status: N/A
- Previous Visa Denials: No
- Criminal History: No
- Language Proficiency: English

## Assessment for Visa: H-1B
- Question: Describe your job offer and why it qualifies as a specialty occupation.
  Answer: I have a job offer as a Senior Software Engineer at a U.S. tech company.
          The role requires a Master's degree in Computer Science and 5+ years of experience.

- Question: How does your education and experience match the job requirements?
  Answer: I hold an MSc in Computer Science and have 6 years building distributed systems.

- Question: Can the sponsoring employer demonstrate ability to pay the prevailing wage?
  Answer: Yes, the company has 500+ employees and has filed H-1B petitions successfully before.

## Task:
Assess this applicant's eligibility for the H-1B visa.
"""

# ── Helpers (same as immisense_workflow.py) ───────────────────────────────────

def _content(run_output) -> str:
    if run_output is None:
        return ""
    raw = getattr(run_output, "content", None)
    if raw is None:
        return ""
    if isinstance(raw, list):
        return " ".join(
            b.get("text", "") if isinstance(b, dict) else str(b)
            for b in raw
        )
    return str(raw)


def _parse_json(text: str, fallback: dict) -> dict:
    s = text.strip()
    if s.startswith("```"):
        parts = s.split("```")
        if len(parts) >= 2:
            s = parts[1]
            if s.lower().startswith("json"):
                s = s[4:]
            s = s.strip()
    start = s.find("{")
    end   = s.rfind("}")
    if start != -1 and end > start:
        s = s[start : end + 1]
    try:
        parsed = json.loads(s)
    except (json.JSONDecodeError, ValueError):
        return fallback
    return parsed if isinstance(parsed, dict) else fallback


def sep(title: str):
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print('─' * 60)


# ── Build agents ─────────────────────────────────────────────────────────────

def build_agents() -> dict:
    api_key     = os.getenv("ANTHROPIC_API_KEY")
    exa_api_key = os.getenv("EXA_API_KEY")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in .env")
    if not exa_api_key:
        raise ValueError("EXA_API_KEY not found in .env")

    model     = Claude(id="claude-sonnet-4-5", api_key=api_key)
    model_big = Claude(id="claude-opus-4-5",   api_key=api_key)
    exa       = ExaTools(api_key=exa_api_key)

    return {
        "profile_parser": Agent(
            name="ProfileParser",
            model=model,
            role="User Profile JSON Extractor",
            instructions=[
                "Read the user query and extract all profile information.",
                "Output ONLY a single valid JSON object. No prose, no markdown fences.",
                "Keys: full_name, age, nationality, birth_country, highest_degree, "
                "field_of_study, years_of_experience, annual_income_usd, "
                "liquid_assets_usd, sponsorship_status, current_residence, "
                "current_us_status, previous_visa_denials, criminal_history, "
                "language_proficiency, visa_category.",
                "Set any missing value to null.",
            ],
            retries=2,
        ),
        "visa_researcher": Agent(
            name="VisaResearcher",
            model=model,
            tools=[exa],
            role="Visa Requirements Specialist",
            instructions=[
                "You receive a U.S. visa category (e.g. 'H-1B').",
                "Search uscis.gov and travel.state.gov for the primary eligibility requirements.",
                "Output ONLY a single valid JSON object with key 'visa_requirements' "
                "holding a list of requirement strings.",
                "No prose, no markdown fences outside the JSON.",
            ],
            retries=2,
        ),
        "scoring_engine": Agent(
            name="ScoringEngine",
            model=model,
            role="Eligibility Scoring Analyst",
            instructions=[
                "You receive a JSON object with 'user_profile' and 'visa_requirements'.",
                "Logically compare the profile against every requirement.",
                "Output ONLY a single valid JSON object with keys: "
                "'overall_score' (int 0-100), "
                "'score_breakdown' (object: requirement -> {score, reason}).",
                "No prose, no markdown fences.",
            ],
            retries=2,
        ),
        "recommendation_agent": Agent(
            name="RecommendationAgent",
            model=model,
            role="Strategic Immigration Advisor",
            instructions=[
                "You receive a JSON object with 'user_profile', 'visa_requirements', 'scoring'.",
                "Output ONLY a single valid JSON object with keys: "
                "'summary' (str), 'key_considerations' (list), "
                "'actionable_steps' (list), 'alternative_pathways' (list).",
                "No prose, no markdown fences.",
            ],
            retries=2,
        ),
        "report_generator": Agent(
            name="ReportGenerator",
            model=model_big,
            role="Final Report Compiler",
            instructions=[
                "You receive a JSON object with: profile, visa_requirements, scoring, recommendations.",
                "Write a comprehensive Markdown eligibility report for 'ImmiSense AI'.",
                "Sections: ## 👤 Applicant Profile, ## 📋 Visa Requirements, "
                "## 📊 Eligibility Score, ## ✅ Key Considerations, "
                "## 🗺️ Actionable Steps, ## 🔄 Alternative Pathways, ## ⚠️ Disclaimer.",
            ],
            markdown=True,
            retries=2,
        ),
    }


# ── Run pipeline ─────────────────────────────────────────────────────────────

def run(agents: dict):

    cache = {}   # simulates st.session_state

    # ── Step 1 ──────────────────────────────────────────────────────────────
    sep("STEP 1 — Profile Parser")
    out     = agents["profile_parser"].run(input=USER_QUERY)
    raw1    = _content(out)
    print("RAW OUTPUT:\n", raw1)

    profile = _parse_json(raw1, fallback={"raw_profile": raw1})
    profile["visa_category"] = VISA_CATEGORY
    cache["profile"] = profile
    print("\nPARSED:\n", json.dumps(profile, indent=2))

    # ── Step 2 ──────────────────────────────────────────────────────────────
    sep("STEP 2 — Visa Researcher")
    out  = agents["visa_researcher"].run(
        input=f"Find official eligibility requirements for the U.S. {VISA_CATEGORY} visa."
    )
    raw2 = _content(out)
    print("RAW OUTPUT:\n", raw2)

    requirements = _parse_json(
        raw2,
        fallback={"visa_requirements": [f"See uscis.gov for {VISA_CATEGORY} requirements."]}
    )
    if "visa_requirements" not in requirements:
        requirements = {"visa_requirements": list(requirements.values())}
    cache["requirements"] = requirements
    print("\nPARSED:\n", json.dumps(requirements, indent=2))

    visa_reqs = requirements.get("visa_requirements", [])

    # ── Step 3 ──────────────────────────────────────────────────────────────
    sep("STEP 3 — Scoring Engine")
    out  = agents["scoring_engine"].run(
        input=json.dumps({"user_profile": profile, "visa_requirements": visa_reqs}, indent=2)
    )
    raw3 = _content(out)
    print("RAW OUTPUT:\n", raw3)

    scoring = _parse_json(raw3, fallback={"overall_score": 0, "score_breakdown": {}})
    cache["scoring"] = scoring
    print("\nPARSED:\n", json.dumps(scoring, indent=2))

    # ── Step 4 ──────────────────────────────────────────────────────────────
    sep("STEP 4 — Recommendation Agent")
    out  = agents["recommendation_agent"].run(
        input=json.dumps(
            {"user_profile": profile, "visa_requirements": visa_reqs, "scoring": scoring},
            indent=2,
        )
    )
    raw4 = _content(out)
    print("RAW OUTPUT:\n", raw4)

    recommendations = _parse_json(
        raw4,
        fallback={
            "summary": "Unavailable.", "key_considerations": [],
            "actionable_steps": [],    "alternative_pathways": [],
        }
    )
    cache["recommendations"] = recommendations
    print("\nPARSED:\n", json.dumps(recommendations, indent=2))

    # ── Step 5 ──────────────────────────────────────────────────────────────
    sep("STEP 5 — Report Generator (streaming)")
    compiled = json.dumps(
        {
            "profile":           profile,
            "visa_requirements": visa_reqs,
            "scoring":           scoring,
            "recommendations":   recommendations,
        },
        indent=2,
    )

    print()
    report_chunks = []
    for chunk in agents["report_generator"].run(input=compiled, stream=True):
        text = _content(chunk)
        if text:
            print(text, end="", flush=True)
            report_chunks.append(text)

    sep("DONE")
    print(f"Report length: {len(''.join(report_chunks))} chars")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🚀 ImmiSense CLI Debug Runner")
    print(f"   Visa: {VISA_CATEGORY}")
    print(f"   Model: Claude (Anthropic)\n")

    try:
        agents = build_agents()
        run(agents)
    except Exception as e:
        import traceback
        print(f"\n❌ FAILED: {e}")
        traceback.print_exc()
