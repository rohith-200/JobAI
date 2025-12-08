# backend-api/routers/job_analysis.py
from fastapi import APIRouter, UploadFile, File, Form
#from backend.services.pdf_parser import extract_text_from_pdf


import os

router = APIRouter()

@router.post("/analyze")
async def analyze_job(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Receives resume (PDF) and job description,
    extracts text, and runs AI model inference.
    """
    temp_path = f"temp_{resume.filename}"

    # Save uploaded file
    with open(temp_path, "wb") as f:
        f.write(await resume.read())

    # Extract resume text
    #resume_text = extract_text_from_pdf(temp_path)

    # Delete temp file after extraction
    os.remove(temp_path)

    # Run model inference
    result = "run_inference(resume_text, job_description)"

    return {"status": "success", "result": result}
