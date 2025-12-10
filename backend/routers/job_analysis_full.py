# backend-api/routers/job_analysis_full.py

from fastapi import APIRouter, UploadFile, File, Form
from backend.services.job_analysis_service import JobAnalysisService
import os
import logging
from fastapi.responses import FileResponse

router = APIRouter()
service = JobAnalysisService()

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
REPORT_DIR = os.path.join(PROJECT_ROOT, "generated_reports")



@router.post("/analyze-full")
async def analyze_full_report(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    YOUR separate API endpoint.
    Runs the FULL resume optimization + interview prep pipeline.
    Produces full report + downloadable .txt / .md / .docx files.
    """

    temp_path = f"temp_{resume.filename}"

    try:
        # Save uploaded resume temporarily
        with open(temp_path, "wb") as f:
            f.write(await resume.read())

        # Run your full pipeline
        logging.info("[analyze_full_report] - Started analyzing")
        result = service.analyze_f(temp_path, job_description)
        logging.info("[analyze_full_report] - Done! analyzing")

        return result

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/downloads/{filename}")
def download_file(filename: str):
    BASE_REPORT_DIR = "/home/922466607/jobAI/JobAI/generated_reports"

    file_path = os.path.join(BASE_REPORT_DIR, filename)

    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    return FileResponse(file_path, filename=filename)




@router.get("/test-model")
async def test_model(
    prompt: str = "Say hello professionally."
):
    """
    Simple endpoint to test:
     - HuggingFace token
     - Model download
     - Model loading
     - chat() generation

    Does NOT require a resume or job description.
    """

    # Step 1: Ensure model is downloaded
    download_status = service.ensure_model_downloaded()
    if download_status["status"] == "error":
        return download_status

    # Step 2: Load model
    load_status = service.load_model()
    if load_status["status"] == "error":
        return load_status

    # Step 3: Run a small test prompt
    response = service.chat(
        system_prompt="You are a helpful AI assistant.",
        user_prompt=prompt,
        max_tokens=150,
        temperature=0.3
    )

    return response
