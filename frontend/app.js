"use strict";

const MAX_FILE_MB = 5;

const $ = (id) => document.getElementById(id);
const form = $("analyze-form");
const fileInput = $("cv-file");
const dropzone = $("dropzone");
const jobInput = $("job-description");

function showError(message) {
  $("form-error").textContent = message;
  $("form-error").hidden = !message;
}

function setFile(file) {
  $("file-label").textContent = file ? `${file.name} (${(file.size / 1024).toFixed(0)} KB)` : "Click to choose a PDF or drop it here";
  dropzone.classList.toggle("has-file", Boolean(file));
}

fileInput.addEventListener("change", () => setFile(fileInput.files[0]));
jobInput.addEventListener("input", () => { $("char-count").textContent = jobInput.value.length; });

["dragenter", "dragover"].forEach((type) =>
  dropzone.addEventListener(type, (e) => { e.preventDefault(); dropzone.classList.add("dragover"); }));
["dragleave", "drop"].forEach((type) =>
  dropzone.addEventListener(type, (e) => { e.preventDefault(); dropzone.classList.remove("dragover"); }));
dropzone.addEventListener("drop", (e) => {
  if (e.dataTransfer.files.length) {
    fileInput.files = e.dataTransfer.files;
    setFile(fileInput.files[0]);
  }
});

function validate() {
  const file = fileInput.files[0];
  if (!file) return "Please choose your CV as a PDF file.";
  if (!file.name.toLowerCase().endsWith(".pdf")) return "The CV must be a PDF file.";
  if (file.size > MAX_FILE_MB * 1024 * 1024) return `The CV must be smaller than ${MAX_FILE_MB} MB.`;
  if (jobInput.value.trim().length < 30) return "Please paste a job description (at least 30 characters).";
  return "";
}

function fillList(id, items, emptyText) {
  const list = $(id);
  list.replaceChildren();
  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.className = "empty";
    li.textContent = emptyText;
    list.append(li);
    return;
  }
  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item; // textContent, never innerHTML: content comes from user input
    list.append(li);
  }
}

function setGauge(gaugeId, labelId, value) {
  $(gaugeId).style.setProperty("--value", value ?? 0);
  $(labelId).textContent = value == null ? "N/A" : `${value}%`;
}

function render(data) {
  const match = data.skill_match;
  setGauge("skill-gauge", "skill-percent", match.match_percentage);
  $("skill-explanation").textContent = match.explanation;

  const semantic = data.semantic_similarity;
  setGauge("semantic-gauge", "semantic-percent", semantic.available ? semantic.percentage : null);
  $("semantic-note").textContent = semantic.available
    ? `Cosine similarity of text embeddings (${semantic.score}). Measures overall topic/wording overlap, not skills.`
    : semantic.message;

  fillList("matched-skills", match.matched_skills, "None detected");
  fillList("missing-skills", match.missing_skills, "Nothing missing");
  fillList("additional-skills", match.additional_skills, "None");

  $("results").hidden = false;
  $("results").scrollIntoView({ behavior: "smooth", block: "start" });
}

async function readError(response) {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") return body.detail;
  } catch { /* not JSON */ }
  return `Request failed (HTTP ${response.status}).`;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const problem = validate();
  showError(problem);
  if (problem) return;

  const body = new FormData();
  body.append("cv_file", fileInput.files[0]);
  body.append("job_description", jobInput.value);

  $("analyze-btn").disabled = true;
  $("loading").hidden = false;
  $("results").hidden = true;
  try {
    const response = await fetch("/api/analyze", { method: "POST", body });
    if (!response.ok) {
      showError(await readError(response));
      return;
    }
    render(await response.json());
  } catch {
    showError("Could not reach the server. Is it running?");
  } finally {
    $("analyze-btn").disabled = false;
    $("loading").hidden = true;
  }
});
