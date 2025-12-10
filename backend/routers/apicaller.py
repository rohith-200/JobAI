import os
import asyncio
from backend.services.job_analysis_service import JobAnalysisService

service = JobAnalysisService()

class ApiCaller:
    async def analyze_full(self, resume_path: str, job_desc_input: str):

        # --- Read job description (string or .txt file) ---
        if os.path.isfile(job_desc_input):
            with open(job_desc_input, "r", encoding="utf-8") as f:
                job_description = f.read()
        else:
            job_description = job_desc_input

        # --- Validate resume path ---
        if not os.path.exists(resume_path):
            raise FileNotFoundError(resume_path)

        # --- Simulate FastAPI's temp file behavior ---
        temp_path = f"temp_{os.path.basename(resume_path)}"
        try:
            # copy file to temp
            with open(resume_path, "rb") as src, open(temp_path, "wb") as dst:
                dst.write(src.read())

            # call actual service (sync)
            result = service.analyze_f(temp_path, job_description)
            return result

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


def main():
    caller = ApiCaller()

    async def run():
        result = await caller.analyze_full(
            resume_path="backend/routers/RohithGannoju_Resume_Up_co.pdf",
            job_desc_input="backend/routers/jd.txt"
        )
        print("Successfull - Good")
        print(result)

    asyncio.run(run())


if __name__ == "__main__":
    main()
