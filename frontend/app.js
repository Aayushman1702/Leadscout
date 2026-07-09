const API_BASE_URL = "http://127.0.0.1:8000";

const form = document.querySelector("#searchForm");
const categorySelect = document.querySelector("#category");
const resultsGrid = document.querySelector("#resultsGrid");
const statusLabel = document.querySelector("#status");
const selectAllCheckbox = document.querySelector("#selectAll");
const selectedCount = document.querySelector("#selectedCount");
const downloadBar = document.querySelector("#downloadBar");
const downloadCount = document.querySelector("#downloadCount");
const downloadSelectedButton = document.querySelector("#downloadSelected");

let allBusinesses = [];
let selectedBusinessKeys = new Set();
let selectedBusinesses = [];

async function loadCategories() {
  try {
    const response = await fetch(`${API_BASE_URL}/categories`);
    if (!response.ok) return;

    const data = await response.json();
    categorySelect.innerHTML = data.categories
      .map((category) => `<option value="${category.value}">${category.label}</option>`)
      .join("");
  } catch {
    statusLabel.textContent = "Using built-in categories";
  }
}

function valueOrDash(value) {
  return value || "-";
}

function businessKey(business, index) {
  return `business-${index}`;
}

function syncSelectedBusinesses() {
  selectedBusinesses = allBusinesses.filter((business, index) =>
    selectedBusinessKeys.has(businessKey(business, index))
  );
}

function updateSelectionUI() {
  syncSelectedBusinesses();
  const selectedTotal = selectedBusinesses.length;
  const hasResults = allBusinesses.length > 0;
  const allSelected = hasResults && selectedTotal === allBusinesses.length;

  selectedCount.textContent = `Selected: ${selectedTotal} Businesses`;
  downloadCount.textContent = `Selected: ${selectedTotal} Businesses`;
  downloadBar.hidden = selectedTotal === 0;
  selectAllCheckbox.checked = allSelected;
  selectAllCheckbox.indeterminate = selectedTotal > 0 && !allSelected;

  document.querySelectorAll(".card").forEach((card) => {
    card.classList.toggle("selected", selectedBusinessKeys.has(card.dataset.businessKey));
  });
}

function renderBusiness(business, index) {
  const key = businessKey(business, index);
  const website = business.website
    ? `<a href="${business.website}" target="_blank" rel="noreferrer">${business.website}</a>`
    : "-";

  return `
    <article class="card" data-business-key="${key}">
      <label class="card-select">
        <input class="business-checkbox" type="checkbox" data-business-key="${key}" />
        <h3>${valueOrDash(business.name)}</h3>
      </label>
      <div class="meta">
        <span class="pill">${valueOrDash(business.category)}</span>
        <span class="pill">Popularity ${business.popularity_score ?? "-"}</span>
        <span class="pill">Rating ${business.rating ?? "-"}</span>
      </div>
      <div class="row"><strong>Phone:</strong> ${valueOrDash(business.phone)}</div>
      <div class="row"><strong>Email:</strong> ${valueOrDash(business.email)}</div>
      <div class="row"><strong>Website:</strong> ${website}</div>
      <div class="row"><strong>Address:</strong> ${valueOrDash(business.address)}</div>
      <div class="row"><strong>Instagram:</strong> ${valueOrDash(business.instagram)}</div>
      <div class="row"><strong>Facebook:</strong> ${valueOrDash(business.facebook)}</div>
      <div class="row"><strong>LinkedIn:</strong> ${valueOrDash(business.linkedin)}</div>
      <div class="row"><strong>WhatsApp:</strong> ${valueOrDash(business.whatsapp)}</div>
    </article>
  `;
}

selectAllCheckbox.addEventListener("change", () => {
  if (selectAllCheckbox.checked) {
    selectedBusinessKeys = new Set(allBusinesses.map(businessKey));
  } else {
    selectedBusinessKeys.clear();
  }

  document.querySelectorAll(".business-checkbox").forEach((checkbox) => {
    checkbox.checked = selectAllCheckbox.checked;
  });
  updateSelectionUI();
});

resultsGrid.addEventListener("change", (event) => {
  if (!event.target.classList.contains("business-checkbox")) return;

  const key = event.target.dataset.businessKey;
  if (event.target.checked) {
    selectedBusinessKeys.add(key);
  } else {
    selectedBusinessKeys.delete(key);
  }
  updateSelectionUI();
});

downloadSelectedButton.addEventListener("click", async () => {
  if (selectedBusinesses.length === 0) return;

  downloadSelectedButton.disabled = true;
  statusLabel.textContent = "Preparing Excel export...";

  try {
    const response = await fetch(`${API_BASE_URL}/export`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ businesses: selectedBusinesses }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Export failed");
    }

    const blob = await response.blob();
    const disposition = response.headers.get("Content-Disposition") || "";
    const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
    const filename = filenameMatch?.[1] || "selected_businesses.xlsx";
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    statusLabel.textContent = "Excel export downloaded";
  } catch (error) {
    statusLabel.textContent = error.message;
  } finally {
    downloadSelectedButton.disabled = false;
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = form.querySelector("button");
  const formData = new FormData(form);

  submitButton.disabled = true;
  statusLabel.textContent = "Searching...";
  resultsGrid.innerHTML = "";
  allBusinesses = [];
  selectedBusinessKeys.clear();
  updateSelectionUI();

  try {
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        location: formData.get("location"),
        state: formData.get("state") || null,
        category: formData.get("category"),
        limit: Number(formData.get("limit") || 100),
        popularity_filter: formData.get("popularity_filter") || null,
      }),
    });

    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new Error(data.detail || data.message || "Search failed");
    }

    statusLabel.textContent = `${data.total_results} businesses found`;
    allBusinesses = data.businesses;
    resultsGrid.innerHTML = allBusinesses.map(renderBusiness).join("");
    updateSelectionUI();
  } catch (error) {
    statusLabel.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});

loadCategories();
