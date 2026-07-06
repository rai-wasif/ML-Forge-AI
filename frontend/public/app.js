const API_BASE = window.location.origin;

const STEPS = [
  { num: 1, label: "Project", title: "Create or Select a Project", desc: "Start by naming your ML project." },
  { num: 2, label: "Upload", title: "Upload Your Dataset", desc: "Upload a CSV, Excel, or Parquet file." },
  { num: 3, label: "Explore", title: "Explore Your Data", desc: "Run automated exploratory data analysis." },
  { num: 4, label: "Clean", title: "Clean & Fix Data", desc: "Handle missing values, duplicates, and outliers." },
  { num: 5, label: "Features", title: "Build ML Features", desc: "Encode, scale, and prepare columns for training." },
  { num: 6, label: "Train", title: "Train & Compare Models", desc: "AutoML training with multiple algorithms." },
  { num: 7, label: "Report", title: "Results & AI Report", desc: "View metrics, SHAP charts, and download reports." },
];

const state = {
  projects: [],
  selectedProject: null,
  datasets: [],
  selectedDatasetId: null,
  edaReports: {},
  cleaningReports: {},
  featureReports: {},
  trainingReports: {},
  agentResponse: null,
  knowledgeResponse: null,
  experiments: [],
  experimentComparison: null,
  view: "home",
  currentStep: 1,
  busy: false,
  targetColumn: "",
};

const workspace = document.querySelector("#workspace");
const statusText = document.querySelector("#statusText");
const topbarTitle = document.querySelector("#topbarTitle");
const topbarEyebrow = document.querySelector("#topbarEyebrow");
const toastContainer = document.querySelector("#toastContainer");

function setStatus(message, isError = false) {
  statusText.textContent = message;
  statusText.classList.toggle("error", isError);
}

function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toastContainer.append(toast);
  setTimeout(() => toast.remove(), 4000);
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    let message = "Request failed.";
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }
  if (response.status === 204) return null;
  return response.json();
}

function getActiveDataset() {
  if (state.selectedDatasetId) {
    return state.datasets.find((d) => d.id === state.selectedDatasetId) || state.datasets[0] || null;
  }
  return state.datasets[0] || null;
}

function suggestStep() {
  if (!state.selectedProject) return 1;
  const dataset = getActiveDataset();
  if (!dataset) return 2;
  if (!state.edaReports[dataset.id]) return 3;
  if (!state.cleaningReports[dataset.id]) return 4;
  if (!state.featureReports[dataset.id]) return 5;
  if (!state.trainingReports[dataset.id]) return 6;
  return 7;
}

function pipelineStages(dataset) {
  const datasetId = dataset ? dataset.id : null;
  const training = datasetId ? state.trainingReports[datasetId] : null;
  const shap = training ? (training.artifacts || {}).shap || {} : {};
  return [
    { num: 1, label: "Project", status: state.selectedProject ? "complete" : "pending" },
    { num: 2, label: "Upload", status: dataset ? "complete" : "pending" },
    { num: 3, label: "Explore", status: datasetId && state.edaReports[datasetId] ? "complete" : "pending" },
    { num: 4, label: "Clean", status: datasetId && state.cleaningReports[datasetId] ? "complete" : "pending" },
    { num: 5, label: "Features", status: datasetId && state.featureReports[datasetId] ? "complete" : "pending" },
    { num: 6, label: "Train", status: training ? "complete" : "pending" },
    { num: 7, label: "Report", status: training && training.final_report_path ? "complete" : training ? "active" : "pending" },
  ];
}

async function setView(view) {
  state.view = view;
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === view);
  });
  if (state.selectedProject && (view === "pipeline" || view === "experiments" || view === "assistant")) {
    await reloadProjectData();
  }
  if (view === "pipeline" && state.selectedProject) {
    state.currentStep = suggestStep();
  }
  render();
}

function setStep(step) {
  state.currentStep = Math.max(1, Math.min(7, step));
  render();
  document.querySelector(".wizard-content")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function updateTopbar() {
  const titles = {
    home: ["Home", "Manage Projects"],
    pipeline: ["ML Pipeline", state.selectedProject ? state.selectedProject.name : "Step-by-Step Wizard"],
    experiments: ["Experiments", "MLflow Tracking"],
    assistant: ["AI Assistant", "Automated ML Pipeline"],
    knowledge: ["Knowledge Base", "RAG Search"],
  };
  const [title, eyebrow] = titles[state.view] || titles.home;
  topbarTitle.textContent = title;
  topbarEyebrow.textContent = eyebrow;
}

async function loadProjects() {
  state.projects = await request("/projects");
}

async function loadEdaReports() {
  const entries = await Promise.all(
    state.datasets.map(async (dataset) => {
      try {
        const report = await request(`/eda/datasets/${dataset.id}/latest`);
        return [dataset.id, report];
      } catch {
        return [dataset.id, null];
      }
    }),
  );
  state.edaReports = Object.fromEntries(entries.filter((e) => e[1]));
}

async function loadCleaningReports() {
  const entries = await Promise.all(
    state.datasets.map(async (dataset) => {
      try {
        const report = await request(`/cleaning/datasets/${dataset.id}/latest`);
        return [dataset.id, report];
      } catch {
        return [dataset.id, null];
      }
    }),
  );
  state.cleaningReports = Object.fromEntries(entries.filter((e) => e[1]));
}

async function loadFeatureReports() {
  const entries = await Promise.all(
    state.datasets.map(async (dataset) => {
      try {
        const report = await request(`/features/datasets/${dataset.id}/latest`);
        return [dataset.id, report];
      } catch {
        return [dataset.id, null];
      }
    }),
  );
  state.featureReports = Object.fromEntries(entries.filter((e) => e[1]));
}

async function loadTrainingReports() {
  const entries = await Promise.all(
    state.datasets.map(async (dataset) => {
      try {
        const report = await request(`/training/datasets/${dataset.id}/latest`);
        return [dataset.id, report];
      } catch {
        return [dataset.id, null];
      }
    }),
  );
  state.trainingReports = Object.fromEntries(entries.filter((e) => e[1]));
}

async function loadExperiments() {
  if (!state.selectedProject) {
    state.experiments = [];
    return;
  }
  state.experiments = await request(`/training/projects/${state.selectedProject.id}/experiments`);
}

async function reloadProjectData() {
  if (!state.selectedProject) return;
  state.datasets = await request(`/datasets/project/${state.selectedProject.id}`);
  if (state.datasets.length && !state.selectedDatasetId) {
    state.selectedDatasetId = state.datasets[0].id;
  }
  await Promise.all([loadEdaReports(), loadCleaningReports(), loadFeatureReports(), loadTrainingReports(), loadExperiments()]);
}

async function openProject(projectId) {
  state.selectedProject = await request(`/projects/${projectId}`);
  state.selectedDatasetId = null;
  state.targetColumn = "";
  state.agentResponse = null;
  state.experimentComparison = null;
  await reloadProjectData();
  state.view = "pipeline";
  state.currentStep = suggestStep();
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === "pipeline");
  });
  render();
  showToast(`Project "${state.selectedProject.name}" opened`);
}

async function createProject(name, description) {
  const project = await request("/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description: description || null }),
  });
  await loadProjects();
  await openProject(project.id);
  showToast("Project created successfully");
}

function render() {
  updateTopbar();
  switch (state.view) {
    case "home":
      workspace.innerHTML = renderHomeView();
      bindHomeEvents();
      break;
    case "pipeline":
      workspace.innerHTML = renderPipelineView();
      bindPipelineEvents();
      break;
    case "experiments":
      workspace.innerHTML = renderExperimentsView();
      bindExperimentsEvents();
      break;
    case "assistant":
      workspace.innerHTML = renderAssistantView();
      bindAssistantEvents();
      break;
    case "knowledge":
      workspace.innerHTML = renderKnowledgeView();
      bindKnowledgeEvents();
      break;
  }
}

function renderHomeView() {
  const projectCards = state.projects.length
    ? state.projects.map((p) => `
        <article class="project-card">
          <div class="project-card-body">
            <h3>${escapeHtml(p.name)}</h3>
            <p>${escapeHtml(p.description || "No description")}</p>
          </div>
          <button type="button" class="btn-primary open-project-btn" data-project-id="${p.id}">Open Project</button>
        </article>
      `).join("")
    : `<div class="empty-card"><p>No projects yet. Create your first project below.</p></div>`;

  return `
    <div class="view-container">
      <div class="view-hero">
        <h2>Welcome to MLForge AI</h2>
        <p>Build, train, and explain machine learning models in 7 simple steps.</p>
      </div>
      <div class="home-steps" aria-label="Pipeline overview">
        ${STEPS.map((s) => `
          <div class="home-step-item">
            <span class="home-step-num">${s.num}</span>
            <strong>${s.label}</strong>
            <small>${s.title}</small>
          </div>
        `).join("")}
      </div>
      <div class="home-grid">
        <section class="step-panel">
          <div class="step-panel-header">
            <span class="step-badge">Start Here</span>
            <h3>Create New Project</h3>
            <p>Give your ML project a name and optional description.</p>
          </div>
          <form class="project-form" id="projectForm">
            <label for="projectName">Project Name</label>
            <input id="projectName" name="name" type="text" required placeholder="Titanic Survival Prediction" />
            <label for="projectDescription">Description (optional)</label>
            <textarea id="projectDescription" name="description" rows="2" placeholder="Binary classification to predict passenger survival"></textarea>
            <button type="submit" class="btn-primary btn-large">Create Project & Start Pipeline</button>
          </form>
        </section>
        <section class="step-panel">
          <div class="step-panel-header">
            <span class="step-badge">Existing</span>
            <h3>Your Projects</h3>
            <p>${formatNumber(state.projects.length)} project${state.projects.length === 1 ? "" : "s"} available</p>
          </div>
          <div class="project-cards">${projectCards}</div>
        </section>
      </div>
    </div>
  `;
}

function renderStepper() {
  const dataset = getActiveDataset();
  const stages = pipelineStages(dataset);
  return `
    <nav class="wizard-stepper" aria-label="Pipeline steps">
      ${stages.map((stage) => {
        const isCurrent = stage.num === state.currentStep;
        const isClickable = stage.status === "complete" || stage.num <= suggestStep();
        return `
          <button type="button"
            class="wizard-step ${stage.status} ${isCurrent ? "current" : ""}"
            data-step="${stage.num}"
            ${isClickable ? "" : "disabled"}
            aria-current="${isCurrent ? "step" : "false"}">
            <span class="wizard-step-num">${stage.num}</span>
            <span class="wizard-step-label">${stage.label}</span>
          </button>
        `;
      }).join("")}
    </nav>
  `;
}

function renderPipelineView() {
  if (!state.selectedProject) {
    return `
      <div class="view-container">
        <div class="empty-card centered">
          <div class="empty-orbit">1</div>
          <h2>No Project Selected</h2>
          <p>Create or open a project from the Home page to start the pipeline.</p>
          <button type="button" class="btn-primary" data-goto="home">Go to Home</button>
        </div>
      </div>
    `;
  }

  const step = STEPS[state.currentStep - 1];
  const p = state.selectedProject;
  return `
    <div class="view-container">
      <div class="project-context">
        <div>
          <span class="eyebrow">Active Project</span>
          <strong>${escapeHtml(p.name)}</strong>
        </div>
        <button type="button" class="btn-secondary" data-goto="home">Switch Project</button>
      </div>
      ${renderStepper()}
      <div class="wizard-content">
        <div class="step-panel">
          <div class="step-panel-header">
            <span class="step-badge">Step ${step.num} of 7</span>
            <h2>${step.title}</h2>
            <p>${step.desc}</p>
          </div>
          <div class="step-body" id="stepBody">${renderStepContent(state.currentStep)}</div>
          <div class="step-footer">${renderStepFooter(state.currentStep)}</div>
        </div>
      </div>
    </div>
  `;
}

function renderStepContent(step) {
  switch (step) {
    case 1: return renderStep1();
    case 2: return renderStep2();
    case 3: return renderStep3();
    case 4: return renderStep4();
    case 5: return renderStep5();
    case 6: return renderStep6();
    case 7: return renderStep7();
    default: return "";
  }
}

function renderStep1() {
  const p = state.selectedProject;
  return `
    <div class="step-info-grid">
      <div class="info-card"><span>Project Name</span><strong>${escapeHtml(p.name)}</strong></div>
      <div class="info-card"><span>Description</span><strong>${escapeHtml(p.description || "None")}</strong></div>
      <div class="info-card"><span>Created</span><strong>${formatDate(p.created_at)}</strong></div>
      <div class="info-card"><span>Datasets</span><strong>${formatNumber(state.datasets.length)}</strong></div>
    </div>
    <p class="step-hint">Your project is ready. Click <strong>Continue</strong> to upload a dataset.</p>
  `;
}

function renderDatasetSelector() {
  if (state.datasets.length <= 1) return "";
  return `
    <div class="dataset-select-row">
      <label for="datasetSelect">Active Dataset</label>
      <select id="datasetSelect">
        ${state.datasets.map((d) => `
          <option value="${d.id}"${d.id === getActiveDataset()?.id ? " selected" : ""}>${escapeHtml(d.name)}</option>
        `).join("")}
      </select>
    </div>
  `;
}

function renderTargetColumnPicker() {
  const dataset = getActiveDataset();
  if (!dataset?.column_names?.length) return "";
  const options = ['<option value="">Auto-detect target column</option>']
    .concat(dataset.column_names.map((col) => `
      <option value="${escapeHtml(col)}"${state.targetColumn === col ? " selected" : ""}>${escapeHtml(col)}</option>
    `));
  return `
    <div class="config-row">
      <label for="targetColumn">Target Column (what you want to predict)</label>
      <select id="targetColumn">${options.join("")}</select>
      <p class="step-hint" style="margin:0;padding:8px 0 0;border:none;background:none">Leave as auto-detect unless you know your target column name.</p>
    </div>
  `;
}

function targetQuery() {
  return state.targetColumn ? `?target_column=${encodeURIComponent(state.targetColumn)}` : "";
}

function renderStep2() {
  const dataset = getActiveDataset();
  if (dataset) {
    return `
      ${renderDatasetSelector()}
      <div class="upload-success">
        <div class="success-icon">✓</div>
        <h3>${escapeHtml(dataset.name)}</h3>
        <p>Uploaded ${formatDate(dataset.created_at)}</p>
      </div>
      <div class="step-info-grid">
        <div class="info-card"><span>Rows</span><strong>${formatNumber(dataset.row_count)}</strong></div>
        <div class="info-card"><span>Columns</span><strong>${formatNumber(dataset.column_count)}</strong></div>
        <div class="info-card"><span>Missing Values</span><strong>${formatNumber(dataset.missing_values)}</strong></div>
        <div class="info-card"><span>File Size</span><strong>${formatBytes(dataset.file_size_bytes)}</strong></div>
      </div>
      ${renderTargetColumnPicker()}
      <p class="step-hint">Dataset uploaded successfully. Set your target column, then click <strong>Continue</strong> to explore your data.</p>
    `;
  }
  return `
    <div class="upload-zone">
      <div class="upload-icon">↑</div>
      <h3>Drop your dataset here</h3>
      <p>Supported formats: CSV, Excel (.xlsx), Parquet</p>
      <form class="upload-form" id="uploadForm">
        <input id="datasetFile" name="file" type="file" accept=".csv,.xlsx,.parquet" required />
        <button type="submit" class="btn-primary btn-large" id="uploadBtn">Upload Dataset</button>
      </form>
    </div>
  `;
}

function renderStep3() {
  const dataset = getActiveDataset();
  if (!dataset) return `<p class="step-hint">Upload a dataset first (Step 2).</p>`;
  const report = state.edaReports[dataset.id];
  if (!report) {
    return `
      ${renderDatasetSelector()}
      ${renderTargetColumnPicker()}
      <div class="action-card">
        <h3>Ready to Analyze</h3>
        <p>We will scan ${formatNumber(dataset.row_count)} rows and ${formatNumber(dataset.column_count)} columns for patterns, missing values, outliers, and class balance.</p>
        <button type="button" class="btn-primary btn-large" id="runEdaBtn">Run Data Exploration</button>
      </div>
    `;
  }
  return `${renderDatasetSelector()}${renderEdaReport(report, false)}`;
}

function renderStep4() {
  const dataset = getActiveDataset();
  if (!dataset) return `<p class="step-hint">Complete Step 3 first.</p>`;
  const report = state.cleaningReports[dataset.id];
  if (!report) {
    return `
      ${renderDatasetSelector()}
      <div class="action-card">
        <h3>Ready to Clean</h3>
        <p>Automatically fix missing values, remove duplicates, handle outliers, and validate data types.</p>
        <button type="button" class="btn-primary btn-large" id="runCleanBtn">Clean Dataset</button>
      </div>
    `;
  }
  return renderCleaningReport(report, false);
}

function renderStep5() {
  const dataset = getActiveDataset();
  if (!dataset) return `<p class="step-hint">Complete Step 4 first.</p>`;
  const report = state.featureReports[dataset.id];
  if (!report) {
    return `
      <div class="action-card">
        <h3>Ready to Build Features</h3>
        <p>Encode categorical columns, scale numeric features, and create model-ready dataset.</p>
        <button type="button" class="btn-primary btn-large" id="runFeaturesBtn">Generate Features</button>
      </div>
    `;
  }
  return renderFeatureReport(report, false);
}

function renderStep6() {
  const dataset = getActiveDataset();
  if (!dataset) return `<p class="step-hint">Complete Step 5 first.</p>`;
  const report = state.trainingReports[dataset.id];
  if (!report) {
    return `
      <div class="action-card">
        <h3>Ready to Train</h3>
        <p>Train and compare multiple models (Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost) with Optuna tuning.</p>
        <div class="loading-hint" id="trainLoading" hidden>
          <div class="spinner"></div>
          <p>Training models — this may take 1–3 minutes...</p>
        </div>
        <button type="button" class="btn-primary btn-large" id="runTrainBtn">Train Models</button>
      </div>
    `;
  }
  return renderTrainingReport(report, false);
}

function renderStep7() {
  const dataset = getActiveDataset();
  if (!dataset) return `<p class="step-hint">Complete Step 6 first.</p>`;
  const report = state.trainingReports[dataset.id];
  if (!report) {
    return `<p class="step-hint">Train models in Step 6 first.</p>`;
  }

  const finalReportUrl = report.final_report_path ? `/training/reports/${report.id}/final-report/download` : "";
  const shap = (report.artifacts || {}).shap || {};

  return `
    <div class="results-hero">
      <div class="results-badge">Pipeline Complete</div>
      <h3>Best Model: ${escapeHtml(report.best_model)}</h3>
      <p>${escapeHtml(getBestMetricText(report))} · ${escapeHtml(report.problem_type)} · Target: ${escapeHtml(report.target_column)}</p>
    </div>
    <div class="download-row">
      <a class="btn-primary download-link" href="/training/reports/${report.id}/download">Download Training Report</a>
      <a class="btn-secondary download-link secondary-link" href="/training/models/${report.id}/download">Download Model</a>
      ${finalReportUrl ? `<a class="btn-secondary download-link secondary-link" href="${finalReportUrl}">Download AI Report</a>` : ""}
      <a class="btn-secondary download-link secondary-link" href="http://localhost:5000" target="_blank" rel="noreferrer">Open MLflow</a>
    </div>
    ${!report.final_report_path ? `
      <div class="action-card" style="margin-top:16px">
        <h3>Generate AI Summary Report</h3>
        <p>Create a final narrative report explaining model performance and key findings.</p>
        <button type="button" class="btn-primary btn-large" id="runReportBtn" data-report-id="${report.id}">Generate AI Report</button>
      </div>
    ` : `<div class="success-banner">✓ AI Report generated and ready for download.</div>`}
    ${renderTrainingReport(report, false)}
    ${shap.status === "completed" ? renderShapSection(shap) : ""}
  `;
}

function renderStepFooter(step) {
  const canBack = step > 1;
  const canNext = step < 7 && isStepComplete(step);
  const isLast = step === 7;

  return `
    <div class="step-nav">
      ${canBack ? `<button type="button" class="btn-secondary" data-step-nav="${step - 1}">← Previous Step</button>` : "<span></span>"}
      <span class="step-nav-info">Step ${step} of 7</span>
      ${canNext ? `<button type="button" class="btn-primary" data-step-nav="${step + 1}">Continue to Step ${step + 1} →</button>` : ""}
      ${isLast && isStepComplete(6) ? `<button type="button" class="btn-secondary" data-goto="experiments">View Experiments</button>` : ""}
    </div>
  `;
}

function isStepComplete(step) {
  const dataset = getActiveDataset();
  switch (step) {
    case 1: return !!state.selectedProject;
    case 2: return !!dataset;
    case 3: return dataset && !!state.edaReports[dataset.id];
    case 4: return dataset && !!state.cleaningReports[dataset.id];
    case 5: return dataset && !!state.featureReports[dataset.id];
    case 6: return dataset && !!state.trainingReports[dataset.id];
    case 7: return dataset && !!state.trainingReports[dataset.id];
    default: return false;
  }
}

function renderExperimentsView() {
  if (!state.selectedProject) {
    return `
      <div class="view-container">
        <div class="empty-card centered">
          <h2>No Project Selected</h2>
          <p>Open a project first to view experiment runs.</p>
          <button type="button" class="btn-primary" data-goto="home">Go to Home</button>
        </div>
      </div>
    `;
  }
  return `<div class="view-container"><div class="step-panel">${renderExperimentPanel()}</div></div>`;
}

function renderAssistantView() {
  const disabled = !state.selectedProject || !state.datasets.length;
  return `
    <div class="view-container">
      <div class="step-panel">
        <div class="step-panel-header">
          <span class="step-badge">AI Powered</span>
          <h2>Run Full Pipeline with AI</h2>
          <p>The AI assistant will automatically run EDA, cleaning, feature engineering, and model training.</p>
        </div>
        ${disabled ? `<div class="empty-card"><p>Create a project and upload a dataset first.</p></div>` : ""}
        <div class="prompt-row">
          <button type="button" class="prompt-chip" data-prompt="Analyze my latest dataset and train the best model.">Analyze & Train</button>
          <button type="button" class="prompt-chip" data-prompt="Compare this experiment with the previous run.">Compare Runs</button>
          <button type="button" class="prompt-chip" data-prompt="Why did the best model perform well?">Explain Results</button>
        </div>
        <form class="assistant-form" id="agentForm">
          <textarea id="agentPrompt" rows="4" placeholder="Analyze my uploaded dataset and train the best model."${disabled ? " disabled" : ""}></textarea>
          <button type="submit" class="btn-primary btn-large"${disabled ? " disabled" : ""}>Run Full Pipeline with AI</button>
        </form>
        ${state.agentResponse ? `<div class="assistant-response">${renderAgentResponse(state.agentResponse)}</div>` : ""}
      </div>
    </div>
  `;
}

function renderKnowledgeView() {
  return `
    <div class="view-container">
      <div class="home-grid">
        <section class="step-panel">
          <div class="step-panel-header">
            <span class="step-badge">Index</span>
            <h3>Upload & Index Documents</h3>
            <p>Add PDF, Markdown, or text files to the knowledge base.</p>
          </div>
          <form class="knowledge-form" id="ragIndexForm">
            <input id="knowledgeFiles" name="files" type="file" accept=".pdf,.md,.txt,.html,.json" multiple />
            <div class="knowledge-actions">
              <input id="knowledgeCollection" name="collection" type="text" value="mlforge_docs" placeholder="Collection name" />
              <button type="submit" class="btn-primary">Index Documents</button>
            </div>
          </form>
        </section>
        <section class="step-panel">
          <div class="step-panel-header">
            <span class="step-badge">Search</span>
            <h3>Ask the Knowledge Base</h3>
            <p>Search indexed documents and generated reports.</p>
          </div>
          <form class="knowledge-form" id="ragQueryForm">
            <textarea id="ragQuestion" rows="4" placeholder="Why can logistic regression beat XGBoost on a small dataset?"></textarea>
            <button type="submit" class="btn-primary btn-large">Search Knowledge Base</button>
          </form>
          ${state.knowledgeResponse ? `<div class="knowledge-response">${renderKnowledgeResponse(state.knowledgeResponse)}</div>` : ""}
        </section>
      </div>
    </div>
  `;
}

function bindHomeEvents() {
  document.querySelector("#projectForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      setStatus("Creating project...");
      await createProject(fd.get("name"), fd.get("description"));
      e.target.reset();
      setStatus("Ready");
    } catch (err) {
      setStatus(err.message, true);
      showToast(err.message, "error");
    }
  });
  document.querySelectorAll(".open-project-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        setStatus("Opening project...");
        await openProject(Number(btn.dataset.projectId));
        setStatus("Ready");
      } catch (err) {
        setStatus(err.message, true);
      }
    });
  });
}

function bindPipelineEvents() {
  document.querySelector('[data-goto="home"]')?.addEventListener("click", () => setView("home"));

  document.querySelectorAll(".wizard-step:not([disabled])").forEach((btn) => {
    btn.addEventListener("click", () => setStep(Number(btn.dataset.step)));
  });

  document.querySelectorAll("[data-step-nav]").forEach((btn) => {
    btn.addEventListener("click", () => setStep(Number(btn.dataset.stepNav)));
  });

  document.querySelector('[data-goto="experiments"]')?.addEventListener("click", () => setView("experiments"));

  document.querySelector("#datasetSelect")?.addEventListener("change", (e) => {
    state.selectedDatasetId = Number(e.target.value);
    render();
  });

  document.querySelector("#targetColumn")?.addEventListener("change", (e) => {
    state.targetColumn = e.target.value;
  });

  document.querySelector("#uploadForm")?.addEventListener("submit", handleUpload);
  document.querySelector("#runEdaBtn")?.addEventListener("click", () => runPipelineAction("eda"));
  document.querySelector("#runCleanBtn")?.addEventListener("click", () => runPipelineAction("clean"));
  document.querySelector("#runFeaturesBtn")?.addEventListener("click", () => runPipelineAction("features"));
  document.querySelector("#runTrainBtn")?.addEventListener("click", () => runPipelineAction("train"));
  document.querySelector("#runReportBtn")?.addEventListener("click", () => runPipelineAction("report"));
}

function bindExperimentsEvents() {
  document.querySelector('[data-goto="home"]')?.addEventListener("click", () => setView("home"));
  document.querySelector("#compareExperiments")?.addEventListener("click", handleCompareExperiments);
}

function bindAssistantEvents() {
  document.querySelector("#agentForm")?.addEventListener("submit", handleAgentPrompt);
  document.querySelectorAll(".prompt-chip").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelector("#agentPrompt").value = btn.dataset.prompt;
    });
  });
}

function bindKnowledgeEvents() {
  document.querySelector("#ragIndexForm")?.addEventListener("submit", handleRagIndex);
  document.querySelector("#ragQueryForm")?.addEventListener("submit", handleRagQuery);
}

async function handleUpload(e) {
  e.preventDefault();
  const fileInput = document.querySelector("#datasetFile");
  if (!fileInput?.files.length || !state.selectedProject) return;

  const btn = document.querySelector("#uploadBtn");
  const body = new FormData();
  body.append("project_id", state.selectedProject.id);
  body.append("file", fileInput.files[0]);

  try {
    btn.disabled = true;
    btn.textContent = "Uploading...";
    setStatus("Uploading dataset...");
    await request("/datasets/upload", { method: "POST", body });
    await reloadProjectData();
    showToast("Dataset uploaded successfully");
    setStatus("Ready");
    render();
  } catch (err) {
    btn.disabled = false;
    btn.textContent = "Upload Dataset";
    setStatus(err.message, true);
    showToast(err.message, "error");
  }
}

async function runPipelineAction(action) {
  const dataset = getActiveDataset();
  if (!dataset || state.busy) return;
  state.busy = true;

  const tq = targetQuery();
  const configs = {
    eda: { btn: "#runEdaBtn", label: "Analyzing...", status: "Running EDA...", url: `/eda/datasets/${dataset.id}/analyze${tq}`, key: "edaReports", next: 4 },
    clean: { btn: "#runCleanBtn", label: "Cleaning...", status: "Cleaning dataset...", url: `/cleaning/datasets/${dataset.id}/run${tq}`, key: "cleaningReports", next: 5 },
    features: { btn: "#runFeaturesBtn", label: "Generating...", status: "Building features...", url: `/features/datasets/${dataset.id}/generate${tq}`, key: "featureReports", next: 6 },
    train: { btn: "#runTrainBtn", label: "Training...", status: "Training models...", url: `/training/datasets/${dataset.id}/train${tq}`, key: "trainingReports", next: 7 },
    report: { btn: "#runReportBtn", label: "Generating...", status: "Generating AI report...", url: null, key: null, next: 7 },
  };

  const cfg = configs[action];
  const btn = document.querySelector(cfg.btn);
  const loading = document.querySelector("#trainLoading");

  try {
    if (btn) { btn.disabled = true; btn.textContent = cfg.label; }
    if (loading) loading.hidden = false;
    setStatus(cfg.status);

    if (action === "report") {
      const reportId = btn.dataset.reportId;
      await request(`/training/reports/${reportId}/final-report`, { method: "POST" });
      await reloadProjectData();
    } else {
      const report = await request(cfg.url, { method: "POST" });
      state[cfg.key][dataset.id] = report;
      if (action === "clean") await loadFeatureReports();
      if (action === "features") await loadTrainingReports();
      if (action === "train") await loadExperiments();
    }

    showToast(`${STEPS[state.currentStep - 1].title} complete!`);
    setStatus("Ready");
    if (cfg.next) state.currentStep = cfg.next;
    render();
  } catch (err) {
    if (btn) { btn.disabled = false; btn.textContent = btn.textContent.replace("...", ""); }
    if (loading) loading.hidden = true;
    setStatus(err.message, true);
    showToast(err.message, "error");
  } finally {
    state.busy = false;
  }
}

async function handleAgentPrompt(e) {
  e.preventDefault();
  if (!state.selectedProject || !state.datasets.length) return;

  const prompt = document.querySelector("#agentPrompt").value.trim() || "Analyze this dataset and train the best model.";
  const dataset = getActiveDataset();
  const btn = e.target.querySelector("button[type=submit]");

  try {
    btn.disabled = true;
    btn.textContent = "Running pipeline...";
    setStatus("AI assistant running full pipeline...");
    const response = await request("/agents/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: prompt, dataset_id: dataset.id, project_id: state.selectedProject.id }),
    });
    state.agentResponse = response;
    await reloadProjectData();
    showToast("AI pipeline complete!");
    setStatus("Ready");
    render();
  } catch (err) {
    btn.disabled = false;
    btn.textContent = "Run Full Pipeline with AI";
    setStatus(err.message, true);
    showToast(err.message, "error");
  }
}

async function handleRagIndex(e) {
  e.preventDefault();
  const fileInput = document.querySelector("#knowledgeFiles");
  const collectionInput = document.querySelector("#knowledgeCollection");
  const body = new FormData();
  body.append("collection", collectionInput.value.trim() || "mlforge_docs");
  body.append("include_knowledge", "true");
  body.append("include_reports", "true");
  Array.from(fileInput.files).forEach((f) => body.append("files", f));

  try {
    setStatus("Indexing documents...");
    const response = await request("/rag/index", { method: "POST", body });
    state.knowledgeResponse = { type: "index", data: response };
    showToast("Documents indexed successfully");
    setStatus("Ready");
    render();
  } catch (err) {
    setStatus(err.message, true);
    showToast(err.message, "error");
  }
}

async function handleRagQuery(e) {
  e.preventDefault();
  const question = document.querySelector("#ragQuestion").value.trim();
  if (!question) { setStatus("Question is required", true); return; }

  try {
    setStatus("Searching knowledge base...");
    const response = await request("/rag/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        collection: document.querySelector("#knowledgeCollection")?.value.trim() || "mlforge_docs",
        top_k: 5,
      }),
    });
    state.knowledgeResponse = { type: "query", data: response };
    showToast("Answer ready");
    setStatus("Ready");
    render();
  } catch (err) {
    setStatus(err.message, true);
    showToast(err.message, "error");
  }
}

async function handleCompareExperiments() {
  if (!state.selectedProject) return;
  try {
    setStatus("Comparing experiments...");
    state.experimentComparison = await request(`/training/projects/${state.selectedProject.id}/experiments/compare`);
    showToast("Comparison ready");
    setStatus("Ready");
    render();
  } catch (err) {
    setStatus(err.message, true);
  }
}

document.querySelectorAll(".nav-item").forEach((btn) => {
  btn.addEventListener("click", () => { setView(btn.dataset.view); });
});

async function checkServices() {
  const el = document.querySelector("#serviceStatus");
  const dot = document.querySelector(".service-dot");
  try {
    await request("/");
    el.textContent = "FastAPI · Postgres · Qdrant · MLflow";
    dot.style.background = "var(--good)";
  } catch {
    el.textContent = "Backend unreachable";
    dot.style.background = "var(--danger)";
  }
}

function getBestMetricText(report) {
  const metrics = report.metrics.best || {};
  const key = report.problem_type === "classification"
    ? (metrics.roc_auc !== undefined ? "roc_auc" : "accuracy")
    : (metrics.r2 !== undefined ? "r2" : "rmse");
  const value = metrics[key];
  return value === undefined ? "Ready" : `${formatLabel(key)} ${formatCell(value)}`;
}

function formatNumber(value) { return new Intl.NumberFormat().format(value || 0); }

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}

function formatBytes(bytes) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / 1024 ** index).toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function renderEdaReport(report, showActions = true) {
  const data = report.report_data;
  const overview = data.dataset_overview;
  const numericRows = data.numerical_statistics.slice(0, 6);
  const missingRows = data.missing_value_analysis.slice(0, 8);
  const outlierRows = data.outlier_detection.filter((i) => i.outlier_count > 0).slice(0, 8);
  const visuals = report.visualizations;

  return `
    <header class="eda-header">
      <div><h4>EDA Report</h4><p>Generated ${formatDate(report.created_at)}</p></div>
      <a class="download-link secondary-link" href="/eda/reports/${report.id}/download">Download Report</a>
    </header>
    <div class="eda-metrics">
      <div><span>Rows</span><strong>${formatNumber(overview.rows)}</strong></div>
      <div><span>Columns</span><strong>${formatNumber(overview.columns)}</strong></div>
      <div><span>Missing</span><strong>${formatNumber(overview.total_missing_values)}</strong></div>
      <div><span>Duplicates</span><strong>${formatNumber(overview.duplicate_rows)}</strong></div>
    </div>
    ${renderClassBalance(data.class_balance)}
    ${renderCompactTable("Numerical Statistics", numericRows, ["column", "mean", "median", "minimum", "maximum", "standard_deviation"])}
    ${renderCompactTable("Missing Values", missingRows, ["column", "missing_count", "missing_percentage"])}
    ${renderCompactTable("Outliers", outlierRows, ["column", "outlier_count", "outlier_percentage"])}
    <div class="visual-grid">${visuals.map((v) => `
      <figure><img src="${escapeHtml(v.url)}" alt="${escapeHtml(v.title)}" /><figcaption>${escapeHtml(v.title)}</figcaption></figure>
    `).join("")}</div>
  `;
}

function renderCleaningReport(report, showActions = true) {
  const summary = report.cleaning_summary;
  return `
    <header class="eda-header">
      <div><h4>Cleaning Report</h4><p>Generated ${formatDate(report.created_at)}</p></div>
      <div class="download-group">
        <a class="download-link secondary-link" href="/cleaning/reports/${report.id}/download">Report</a>
        <a class="download-link secondary-link" href="/cleaning/reports/${report.id}/cleaned-dataset/download">Cleaned CSV</a>
      </div>
    </header>
    <div class="eda-metrics">
      <div><span>Rows Before</span><strong>${formatNumber(report.original_rows)}</strong></div>
      <div><span>Rows After</span><strong>${formatNumber(report.final_rows)}</strong></div>
      <div><span>Missing Before</span><strong>${formatNumber(report.missing_values_before)}</strong></div>
      <div><span>Missing After</span><strong>${formatNumber(report.missing_values_after)}</strong></div>
      <div><span>Duplicates Removed</span><strong>${formatNumber(report.duplicates_removed)}</strong></div>
      <div><span>Outliers Handled</span><strong>${formatNumber(report.outliers_handled)}</strong></div>
    </div>
    ${renderCompactTable("Filled Missing Values", summary.missing_value_report.filled_columns, ["column", "missing_before", "strategy", "fill_value"])}
    ${renderCompactTable("Outliers Handled", summary.outlier_report.columns, ["column", "outlier_count", "strategy", "lower_bound", "upper_bound"])}
  `;
}

function renderFeatureReport(report, showActions = true) {
  const summary = report.feature_summary;
  return `
    <header class="eda-header">
      <div><h4>Feature Report</h4><p>Generated ${formatDate(report.created_at)}</p></div>
      <div class="download-group">
        <a class="download-link secondary-link" href="/features/reports/${report.id}/download">Report</a>
        <a class="download-link secondary-link" href="/features/datasets/${report.dataset_id}/download">Feature Dataset</a>
      </div>
    </header>
    <div class="eda-metrics">
      <div><span>Original Columns</span><strong>${formatNumber(report.original_columns)}</strong></div>
      <div><span>Final Columns</span><strong>${formatNumber(report.final_columns)}</strong></div>
      <div><span>Encoding</span><strong>${escapeHtml(report.encoding_method)}</strong></div>
      <div><span>Scaling</span><strong>${escapeHtml(report.scaling_method)}</strong></div>
      <div><span>Features Created</span><strong>${formatNumber(report.features_created.length)}</strong></div>
      <div><span>Target</span><strong>${escapeHtml(report.target_column || "None")}</strong></div>
    </div>
    ${renderFeatureList("Created Features", report.features_created)}
    ${renderFeatureList("Scaled Columns", summary.scaling_report.scaled_columns)}
  `;
}

function renderTrainingReport(report, showActions = true) {
  const metrics = report.metrics.best || {};
  const comparison = report.metrics.comparison || [];
  return `
    <header class="eda-header">
      <div><h4>Training Report</h4><p>Generated ${formatDate(report.created_at)}</p></div>
    </header>
    <div class="eda-metrics">
      <div><span>Problem Type</span><strong>${escapeHtml(report.problem_type)}</strong></div>
      <div><span>Best Model</span><strong>${escapeHtml(report.best_model)}</strong></div>
      <div><span>Training Time</span><strong>${report.training_time.toFixed(2)}s</strong></div>
      ${Object.entries(metrics).filter(([k]) => k !== "confusion_matrix").slice(0, 3).map(([k, v]) => `
        <div><span>${escapeHtml(formatLabel(k))}</span><strong>${escapeHtml(formatCell(v))}</strong></div>
      `).join("")}
    </div>
    ${renderModelComparison(comparison)}
  `;
}

function renderExperimentPanel() {
  const rows = state.experiments.map((run) => `
    <tr>
      <td>${escapeHtml(run.id)}</td>
      <td>${escapeHtml(run.best_model)}</td>
      <td>${escapeHtml(formatCell(run.score))}</td>
      <td>${escapeHtml(formatCell(run.roc_auc || run.accuracy || run.r2 || run.rmse))}</td>
      <td>${run.mlflow_run_id ? "Logged" : "Local"}</td>
    </tr>
  `).join("");

  return `
    <div class="experiment-header">
      <div>
        <h3>Experiment Tracking</h3>
        <p>All model training runs tracked in MLflow.</p>
      </div>
      <div class="download-group">
        <a class="download-link secondary-link" href="http://localhost:5000" target="_blank" rel="noreferrer">Open MLflow UI</a>
        <button type="button" class="btn-primary" id="compareExperiments">Compare Experiments</button>
      </div>
    </div>
    <section class="eda-section">
      <h5>Recent Runs</h5>
      <table>
        <thead><tr><th>Run</th><th>Best Model</th><th>Score</th><th>Main Metric</th><th>Tracking</th></tr></thead>
        <tbody>${rows || '<tr><td colspan="5">No experiments yet. Complete the pipeline first.</td></tr>'}</tbody>
      </table>
    </section>
    ${state.experimentComparison ? renderExperimentComparison(state.experimentComparison) : ""}
  `;
}

function renderExperimentComparison(comparison) {
  return `
    <section class="eda-section">
      <h5>Comparison</h5>
      <p>${escapeHtml(comparison.summary)}</p>
      <div class="eda-metrics">
        <div><span>Runs</span><strong>${formatNumber(comparison.runs.length)}</strong></div>
        <div><span>Score Delta</span><strong>${escapeHtml(formatCell(comparison.score_delta))}</strong></div>
        <div><span>Latest</span><strong>${escapeHtml(comparison.latest ? comparison.latest.best_model : "None")}</strong></div>
        <div><span>Previous</span><strong>${escapeHtml(comparison.previous ? comparison.previous.best_model : "None")}</strong></div>
      </div>
    </section>
  `;
}

function renderShapSection(shap) {
  if (!shap || shap.status !== "completed") return "";
  const rows = (shap.top_features || []).slice(0, 8).map((i) => `
    <tr><td>${escapeHtml(i.feature)}</td><td>${escapeHtml(formatCell(i.importance))}</td></tr>
  `).join("");
  return `
    <section class="eda-section">
      <h5>SHAP Explainability</h5>
      <div class="visual-grid">
        ${shap.importance_url ? `<figure><img src="${escapeHtml(shap.importance_url)}" alt="SHAP importance" /><figcaption>Feature Importance</figcaption></figure>` : ""}
        ${shap.summary_url ? `<figure><img src="${escapeHtml(shap.summary_url)}" alt="SHAP summary" /><figcaption>SHAP Summary</figcaption></figure>` : ""}
      </div>
      <table><thead><tr><th>Feature</th><th>Importance</th></tr></thead><tbody>${rows}</tbody></table>
    </section>
  `;
}

function renderAgentResponse(response) {
  return `
    <h4>AI Pipeline Result</h4>
    <pre>${escapeHtml(response.message)}</pre>
    <section class="eda-section">
      <h5>Execution Plan</h5>
      <table><tbody>${response.plan.map((s) => `<tr><td>${escapeHtml(s)}</td></tr>`).join("")}</tbody></table>
    </section>
  `;
}

function renderKnowledgeResponse(response) {
  if (response.type === "index") {
    const data = response.data;
    return `
      <h4>Documents Indexed</h4>
      <div class="eda-metrics">
        <div><span>Collection</span><strong>${escapeHtml(data.collection)}</strong></div>
        <div><span>Documents</span><strong>${formatNumber(data.documents)}</strong></div>
        <div><span>Chunks</span><strong>${formatNumber(data.chunks)}</strong></div>
      </div>
    `;
  }
  const data = response.data;
  const rows = data.sources.map((s) => `
    <tr><td>${escapeHtml(s.title || s.source)}</td><td>${escapeHtml(formatCell(s.score))}</td><td>${escapeHtml(s.document_type || "")}</td></tr>
  `).join("");
  return `
    <h4>Answer</h4>
    <pre>${escapeHtml(data.answer)}</pre>
    <section class="eda-section"><h5>Sources</h5>
      <table><thead><tr><th>Source</th><th>Score</th><th>Type</th></tr></thead><tbody>${rows}</tbody></table>
    </section>
  `;
}

function renderModelComparison(rows) {
  if (!rows.length) return "";
  return `
    <section class="eda-section">
      <h5>Model Comparison</h5>
      <table>
        <thead><tr><th>Model</th><th>Score</th><th>Training Time</th><th>Inference Time</th></tr></thead>
        <tbody>${rows.map((r) => `
          <tr><td>${escapeHtml(r.model)}</td><td>${escapeHtml(formatCell(r.score))}</td>
          <td>${escapeHtml(formatCell(r.training_time))}</td><td>${escapeHtml(formatCell(r.inference_time))}</td></tr>
        `).join("")}</tbody>
      </table>
    </section>
  `;
}

function renderClassBalance(classBalance) {
  if (!classBalance) return "";
  const rows = classBalance.classes.map((i) => `
    <tr><td>${escapeHtml(i.class)}</td><td>${formatNumber(i.count)}</td><td>${i.percentage}%</td></tr>
  `).join("");
  return `
    <section class="eda-section">
      <h5>Class Balance: ${escapeHtml(classBalance.target_column)}</h5>
      <table><thead><tr><th>Class</th><th>Count</th><th>Percent</th></tr></thead><tbody>${rows}</tbody></table>
    </section>
  `;
}

function renderCompactTable(title, rows, columns) {
  if (!rows.length) return "";
  const headers = columns.map((c) => `<th>${escapeHtml(formatLabel(c))}</th>`).join("");
  const body = rows.map((row) => `
    <tr>${columns.map((c) => `<td>${escapeHtml(formatCell(row[c]))}</td>`).join("")}</tr>
  `).join("");
  return `<section class="eda-section"><h5>${escapeHtml(title)}</h5><table><thead><tr>${headers}</tr></thead><tbody>${body}</tbody></table></section>`;
}

function renderFeatureList(title, items) {
  if (!items?.length) return "";
  return `<section class="eda-section"><h5>${escapeHtml(title)}</h5><table><tbody>${items.map((i) => `<tr><td>${escapeHtml(i)}</td></tr>`).join("")}</tbody></table></section>`;
}

function formatLabel(value) { return String(value).replaceAll("_", " ").replace(/\b\w/g, (l) => l.toUpperCase()); }

function formatCell(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "number") return Number.isInteger(value) ? formatNumber(value) : value.toFixed(3);
  return value;
}

function escapeHtml(value) {
  return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
}

loadProjects()
  .then(() => { render(); setStatus("Ready"); checkServices(); })
  .catch((err) => setStatus(err.message, true));
