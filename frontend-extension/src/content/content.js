// Heuristic selectors for LinkedIn job detail pages
function extractJD() {
  // Common containers on LinkedIn job pages
  const candidates = [
    '[class*="description__text"]',
    "[data-test-description] article",
    "[data-test-description] div",
    "section.jobs-description__container *",
    "div.jobs-description__content *",
    "div.show-more-less-html__markup",
  ];

  for (const sel of candidates) {
    const el = document.querySelector(sel);
    if (el && el.innerText && el.innerText.trim().length > 120) {
      return el.innerText;
    }
  }

  // Fallback: longest text block on page
  let best = "";
  document.querySelectorAll("p, div").forEach((n) => {
    const t = n.innerText?.trim();
    if (t && t.length > best.length) best = t;
  });
  return best;
}

// Respond to popup requests
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "GET_JOB_DESCRIPTION") {
    try {
      const jd = extractJD();
      sendResponse({ ok: true, jd });
    } catch (e) {
      sendResponse({ ok: false, error: e?.message || "Failed to extract JD" });
    }
    return true;
  }
});
