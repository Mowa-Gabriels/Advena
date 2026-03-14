

import json
from typing import Generator

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.exa import ExaTools


def _sonnet(api_key: str) -> Claude:
    return Claude(id="claude-sonnet-4-5", api_key=api_key)

def _opus(api_key: str) -> Claude:
    return Claude(id="claude-opus-4-5", api_key=api_key)


# ---------------------------------------------------------------------------
# JSON parsing helper
# ---------------------------------------------------------------------------

def _parse_json(text: str, fallback: dict) -> dict:
    """
    Parse a JSON string into a dict robustly.
    Strips markdown fences, finds outermost {}, never returns None.
    """
    if not text:
        return fallback
    s = text.strip()
    # Strip ```json...``` fences
    if s.startswith("```"):
        parts = s.split("```")
        if len(parts) >= 2:
            s = parts[1]
            if s.lower().startswith("json"):
                s = s[4:]
            s = s.strip()
    # Find outermost JSON object
    start = s.find("{")
    end   = s.rfind("}")
    if start != -1 and end > start:
        s = s[start : end + 1]
    try:
        parsed = json.loads(s)
    except (json.JSONDecodeError, ValueError):
        return fallback
    return parsed if isinstance(parsed, dict) else fallback


def _content(run_output) -> str:
    """Safely extract string content from agent.run() output."""
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


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------

def build_agents(google_api_key: str, exa_api_key: str) -> dict:
    """Create and return all agents as a plain dict."""
    model     = _sonnet(google_api_key)   # google_api_key param reused as anthropic_api_key
    model_big = _opus(google_api_key)
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
                "Output ONLY a single valid JSON object with keys:",
                "  'overall_score': integer 0-100,",
                "  'score_breakdown': object mapping each requirement to "
                "    {'score': 0-100, 'reason': string}.",
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
                "Use the score_breakdown to find strengths and weaknesses.",
                "Output ONLY a single valid JSON object with keys:",
                "  'summary': string,",
                "  'key_considerations': list of strings,",
                "  'actionable_steps': list of strings,",
                "  'alternative_pathways': list of strings.",
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
                "Write a comprehensive polished Markdown eligibility report for 'Advena'.",
                "Include sections: ## 👤 Applicant Profile, ## 📋 Visa Requirements, "
                "## 📊 Eligibility Score (show overall_score prominently then a breakdown table), "
                "## ✅ Key Considerations, ## 🗺️ Actionable Steps, "
                "## 🔄 Alternative Pathways, ## ⚠️ Disclaimer.",
                "Use professional, clear, encouraging language.",
            ],
            markdown=True,
            retries=2,
        ),
    }


# ---------------------------------------------------------------------------
# Pipeline: Steps 1-4 (blocking) + Step 5 (streaming) — split for Streamlit
# ---------------------------------------------------------------------------

def run_pipeline_steps(
    agents: dict,
    user_query: str,
    visa_category: str,
    cache: dict,
    status=None,           # optional st.status context for live updates
) -> dict:
    """
    Run steps 1-4 synchronously. Returns a dict with all intermediate data.
    Pass cache=st.session_state so steps 1 & 2 are cached across reruns.
    Pass status=st.status(...) for live step labels in the Streamlit UI.
    """

    def _update(msg: str):
        if status is not None:
            status.write(msg)

    # ── Step 1: Parse Profile ───────────────────────────────────────────
    cached_profile = cache.get("advena_profile")
    if isinstance(cached_profile, dict):
        profile = cached_profile
        _update("🔄 Step 1/4 — Profile parse *(cached)*")
    else:
        _update("⚙️ Step 1/4 — Parsing profile...")
        out     = agents["profile_parser"].run(input=user_query)
        profile = _parse_json(_content(out), fallback={"raw_profile": _content(out)})
        profile["visa_category"] = visa_category
        cache["advena_profile"] = profile

    # ── Step 2: Research Visa Requirements ──────────────────────────────
    cache_key   = f"advena_reqs_{visa_category}"
    cached_reqs = cache.get(cache_key)
    if isinstance(cached_reqs, dict) and "visa_requirements" in cached_reqs:
        requirements = cached_reqs
        _update("🔄 Step 2/4 — Visa research *(cached)*")
    else:
        _update("🔍 Step 2/4 — Researching USCIS requirements...")
        out          = agents["visa_researcher"].run(
            input=f"Find official eligibility requirements for the U.S. {visa_category} visa."
        )
        requirements = _parse_json(
            _content(out),
            fallback={"visa_requirements": [f"See uscis.gov for {visa_category} requirements."]},
        )
        if "visa_requirements" not in requirements:
            requirements = {"visa_requirements": list(requirements.values())}
        cache[cache_key] = requirements

    visa_reqs = requirements.get("visa_requirements", [])

    # ── Step 3: Score Eligibility ────────────────────────────────────────
    _update("📊 Step 3/4 — Scoring eligibility...")
    out     = agents["scoring_engine"].run(
        input=json.dumps({"user_profile": profile, "visa_requirements": visa_reqs}, indent=2)
    )
    scoring = _parse_json(
        _content(out),
        fallback={"overall_score": 0, "score_breakdown": {}},
    )

    # ── Step 4: Generate Recommendations ────────────────────────────────
    _update("🧠 Step 4/4 — Generating recommendations...")
    out             = agents["recommendation_agent"].run(
        input=json.dumps(
            {"user_profile": profile, "visa_requirements": visa_reqs, "scoring": scoring},
            indent=2,
        )
    )
    recommendations = _parse_json(
        _content(out),
        fallback={
            "summary": "Analysis unavailable.",
            "key_considerations": [],
            "actionable_steps": [],
            "alternative_pathways": [],
        },
    )

    return {
        "profile":           profile,
        "visa_requirements": visa_reqs,
        "scoring":           scoring,
        "recommendations":   recommendations,
    }


def stream_report(agents: dict, pipeline_data: dict) -> Generator[str, None, None]:
    """
    Step 5: Stream the final Markdown report token by token.
    Designed for use with st.write_stream() in Streamlit.
    Yields plain strings (tokens) — no Agno types exposed.
    """
    compiled = json.dumps(pipeline_data, indent=2)
    for chunk in agents["report_generator"].run(input=compiled, stream=True):
        text = _content(chunk)
        if text:
            yield text