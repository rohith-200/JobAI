import React from "react";

export default function ReportCard({
  ats,
  keywords,
  starBullets,
  outreach,
  interview,
  pdfUrl,
}) {
  return (
    <div className="rounded-2xl border p-3 space-y-3">
      <h2 className="text-lg font-semibold">Report</h2>

      <section className="space-y-1">
        <h3 className="font-medium">ATS Feedback</h3>
        <ul className="list-disc pl-5 text-sm">
          {(ats ?? []).map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="space-y-1">
        <h3 className="font-medium">Keywords</h3>
        <div className="flex flex-wrap gap-2">
          {(keywords ?? []).map((k, i) => (
            <span key={i} className="rounded-full border px-2 py-0.5 text-xs">
              {k}
            </span>
          ))}
        </div>
      </section>

      <section className="space-y-1">
        <h3 className="font-medium">STAR Bullet Rewrites</h3>
        <ul className="list-disc pl-5 text-sm">
          {(starBullets ?? []).map((b, i) => (
            <li key={i}>{b}</li>
          ))}
        </ul>
      </section>

      <section className="space-y-1">
        <h3 className="font-medium">Outreach Drafts</h3>
        <div className="text-sm space-y-2">
          <div>
            <p className="font-medium">Email</p>
            <pre className="whitespace-pre-wrap rounded-lg border p-2">
              {outreach?.email}
            </pre>
          </div>
          <div>
            <p className="font-medium">LinkedIn Message</p>
            <pre className="whitespace-pre-wrap rounded-lg border p-2">
              {outreach?.linkedin}
            </pre>
          </div>
        </div>
      </section>

      <section className="space-y-1">
        <h3 className="font-medium">Interview Prep</h3>
        <ul className="list-disc pl-5 text-sm">
          {(interview ?? []).map((q, i) => (
            <li key={i}>{q}</li>
          ))}
        </ul>
      </section>

      {pdfUrl && (
        <div className="space-y-2">
          <a
            href={pdfUrl}
            download="JobAI-Report.pdf"
            className="inline-block rounded-xl border bg-black text-white px-3 py-1 text-sm"
          >
            Download PDF Report
          </a>
          <iframe
            src={pdfUrl}
            className="w-full h-64 border rounded-xl"
            title="Report Preview"
          />
        </div>
      )}
    </div>
  );
}
