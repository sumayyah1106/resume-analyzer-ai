import logging
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)


class SectionFeedback(BaseModel):
    education: str = Field(default="")
    skills: str = Field(default="")
    experience: str = Field(default="")
    projects: str = Field(default="")
    summary: str = Field(default="")


class ResumeAnalysis(BaseModel):
    resume_score: int = Field(description="Score out of 100")
    overall_summary: str = Field(description="Overall resume summary")
    strengths: list[str] = Field(description="List of strengths")
    weaknesses: list[str] = Field(description="List of weaknesses")
    skills_detected: list[str] = Field(description="Detected skills")
    recommended_skills: list[str] = Field(description="Recommended skills to add")
    section_feedback: SectionFeedback = Field(description="Per-section feedback")
    improvement_suggestions: list[str] = Field(description="Actionable suggestions")


PROMPT_TEMPLATE = """
You are an expert HR consultant and career coach with 15+ years of experience reviewing resumes.

Analyze the resume below and return ONLY a valid JSON object — no markdown, no explanation, just raw JSON.

RESUME:
{resume_text}

Return this exact JSON structure:
{{
  "resume_score": <integer 0-100>,
  "overall_summary": "<2-3 sentence summary>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>"],
  "skills_detected": ["<skill 1>", "<skill 2>"],
  "recommended_skills": ["<skill 1>", "<skill 2>"],
  "section_feedback": {{
    "education": "<feedback>",
    "skills": "<feedback>",
    "experience": "<feedback>",
    "projects": "<feedback>",
    "summary": "<feedback>"
  }},
  "improvement_suggestions": ["<suggestion 1>", "<suggestion 2>", "<suggestion 3>"]
}}

Scoring guide: 90-100 excellent | 75-89 strong | 60-74 average | 45-59 below average | <45 poor
"""


def _build_llm():
    if not GROQ_API_KEY:
        raise EnvironmentError("GROQ_API_KEY is not set in your .env file.")
    return ChatGroq(api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile", temperature=0.3)


def analyze_resume(resume_text: str) -> ResumeAnalysis:
    if not resume_text.strip():
        raise ValueError("Resume text is empty.")

    if len(resume_text) > 8000:
        resume_text = resume_text[:8000] + "\n[truncated]"

    llm = _build_llm()
    prompt = PromptTemplate(input_variables=["resume_text"], template=PROMPT_TEMPLATE)
    parser = JsonOutputParser(pydantic_object=ResumeAnalysis)
    chain = prompt | llm | parser

    result: dict = chain.invoke({"resume_text": resume_text})

    sf = result.get("section_feedback", {})
    if isinstance(sf, dict):
        result["section_feedback"] = SectionFeedback(**sf)

    return ResumeAnalysis(**result)