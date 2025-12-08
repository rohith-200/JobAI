# backend-api/routers/job_analysis_full.py

from fastapi import APIRouter, UploadFile, File, Form
from backend.services.job_analysis_service import JobAnalysisService
import os

router = APIRouter()
service = JobAnalysisService()


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
        result = service.analyze_f(temp_path, job_description)

        return result

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


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
