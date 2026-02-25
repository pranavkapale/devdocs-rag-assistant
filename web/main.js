// web/main.js
const API_BASE = "http://localhost:8000";

document.getElementById("ask-btn").addEventListener("click", async () => {
  const question = document.getElementById("question").value;
  const answerEl = document.getElementById("answer");
  const sourcesEl = document.getElementById("sources");
  answerEl.textContent = "Loading...";
  sourcesEl.textContent = "";

  try {
    const resp = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await resp.json();
    if (!resp.ok) {
      answerEl.textContent = `Error: ${data.detail}`;
      return;
    }
    answerEl.textContent = data.answer;
    sourcesEl.textContent = "Sources:\n" + data.sources.map(
      (s) => `- ${s.source} (chunk ${s.chunk_id})`
    ).join("\n");
  } catch (err) {
    answerEl.textContent = `Request failed: ${err}`;
  }
});
