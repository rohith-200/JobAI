const BASE_URL = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function analyzeJob({ jd, resumeFile }) {
  const form = new FormData();
  form.append("job_description", jd);
  form.append("resume", resumeFile);

  const res = await fetch(`${BASE_URL}/api/job/analyze`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `Request failed: ${res.status}`);
  }

  // Expecting: multipart/mixed or JSON + separate PDF endpoint.
  // Here we assume JSON with a `pdf_url` OR binary PDF in a second call.
  const contentType = res.headers.get("content-type") || "";
  let data,
    pdfBlob = null;

  if (contentType.includes("application/json")) {
    data = await res.json();
    if (data?.pdf_url) {
      const pdfRes = await fetch(data.pdf_url);
      pdfBlob = await pdfRes.blob();
    }
  } else if (contentType.includes("application/pdf")) {
    pdfBlob = await res.blob();
    data = {};
  } else {
    data = await res.json().catch(() => ({}));
  }

  return { data, pdfBlob };
}

export const api = { analyzeJob };
