import os
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FILE_ENDPOINT = f"{BACKEND_URL}/analyze-resume"
TEXT_ENDPOINT = f"{BACKEND_URL}/analyze-text"

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #0f172a; }
.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.section-title {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.6rem;
}
.chip {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 3px;
}
.chip-blue   { background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid rgba(59,130,246,0.3); }
.chip-orange { background: rgba(245,158,11,0.15);  color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
.bullet { display: flex; gap: 8px; color: #cbd5e1; font-size: 0.9rem; margin: 5px 0; line-height: 1.5; }
h1, h2, h3 { color: #f1f5f9 !important; }
p, li { color: #94a3b8; }
[data-testid="stFileUploaderDropzone"] {
    background: rgba(59,130,246,0.05) !important;
    border: 2px dashed rgba(59,130,246,0.35) !important;
    border-radius: 10px !important;
}
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.6rem 1.5rem;
}
.stProgress > div > div > div { background: linear-gradient(90deg,#3b82f6,#6366f1) !important; }
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] { border-radius: 8px; color: #64748b; font-weight: 500; }
.stTabs [aria-selected="true"] { background: rgba(59,130,246,0.2) !important; color: #60a5fa !important; }
textarea {
    background: rgba(255,255,255,0.05) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def score_color(score):
    if score >= 85: return "#22c55e"
    if score >= 70: return "#3b82f6"
    if score >= 50: return "#f59e0b"
    return "#ef4444"


def score_label(score):
    if score >= 85: return "Excellent"
    if score >= 70: return "Good"
    if score >= 50: return "Average"
    return "Needs Work"


def chips(items, cls):
    return "".join(f'<span class="chip {cls}">{i}</span>' for i in items)


def bullets(items):
    return "".join(
        f'<div class="bullet"><span>—</span><span>{i}</span></div>'
        for i in items
    )


# ── Render result ─────────────────────────────────────────────────────────────

def render_analysis(data):
    score = data.get("resume_score", 0)

    col1, col2 = st.columns([1, 2])
    with col1:
        color = score_color(score)
        st.markdown(f"""
        <div class="card" style="text-align:center; padding:2rem 1rem;">
            <div style="font-size:3rem; font-weight:700; color:{color};">{score}</div>
            <div style="color:#64748b; font-size:0.75rem; text-transform:uppercase; letter-spacing:.08em;">out of 100</div>
            <div style="font-size:1.1rem; font-weight:600; color:{color}; margin-top:4px;">{score_label(score)}</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(score / 100)

    with col2:
        st.markdown(f"""
        <div class="card">
            <div class="section-title">Overall Summary</div>
            <p style="color:#cbd5e1; font-size:0.9rem; line-height:1.7; margin:0;">
                {data.get("overall_summary", "")}
            </p>
        </div>
        """, unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""
        <div class="card">
            <div class="section-title">Strengths</div>
            {bullets(data.get("strengths", []))}
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="card">
            <div class="section-title">Weaknesses</div>
            {bullets(data.get("weaknesses", []))}
        </div>
        """, unsafe_allow_html=True)

    col5, col6 = st.columns(2)
    with col5:
        st.markdown(f"""
        <div class="card">
            <div class="section-title">Skills Detected</div>
            <div>{chips(data.get("skills_detected", []), "chip-blue")}</div>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
        <div class="card">
            <div class="section-title">Recommended Skills</div>
            <div>{chips(data.get("recommended_skills", []), "chip-orange")}</div>
        </div>
        """, unsafe_allow_html=True)

    sf = data.get("section_feedback", {})
    if isinstance(sf, dict):
        rows = "".join(
            f'<div style="margin-bottom:10px;">'
            f'<span style="font-weight:600;color:#94a3b8;">{k.title()}:</span>'
            f'<span style="color:#cbd5e1; font-size:0.88rem;"> {v}</span></div>'
            for k, v in sf.items() if v
        )
        st.markdown(
            f'<div class="card"><div class="section-title">Section Feedback</div>{rows}</div>',
            unsafe_allow_html=True
        )

    suggestions = data.get("improvement_suggestions", [])
    if suggestions:
        numbered = "".join(
            f'<div class="bullet">'
            f'<span style="color:#6366f1;font-weight:700;">{i}.</span>'
            f'<span>{s}</span></div>'
            for i, s in enumerate(suggestions, 1)
        )
        st.markdown(
            f'<div class="card"><div class="section-title">Improvement Suggestions</div>{numbered}</div>',
            unsafe_allow_html=True
        )

    with st.expander("View Raw JSON Response"):
        st.json(data)


def call_api(endpoint: str, payload: dict):
    try:
        resp = requests.post(endpoint, timeout=120, **payload)
        if resp.status_code == 200:
            st.success("Analysis complete!")
            st.markdown("---")
            render_analysis(resp.json())
        else:
            st.error(f"Backend error {resp.status_code}: {resp.json().get('detail', resp.text)}")
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot connect to backend at {BACKEND_URL}. Is the FastAPI server running?")
    except requests.exceptions.Timeout:
        st.error("Request timed out. Try again.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")


# ── Page header ───────────────────────────────────────────────────────────────

st.markdown("""
<div style="text-align:center; padding:2rem 0 1.5rem;">
    <h1 style="font-size:2.2rem; font-weight:700;
               background:linear-gradient(135deg,#60a5fa,#818cf8);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0;">
        AI Resume Analyzer
    </h1>
    <p style="color:#64748b; margin-top:6px;">
        Upload a file or paste your resume text to get instant AI-powered feedback.
    </p>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["File Upload  (PDF / DOCX / TXT)", "Paste Resume Text"])


# ── Tab 1: File upload ────────────────────────────────────────────────────────

with tab1:
    col_up, col_info = st.columns([2, 1], gap="large")

    with col_up:
        st.markdown("#### Upload Your Resume")
        uploaded = st.file_uploader(
            "PDF, DOCX, or TXT — max 10 MB",
            type=["pdf", "docx", "txt"],
        )

    with col_info:
        st.markdown("""
        <div class="card" style="margin-top:1.8rem;">
            <div class="bullet"><span>—</span><span>Score out of 100</span></div>
            <div class="bullet"><span>—</span><span>Strengths and weaknesses</span></div>
            <div class="bullet"><span>—</span><span>Skills gap analysis</span></div>
            <div class="bullet"><span>—</span><span>Section-wise feedback</span></div>
            <div class="bullet"><span>—</span><span>Actionable suggestions</span></div>
        </div>
        """, unsafe_allow_html=True)

    if uploaded:
        st.markdown(f"`{uploaded.name}` — {uploaded.size / 1024:.1f} KB")
        if st.button("Analyze Resume", key="btn_file"):
            with st.spinner("Analyzing with AI... please wait 15-30 seconds"):
                call_api(FILE_ENDPOINT, {
                    "files": {
                        "file": (
                            uploaded.name,
                            uploaded.getvalue(),
                            uploaded.type or "application/octet-stream",
                        )
                    }
                })
    else:
        st.info("Upload a PDF, DOCX, or TXT resume file to get started.")


# ── Tab 2: Paste text ─────────────────────────────────────────────────────────

with tab2:
    st.markdown("#### Paste Your Resume Text")
    st.markdown(
        "<p style='color:#64748b; font-size:0.85rem; margin-bottom:8px;'>"
        "Copy your resume from any source (Word, Google Docs, LinkedIn) and paste it below.</p>",
        unsafe_allow_html=True
    )

    pasted_text = st.text_area(
        label="Resume text",
        placeholder=(
            "Paste your full resume here...\n\n"
            "Example:\n"
            "John Doe\n"
            "johndoe@email.com | LinkedIn: linkedin.com/in/johndoe\n\n"
            "EXPERIENCE\n"
            "Software Engineer at XYZ Corp (2021-2024)\n"
            "- Built REST APIs using FastAPI and Python\n\n"
            "EDUCATION\n"
            "B.Tech Computer Science — ABC University (2021)"
        ),
        height=320,
        label_visibility="collapsed",
    )

    char_count = len(pasted_text.strip())
    if char_count > 0:
        color = "#22c55e" if char_count >= 200 else "#f59e0b"
        st.markdown(
            f"<p style='color:{color}; font-size:0.8rem;'>{char_count} characters pasted</p>",
            unsafe_allow_html=True
        )

    if st.button("Analyze Resume", key="btn_text"):
        if char_count < 50:
            st.warning("Please paste more text — a resume should have at least 50 characters.")
        else:
            with st.spinner("Analyzing with AI... please wait 15-30 seconds"):
                call_api(TEXT_ENDPOINT, {"data": {"text": pasted_text}})


# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#334155; font-size:0.78rem;'>"
    "No data stored · Processed in memory · Powered by LangChain + Groq</p>",
    unsafe_allow_html=True,
)