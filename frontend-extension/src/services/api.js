const BASE_URL = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function analyzeJob({ jd, resumeFile }) {
  const form = new FormData();
  form.append("job_description", jd);
  form.append("resume", resumeFile);

  const res = await fetch(`${BASE_URL}/jobai/analyze-full`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `Request failed: ${res.status}`);
  }

  // We ignore backend JSON since we only care about the docx file
  await res.json();

  // Always fetch resume_report.docx
  const fileUrl = `${BASE_URL}/jobai/downloads/report_after_separator.md`;

  const fileRes = await fetch(fileUrl);
  if (!fileRes.ok) {
    throw new Error("Could not download DOCX file.");
  }

  const docxBlob = await fileRes.blob();

  return { docxBlob };
}

export const api = { analyzeJob };
