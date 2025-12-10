const BASE_URL = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

async function analyzeJob({ jd, resumeFile }) {
  const form = new FormData();
  form.append("job_description", jd);
  form.append("resume", resumeFile);

  const res = await fetch(`${BASE_URL}/analyze-full`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `Request failed: ${res.status}`);
  }

  // FastAPI returns JSON ONLY.
  const data = await res.json();

  // Validate expected fields:
  if (!data.status || !data.downloads) {
    throw new Error("Invalid response from server.");
  }

  // Optional: Download DOCX file in the frontend
  let docxBlob = null;
  if (data.downloads.docx) {
    const docxRes = await fetch(`${BASE_URL}${data.downloads.docx}`);
    if (docxRes.ok) {
      docxBlob = await docxRes.blob();
    }
  }

  return {
    data,
    docxBlob, // frontend can download/save this
  };
}

export const api = { analyzeJob };
