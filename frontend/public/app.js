const API_BASE = window.location.origin;

const state = {
  projects: [],
  selectedProject: null,
  datasets: [],
  edaReports: {},
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
    <div class="dataset-list" id="datasetList"></div>
  `;

  renderDatasets();
  document.querySelector("#uploadForm").addEventListener("submit", handleUpload);
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
    renderWorkspace();
    setStatus("Dataset saved");
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
