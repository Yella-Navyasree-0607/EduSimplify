/* ═══════════════════════════════════════════════════════════════
   EduSimplify – Client-Side JavaScript
   ═══════════════════════════════════════════════════════════════ */

"use strict";

// ─── State ────────────────────────────────────────────────────────────────
let selectedLevel = "Beginner";

// ─── Sample Texts ─────────────────────────────────────────────────────────
const SAMPLES = {
  physics: `Newton's three laws of motion form the foundation of classical mechanics.
The first law, known as the law of inertia, states that an object at rest remains at rest,
and an object in motion continues in motion at a constant velocity unless acted upon by a
net external force. The second law establishes the relationship between force, mass, and
acceleration: F = ma, meaning that the net force on an object equals its mass multiplied
by its acceleration. The third law states that for every action there is an equal and
opposite reaction. These laws explain phenomena ranging from planetary orbits to the
motion of vehicles and are essential to understanding classical physics.`,

  cs: `An operating system (OS) is system software that manages computer hardware and software
resources and provides common services for computer programs. Key components include the
kernel, which is the core program that has complete control over the system; the process
scheduler, which determines the order in which processes access the CPU using algorithms
such as Round Robin, First-Come-First-Served, and Shortest Job First; memory management,
which handles the allocation and de-allocation of memory spaces; and the file system, which
organises data on storage devices. Modern operating systems also provide virtual memory
using paging and segmentation techniques, allowing programs to use more memory than
physically available.`,

  biology: `Deoxyribonucleic acid (DNA) is a molecule composed of two polynucleotide chains that
coil around each other to form a double helix. Each nucleotide consists of a deoxyribose
sugar, a phosphate group, and one of four nitrogenous bases: adenine (A), thymine (T),
guanine (G), and cytosine (C). The bases pair specifically — A with T and G with C —
held together by hydrogen bonds. This complementary base pairing is the key to DNA
replication and gene expression. During replication, the double helix unwinds and each
strand serves as a template for a new strand, ensuring genetic information is faithfully
copied and passed to daughter cells. Mutations, or changes in the DNA sequence, can alter
protein synthesis and may lead to genetic disorders or cancer.`
};

// ─── Initialise ───────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  checkStatus();
  setupLevelButtons();
});

function setupLevelButtons() {
  document.querySelectorAll(".level-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".level-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedLevel = btn.dataset.level;
      document.getElementById("selectedLevel").value = selectedLevel;
    });
  });
}

// ─── Status Check ─────────────────────────────────────────────────────────
async function checkStatus() {
  const badge    = document.getElementById("statusBadge");
  const badgeTxt = document.getElementById("statusText");
  const demoBanner = document.getElementById("demoBanner");
  try {
    const res  = await fetch("/api/status");
    const data = await res.json();
    if (data.credentials_configured) {
      badge.className      = "status-badge status-ok";
      badgeTxt.textContent = "IBM Granite: Live";
      if (demoBanner) demoBanner.classList.add("hidden");
    } else if (data.demo_mode) {
      badge.className      = "status-badge status-demo";
      badgeTxt.textContent = "Demo Mode Active";
      if (demoBanner) demoBanner.classList.remove("hidden");
    } else {
      badge.className      = "status-badge status-error";
      badgeTxt.textContent = "Credentials Not Set";
      if (demoBanner) demoBanner.classList.add("hidden");
    }
  } catch (_) {
    badge.className      = "status-badge status-error";
    badgeTxt.textContent = "Server Offline";
  }
}

// ─── Load Sample ──────────────────────────────────────────────────────────
function loadSample(key) {
  const ta = document.getElementById("academicContent");
  ta.value = SAMPLES[key] || "";
  ta.focus();
}

// ─── Tab Switching ─────────────────────────────────────────────────────────
function switchTab(name) {
  // Hide all panels
  document.querySelectorAll(".tab-panel").forEach(p => p.classList.add("hidden"));
  // Show target panel
  const panel = document.getElementById("tab-" + name);
  if (panel) panel.classList.remove("hidden");

  // Activate matching button by index
  const tabMap = { explanation: 0, concepts: 1, examples: 2, exam: 3, review: 4 };
  const idx = tabMap[name];
  const btns = document.querySelectorAll(".tab-btn");
  btns.forEach(b => b.classList.remove("active"));
  if (idx !== undefined && btns[idx]) btns[idx].classList.add("active");
}

// ─── Main Simplify Call ───────────────────────────────────────────────────
async function runSimplify() {
  const content = document.getElementById("academicContent").value.trim();
  if (!content) {
    showError("Please paste some academic content before clicking Simplify.");
    return;
  }

  const btn = document.getElementById("simplifyBtn");
  btn.disabled = true;

  hideAll();
  showProgress("Sending content to the agent pipeline…");

  try {
    const steps = [
      "Agent 1: Analyzing content domain and complexity…",
      "Agent 2: Generating simplified explanation…",
      "Agent 3: Creating real-world examples…",
      "Agent 4: Formulating exam questions…",
      "Agent 5: Running quality review…",
    ];
    let stepIdx = 0;
    const stepTimer = setInterval(() => {
      if (stepIdx < steps.length) {
        updateProgressStep(steps[stepIdx++]);
      }
    }, 800);

    const res  = await fetch("/api/simplify", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, level: selectedLevel }),
    });
    clearInterval(stepTimer);

    const data = await res.json();
    hideProgress();

    if (data.error) {
      showError(data.message || "An error occurred. Please try again.");
      return;
    }

    renderResults(data);

  } catch (err) {
    hideProgress();
    showError("Network error: " + err.message);
  } finally {
    btn.disabled = false;
  }
}

// ─── Render Results ────────────────────────────────────────────────────────
function renderResults(data) {
  // Demo mode indicator in meta bar
  const demoChip = document.getElementById("metaDemo");
  if (demoChip) {
    if (data.demo_mode) {
      demoChip.textContent = "🎭 Demo Mode";
      demoChip.classList.remove("hidden");
    } else {
      demoChip.classList.add("hidden");
    }
  }

  // Meta bar
  document.getElementById("metaDomain").textContent   = "📚 " + (data.domain || "General");
  document.getElementById("metaLevel").textContent    = "🎯 Level: " + data.level;
  document.getElementById("metaDetected").textContent = "🔍 Detected: " + (data.detected_complexity || "—");

  // ── Tab 1: Explanation ──────────────────────────────────────────────────
  document.getElementById("simpleExplanation").textContent =
    data.simple_explanation || "No explanation generated.";

  const ptsList = document.getElementById("importantPoints");
  ptsList.innerHTML = "";
  (data.important_points || []).forEach(pt => {
    const li = document.createElement("li");
    li.textContent = pt;
    ptsList.appendChild(li);
  });

  document.getElementById("shortSummary").textContent =
    data.short_summary || "No summary generated.";

  // ── Tab 2: Concepts ─────────────────────────────────────────────────────
  const conceptsGrid = document.getElementById("keyConcepts");
  conceptsGrid.innerHTML = "";
  (data.key_concepts || []).forEach(concept => {
    // Concepts may be "Name: definition" or just "Name"
    const colonIdx = concept.indexOf(":");
    const name = colonIdx > -1 ? concept.slice(0, colonIdx).trim() : concept;
    const def  = colonIdx > -1 ? concept.slice(colonIdx + 1).trim() : "";
    const card = document.createElement("div");
    card.className = "concept-card";
    card.innerHTML = `<div class="concept-name">${escHtml(name)}</div>
                      <div class="concept-def">${escHtml(def)}</div>`;
    conceptsGrid.appendChild(card);
  });

  const topicsDiv = document.getElementById("mainTopics");
  topicsDiv.innerHTML = "";
  (data.main_topics || []).forEach(topic => {
    const span = document.createElement("span");
    span.className = "tag";
    span.textContent = topic;
    topicsDiv.appendChild(span);
  });

  // ── Tab 3: Examples ──────────────────────────────────────────────────────
  const exCont = document.getElementById("examplesContainer");
  exCont.innerHTML = "";
  const examples = data.examples || [];
  if (examples.length === 0) {
    exCont.innerHTML = "<p style='color:var(--muted);font-size:14px'>No examples generated.</p>";
  } else {
    examples.forEach((ex, i) => {
      const div = document.createElement("div");
      div.className = "example-card";
      div.innerHTML = `<div class="example-num">Example ${i + 1}</div>
                       <div class="example-title">${escHtml(ex.title || "")}</div>
                       <div class="example-body">${escHtml(ex.body || "")}</div>`;
      exCont.appendChild(div);
    });
  }

  // ── Tab 4: Exam Questions ─────────────────────────────────────────────────
  // MCQ
  const mcqCont = document.getElementById("mcqContainer");
  mcqCont.innerHTML = "";
  (data.exam_mcq || []).forEach((q, i) => {
    const div = document.createElement("div");
    div.className = "mcq-item";
    const correctLetter = (q.answer || "").trim().charAt(0).toUpperCase();
    const optionsHtml = (q.options || []).map(opt => {
      const letter = opt.trim().charAt(0).toUpperCase();
      const isCorrect = letter === correctLetter;
      return `<div class="mcq-option ${isCorrect ? "correct-answer" : ""}">
                ${escHtml(opt)}
              </div>`;
    }).join("");
    div.innerHTML = `<div class="mcq-question">Q${i + 1}. ${escHtml(q.question || "")}</div>
                     <div class="mcq-options">${optionsHtml}</div>
                     <div class="mcq-answer-label">✓ Answer: ${escHtml(q.answer || "")}</div>`;
    mcqCont.appendChild(div);
  });

  // Short Answer
  const saCont = document.getElementById("saContainer");
  saCont.innerHTML = "";
  (data.exam_short_answer || []).forEach((q, i) => {
    const div = document.createElement("div");
    div.className = "sa-item";
    div.innerHTML = `<div class="sa-question">Q${i + 1}. ${escHtml(q.question || "")}</div>
                     <div class="sa-hint"><span>Hint:</span> ${escHtml(q.hint || "")}</div>`;
    saCont.appendChild(div);
  });

  // Application Question
  document.getElementById("applicationQuestion").textContent =
    data.exam_application || "No application question generated.";

  // ── Tab 5: Review ──────────────────────────────────────────────────────
  const review = data.review || {};
  const scoresGrid = document.getElementById("scoresGrid");
  scoresGrid.innerHTML = "";
  const scoreItems = [
    { label: "Clarity",       value: review.clarity      },
    { label: "Completeness",  value: review.completeness },
    { label: "Level Match",   value: review.level_match  },
    { label: "Usefulness",    value: review.usefulness   },
    { label: "Overall",       value: review.overall      },
  ];
  scoreItems.forEach(item => {
    const v   = parseInt(item.value) || 0;
    const cls = v >= 7 ? "high" : v >= 4 ? "medium" : "low";
    const box = document.createElement("div");
    box.className = "score-box";
    box.innerHTML = `<div class="score-label">${item.label}</div>
                     <div class="score-value ${cls}">${v}<span style="font-size:14px;font-weight:400">/10</span></div>`;
    scoresGrid.appendChild(box);
  });

  document.getElementById("reviewNote").textContent      = review.review_note      || "";
  document.getElementById("improvementTip").textContent  = review.improvement_tip  || "";

  // Pipeline log
  const logList = document.getElementById("pipelineLog");
  logList.innerHTML = "";
  (data.pipeline_log || []).forEach(step => {
    const li = document.createElement("li");
    li.textContent = step;
    logList.appendChild(li);
  });

  // Show container & switch to first tab
  document.getElementById("resultsContainer").classList.remove("hidden");
  switchTab("explanation");
  document.getElementById("resultsContainer").scrollIntoView({ behavior: "smooth" });
}

// ─── UI Helpers ────────────────────────────────────────────────────────────
function showProgress(msg) {
  updateProgressStep(msg);
  document.getElementById("progressBanner").classList.remove("hidden");
}
function hideProgress() {
  document.getElementById("progressBanner").classList.add("hidden");
}
function updateProgressStep(msg) {
  document.getElementById("progressStep").textContent = msg;
}
function showError(msg) {
  const eb = document.getElementById("errorBanner");
  document.getElementById("errorMessage").textContent = msg;
  eb.classList.remove("hidden");
}
function hideAll() {
  document.getElementById("progressBanner").classList.add("hidden");
  document.getElementById("errorBanner").classList.add("hidden");
  document.getElementById("resultsContainer").classList.add("hidden");
}
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
