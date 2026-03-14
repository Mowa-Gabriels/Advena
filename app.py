
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

from immisense_workflow import build_agents, run_pipeline_steps, stream_report
from pdf_report import markdown_to_pdf
from visa_data import VISA_DESCRIPTIONS, GOAL_TO_VISA_MAPPING, ASSESSMENT_QUESTIONS

# Load .env relative to this file, not the shell cwd
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

# ─── Page Config ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Advena",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS — Luxury Navy & Gold Theme ───────────────────────────────────

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');

  /* ── Global Reset ── */
  html, body, [data-testid="stAppViewContainer"] {
    background-color: #080C18 !important;
    color: #E8E4D9 !important;
    font-family: 'DM Sans', sans-serif !important;
  }
  [data-testid="stHeader"] { background: transparent !important; }
  [data-testid="stSidebar"] {
    background: #0D1220 !important;
    border-right: 1px solid #1E2A42 !important;
  }

  /* ── Typography ── */
  h1, h2, h3 { font-family: 'Playfair Display', serif !important; }

  /* ── Sidebar nav buttons ── */
  .stButton > button {
    background: transparent !important;
    color: #8A9BBE !important;
    border: 1px solid #1E2A42 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    transition: all 0.25s ease !important;
    padding: 0.55rem 1rem !important;
  }
  .stButton > button:hover {
    background: #1A2540 !important;
    color: #C9A84C !important;
    border-color: #C9A84C !important;
  }

  /* ── Primary CTA button ── */
  .primary-btn > button {
    background: linear-gradient(135deg, #C9A84C, #E6C76B) !important;
    color: #08090F !important;
    border: none !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    font-size: 0.8rem !important;
    padding: 0.7rem 2rem !important;
    border-radius: 6px !important;
  }
  .primary-btn > button:hover {
    background: linear-gradient(135deg, #D4B55A, #EDD47A) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(201, 168, 76, 0.3) !important;
  }

  /* ── Cards ── */
  .card {
    background: linear-gradient(145deg, #0D1526, #111927);
    border: 1px solid #1E2A42;
    border-radius: 12px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.2rem;
    transition: border-color 0.25s ease;
  }
  .card:hover { border-color: #2D3F5E; }

  /* ── Gold accent headings ── */
  .gold { color: #C9A84C !important; }
  .muted { color: #5A6A86 !important; font-size: 0.85rem; }

  /* ── Hero section ── */
  .hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.8rem;
    font-weight: 700;
    color: #E8E4D9;
    line-height: 1.15;
    letter-spacing: -0.01em;
  }
  .hero-title span { color: #C9A84C; }
  .hero-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.05rem;
    color: #7A8BA8;
    max-width: 560px;
    line-height: 1.7;
    margin-top: 1rem;
  }

  /* ── Feature pill ── */
  .pill {
    display: inline-block;
    background: #111927;
    border: 1px solid #1E2A42;
    border-radius: 999px;
    padding: 0.3rem 1rem;
    font-size: 0.78rem;
    color: #8A9BBE;
    margin: 0.25rem;
    letter-spacing: 0.04em;
  }

  /* ── Pipeline steps indicator ── */
  .pipeline {
    display: flex;
    align-items: center;
    gap: 0;
    margin: 2rem 0;
  }
  .step-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    flex: 1;
    position: relative;
  }
  .step-node:not(:last-child)::after {
    content: '';
    position: absolute;
    top: 16px;
    left: calc(50% + 20px);
    right: calc(-50% + 20px);
    height: 1px;
    background: #1E2A42;
  }
  .step-circle {
    width: 36px; height: 36px;
    border-radius: 50%;
    border: 2px solid #1E2A42;
    background: #0D1526;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    color: #5A6A86;
    font-weight: 600;
    z-index: 1;
  }
  .step-circle.active {
    border-color: #C9A84C;
    color: #C9A84C;
    background: #18200E;
    box-shadow: 0 0 12px rgba(201,168,76,0.25);
  }
  .step-circle.done {
    border-color: #2A6A4A;
    background: #0E2018;
    color: #4CAF80;
  }
  .step-label {
    font-size: 0.68rem;
    color: #5A6A86;
    text-align: center;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  /* ── Score badge ── */
  .score-badge {
    font-family: 'Playfair Display', serif;
    font-size: 4rem;
    font-weight: 700;
    line-height: 1;
  }
  .score-high { color: #4CAF80; }
  .score-mid  { color: #F59E0B; }
  .score-low  { color: #EF4444; }

  /* ── Form fields ── */
  [data-testid="stTextInput"] input,
  [data-testid="stNumberInput"] input,
  [data-testid="stSelectbox"] select,
  [data-testid="stTextArea"] textarea,
  .stMultiSelect [data-baseweb="select"] {
    background: #0D1526 !important;
    border-color: #1E2A42 !important;
    color: #E8E4D9 !important;
    font-family: 'DM Sans', sans-serif !important;
    border-radius: 8px !important;
  }
  [data-testid="stTextInput"] input:focus,
  [data-testid="stTextArea"] textarea:focus {
    border-color: #C9A84C !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.15) !important;
  }
  label, .stSelectbox label, .stTextInput label, .stNumberInput label {
    color: #8A9BBE !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
  }

  /* ── Info / warning boxes ── */
  .stInfo {
    background: #0D1930 !important;
    border-left-color: #2563EB !important;
    color: #8AA4CC !important;
  }
  .stWarning {
    background: #1A1200 !important;
    border-left-color: #F59E0B !important;
    color: #C9A84C !important;
  }
  .stSuccess {
    background: #0A1E14 !important;
    border-left-color: #22C55E !important;
    color: #4ADE80 !important;
  }
  .stError {
    background: #1A0808 !important;
    border-left-color: #EF4444 !important;
    color: #FCA5A5 !important;
  }

  /* ── Divider ── */
  hr { border-color: #1E2A42 !important; }

  /* ── Report output ── */
  .report-container {
    background: linear-gradient(145deg, #0D1526, #111927);
    border: 1px solid #1E2A42;
    border-radius: 12px;
    padding: 2.5rem;
    margin-top: 1.5rem;
  }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #080C18; }
  ::-webkit-scrollbar-thumb { background: #1E2A42; border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: #2D3F5E; }

  /* ── Progress bar override ── */
  [data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #C9A84C, #E6C76B) !important;
  }
  [data-testid="stProgress"] > div {
    background: #1E2A42 !important;
  }

  /* ── Remove Streamlit branding ── */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 2rem !important; max-width: 1100px; }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────

defaults = {
    "page": "home",
    "user_profile": {},
    "final_report": None,
    "analysis_running": False,
    "profile_just_saved": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Workflow Init (cached) ──────────────────────────────────────────────────

@st.cache_resource
def load_agents() -> dict:
    # Re-load inside the cached function — guarantees keys are present
    # even if Streamlit's cache runs before module-level load_dotenv.
    load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

    google_api_key = os.getenv("ANTHROPIC_API_KEY")
    exa_api_key = os.getenv("EXA_API_KEY")

    if not google_api_key or not exa_api_key:
        missing = []
        if not google_api_key: missing.append("ANTHROPIC_API_KEY")
        if not exa_api_key:    missing.append("EXA_API_KEY")
        st.error(
            f"Missing API key(s): **{', '.join(missing)}**\n\n"
            f"Make sure your `.env` file is in the same folder as `app.py` "
            f"and contains these keys."
        )
        st.stop()
    return build_agents(google_api_key=google_api_key, exa_api_key=exa_api_key)

try:
    agents = load_agents()
except Exception as e:
    st.error(f"Failed to initialise Advena agents: {e}")
    st.stop()

# ─── Navigation ─────────────────────────────────────────────────────────────

def nav(page: str):
    st.session_state.page = page
    if page == "assessment":
        st.session_state.final_report = None

# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 2rem 0;">
      <div style="font-family:'Playfair Display',serif; font-size:1.4rem; color:#E8E4D9;">
        Immi<span style="color:#C9A84C;">Sense</span>
      </div>
      <div style="font-size:0.72rem; color:#5A6A86; letter-spacing:0.08em; text-transform:uppercase; margin-top:4px;">
        AI Immigration Advisor
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.button("✦  Home",              on_click=nav, args=("home",),       use_container_width=True)
    st.button("◈  My Profile",        on_click=nav, args=("profile",),    use_container_width=True)
    st.button("◉  Run Assessment",    on_click=nav, args=("assessment",), use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.session_state.user_profile:
        name = st.session_state.user_profile.get("full_name", "—")
        nationality = st.session_state.user_profile.get("nationality", "—")
        st.markdown(f"""
        <div class="card" style="padding:1rem;">
          <div style="font-size:0.7rem; color:#5A6A86; text-transform:uppercase; letter-spacing:0.06em;">Logged Profile</div>
          <div style="font-family:'Playfair Display',serif; font-size:1rem; margin-top:4px; color:#E8E4D9;">{name}</div>
          <div style="font-size:0.78rem; color:#8A9BBE; margin-top:2px;">🌍 {nationality}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="muted" style="padding:0.5rem 0;">No profile saved yet.</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="position:absolute; bottom:2rem; left:1rem; right:1rem; font-size:0.68rem; color:#2D3F5E; line-height:1.5;">
      Advena is for informational purposes only and does not constitute legal advice.
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════════════════

if st.session_state.page == "home":
    # Hero
    col_hero, col_vis = st.columns([1.1, 0.9], gap="large")

    with col_hero:
        st.markdown("""
        <div style="padding: 3rem 0 2rem 0;">
          <div class="pill">✦ Powered by Agno v2 & Anthropic </div>
          <div class="hero-title" style="margin-top:1.5rem;">
            Navigate U.S.<br>Immigration with<br><span>Confidence.</span>
          </div>
          <div class="hero-sub">
            Advenacombines official USCIS data with a multi-agent AI pipeline
            to score your eligibility, identify gaps, and chart the clearest path forward.
          </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            st.button("Begin Assessment →", on_click=nav, args=("assessment",), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.button("Complete My Profile", on_click=nav, args=("profile",), use_container_width=True)

    with col_vis:
        st.markdown("""
        <div style="padding: 3rem 0 0 1rem;">
          <div class="card" style="border-color:#C9A84C22;">
            <div style="font-size:0.7rem; color:#C9A84C; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:1rem;">
              ANALYSIS PIPELINE
            </div>
            <div style="display:flex; flex-direction:column; gap:1rem;">
              <div style="display:flex; align-items:center; gap:1rem;">
                <div style="width:36px; height:36px; border-radius:50%; border:2px solid #C9A84C; display:flex; align-items:center; justify-content:center; font-size:0.75rem; color:#C9A84C; flex-shrink:0;">01</div>
                <div>
                  <div style="font-weight:500; font-size:0.9rem; color:#E8E4D9;">Profile Parser</div>
                  <div style="font-size:0.75rem; color:#5A6A86;">Extracts structured data from your profile</div>
                </div>
              </div>
              <div style="width:2px; height:16px; background:#1E2A42; margin-left:17px;"></div>
              <div style="display:flex; align-items:center; gap:1rem;">
                <div style="width:36px; height:36px; border-radius:50%; border:2px solid #2563EB; display:flex; align-items:center; justify-content:center; font-size:0.75rem; color:#2563EB; flex-shrink:0;">02</div>
                <div>
                  <div style="font-weight:500; font-size:0.9rem; color:#E8E4D9;">Visa Researcher</div>
                  <div style="font-size:0.75rem; color:#5A6A86;">Fetches live data from USCIS & travel.state.gov</div>
                </div>
              </div>
              <div style="width:2px; height:16px; background:#1E2A42; margin-left:17px;"></div>
              <div style="display:flex; align-items:center; gap:1rem;">
                <div style="width:36px; height:36px; border-radius:50%; border:2px solid #7C3AED; display:flex; align-items:center; justify-content:center; font-size:0.75rem; color:#7C3AED; flex-shrink:0;">03</div>
                <div>
                  <div style="font-weight:500; font-size:0.9rem; color:#E8E4D9;">Analysis Team</div>
                  <div style="font-size:0.75rem; color:#5A6A86;">ScoringEngine + RecommendationAgent collaborate</div>
                </div>
              </div>
              <div style="width:2px; height:16px; background:#1E2A42; margin-left:17px;"></div>
              <div style="display:flex; align-items:center; gap:1rem;">
                <div style="width:36px; height:36px; border-radius:50%; border:2px solid #22C55E; display:flex; align-items:center; justify-content:center; font-size:0.75rem; color:#22C55E; flex-shrink:0;">04</div>
                <div>
                  <div style="font-weight:500; font-size:0.9rem; color:#E8E4D9;">Report Generator</div>
                  <div style="font-size:0.75rem; color:#5A6A86;">Compiles final eligibility & strategy report</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Feature grid
    st.markdown("""
    <div style="font-family:'Playfair Display',serif; font-size:1.4rem; color:#E8E4D9; margin:1rem 0 1.5rem 0;">
      Why Advena?
    </div>
    """, unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns(3)
    features = [
        ("🔍", "Live Research", "Pulls current requirements directly from USCIS.gov and travel.state.gov — not outdated databases."),
        ("📊", "Precision Scoring", "Each eligibility criterion is scored individually so you know exactly where you stand."),
        ("🗺️", "Strategic Guidance", "Actionable next steps and alternative pathways tailored to your specific profile."),
    ]
    for col, (icon, title, desc) in zip([fc1, fc2, fc3], features):
        with col:
            st.markdown(f"""
            <div class="card">
              <div style="font-size:1.8rem; margin-bottom:0.8rem;">{icon}</div>
              <div style="font-family:'Playfair Display',serif; font-size:1rem; color:#E8E4D9; margin-bottom:0.5rem;">{title}</div>
              <div style="font-size:0.82rem; color:#5A6A86; line-height:1.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: PROFILE
# ═══════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "profile":
    st.markdown("""
    <div style="padding-bottom:1.5rem;">
      <div style="font-size:0.72rem; color:#C9A84C; letter-spacing:0.12em; text-transform:uppercase;">Step 0</div>
      <div style="font-family:'Playfair Display',serif; font-size:2.2rem; color:#E8E4D9; margin-top:4px;">My Profile</div>
      <div style="font-size:0.9rem; color:#5A6A86; margin-top:6px;">A complete profile enables the most accurate AI assessment.</div>
    </div>
    """, unsafe_allow_html=True)

    prev = st.session_state.user_profile

    with st.form("profile_form", clear_on_submit=False):

        # Personal
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Playfair Display\',serif; font-size:1.1rem; color:#C9A84C; margin-bottom:1rem;">Personal Details</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            full_name = st.text_input("Full Name", prev.get("full_name", ""))
        with c2:
            age = st.number_input("Age", 1, 120, prev.get("age", 30))
        with c3:
            language_proficiency = st.multiselect(
                "Language Proficiency",
                ["English", "Spanish", "French", "German", "Mandarin", "Other"],
                default=prev.get("language_proficiency", []),
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # Education & Work
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Playfair Display\',serif; font-size:1.1rem; color:#C9A84C; margin-bottom:1rem;">Education & Experience</div>', unsafe_allow_html=True)

        c4, c5, c6 = st.columns(3)
        degrees = ["Select...", "High School Diploma", "Associate's Degree", "Bachelor's Degree", "Master's Degree", "PhD / Doctorate"]
        current_degree = prev.get("highest_degree", "Select...")
        degree_idx = degrees.index(current_degree) if current_degree in degrees else 0
        with c4:
            highest_degree = st.selectbox("Highest Degree", degrees, index=degree_idx)
        with c5:
            field_of_study = st.text_input("Field of Study", prev.get("field_of_study", ""))
        with c6:
            years_of_experience = st.number_input("Years of Experience", 0, 60, prev.get("years_of_experience", 5))
        st.markdown('</div>', unsafe_allow_html=True)

        # Financial
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Playfair Display\',serif; font-size:1.1rem; color:#C9A84C; margin-bottom:1rem;">Financial Position</div>', unsafe_allow_html=True)

        c7, c8, c9 = st.columns(3)
        sponsor_opts = ["Select...", "Seeking sponsorship", "Have a job offer / sponsorship", "Not applicable"]
        current_sponsor = prev.get("sponsorship_status", "Select...")
        sponsor_idx = sponsor_opts.index(current_sponsor) if current_sponsor in sponsor_opts else 0
        with c7:
            annual_income = st.number_input("Annual Income (USD)", 0, 10_000_000, prev.get("annual_income_usd", 50_000), step=1_000)
        with c8:
            liquid_assets = st.number_input("Liquid Assets (USD)", 0, 100_000_000, prev.get("liquid_assets_usd", 20_000), step=1_000)
        with c9:
            sponsorship_status = st.selectbox("Sponsorship Status", sponsor_opts, index=sponsor_idx)
        st.markdown('</div>', unsafe_allow_html=True)

        # Legal & Country
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Playfair Display\',serif; font-size:1.1rem; color:#C9A84C; margin-bottom:1rem;">Legal & Country Details</div>', unsafe_allow_html=True)

        c10, c11, c12 = st.columns(3)
        with c10:
            nationality = st.text_input("Country of Nationality", prev.get("nationality", ""))
            birth_country = st.text_input("Country of Birth", prev.get("birth_country", ""))
        with c11:
            current_location = st.text_input("Country of Residence", prev.get("current_residence", ""))
            current_us_status = st.text_input("Current U.S. Status (or N/A)", prev.get("current_us_status", ""))
        with c12:
            previous_denials = st.radio(
                "Previous U.S. Visa Denial?",
                ["No", "Yes"],
                index=1 if prev.get("previous_visa_denials") == "Yes" else 0,
                horizontal=True,
            )
            criminal_history = st.radio(
                "Criminal History?",
                ["No", "Yes"],
                index=1 if prev.get("criminal_history") == "Yes" else 0,
                horizontal=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("💾  Save Profile", use_container_width=True)

        if submitted:
            profile_data = {
                "Full Name": full_name, "Language Proficiency": language_proficiency,
                "Highest Degree": highest_degree, "Field of Study": field_of_study,
                "Country of Nationality": nationality, "Country of Birth": birth_country,
                "Country of Residence": current_location, "Current U.S. Status": current_us_status,
                "Sponsorship Status": sponsorship_status,
            }
            missing = [
                k for k, v in profile_data.items()
                if (isinstance(v, str) and not v.strip()) or
                   (isinstance(v, list) and not v) or
                   v in ("Select...", None)
            ]
            if missing:
                st.error("Please complete all fields:\n\n" + "\n".join(f"• {f}" for f in missing))
            else:
                st.session_state.user_profile = {
                    "full_name": full_name, "age": age,
                    "language_proficiency": language_proficiency,
                    "highest_degree": highest_degree, "field_of_study": field_of_study,
                    "years_of_experience": years_of_experience,
                    "annual_income_usd": annual_income, "liquid_assets_usd": liquid_assets,
                    "sponsorship_status": sponsorship_status,
                    "nationality": nationality, "birth_country": birth_country,
                    "previous_visa_denials": previous_denials,
                    "current_residence": current_location,
                    "current_us_status": current_us_status,
                    "criminal_history": criminal_history,
                }
                st.success("✓ Profile saved successfully!")
                st.session_state.profile_just_saved = True

    # ── Post-save CTA — must live outside the form to allow on_click callback ──
    if st.session_state.get("profile_just_saved"):
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        st.button("◉  Run Assessment →", on_click=nav, args=("assessment",), use_container_width=False, key="post_save_cta")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.user_profile:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Playfair Display\',serif; font-size:1rem; color:#E8E4D9; margin-bottom:0.8rem;">Saved Profile</div>', unsafe_allow_html=True)
        with st.expander("View raw profile JSON"):
            st.json(st.session_state.user_profile)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: ASSESSMENT
# ═══════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "assessment":
    st.markdown("""
    <div style="padding-bottom:1.5rem;">
      <div style="font-size:0.72rem; color:#C9A84C; letter-spacing:0.12em; text-transform:uppercase;">AI Analysis</div>
      <div style="font-family:'Playfair Display',serif; font-size:2.2rem; color:#E8E4D9; margin-top:4px;">Visa Assessment</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.user_profile:
        st.warning("⚠️ Please complete and save your profile before running an assessment.")
        st.button("Go to My Profile →", on_click=nav, args=("profile",))
        st.stop()

    # ── Report display (post-analysis) ────────────────────────────────
    if st.session_state.final_report is not None:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:1rem; margin-bottom:1.5rem;">
          <div style="font-size:0.72rem; color:#22C55E; letter-spacing:0.1em; text-transform:uppercase; 
               background:#0A1E14; border:1px solid #1A4028; border-radius:999px; padding:0.3rem 1rem;">
            ✓ Analysis Complete
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.markdown(st.session_state.final_report)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            st.button("◉  Start New Assessment", on_click=nav, args=("assessment",), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c_right:
            pdf_bytes = markdown_to_pdf(st.session_state.final_report)
            
            st.download_button("⬇ Download Report (.pdf)", data=pdf_bytes,
                   file_name="Advena_report.pdf", mime="application/pdf",
                use_container_width=True,
            )
        st.stop()

    # ── Visa selection ────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Playfair Display\',serif; font-size:1.1rem; color:#C9A84C; margin-bottom:1rem;">Select Your Visa Category</div>', unsafe_allow_html=True)

    col_goal, col_visa = st.columns(2)
    with col_goal:
        selected_goal = st.selectbox("Primary Immigration Goal", list(GOAL_TO_VISA_MAPPING.keys()))
    with col_visa:
        if selected_goal != "Select a Goal...":
            possible_visas = GOAL_TO_VISA_MAPPING[selected_goal]
            selected_visa = st.selectbox("Visa Category", possible_visas)
        else:
            selected_visa = None
            st.selectbox("Visa Category", ["—"], disabled=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if selected_visa:
        description = VISA_DESCRIPTIONS.get(selected_visa, "")
        st.markdown(f"""
        <div class="card" style="border-color:#2563EB33;">
          <div style="font-size:0.7rem; color:#2563EB; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.5rem;">
            {selected_visa} — About This Visa
          </div>
          <div style="font-size:0.88rem; color:#8A9BBE; line-height:1.65;">{description}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Assessment questions form ──────────────────────────────────
        questions = ASSESSMENT_QUESTIONS.get(
            selected_visa,
            [f"Please describe your qualifications and plans for the {selected_visa} visa."]
        )

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Playfair Display\',serif; font-size:1.1rem; color:#C9A84C; margin-bottom:1rem;">Assessment Questions</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.82rem; color:#5A6A86; margin-bottom:1.2rem;">Answer each question with as much detail as possible for the most accurate analysis.</div>', unsafe_allow_html=True)

        with st.form("assessment_form"):
            assessment_answers = {}
            for i, q in enumerate(questions, 1):
                st.markdown(f'<div style="font-size:0.8rem; color:#C9A84C; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:0.3rem; margin-top:{"0" if i==1 else "1rem"}">Question {i}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:0.9rem; color:#E8E4D9; margin-bottom:0.5rem;">{q}</div>', unsafe_allow_html=True)
                assessment_answers[q] = st.text_area(
                    label=f"q{i}",
                    placeholder="Your answer here...",
                    key=f"qa_{i}",
                    height=120,
                    label_visibility="collapsed",
                )

            st.markdown("<br>", unsafe_allow_html=True)
            run_assessment = st.form_submit_button(
                "🚀  Launch AI Analysis",
                use_container_width=True,
            )

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Run the workflow ──────────────────────────────────────────
        if run_assessment:
            unanswered = [q for q, a in assessment_answers.items() if not a.strip()]
            if unanswered:
                st.warning(f"Please answer all {len(unanswered)} remaining question(s) before proceeding.")
                st.stop()

            # Pipeline progress display
            st.markdown("""
            <div style="font-family:'Playfair Display',serif; font-size:1.1rem; color:#E8E4D9; margin:1.5rem 0 1rem 0;">
              Analysis in Progress
            </div>
            """, unsafe_allow_html=True)



            profile_details = "\n".join(
                f"- {k.replace('_', ' ').title()}: {v}"
                for k, v in st.session_state.user_profile.items()
            )
            answer_details = "\n".join(
                f"- Question: {q}\n  Answer: {a}"
                for q, a in assessment_answers.items()
            )
            user_query = (
                f"## Applicant Profile:\n{profile_details}\n\n"
                f"## Assessment for Visa: {selected_visa}\n{answer_details}\n\n"
                f"## Task:\nAssess this applicant's eligibility for the {selected_visa} visa."
            )
            try:
                # ── Phase 1: Steps 1-4 — blocking with live status ────────
                with st.status("🔍 Running analysis...", expanded=True) as status_box:
                    pipeline_data = run_pipeline_steps(
                        agents=agents,
                        user_query=user_query,
                        visa_category=selected_visa,
                        cache=st.session_state,
                        status=status_box,
                    )
                    status_box.update(
                        label="✓ Research & scoring complete — generating report...",
                        state="running",
                    )

                # ── Phase 2: Step 5 — stream report live ──────────────────
                st.markdown("""
                <div style="font-family:'Playfair Display',serif; font-size:1.4rem;
                     color:#E8E4D9; margin:1.5rem 0 1rem 0;">
                  Your AdvenaReport
                </div>""", unsafe_allow_html=True)

                report_buffer = []

                def _report_stream():
                    for chunk in stream_report(agents=agents, pipeline_data=pipeline_data):
                        report_buffer.append(chunk)
                        yield chunk

                # st.write_stream() renders tokens live as they arrive
                st.write_stream(_report_stream())

                status_box.update(label="✓ Analysis complete", state="complete")
                st.session_state.final_report = "".join(report_buffer)
                st.rerun()

            except Exception as e:
                import traceback
                st.error(f"Analysis failed: {e}")
                st.code(traceback.format_exc(), language="python")