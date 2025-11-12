# backend-api/main.py
from fastapi import FastAPI
from routers.job_analysis import router as job_router

app = FastAPI(
    title="JobAI Backend API",
    description="Backend for AI-powered resume & job description analysis",
    version="1.0.0",
)

# Include router
app.include_router(job_router, prefix="/api", tags=["Job Analysis"])

@app.get("/")
def home():
    return {"message": "JobAI Backend is running 🚀"}
