# backend-api/services/model_inference.py
from prompt_engine.prompt_engine import generate_output  # from Jaideep's module

def run_inference(resume_text: str, job_description: str):
    """
    Calls Jaideep's prompt engine to generate AI insights.
    """
    resume_analysis = generate_output("resume_prompts", resume_text, job_description)
    outreach_draft = generate_output("outreach_prompts", resume_text, job_description)
    interview_pack = generate_output("interview_prompts", resume_text, job_description)

    return {
        "resume_analysis": resume_analysis,
        "outreach_draft": outreach_draft,
        "interview_pack": interview_pack
    }
