import React, { useEffect, useState } from "react";
import "../styles/tailwind.css";
import ReportCard from "../components/ReportCard.jsx";
import Loader from "../components/loader.jsx";
import { api } from "../services/api.js";

export default function App() {
  const [jd, setJd] = useState(""); // job description from content script
  const [resumeFile, setResumeFile] = useState(null);
  const [report, setReport] = useState(null); // structured JSON from backend
  const [pdfUrl, setPdfUrl] = useState(null); // blob URL for viewing/downloading
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Pull JD from content script via chrome.tabs
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
        if (response && response.jd) setJd(response.jd.trim());
      } catch {
        // content script may not be injected on non-LinkedIn pages
      }
    })();
  }, []);

  async function handleAnalyze(e) {
    e.preventDefault();
    setError("");
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
      const { data, pdfBlob } = await api.analyzeJob({ jd, resumeFile });
      setReport(data);
      if (pdfBlob) {
        const url = URL.createObjectURL(pdfBlob);
        setPdfUrl(url);
      }
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">JobAI — Everything You Need</h1>

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
          {loading ? "Analyzing…" : "Analyze & Generate Report"}
        </button>
      </form>

      {error && <p className="text-red-600 text-sm">{error}</p>}
      {loading && <Loader label="Generating personalized report…" />}

      {report && (
        <ReportCard
          ats={report.ats_feedback}
          keywords={report.keywords}
          starBullets={report.star_bullets}
          outreach={report.outreach}
          interview={report.interview}
          pdfUrl={pdfUrl}
        />
      )}
    </div>
  );
}
