import os
import re
import torch
import logging
from pathlib import Path
from huggingface_hub import snapshot_download, login
from transformers import AutoTokenizer, AutoModelForCausalLM
from docx import Document
from backend.services.pdf_parser import extract_text_from_pdf
from dotenv import load_dotenv
load_dotenv()


class JobAnalysisService:

    def __init__(self):
        # Model directory and repo name
        self.model_dir = Path("models/Qwen2.5-Coder-7B-Instruct")
        self.model_repo = "Qwen/Qwen2.5-Coder-7B-Instruct"

        # Model & Tokenizer
        self.tokenizer = None
        self.model = None

        # Role and Task Descriptions (Prompt)
        self.role_description = """
You are an expert ATS resume optimization assistant and interview coach.
You specialize in tailoring technical and non-technical resumes to job descriptions,
and preparing candidates with realistic interview questions and strong answers.
Your tone is clear, professional, and encouraging.
"""

        self.task_description = """
Analyze the Job Description (JD) and the candidate's Resume.

Your output must be a clean HUMAN-READABLE report (NO JSON, NO code) with
the following sections in this exact order and headings:

### Key Skills Required by Job Description:
- List the most important technical skills, tools, domains, responsibilities, and soft skills
  that the JD emphasizes.

### Skills Found in the Resume:
- List the main skills, tools, domains, responsibilities, and strengths found in the resume
  that are relevant to the JD.

### Missing or Weak Skills:
- List important JD skills that are missing from the resume OR only mentioned weakly.

### Recommended Resume Additions:
- Bullet list of concrete suggestions of what to add, emphasize, reorder, or quantify
  in the resume so it better matches the JD.

### New Bullet Points to Strengthen the Resume:
- 4–8 new resume bullet points written in a concise, impact-focused style.
- Whenever possible, use STAR (Situation, Task, Action, Result) and include metrics
  like percentages, time saved, improvements, etc.
- These bullets should be realistic based on the resume, not fake experience.

### Recruiter Cold Email:
- A 120–180 word professional email to a recruiter or hiring manager.
- It should reference the role, show alignment with the JD, and highlight 2–3 key strengths.

### LinkedIn Outreach Message:
- A short 2–4 sentence LinkedIn message suitable for sending to a recruiter or hiring manager.

### Resume Score Breakdown (/100):
- Skill Match: X/100
- Experience Alignment: X/100
- Impact & Metrics: X/100
- ATS Keyword Coverage: X/100
- Overall Score: X/100
After the score breakdown, add 2–4 sentences explaining why the resume scored that way.

### Interview Preparation Q&A:
- Technical / Role-Specific Questions + strong sample answers (3–6).
- Behavioral STAR Questions + sample STAR answers (2–4).
- Resume-Based Deep-Dive Questions (what interviewers may ask based on this resume).
- Challenge / Problem-Solving Questions + sample answers (2–3).
- 3–5 smart questions the candidate should ask the interviewer.

Rules:
- Use bullet points where helpful.
- Be specific and practical, not generic.
- Only use experience that is plausible given the resume; do NOT invent wild new projects.
- Do NOT output JSON or any machine-readable format; only human-readable text.
"""

    # ---------------------------------------------------
    # CELL 3 — Download model if missing
    # ---------------------------------------------------
    def ensure_model_downloaded(self):
        try:
            hf_token = os.getenv("HUGGINGFACE_TOKEN")
            if not hf_token:
                return {"status": "error", "message": "Missing HuggingFace token."}

            login(token=hf_token, add_to_git_credential=False)

            if not self.model_dir.exists() or len(os.listdir(self.model_dir)) == 0:
                print("⏳ Downloading model for first time...")
                self.model_dir.mkdir(parents=True, exist_ok=True)

                snapshot_download(
                    repo_id=self.model_repo,
                    local_dir=str(self.model_dir),
                    local_dir_use_symlinks=False,
                )

            return {"status": "success"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------------------------------------------------
    # CELL 4 — Load tokenizer & model
    # ---------------------------------------------------
    def load_model(self):
        try:
            if self.model and self.tokenizer:
                return {"status": "success"}

            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_dir,
                trust_remote_code=True,
                use_fast=False,
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_dir,
                trust_remote_code=True,
                device_map="auto",
                torch_dtype=torch_dtype,
            )

            self.model.eval()
            return {"status": "success"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------------------------------------------------
    # CHAT (from Cell 4)
    # ---------------------------------------------------
    def chat(self, system_prompt, user_prompt, max_tokens=1800, temperature=0.2):
        try:
            if not self.model or not self.tokenizer:
                load_status = self.load_model()
                if load_status["status"] == "error":
                    return load_status

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            inputs = self.tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to(self.model.device)

            with torch.no_grad():
                output_ids = self.model.generate(
                    inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

            response = self.tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
            return {"status": "success", "response": response}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------------------------------------------------
    # CELL 5 — Normalize text & prepare inputs
    # ---------------------------------------------------
    def normalize_text(self, text: str) -> str:
        try:
            text = text.replace("\u00a0", " ").replace("\x0c", " ")
            text = re.sub(r"[^\S\r\n]+", " ", text)
            text = re.sub(r"\s+\n", "\n", text)
            text = re.sub(r"\n\s+", "\n", text)
            return text.strip()
        except:
            return text

    def prepare_inputs(self, resume_file_path, job_description):
        try:
            resume_text = extract_text_from_pdf(resume_file_path)
            resume_text = self.normalize_text(resume_text)
            job_text = self.normalize_text(job_description)

            return {
                "status": "success",
                "resume_text": resume_text,
                "job_description": job_text
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------------------------------------------------
    # CELL 7 — Generate Full AI Report
    # ---------------------------------------------------
    def generate_full_resume_report(self, jd_text: str, resume_text: str):
        try:
            user_prompt = (
                self.task_description
                + "\n\n=== JOB DESCRIPTION ===\n"
                + jd_text
                + "\n\n=== RESUME ===\n"
                + resume_text
                + "\n\nGenerate the full report now. Return ONLY the report text."
            )

            return self.chat(
                system_prompt=self.role_description,
                user_prompt=user_prompt,
                max_tokens=1800,
                temperature=0.15
            )

        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------------------------------------------------
    # CELL 8 — Save report (txt, md, docx)
    # ---------------------------------------------------
    def save_report(self, report_text: str, filename: str, filetype: str):
        try:
            save_dir = Path("generated_reports")
            save_dir.mkdir(parents=True, exist_ok=True)
            filepath = save_dir / f"{filename}.{filetype}"

            if filetype.lower() in ["txt", "md"]:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(report_text)

            elif filetype.lower() == "docx":
                doc = Document()
                for line in report_text.split("\n"):
                    doc.add_paragraph(line)
                doc.save(filepath)

            else:
                return {"status": "error", "message": "Unsupported format"}

            return {"status": "success", "filepath": str(filepath)}

        except Exception as e:
            return {"status": "error", "message": str(e)}
    # ---------------------------------------------------
    # CELL — Split report into two parts
    # ---------------------------------------------------
    def split_report(self, report_text: str):
        try:
            SEPARATOR = "Generate the full report now. Return ONLY the report text."

            if SEPARATOR in report_text:
                part_before, part_after = report_text.split(SEPARATOR, 1)
            else:
                # If separator not found, still return whole text in part_before
                part_before = report_text
                part_after = ""

            return {
                "status": "success",
                "before": part_before.strip(),
                "after": part_after.strip()
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------------------------------------------------
    # MAIN PIPELINE (Entire Notebook Combined)
    # ---------------------------------------------------
    def analyze_f(self, resume_file_path: str, job_description: str):
        try:
            # 1. Download model if needed
            logging.info("[analyze_f] - In to service method - Started analyzing")
            download_status = self.ensure_model_downloaded()
            if download_status["status"] == "error":
                return download_status

            # 2. Load model into memory
            load_status = self.load_model()
            if load_status["status"] == "error":
                return load_status

            # 3. Extract + clean inputs
            inputs = self.prepare_inputs(resume_file_path, job_description)
            if inputs["status"] == "error":
                return inputs

            # 4. Generate the full report
            logging.info("[analyze_f] - Generating resume report")
            report = self.generate_full_resume_report(
                jd_text=inputs["job_description"],
                resume_text=inputs["resume_text"]
            )
            logging.info("[analyze_f] - Generated resume report, Status - "+report["status"])
            if report["status"] == "error":
                return report

            full_report = report["response"]

            logging.info("[analyze_f] - Creating files")

            # 5. Split into before/after sections
            split = self.split_report(full_report)
            if split["status"] == "error":
                return split

            before_text = split["before"]
            after_text = split["after"]

            # 6. Save the DOCX files into generated_reports/
            before_docx = self.save_report(before_text, "report_before_separator", "docx")
            after_docx = self.save_report(after_text, "report_after_separator", "docx")
            after_md = self.save_report(after_text, "report_after_separator", "md")

            # --- FIX: return only filenames, not full paths ---
            before_filename = os.path.basename(before_docx.get("filepath"))
            after_filename = os.path.basename(after_docx.get("filepath"))
            after_md_filename = os.path.basename(after_md.get("filepath"))
            logging.info("[analyze_f] - Done creating files and report")

            return {
                "status": "success",
                "full_report": full_report,
                "before_part": before_text,
                "after_part": after_text,
                "downloads": {
                    "before_docx": before_filename,
                    "after_docx": after_filename,
                    "after_md":after_md_filename,
                }
            }

        except Exception as e:
            logging.exception("[analyze_f] - Error!!, "+str(e))
            return {"status": "error", "message": str(e)}

