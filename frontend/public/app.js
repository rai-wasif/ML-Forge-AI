const API_BASE = window.location.origin;

const state = {
  projects: [],
  selectedProject: null,
  datasets: [],
  edaReports: {},
  cleaningReports: {},
  featureReports: {},
  trainingReports: {},
  agentResponse: null,
};

const projectForm = document.querySelector("#projectForm");
const projectList = document.querySelector("#projectList");
const workspace = document.querySelector("#workspace");
const statusText = document.querySelector("#statusText");
const projectTemplate = document.querySelector("#projectTemplate");
const datasetTemplate = document.querySelector("#datasetTemplate");

function setStatus(message, isError = false) {
  statusText.textContent = message;
  statusText.classList.toggle("error", isError);
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

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

async function loadProjects() {
  state.projects = await request("/projects");
  renderProjects();
}

function renderProjects() {
  projectList.replaceChildren();

  if (state.projects.length === 0) {
    const empty = document.createElement("p");
    empty.textContent = "No projects yet.";
    projectList.append(empty);
    return;
  }

  state.projects.forEach((project) => {
    const node = projectTemplate.content.cloneNode(true);
    const item = node.querySelector(".project-item");
    item.dataset.projectId = project.id;
    node.querySelector("h3").textContent = project.name;
    node.querySelector("p").textContent = project.description || "No description";
    projectList.append(node);
  });
}

async function openProject(projectId) {
  state.selectedProject = await request(`/projects/${projectId}`);
  state.datasets = await request(`/datasets/project/${projectId}`);
  await loadEdaReports();
  await loadCleaningReports();
  await loadFeatureReports();
  await loadTrainingReports();
  renderWorkspace();
}

async function loadEdaReports() {
  const entries = await Promise.all(
    state.datasets.map(async (dataset) => {
      const report = await request(`/eda/datasets/${dataset.id}/latest`);
      return [dataset.id, report];
    }),
  );

  state.edaReports = Object.fromEntries(entries.filter((entry) => entry[1]));
}

async function loadCleaningReports() {
  const entries = await Promise.all(
    state.datasets.map(async (dataset) => {
      const report = await request(`/cleaning/datasets/${dataset.id}/latest`);
      return [dataset.id, report];
    }),
  );

  state.cleaningReports = Object.fromEntries(entries.filter((entry) => entry[1]));
}

async function loadFeatureReports() {
  const entries = await Promise.all(
    state.datasets.map(async (dataset) => {
      const report = await request(`/features/datasets/${dataset.id}/latest`);
      return [dataset.id, report];
    }),
  );

  state.featureReports = Object.fromEntries(entries.filter((entry) => entry[1]));
}

async function loadTrainingReports() {
  const entries = await Promise.all(
    state.datasets.map(async (dataset) => {
      const report = await request(`/training/datasets/${dataset.id}/latest`);
      return [dataset.id, report];
    }),
  );

  state.trainingReports = Object.fromEntries(entries.filter((entry) => entry[1]));
}

function renderWorkspace() {
  const project = state.selectedProject;

  if (!project) {
    workspace.innerHTML = `
      <div class="empty-state">
        <h2>No project selected</h2>
        <p>Create or open a project to begin.</p>
      </div>
    `;
    return;
  }

  workspace.innerHTML = `
    <header class="workspace-header">
      <div>
        <h2>${escapeHtml(project.name)}</h2>
        <p>${escapeHtml(project.description || "No description")}</p>
      </div>
      <form class="upload-form" id="uploadForm">
        <input id="datasetFile" name="file" type="file" accept=".csv,.xlsx,.parquet" required />
        <button type="submit">Upload Dataset</button>
      </form>
    </header>
    <section class="assistant-panel">
      <div>
        <h3>AI Assistant</h3>
        <p>Ask the ML Engineer Crew to run the pipeline for this project.</p>
      </div>
      <form class="assistant-form" id="agentForm">
        <textarea id="agentPrompt" rows="3" placeholder="Analyze my uploaded Titanic dataset and train the best model."></textarea>
        <button type="submit"${state.datasets.length ? "" : " disabled"}>Run Crew</button>
      </form>
      <div class="assistant-response" id="agentResponse"${state.agentResponse ? "" : " hidden"}>
        ${state.agentResponse ? renderAgentResponse(state.agentResponse) : ""}
      </div>
    </section>
    <div class="dataset-list" id="datasetList"></div>
  `;

  renderDatasets();
  document.querySelector("#uploadForm").addEventListener("submit", handleUpload);
  document.querySelector("#agentForm").addEventListener("submit", handleAgentPrompt);
}

function renderDatasets() {
  const datasetList = document.querySelector("#datasetList");
  datasetList.replaceChildren();

  if (state.datasets.length === 0) {
    const empty = document.createElement("p");
    empty.textContent = "No datasets uploaded.";
    datasetList.append(empty);
    return;
  }

  state.datasets.forEach((dataset) => {
    const node = datasetTemplate.content.cloneNode(true);
    const item = node.querySelector(".dataset-item");
    item.dataset.datasetId = dataset.id;
    node.querySelector("h3").textContent = dataset.name;
    node.querySelector("p").textContent = `Uploaded ${formatDate(dataset.created_at)}`;
    node.querySelector(".file-type").textContent = dataset.file_type || "file";
    node.querySelector('[data-field="rows"]').textContent = formatNumber(dataset.row_count);
    node.querySelector('[data-field="columns"]').textContent = formatNumber(dataset.column_count);
    node.querySelector('[data-field="missing"]').textContent = formatNumber(dataset.missing_values);
    node.querySelector('[data-field="duplicates"]').textContent = formatNumber(dataset.duplicate_rows);
    node.querySelector('[data-field="size"]').textContent = formatBytes(dataset.file_size_bytes);
    node.querySelector('[data-field="memory"]').textContent = formatBytes(dataset.memory_usage_bytes);
    const report = state.edaReports[dataset.id];
    const reportNode = node.querySelector(".eda-report");
    if (report) {
      reportNode.hidden = false;
      reportNode.innerHTML = renderEdaReport(report);
    }
    const cleaningReport = state.cleaningReports[dataset.id];
    const cleaningReportNode = node.querySelector(".cleaning-report");
    if (cleaningReport) {
      cleaningReportNode.hidden = false;
      cleaningReportNode.innerHTML = renderCleaningReport(cleaningReport);
    }
    const featureReport = state.featureReports[dataset.id];
    const featureReportNode = node.querySelector(".feature-report");
    if (featureReport) {
      featureReportNode.hidden = false;
      featureReportNode.innerHTML = renderFeatureReport(featureReport);
    }
    const trainingReport = state.trainingReports[dataset.id];
    const trainingReportNode = node.querySelector(".training-report");
    if (trainingReport) {
      trainingReportNode.hidden = false;
      trainingReportNode.innerHTML = renderTrainingReport(trainingReport);
    }
    datasetList.append(node);
  });
}

async function handleUpload(event) {
  event.preventDefault();
  const fileInput = document.querySelector("#datasetFile");

  if (!fileInput.files.length || !state.selectedProject) {
    return;
  }

  const body = new FormData();
  body.append("project_id", state.selectedProject.id);
  body.append("file", fileInput.files[0]);

  try {
    setStatus("Uploading");
    await request("/datasets/upload", {
      method: "POST",
      body,
    });
    state.datasets = await request(`/datasets/project/${state.selectedProject.id}`);
    await loadEdaReports();
    await loadCleaningReports();
    await loadFeatureReports();
    await loadTrainingReports();
    renderWorkspace();
    setStatus("Dataset saved");
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function handleAgentPrompt(event) {
  event.preventDefault();

  if (!state.selectedProject || !state.datasets.length) {
    setStatus("Upload a dataset first", true);
    return;
  }

  const promptInput = document.querySelector("#agentPrompt");
  const prompt = promptInput.value.trim() || "Analyze this dataset and train the best model.";
  const dataset = state.datasets[0];

  try {
    setStatus("Crew running");
    const response = await request("/agents/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: prompt,
        dataset_id: dataset.id,
        project_id: state.selectedProject.id,
      }),
    });
    state.agentResponse = response;
    state.datasets = await request(`/datasets/project/${state.selectedProject.id}`);
    await loadEdaReports();
    await loadCleaningReports();
    await loadFeatureReports();
    await loadTrainingReports();
    renderWorkspace();
    setStatus("Crew complete");
  } catch (error) {
    setStatus(error.message, true);
  }
}

projectForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(projectForm);
  const payload = {
    name: formData.get("name"),
    description: formData.get("description") || null,
  };

  try {
    setStatus("Creating");
    const project = await request("/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    projectForm.reset();
    await loadProjects();
    await openProject(project.id);
    setStatus("Project created");
  } catch (error) {
    setStatus(error.message, true);
  }
});

workspace.addEventListener("click", async (event) => {
  const button = event.target.closest(".analyze-dataset");
  if (!button) {
    return;
  }

  const datasetId = button.closest(".dataset-item").dataset.datasetId;

  try {
    button.disabled = true;
    button.textContent = "Analyzing";
    setStatus("Analyzing dataset");
    const report = await request(`/eda/datasets/${datasetId}/analyze`, {
      method: "POST",
    });
    state.edaReports[datasetId] = report;
    renderWorkspace();
    setStatus("EDA complete");
  } catch (error) {
    button.disabled = false;
    button.textContent = "Analyze Dataset";
    setStatus(error.message, true);
  }
});

workspace.addEventListener("click", async (event) => {
  const button = event.target.closest(".clean-dataset");
  if (!button) {
    return;
  }

  const datasetId = button.closest(".dataset-item").dataset.datasetId;

  try {
    button.disabled = true;
    button.textContent = "Cleaning";
    setStatus("Cleaning dataset");
    const report = await request(`/cleaning/datasets/${datasetId}/run`, {
      method: "POST",
    });
    state.cleaningReports[datasetId] = report;
    await loadFeatureReports();
    renderWorkspace();
    setStatus("Cleaning complete");
  } catch (error) {
    button.disabled = false;
    button.textContent = "Clean Dataset";
    setStatus(error.message, true);
  }
});

workspace.addEventListener("click", async (event) => {
  const button = event.target.closest(".generate-features");
  if (!button) {
    return;
  }

  const datasetId = button.closest(".dataset-item").dataset.datasetId;

  try {
    button.disabled = true;
    button.textContent = "Generating";
    setStatus("Generating features");
    const report = await request(`/features/datasets/${datasetId}/generate`, {
      method: "POST",
    });
    state.featureReports[datasetId] = report;
    await loadTrainingReports();
    renderWorkspace();
    setStatus("Features ready");
  } catch (error) {
    button.disabled = false;
    button.textContent = "Generate Features";
    setStatus(error.message, true);
  }
});

workspace.addEventListener("click", async (event) => {
  const button = event.target.closest(".train-model");
  if (!button) {
    return;
  }

  const datasetId = button.closest(".dataset-item").dataset.datasetId;

  try {
    button.disabled = true;
    button.textContent = "Preparing Dataset... 35%";
    setStatus("Training model");
    await new Promise((resolve) => setTimeout(resolve, 250));
    button.textContent = "Training Models... 60%";
    const report = await request(`/training/datasets/${datasetId}/train`, {
      method: "POST",
    });
    button.textContent = "Evaluating... 100%";
    state.trainingReports[datasetId] = report;
    renderWorkspace();
    setStatus("Training complete");
  } catch (error) {
    button.disabled = false;
    button.textContent = "Train Model";
    setStatus(error.message, true);
  }
});

projectList.addEventListener("click", async (event) => {
  const button = event.target.closest(".open-project");
  if (!button) {
    return;
  }

  const projectId = button.closest(".project-item").dataset.projectId;

  try {
    setStatus("Opening");
    await openProject(projectId);
    setStatus("Ready");
  } catch (error) {
    setStatus(error.message, true);
  }
});

function formatNumber(value) {
  return new Intl.NumberFormat().format(value || 0);
}

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

function formatBytes(bytes) {
  if (!bytes) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** index;
  return `${value.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function renderEdaReport(report) {
  const data = report.report_data;
  const overview = data.dataset_overview;
  const numericRows = data.numerical_statistics.slice(0, 6);
  const missingRows = data.missing_value_analysis.slice(0, 8);
  const outlierRows = data.outlier_detection.filter((item) => item.outlier_count > 0).slice(0, 8);
  const visuals = report.visualizations;

  return `
    <header class="eda-header">
      <div>
        <h4>EDA Report</h4>
        <p>Generated ${formatDate(report.created_at)}</p>
      </div>
      <a class="download-link" href="/eda/reports/${report.id}/download">Download Report</a>
    </header>
    <div class="dataset-actions">
      <button type="button" class="clean-dataset">Clean Dataset</button>
    </div>
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
    <div class="visual-grid">
      ${visuals.map((visual) => `
        <figure>
          <img src="${escapeHtml(visual.url)}" alt="${escapeHtml(visual.title)}" />
          <figcaption>${escapeHtml(visual.title)}</figcaption>
        </figure>
      `).join("")}
    </div>
  `;
}

function renderCleaningReport(report) {
  const summary = report.cleaning_summary;

  return `
    <header class="eda-header">
      <div>
        <h4>Cleaning Report</h4>
        <p>Generated ${formatDate(report.created_at)}</p>
      </div>
      <div class="download-group">
        <a class="download-link" href="/cleaning/reports/${report.id}/download">Report</a>
        <a class="download-link secondary-link" href="/cleaning/reports/${report.id}/cleaned-dataset/download">Cleaned CSV</a>
      </div>
    </header>
    <div class="dataset-actions">
      <button type="button" class="generate-features">Generate Features</button>
    </div>
    <div class="eda-metrics">
      <div><span>Rows Before</span><strong>${formatNumber(report.original_rows)}</strong></div>
      <div><span>Rows After</span><strong>${formatNumber(report.final_rows)}</strong></div>
      <div><span>Missing Before</span><strong>${formatNumber(report.missing_values_before)}</strong></div>
      <div><span>Missing After</span><strong>${formatNumber(report.missing_values_after)}</strong></div>
      <div><span>Duplicates</span><strong>${formatNumber(report.duplicates_removed)}</strong></div>
      <div><span>Outliers</span><strong>${formatNumber(report.outliers_handled)}</strong></div>
      <div><span>Target</span><strong>${escapeHtml(summary.target_column || "None")}</strong></div>
    </div>
    ${renderCompactTable("Filled Missing Values", summary.missing_value_report.filled_columns, ["column", "missing_before", "strategy", "fill_value"])}
    ${renderCompactTable("Outliers Handled", summary.outlier_report.columns, ["column", "outlier_count", "strategy", "lower_bound", "upper_bound"])}
    ${renderCompactTable("Invalid Values", summary.invalid_value_report.invalid_values, ["column", "invalid_count", "rule", "strategy"])}
  `;
}

function renderFeatureReport(report) {
  const summary = report.feature_summary;

  return `
    <header class="eda-header">
      <div>
        <h4>Feature Report</h4>
        <p>Generated ${formatDate(report.created_at)}</p>
      </div>
      <div class="download-group">
        <a class="download-link" href="/features/reports/${report.id}/download">Report</a>
        <a class="download-link secondary-link" href="/features/datasets/${report.dataset_id}/download">Feature Dataset</a>
      </div>
    </header>
    <div class="dataset-actions">
      <button type="button" class="train-model">Train Model</button>
    </div>
    <div class="eda-metrics">
      <div><span>Original Columns</span><strong>${formatNumber(report.original_columns)}</strong></div>
      <div><span>Final Columns</span><strong>${formatNumber(report.final_columns)}</strong></div>
      <div><span>Encoding</span><strong>${escapeHtml(report.encoding_method)}</strong></div>
      <div><span>Scaling</span><strong>${escapeHtml(report.scaling_method)}</strong></div>
      <div><span>Created</span><strong>${formatNumber(report.features_created.length)}</strong></div>
      <div><span>Dropped</span><strong>${formatNumber(report.dropped_columns.length)}</strong></div>
      <div><span>Target</span><strong>${escapeHtml(report.target_column || "None")}</strong></div>
    </div>
    ${renderFeatureList("Created Features", report.features_created)}
    ${renderFeatureList("Dropped Columns", report.dropped_columns)}
    ${renderFeatureList("Scaled Columns", summary.scaling_report.scaled_columns)}
    ${renderFeatureList("One-Hot Encoded", summary.encoding_report.one_hot_columns)}
    ${renderFeatureList("Label Encoded", summary.encoding_report.label_encoded_columns)}
  `;
}

function renderTrainingReport(report) {
  const metrics = report.metrics.best || {};
  const comparison = report.metrics.comparison || [];

  return `
    <header class="eda-header">
      <div>
        <h4>Training Report</h4>
        <p>Generated ${formatDate(report.created_at)}</p>
      </div>
      <div class="download-group">
        <a class="download-link" href="/training/reports/${report.id}/download">Report</a>
        <a class="download-link secondary-link" href="/training/models/${report.id}/download">Model</a>
      </div>
    </header>
    <div class="eda-metrics">
      <div><span>Problem</span><strong>${escapeHtml(report.problem_type)}</strong></div>
      <div><span>Target</span><strong>${escapeHtml(report.target_column)}</strong></div>
      <div><span>Best Model</span><strong>${escapeHtml(report.best_model)}</strong></div>
      <div><span>Training Time</span><strong>${report.training_time.toFixed(2)}s</strong></div>
      ${Object.entries(metrics).filter(([key]) => key !== "confusion_matrix").slice(0, 4).map(([key, value]) => `
        <div><span>${escapeHtml(formatLabel(key))}</span><strong>${escapeHtml(formatCell(value))}</strong></div>
      `).join("")}
    </div>
    ${renderModelComparison(comparison)}
  `;
}

function renderAgentResponse(response) {
  return `
    <h4>ML Engineer Crew</h4>
    <pre>${escapeHtml(response.message)}</pre>
    <section class="eda-section">
      <h5>Plan</h5>
      <table>
        <tbody>${response.plan.map((step) => `<tr><td>${escapeHtml(step)}</td></tr>`).join("")}</tbody>
      </table>
    </section>
  `;
}

function renderModelComparison(rows) {
  if (!rows.length) {
    return "";
  }

  const body = rows.map((row) => `
    <tr>
      <td>${escapeHtml(row.model)}</td>
      <td>${escapeHtml(formatCell(row.score))}</td>
      <td>${escapeHtml(formatCell(row.training_time))}</td>
      <td>${escapeHtml(formatCell(row.inference_time))}</td>
    </tr>
  `).join("");

  return `
    <section class="eda-section">
      <h5>Model Comparison</h5>
      <table>
        <thead><tr><th>Model</th><th>Score</th><th>Training Time</th><th>Inference Time</th></tr></thead>
        <tbody>${body}</tbody>
      </table>
    </section>
  `;
}

function renderClassBalance(classBalance) {
  if (!classBalance) {
    return "";
  }

  const rows = classBalance.classes
    .map((item) => `<tr><td>${escapeHtml(item.class)}</td><td>${formatNumber(item.count)}</td><td>${item.percentage}%</td></tr>`)
    .join("");

  return `
    <section class="eda-section">
      <h5>Class Balance: ${escapeHtml(classBalance.target_column)}</h5>
      <table>
        <thead><tr><th>Class</th><th>Count</th><th>Percent</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </section>
  `;
}

function renderCompactTable(title, rows, columns) {
  if (!rows.length) {
    return "";
  }

  const headers = columns.map((column) => `<th>${escapeHtml(formatLabel(column))}</th>`).join("");
  const body = rows.map((row) => `
    <tr>
      ${columns.map((column) => `<td>${escapeHtml(formatCell(row[column]))}</td>`).join("")}
    </tr>
  `).join("");

  return `
    <section class="eda-section">
      <h5>${escapeHtml(title)}</h5>
      <table>
        <thead><tr>${headers}</tr></thead>
        <tbody>${body}</tbody>
      </table>
    </section>
  `;
}

function renderFeatureList(title, items) {
  if (!items || !items.length) {
    return "";
  }

  const rows = items.map((item) => `<tr><td>${escapeHtml(item)}</td></tr>`).join("");

  return `
    <section class="eda-section">
      <h5>${escapeHtml(title)}</h5>
      <table>
        <tbody>${rows}</tbody>
      </table>
    </section>
  `;
}

function formatLabel(value) {
  return String(value).replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatCell(value) {
  if (value === null || value === undefined) {
    return "";
  }

  if (typeof value === "number") {
    return Number.isInteger(value) ? formatNumber(value) : value.toFixed(3);
  }

  return value;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

loadProjects()
  .then(() => setStatus("Ready"))
  .catch((error) => setStatus(error.message, true));
