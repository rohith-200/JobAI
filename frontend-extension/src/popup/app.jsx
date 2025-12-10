import React, { useEffect, useState } from "react";
import "../styles/tailwind.css";
import Loader from "../components/loader.jsx";
import { api } from "../services/api.js";

export default function App() {
  const [jd, setJd] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [docxUrl, setDocxUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Auto-extract JD from content script
  useEffect(() => {
    (async () => {
      try {
        const [tab] = await chrome.tabs.query({
          active: true,
          currentWindow: true,
        });
        const response = await chrome.tabs.sendMessage(tab.id, {
          type: "GET_JOB_DESCRIPTION",
        });
        if (response?.jd) setJd(response.jd.trim());
      } catch {}
    })();
  }, []);

  async function handleAnalyze(e) {
    e.preventDefault();
    setError("");
    setDocxUrl(null);

    if (!jd) {
      setError("No job description found.");
      return;
    }
    if (!resumeFile) {
      setError("Please upload your resume.");
      return;
    }

    try {
      setLoading(true);
      const { docxBlob } = await api.analyzeJob({ jd, resumeFile });

      if (docxBlob) {
        const url = URL.createObjectURL(docxBlob);
        setDocxUrl(url);
      } else {
        setError("No DOCX report returned from API.");
      }
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">JobAI Resume Analyzer</h1>

      <form onSubmit={handleAnalyze} className="space-y-3">
        <div>
          <label className="text-sm font-medium">Job Description</label>
          <textarea
            className="mt-1 w-full h-28 rounded-lg border p-2 text-sm"
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            placeholder="Paste or auto-extracted from LinkedIn…"
          />
        </div>

        <div>
          <label className="text-sm font-medium">Resume (PDF/DOCX)</label>
          <input
            className="mt-1 block w-full text-sm"
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={(e) => setResumeFile(e.target.files?.[0] ?? null)}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl border bg-black text-white py-2 text-sm disabled:opacity-60"
        >
          {loading ? "Processing…" : "Generate Report"}
        </button>
      </form>

      {error && <p className="text-red-600 text-sm">{error}</p>}
      {loading && <Loader label="Generating report…" />}

      {docxUrl && (
        <a
          href={docxUrl}
          download="Resume Report"
          className="block text-center rounded-xl border bg-green-600 text-white px-3 py-2 text-sm"
        >
          Download Resume Report
        </a>
      )}
    </div>
  );
}
