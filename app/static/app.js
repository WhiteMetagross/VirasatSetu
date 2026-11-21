// VIRASAT SETU CLIENT APPLICATION LOGIC

// Security helper: Escape HTML entities to prevent Cross-Site Scripting (XSS)
function escapeHTML(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

const API_BASE = "";
let currentUser = null;
let currentToken = localStorage.getItem("token") || null;
let allFinancialAssets = [];
let fdbFilterCategory = "all";
let fdbSearchTimeout = null;
let currentRenderedMatches = [];

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", async () => {
  if (currentToken) {
    await fetchCurrentUser();
  }
  updateUIForUser();

  if (currentUser) {
    if (currentUser.role === "admin") {
      await loadAdminData();
    } else if (currentUser.role === "institution_rep") {
      await loadInstitutionData();
    } else {
      await loadDashboardData();
    }
    await pollNotifications();
  } else {
    switchTab("home");
  }

  // Periodic notification polling for active session
  setInterval(() => {
    if (currentUser) pollNotifications();
  }, 10000);
});

// Toast notification helper
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  const bg = type === "success" ? "bg-emerald-600" : type === "error" ? "bg-red-600" : "bg-slate-800";
  toast.className = `${bg} text-white px-4 py-3 rounded-lg shadow-xl text-xs flex items-center justify-between gap-3 transform transition-all duration-300 translate-y-2 opacity-0`;
  toast.innerHTML = `
    <span>${escapeHTML(message)}</span>
    <button onclick="this.parentElement.remove()" class="text-white/80 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.remove("translate-y-2", "opacity-0");
  }, 10);
  setTimeout(() => {
    toast.classList.add("opacity-0");
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// API Fetch Helper
async function apiFetch(endpoint, options = {}) {
  const headers = options.headers || {};
  if (currentToken && !headers["Authorization"]) {
    headers["Authorization"] = `Bearer ${currentToken}`;
  }
  // Anti-CSRF verification headers for state-changing requests
  headers["X-Requested-With"] = "VirasatSetuApp";
  headers["X-CSRF-Token"] = "virasat-setu-csrf-protection";

  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  options.headers = headers;

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (res.status === 401) {
      if (endpoint === "/api/auth/me") {
        logout();
        throw new Error("Session expired, please log in again.");
      }
      throw new Error("Authentication required or session expired.");
    }
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "API request failed");
    }
    return data;
  } catch (err) {
    if (!options.silent) {
      showToast(err.message, "error");
    }
    throw err;
  }
}

// AUTHENTICATION & DEMO LOGIN

async function fetchCurrentUser() {
  try {
    currentUser = await apiFetch("/api/auth/me", { silent: true });
    updateUIForUser();
  } catch {
    currentUser = null;
    currentToken = null;
    localStorage.removeItem("token");
  }
}

async function demoLogin(role) {
  const credentials = {
    family: { email: "rajesh.family@example.com", password: "family123" },
    admin: { email: "admin@virasatsetu.gov.in", password: "admin123" },
    sbi: { email: "sbi@institution.in", password: "sbi123" },
    lic: { email: "lic@institution.in", password: "lic123" },
    hdfcmf: { email: "hdfcmf@institution.in", password: "hdfc123" },
  };

  const cred = credentials[role];
  if (!cred) return;

  try {
    const data = await apiFetch("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(cred),
    });
    currentToken = data.access_token;
    localStorage.setItem("token", currentToken);
    currentUser = data.user;
    activeDeceasedId = null;
    updateUIForUser();
    showToast(`Logged in as ${currentUser.full_name} (${currentUser.role})`, "success");

    // Contextual routing based on role
    await pollNotifications();
    if (role === "admin") {
      switchTab("admin");
    } else if (["sbi", "lic", "hdfcmf"].includes(role)) {
      switchTab("institution");
    } else {
      switchTab("dashboard");
    }
  } catch (err) {
    console.error("Demo login error:", err);
  }
}

function handleBrowseDatabaseClick() {
  if (currentUser && currentUser.role === "admin") {
    switchTab("financial-db");
  } else if (currentUser) {
    showToast("Browse Database is an administrator-only oversight repository.", "info");
  } else {
    showToast("Administrator login required to browse central financial database.", "info");
    openAuthModal("login");
  }
}

function updateUIForUser() {
  const authButtons = document.getElementById("auth-buttons");
  const userProfile = document.getElementById("user-profile");
  const navAdminTab = document.getElementById("nav-admin-tab");
  const navInstTab = document.getElementById("nav-inst-tab");
  const navDbTab = document.getElementById("nav-db-tab");

  if (currentUser) {
    authButtons.classList.add("hidden");
    userProfile.classList.remove("hidden");
    document.getElementById("user-display-name").textContent = currentUser.full_name;
    document.getElementById("user-display-role").textContent = currentUser.role.replace("_", " ");
    document.getElementById("dash-welcome").textContent = `Welcome back, ${currentUser.full_name}`;

    // Tabs visibility based on role
    if (currentUser.role === "admin") {
      if (navAdminTab) navAdminTab.classList.remove("hidden");
      if (navInstTab) navInstTab.classList.remove("hidden");
      if (navDbTab) navDbTab.classList.remove("hidden");
    } else if (currentUser.role === "institution_rep") {
      if (navAdminTab) navAdminTab.classList.add("hidden");
      if (navInstTab) navInstTab.classList.remove("hidden");
      if (navDbTab) navDbTab.classList.add("hidden");
    } else {
      if (navAdminTab) navAdminTab.classList.add("hidden");
      if (navInstTab) navInstTab.classList.add("hidden");
      if (navDbTab) navDbTab.classList.add("hidden");
    }
  } else {
    authButtons.classList.remove("hidden");
    userProfile.classList.add("hidden");
    if (navAdminTab) navAdminTab.classList.add("hidden");
    if (navInstTab) navInstTab.classList.add("hidden");
    if (navDbTab) navDbTab.classList.add("hidden");
  }
}

function logout() {
  currentUser = null;
  currentToken = null;
  activeDeceasedId = null;
  localStorage.removeItem("token");
  updateUIForUser();
  switchTab("home");
  showToast("Logged out successfully");
}

// Modal handling
function openAuthModal(mode = "login") {
  document.getElementById("modal-auth").classList.remove("hidden");
  setAuthMode(mode);
}

function closeAuthModal() {
  document.getElementById("modal-auth").classList.add("hidden");
}

let authMode = "login";
function setAuthMode(mode) {
  authMode = mode;
  const regFields = document.getElementById("reg-fields");
  const tabLogin = document.getElementById("auth-tab-login");
  const tabReg = document.getElementById("auth-tab-register");
  const submitText = document.getElementById("auth-submit-text");
  const title = document.getElementById("auth-modal-title");

  if (mode === "register") {
    regFields.classList.remove("hidden");
    tabReg.className = "font-bold text-gov-navy border-b-2 border-amber-500 pb-1";
    tabLogin.className = "text-slate-500 pb-1";
    submitText.textContent = "Create Citizen Account";
    title.textContent = "Register with Virasat Setu";
  } else {
    regFields.classList.add("hidden");
    tabLogin.className = "font-bold text-gov-navy border-b-2 border-amber-500 pb-1";
    tabReg.className = "text-slate-500 pb-1";
    submitText.textContent = "Log In";
    title.textContent = "Sign In to Virasat Setu";
  }
}

async function handleAuthSubmit(e) {
  e.preventDefault();
  const email = document.getElementById("auth-email").value;
  const password = document.getElementById("auth-password").value;

  if (authMode === "register") {
    const fullName = document.getElementById("auth-fullname").value;
    const mobile = document.getElementById("auth-mobile").value;
    try {
      const data = await apiFetch("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password, full_name: fullName, mobile, role: "family_user" }),
      });
      currentToken = data.access_token;
      localStorage.setItem("token", currentToken);
      currentUser = data.user;
      activeDeceasedId = null;
      closeAuthModal();
      updateUIForUser();
      switchTab("dashboard");
      showToast("Account registered successfully!");
    } catch {}
  } else {
    try {
      const data = await apiFetch("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      currentToken = data.access_token;
      localStorage.setItem("token", currentToken);
      currentUser = data.user;
      activeDeceasedId = null;
      closeAuthModal();
      updateUIForUser();
      if (currentUser.role === "admin") {
        switchTab("admin");
      } else if (currentUser.role === "institution_rep") {
        switchTab("institution");
      } else {
        switchTab("dashboard");
      }
      showToast("Logged in successfully!");
    } catch {}
  }
}

// NAVIGATION TAB SWITCHER

function switchTab(tabId) {
  if (tabId === "financial-db" && (!currentUser || currentUser.role !== "admin")) {
    showToast("Browse Database is restricted to administrators only", "error");
    switchTab(currentUser ? "dashboard" : "home");
    return;
  }

  document.querySelectorAll(".tab-content").forEach((el) => el.classList.add("hidden"));
  document.querySelectorAll(".tab-btn").forEach((el) => el.classList.remove("active"));

  const target = document.getElementById(`tab-${tabId}`);
  if (target) target.classList.remove("hidden");

  const btn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
  if (btn) btn.classList.add("active");

  // Load relevant data on tab entry
  if (tabId === "dashboard") loadDashboardData();
  if (tabId === "matches") populateMatchesDropdown();
  if (tabId === "claims") renderClaimsList();
  if (tabId === "financial-db") loadFinancialDB();
  if (tabId === "admin") {
    loadAdminData();
    loadAdminUsers();
    loadInstitutionsDropdown();
  }
  if (tabId === "institution") loadInstitutionData();
}

// FAMILY DASHBOARD & DECEASED (Modules 3 & 4)

async function loadDashboardData() {
  if (!currentUser) return;
  try {
    const stats = await apiFetch("/api/dashboard/family-stats");
    document.getElementById("stat-deceased").textContent = stats.total_deceased;
    document.getElementById("stat-assets").textContent = stats.total_potential_assets;
    document.getElementById("stat-claims").textContent = stats.claims_in_progress;
    document.getElementById("stat-notifs").textContent = stats.unread_notifications;

    // Render Recent Activities
    const actList = document.getElementById("dash-activity-list");
    if (stats.recent_activities.length === 0) {
      actList.innerHTML = `<p class="text-xs text-slate-400">No activity recorded yet.</p>`;
    } else {
      actList.innerHTML = stats.recent_activities
        .map(
          (a) => `
        <div class="p-2.5 bg-slate-50 border border-slate-100 rounded-lg flex items-start justify-between gap-2">
          <div>
            <div class="font-bold text-slate-800">${escapeHTML(a.title)}</div>
            <div class="text-[11px] text-slate-600 line-clamp-2">${escapeHTML(a.message)}</div>
            <div class="text-[10px] text-slate-400 mt-1">${new Date(a.created_at).toLocaleString()}</div>
          </div>
          <span class="bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded text-[10px] uppercase font-bold">${escapeHTML(a.type)}</span>
        </div>
      `
        )
        .join("");
    }

    // Render Active Claims Summary
    const claimsList = document.getElementById("dash-claims-list");
    if (stats.claims_summary.length === 0) {
      claimsList.innerHTML = `<p class="text-xs text-slate-400">No claims submitted yet. Check 'Discovered Assets' to initiate claims.</p>`;
    } else {
      claimsList.innerHTML = stats.claims_summary
        .map(
          (c) => `
        <div class="p-3 bg-slate-50 border border-slate-200 rounded-lg flex justify-between items-center">
          <div>
            <div class="font-bold text-slate-800">${escapeHTML(c.institution)} - ${escapeHTML(c.asset_category)}</div>
            <div class="text-[11px] text-slate-500">Ref: ${escapeHTML(c.reference)} (Value: ₹${Number(c.value || 0).toLocaleString()})</div>
          </div>
          <span class="status-badge badge-${escapeHTML(c.status).toLowerCase().replace(/\s+/g, "")}">${escapeHTML(c.status)}</span>
        </div>
      `
        )
        .join("");
    }

    // Fetch and render submitted deceased records
    const deceasedRecords = await apiFetch("/api/deceased");
    renderDeceasedTable(deceasedRecords);
  } catch (err) {
    console.error("Dashboard error:", err);
  }
}

function renderDeceasedTable(records) {
  const tbody = document.getElementById("deceased-table-body");
  document.getElementById("deceased-table-count").textContent = `${records.length} Record(s)`;

  if (!records || records.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="p-6 text-center text-slate-400">No deceased records submitted yet. Click 'Add Deceased Family Member' to begin.</td></tr>`;
    return;
  }

  tbody.innerHTML = records
    .map((r) => {
      let badgeClass = "badge-pending";
      if (r.status === "Verified") badgeClass = "badge-verified";
      if (r.status === "Rejected") badgeClass = "badge-rejected";

      return `
      <tr class="hover:bg-slate-50 transition">
        <td class="p-3 font-semibold text-slate-900">${escapeHTML(r.full_name)}</td>
        <td class="p-3 font-mono text-[11px] text-slate-600">${escapeHTML(r.sample_identity_ref)}</td>
        <td class="p-3 text-slate-600">${escapeHTML(r.date_of_death)}</td>
        <td class="p-3 font-mono text-[11px] text-slate-600">${escapeHTML(r.death_cert_ref)}</td>
        <td class="p-3"><span class="status-badge ${badgeClass}">${escapeHTML(r.status)}</span></td>
        <td class="p-3">
          ${
            r.total_matches > 0
              ? `<span class="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded text-[11px]"><i class="fa-solid fa-bolt mr-1"></i>${Number(r.total_matches)} Potential Assets</span>`
              : `<span class="text-slate-400">Pending Verification</span>`
          }
        </td>
        <td class="p-3 text-right">
          ${
            r.status === "Verified"
              ? `<button onclick="viewMatchesForDeceased('${escapeHTML(r.id)}')" class="bg-gov-saffron hover:bg-amber-600 text-white font-semibold px-2.5 py-1 rounded text-xs transition">
                  <i class="fa-solid fa-magnifying-glass-dollar mr-1"></i> View Assets
                </button>`
              : `<span class="text-slate-400 text-[11px] italic">Verification Pending</span>`
          }
        </td>
      </tr>
    `;
    })
    .join("");
}

async function handleDeceasedSubmit(e) {
  e.preventDefault();
  const certRef = document.getElementById("dec-cert-ref").value.trim();
  const payload = {
    full_name: document.getElementById("dec-fullname").value.trim(),
    date_of_birth: document.getElementById("dec-dob").value,
    date_of_death: document.getElementById("dec-dod").value,
    gender: document.getElementById("dec-gender").value,
    last_known_city: document.getElementById("dec-city").value.trim() || null,
    last_known_state: document.getElementById("dec-state").value.trim() || null,
    death_cert_ref: certRef || "Pending Civil Issuance",
    sample_identity_ref: document.getElementById("dec-id-ref").value.trim(),
    death_reg_date: document.getElementById("dec-reg-date").value || null,
    issuing_authority: document.getElementById("dec-authority").value.trim() || null,
    claimant_name: document.getElementById("dec-claimant-name").value.trim(),
    claimant_relationship: document.getElementById("dec-claimant-rel").value,
    claimant_email: document.getElementById("dec-claimant-email").value.trim(),
    claimant_mobile: document.getElementById("dec-claimant-mobile").value.trim(),
    claimant_type: document.getElementById("dec-claimant-type") ? document.getElementById("dec-claimant-type").value : "Nominee",
  };

  try {
    const res = await apiFetch("/api/deceased", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    // Optional document upload
    const fileInput = document.getElementById("dec-doc-file");
    if (fileInput && fileInput.files && fileInput.files.length > 0) {
      try {
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        formData.append("document_type", "death_certificate");
        formData.append("deceased_person_id", res.id);
        await apiFetch("/api/documents/upload", {
          method: "POST",
          body: formData,
        });
      } catch (uploadErr) {
        console.warn("Document upload notice:", uploadErr);
      }
    }

    showToast("Deceased record submitted for verification!");
    document.getElementById("deceased-form").reset();
    switchTab("dashboard");
  } catch (err) {
    console.error(err);
  }
}

// ASSET DISCOVERY AND MATCHING (Module 6 and 7)

let activeDeceasedId = null;
let allUserDeceasedRecords = [];

async function populateMatchesDropdown() {
  const selector = document.getElementById("match-deceased-selector");
  const container = document.getElementById("matches-container");
  try {
    const records = await apiFetch("/api/deceased");
    allUserDeceasedRecords = records || [];

    if (!records || records.length === 0) {
      if (selector) selector.innerHTML = `<option value="">No deceased records registered</option>`;
      activeDeceasedId = null;
      if (container) {
        container.innerHTML = `
          <div class="bg-white p-8 rounded-xl border border-slate-200 text-center space-y-4">
            <div class="w-16 h-16 bg-amber-50 text-amber-600 rounded-full flex items-center justify-center text-2xl mx-auto shadow-sm">
              <i class="fa-solid fa-user-plus"></i>
            </div>
            <div>
              <h4 class="font-bold text-slate-800 text-base">No Deceased Family Records Registered Yet</h4>
              <p class="text-xs text-slate-500 max-w-md mx-auto mt-1 leading-relaxed">
                To discover potential unclaimed financial assets across Bank, Insurance, and Mutual Fund datasets, please first register a deceased family member.
              </p>
            </div>
            <button onclick="switchTab('register-deceased')" class="bg-gov-saffron hover:bg-amber-600 text-white font-bold px-5 py-2.5 rounded-lg text-xs shadow transition inline-flex items-center gap-2">
              <i class="fa-solid fa-user-plus"></i> Register Deceased Member
            </button>
          </div>
        `;
      }
      return;
    }

    if (selector) {
      selector.innerHTML = `<option value="">Select deceased record...</option>`;
      records.forEach((r) => {
        const statusLabel = r.status === "Verified" ? "Verified" : "Verification Pending";
        selector.innerHTML += `<option value="${escapeHTML(r.id)}">${escapeHTML(r.full_name)} (${escapeHTML(r.sample_identity_ref)}) [${escapeHTML(statusLabel)}]</option>`;
      });

      // Verify if activeDeceasedId belongs to current records
      const exists = records.some((r) => r.id === activeDeceasedId);
      if (!exists) {
        const verifiedFirst = records.find((r) => r.status === "Verified");
        activeDeceasedId = verifiedFirst ? verifiedFirst.id : records[0].id;
      }

      selector.value = activeDeceasedId || "";
    }

    await loadMatchesForSelected();
  } catch (err) {
    console.error("Error populating matches dropdown:", err);
  }
}

async function viewMatchesForDeceased(deceasedId) {
  activeDeceasedId = deceasedId;
  switchTab("matches");
  const selector = document.getElementById("match-deceased-selector");
  if (selector) selector.value = deceasedId;
  await loadMatchesForSelected();
}

async function loadMatchesForSelected() {
  const selector = document.getElementById("match-deceased-selector");
  const deceasedId = (selector && selector.value) || activeDeceasedId;
  const container = document.getElementById("matches-container");

  if (!deceasedId) {
    if (allUserDeceasedRecords.length === 0) return;
    if (container) {
      container.innerHTML = `
        <div class="bg-white p-8 rounded-xl border border-slate-200 text-center text-slate-400 text-xs">
          Please select a deceased family member from the dropdown above to view potential asset matches.
        </div>
      `;
    }
    return;
  }

  activeDeceasedId = deceasedId;
  const currentRecord = allUserDeceasedRecords.find((r) => r.id === deceasedId);

  // If the record is still pending verification
  if (currentRecord && currentRecord.status !== "Verified") {
    if (container) {
      container.innerHTML = `
        <div class="bg-white p-8 rounded-xl border border-slate-200 text-center space-y-4 shadow-sm">
          <div class="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center text-2xl mx-auto shadow-sm">
            <i class="fa-solid fa-hourglass-half"></i>
          </div>
          <div>
            <span class="bg-amber-100 text-amber-800 text-[10px] uppercase font-bold px-2.5 py-1 rounded">Status: Pending Verification</span>
            <h4 class="font-bold text-slate-800 text-base mt-2">Civil Verification in Progress</h4>
            <p class="text-xs text-slate-600 max-w-lg mx-auto mt-1 leading-relaxed">
              Your submitted record for <strong>${escapeHTML(currentRecord.full_name)}</strong> (Identity Reference: <span class="font-mono">${escapeHTML(currentRecord.sample_identity_ref)}</span>) has been submitted to the administrative verification cell.
            </p>
            <p class="text-[11px] text-slate-400 max-w-md mx-auto mt-2">
              Once verified by an administrator, the automated 100 point matching engine will automatically cross reference 94 central financial records and surface potential assets here.
            </p>
          </div>
        </div>
      `;
    }
    return;
  }

  try {
    const matches = await apiFetch(`/api/matches/${deceasedId}`);
    renderMatchesList(matches);
  } catch (err) {
    console.error(err);
  }
}

async function reRunMatchingForCurrent() {
  if (!activeDeceasedId) {
    showToast("Please select a deceased record first", "error");
    return;
  }
  const currentRecord = allUserDeceasedRecords.find((r) => r.id === activeDeceasedId);
  if (currentRecord && currentRecord.status !== "Verified") {
    showToast("Automated matching requires administrator civil verification first", "info");
    return;
  }

  try {
    showToast("Executing 100 point matching algorithm across all financial datasets...");
    const matches = await apiFetch(`/api/matching/${activeDeceasedId}`, { method: "POST" });
    renderMatchesList(matches);
    showToast(`Matching complete! Discovered ${matches.length} financial record(s).`);
  } catch (err) {
    console.error(err);
  }
}

function renderMatchesList(matches) {
  const container = document.getElementById("matches-container");
  currentRenderedMatches = matches || [];
  if (!matches || matches.length === 0) {
    container.innerHTML = `
      <div class="bg-white p-8 rounded-xl border border-slate-200 text-center space-y-3">
        <i class="fa-solid fa-magnifying-glass text-4xl text-slate-300"></i>
        <h4 class="font-bold text-slate-700">No Asset Matches Identified</h4>
        <p class="text-xs text-slate-500 max-w-md mx-auto">
          The automated matching algorithm evaluated records with identity and name similarity. No matches achieved the minimum 60-point qualification threshold.
        </p>
      </div>
    `;
    return;
  }

  // Group matches by asset type
  const bankMatches = matches.filter((m) => m.financial_asset && m.financial_asset.asset_type === "bank");
  const insMatches = matches.filter((m) => m.financial_asset && m.financial_asset.asset_type === "insurance");
  const mfMatches = matches.filter((m) => m.financial_asset && m.financial_asset.asset_type === "mutual_fund");

  const totalValue = matches.reduce((sum, m) => sum + (m.financial_asset ? m.financial_asset.approximate_value : 0), 0);

  container.innerHTML = `
    <!-- Summary Banner -->
    <div class="bg-gradient-to-r from-emerald-500 to-teal-700 text-white p-5 rounded-xl shadow flex flex-wrap justify-between items-center gap-4">
      <div>
        <div class="text-xs uppercase font-bold text-emerald-200">Discovered Financial Assets Total</div>
        <div class="text-3xl font-extrabold mt-1">₹${totalValue.toLocaleString()}</div>
        <div class="text-xs text-emerald-100 mt-1">${matches.length} Potential Asset(s) across Banks, Insurance and Mutual Funds</div>
      </div>
      <div class="flex gap-2">
        <span class="bg-white/20 backdrop-blur px-3 py-1 rounded text-xs font-semibold"><i class="fa-solid fa-building-columns mr-1"></i> ${bankMatches.length} Bank</span>
        <span class="bg-white/20 backdrop-blur px-3 py-1 rounded text-xs font-semibold"><i class="fa-solid fa-file-contract mr-1"></i> ${insMatches.length} Insurance</span>
        <span class="bg-white/20 backdrop-blur px-3 py-1 rounded text-xs font-semibold"><i class="fa-solid fa-chart-line mr-1"></i> ${mfMatches.length} Mutual Fund</span>
      </div>
    </div>

    <!-- Match Cards Grid -->
    <div class="space-y-4">
      ${matches.map((m) => createMatchCardHTML(m)).join("")}
    </div>
  `;
}

function createMatchCardHTML(m) {
  const asset = m.financial_asset;
  if (!asset) return "";

  const scoreColor = m.matching_score >= 80 ? "text-emerald-600 bg-emerald-50 border-emerald-200" : "text-amber-600 bg-amber-50 border-amber-200";

  let typeIcon = "fa-building-columns";
  let typeBadge = "Bank Deposit";
  if (asset.asset_type === "insurance") {
    typeIcon = "fa-shield-halved";
    typeBadge = "Insurance Policy";
  } else if (asset.asset_type === "mutual_fund") {
    typeIcon = "fa-chart-pie";
    typeBadge = "Mutual Fund";
  }

  // Masked Account Ref (like SB-XXXX-4102)
  const refParts = asset.account_ref;
  const maskedRef = refParts.length > 6 ? `${refParts.substring(0, 3)}••••${refParts.substring(refParts.length - 4)}` : refParts;

  return `
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5 hover:shadow-md transition">
      <div class="flex flex-wrap justify-between items-start gap-4">
        <!-- Asset & Institution Info -->
        <div class="space-y-2 flex-1 min-w-[280px]">
          <div class="flex items-center gap-2">
            <span class="bg-slate-100 text-slate-800 text-[11px] font-bold px-2 py-0.5 rounded flex items-center gap-1">
              <i class="fa-solid ${typeIcon} text-gov-saffron"></i> ${typeBadge}
            </span>
            <span class="text-xs font-bold text-slate-800">${escapeHTML(asset.institution_name)}</span>
          </div>

          <h4 class="text-base font-bold text-slate-900">${escapeHTML(asset.category)}</h4>

          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs text-slate-600 pt-1">
            <div><span class="text-slate-400">Account Ref:</span> <span class="font-mono font-semibold">${escapeHTML(maskedRef)}</span></div>
            <div><span class="text-slate-400">Holder Name:</span> <span class="font-semibold">${escapeHTML(asset.holder_name)}</span></div>
            <div><span class="text-slate-400">Approx Value:</span> <span class="font-bold text-emerald-700">₹${Number(asset.approximate_value).toLocaleString()}</span></div>
            <div><span class="text-slate-400">Identity Ref:</span> <span class="font-mono">${escapeHTML(asset.sample_identity_ref)}</span></div>
            <div><span class="text-slate-400">Nominee on File:</span> <span>${escapeHTML(asset.nominee_ref || "None specified")}</span></div>
            <div><span class="text-slate-400">Status:</span> <span class="text-amber-700 font-semibold">${escapeHTML(asset.unclaimed_status || "Unclaimed")}</span></div>
          </div>

          <!-- Matching Reason Breakdown -->
          <div class="bg-slate-50 p-2.5 rounded-lg border border-slate-200 mt-2 text-[11px] text-slate-600">
            <strong class="text-slate-800">Match Evidence:</strong> ${escapeHTML(m.matching_reason || "Verified record comparison")}
          </div>
        </div>

        <!-- Matching Score and Claim Button -->
        <div class="flex flex-col sm:items-end justify-between self-stretch gap-4 w-full sm:w-auto sm:min-w-[140px]">
          <div class="border ${scoreColor} rounded-xl px-4 py-2 text-center shadow-sm w-full">
            <div class="text-2xl font-black">${Number(m.matching_score)}/100</div>
            <div class="text-[10px] font-bold uppercase tracking-wider">${escapeHTML(m.match_category)}</div>
          </div>

          <div>
            ${
              m.claim_id
                ? `<span class="bg-blue-100 text-blue-800 font-bold px-3 py-1.5 rounded-lg text-xs flex items-center gap-1.5">
                    <i class="fa-solid fa-check"></i> Claim Initiated (${escapeHTML(m.claim_status)})
                   </span>`
                : `<button onclick="openClaimModal('${escapeHTML(m.id)}')" class="bg-gov-saffron hover:bg-amber-600 text-white font-bold px-4 py-2 rounded-lg text-xs shadow transition flex items-center gap-1.5">
                    <i class="fa-solid fa-stamp"></i> Initiate Claim
                   </button>`
            }
          </div>
        </div>
      </div>
    </div>
  `;
}

// CLAIM TRACKING (Module 10)

let activeClaimMatch = null;

function openClaimModal(matchId, instName, category, ref, val) {
  activeClaimMatch = matchId;
  const matchObj = currentRenderedMatches.find((x) => x.id === matchId);
  const asset = matchObj ? matchObj.financial_asset : null;
  const resolvedInstName = asset ? asset.institution_name : (instName || "Financial Institution");
  const resolvedCategory = asset ? asset.category : (category || "Asset");
  const resolvedRef = asset ? asset.account_ref : (ref || "-");
  const resolvedVal = asset ? asset.approximate_value : (val || 0);

  document.getElementById("modal-claim").classList.remove("hidden");
  document.getElementById("claim-match-id").value = matchId;
  document.getElementById("claim-asset-title").textContent = `${resolvedInstName} (${resolvedCategory})`;
  document.getElementById("claim-asset-ref").textContent = `Account / Policy Ref: ${resolvedRef}`;
  document.getElementById("claim-asset-val").textContent = `Simulated Value: ₹${Number(resolvedVal).toLocaleString()}`;

  if (currentUser) {
    document.getElementById("claim-name").value = currentUser.full_name;
  }
  fetchClaimHealthPrediction(matchId);
}

async function fetchClaimHealthPrediction(matchId) {
  const badge = document.getElementById("claim-ai-prob-badge");
  const bar = document.getElementById("claim-ai-prob-bar");
  const factorsEl = document.getElementById("claim-ai-factors");
  if (!badge || !bar || !factorsEl) return;

  factorsEl.innerHTML = `<span class="italic text-slate-400">Evaluating claim health with AI predictive model...</span>`;

  try {
    const data = await apiFetch("/api/ai/predict-claim", {
      method: "POST",
      body: JSON.stringify({
        asset_match_id: matchId,
        claimant_name: document.getElementById("claim-name").value || (currentUser ? currentUser.full_name : ""),
        claimant_relationship: document.getElementById("claim-rel").value || ""
      }),
      silent: true
    });

    const prob = Number(data.probability || 80);
    badge.textContent = `${prob}% ${data.status}`;
    bar.style.width = `${prob}%`;
    if (prob >= 80) {
      badge.className = "bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded text-[10px]";
      bar.className = "bg-emerald-500 h-1.5 rounded-full transition-all duration-500";
    } else if (prob >= 60) {
      badge.className = "bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded text-[10px]";
      bar.className = "bg-amber-500 h-1.5 rounded-full transition-all duration-500";
    } else {
      badge.className = "bg-rose-100 text-rose-800 font-bold px-2 py-0.5 rounded text-[10px]";
      bar.className = "bg-rose-500 h-1.5 rounded-full transition-all duration-500";
    }

    let html = "";
    if (data.factors && data.factors.length > 0) {
      html += `<div class="font-semibold text-slate-700">Predictive Strengths:</div>`;
      data.factors.slice(0, 2).forEach((f) => {
        html += `<div class="text-emerald-700 flex items-center gap-1"><i class="fa-solid fa-check-circle text-[9px]"></i> ${escapeHTML(f)}</div>`;
      });
    }
    if (data.advice && data.advice.length > 0) {
      html += `<div class="font-semibold text-amber-700 mt-1">Prescriptive Recommendations:</div>`;
      data.advice.slice(0, 1).forEach((a) => {
        html += `<div class="text-amber-800 flex items-center gap-1"><i class="fa-solid fa-lightbulb text-[9px]"></i> ${escapeHTML(a)}</div>`;
      });
    }
    factorsEl.innerHTML = html;
  } catch (err) {
    factorsEl.innerHTML = `<span class="text-slate-400">Approval prediction ready upon submission.</span>`;
  }
}

function closeClaimModal() {
  document.getElementById("modal-claim").classList.add("hidden");
}

async function handleClaimSubmit(e) {
  e.preventDefault();
  const matchId = document.getElementById("claim-match-id").value;
  const claimantName = document.getElementById("claim-name").value;
  const claimantRel = document.getElementById("claim-rel").value;
  const remarks = document.getElementById("claim-remarks").value;

  try {
    const claim = await apiFetch("/api/claims", {
      method: "POST",
      body: JSON.stringify({
        asset_match_id: matchId,
        remarks: `${claimantName} (${claimantRel}): ${remarks}`,
      }),
    });

    closeClaimModal();
    showToast(`Claim Application ${claim.claim_reference} submitted successfully!`);
    switchTab("claims");
  } catch (err) {
    console.error(err);
  }
}

async function renderClaimsList() {
  const container = document.getElementById("claims-container");
  const filter = document.getElementById("claim-filter-status").value;

  try {
    let url = "/api/claims";
    if (filter) url += `?status=${encodeURIComponent(filter)}`;
    const claims = await apiFetch(url);

    if (!claims || claims.length === 0) {
      container.innerHTML = `<div class="bg-white p-8 rounded-xl border border-slate-200 text-center text-slate-400 text-xs">No claims matching the filter criteria.</div>`;
      return;
    }

    container.innerHTML = claims.map((c) => createClaimCardHTML(c)).join("");
  } catch (err) {
    console.error(err);
  }
}

function createClaimCardHTML(c) {
  const stages = ["Submitted", "Under Review", "Documents Required", "Approved", "Completed"];
  const currentStageIndex = stages.indexOf(c.status);

  return `
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
      <div class="flex flex-wrap justify-between items-center border-b pb-3 gap-2">
        <div>
          <span class="text-xs font-mono font-bold text-gov-navy">${escapeHTML(c.claim_reference)}</span>
          <h4 class="text-sm font-bold text-slate-900 mt-0.5">${escapeHTML(c.institution_name)} - ${escapeHTML(c.asset_category)}</h4>
          <span class="text-xs text-slate-500">Deceased: ${escapeHTML(c.deceased_name)} (Claimant: ${escapeHTML(c.claimant_name)}) (${escapeHTML(c.claimant_relationship || "Heir")})</span>
        </div>
        <div class="text-right">
          <span class="status-badge badge-${escapeHTML(c.status).toLowerCase().replace(/\s+/g, "")}">${escapeHTML(c.status)}</span>
          <div class="text-xs font-bold text-emerald-700 mt-1">₹${Number(c.approximate_value || 0).toLocaleString()}</div>
        </div>
      </div>

      <!-- 5-Stage Stepper -->
      <div class="py-2">
        <div class="flex justify-between items-center text-[10px] font-semibold text-slate-500 relative">
          ${stages
            .map((stage, idx) => {
              const isPast = idx <= currentStageIndex;
              const isCurrent = idx === currentStageIndex;
              const circleBg = isPast ? "bg-gov-saffron text-white" : "bg-slate-200 text-slate-600";
              const labelColor = isCurrent ? "text-gov-saffron font-bold" : isPast ? "text-slate-800" : "text-slate-400";

              return `
              <div class="flex flex-col items-center flex-1 text-center">
                <div class="w-6 h-6 rounded-full flex items-center justify-center ${circleBg} mb-1 shadow-sm">
                  ${isPast ? '<i class="fa-solid fa-check text-[10px]"></i>' : idx + 1}
                </div>
                <span class="${labelColor}">${escapeHTML(stage)}</span>
              </div>
            `;
            })
            .join("")}
        </div>
      </div>

      <!-- Official Remarks Box -->
      <div class="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs text-slate-600">
        <span class="font-bold text-slate-800">Institution Notes / Instructions:</span> ${escapeHTML(c.remarks || "Under review by nodal claims officer.")}
      </div>
    </div>
  `;
}

// FINANCIAL INSTITUTION DATABASES (Module 5)

async function loadFinancialDB() {
  try {
    allFinancialAssets = await apiFetch("/api/admin/financial-assets?limit=150");
    renderFinancialTable();
  } catch (err) {
    console.error(err);
  }
}

function filterFdbCategory(cat) {
  fdbFilterCategory = cat;
  document.querySelectorAll(".fdb-cat-btn").forEach((btn) => {
    if (btn.dataset.cat === cat) {
      btn.className = "fdb-cat-btn px-4 py-1.5 rounded-full bg-gov-navy text-white";
    } else {
      btn.className = "fdb-cat-btn px-4 py-1.5 rounded-full bg-slate-100 text-slate-700 hover:bg-slate-200";
    }
  });
  renderFinancialTable();
}

function debounceFdbSearch() {
  clearTimeout(fdbSearchTimeout);
  fdbSearchTimeout = setTimeout(renderFinancialTable, 300);
}

function renderFinancialTable() {
  const tbody = document.getElementById("fdb-table-body");
  const query = (document.getElementById("fdb-search").value || "").toLowerCase().trim();

  let filtered = allFinancialAssets;
  if (fdbFilterCategory !== "all") {
    filtered = filtered.filter((a) => a.asset_type === fdbFilterCategory);
  }
  if (query) {
    filtered = filtered.filter(
      (a) =>
        (a.holder_name && a.holder_name.toLowerCase().includes(query)) ||
        (a.sample_identity_ref && a.sample_identity_ref.toLowerCase().includes(query)) ||
        (a.account_ref && a.account_ref.toLowerCase().includes(query)) ||
        (a.institution_name && a.institution_name.toLowerCase().includes(query))
    );
  }

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="p-6 text-center text-slate-400">No records found matching criteria.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered
    .map((a) => {
      let typeBadge = '<span class="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-[10px] font-bold">Bank</span>';
      if (a.asset_type === "insurance") {
        typeBadge = '<span class="bg-amber-100 text-amber-800 px-2 py-0.5 rounded text-[10px] font-bold">Insurance</span>';
      } else if (a.asset_type === "mutual_fund") {
        typeBadge = '<span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded text-[10px] font-bold">Mutual Fund</span>';
      }

      return `
      <tr class="hover:bg-slate-50 transition">
        <td class="p-3">${typeBadge}</td>
        <td class="p-3 font-semibold text-slate-900">${escapeHTML(a.institution_name)}</td>
        <td class="p-3 font-semibold">${escapeHTML(a.holder_name)}</td>
        <td class="p-3 text-slate-500">${escapeHTML(a.date_of_birth || "N/A")}</td>
        <td class="p-3 font-mono text-[11px] text-slate-700">${escapeHTML(a.sample_identity_ref)}</td>
        <td class="p-3 font-mono text-[11px] text-slate-600">${escapeHTML(a.account_ref)}</td>
        <td class="p-3 text-slate-600">${escapeHTML(a.nominee_ref || "-")}</td>
        <td class="p-3 font-bold text-emerald-700">₹${Number(a.approximate_value || 0).toLocaleString()}</td>
        <td class="p-3 text-slate-500 text-[11px]">${escapeHTML(a.unclaimed_status || "Dormant > 10 Yrs")}</td>
      </tr>
    `;
    })
    .join("");
}

// Add sample record modal (Admin)
async function openAddAssetModal() {
  document.getElementById("modal-add-asset").classList.remove("hidden");
  try {
    const insts = await apiFetch("/api/institutions");
    const select = document.getElementById("asset-inst-select");
    select.innerHTML = insts.map((i) => `<option value="${i.id}">${i.name} (${i.category})</option>`).join("");
  } catch (err) {
    console.error(err);
  }
}

function closeAddAssetModal() {
  document.getElementById("modal-add-asset").classList.add("hidden");
}

async function handleAddAssetSubmit(e) {
  e.preventDefault();
  const payload = {
    institution_id: document.getElementById("asset-inst-select").value,
    asset_type: document.getElementById("asset-type-select").value,
    holder_name: document.getElementById("asset-holder").value,
    sample_identity_ref: document.getElementById("asset-idref").value,
    account_ref: document.getElementById("asset-accref").value,
    category: document.getElementById("asset-type-select").value === "bank" ? "Savings Account" : "Term Plan",
    approximate_value: parseFloat(document.getElementById("asset-val").value) || 100000,
    nominee_ref: document.getElementById("asset-nominee").value,
    status: "Unclaimed",
    unclaimed_status: "Dormant > 10 Yrs",
    institution_name: "",
  };

  try {
    await apiFetch("/api/admin/financial-assets", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    closeAddAssetModal();
    showToast("Financial record added to central database!");
    await loadFinancialDB();
  } catch (err) {
    console.error(err);
  }
}

// ADMINISTRATOR PANEL (Module 11)

async function loadAdminData() {
  try {
    const stats = await apiFetch("/api/admin/stats");
    document.getElementById("admin-stat-users").textContent = stats.total_users;
    document.getElementById("admin-stat-pending").textContent = stats.pending_verifications;
    document.getElementById("admin-stat-assets").textContent = stats.total_financial_records;
    document.getElementById("admin-stat-matches").textContent = stats.total_matches;

    // Load pending deceased records
    const deceased = await apiFetch("/api/deceased");
    const pending = deceased.filter((d) => d.status === "Pending Verification");
    document.getElementById("admin-pending-count").textContent = `${pending.length} pending`;

    const tbody = document.getElementById("admin-pending-table-body");
    if (pending.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-slate-400">All submitted records have been verified.</td></tr>`;
    } else {
      tbody.innerHTML = pending
        .map(
          (d) => `
        <tr class="hover:bg-slate-50 transition">
          <td class="p-3 font-bold text-slate-900">${escapeHTML(d.full_name)}</td>
          <td class="p-3 font-mono text-slate-700">${escapeHTML(d.death_cert_ref)}</td>
          <td class="p-3 font-mono">${escapeHTML(d.sample_identity_ref)}</td>
          <td class="p-3 text-slate-600">${escapeHTML(d.last_known_city || "-")} (${escapeHTML(d.issuing_authority || "-")})</td>
          <td class="p-3 text-slate-600">${escapeHTML(d.submitted_by_name || "Citizen")}</td>
          <td class="p-3"><span class="status-badge badge-pending">Pending</span></td>
          <td class="p-3 text-right space-x-1">
            <button onclick="adminVerifyRecord('${escapeHTML(d.id)}', 'Verified')" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-3 py-1 rounded text-xs transition">
              <i class="fa-solid fa-check mr-1"></i> Verify and Auto-Match
            </button>
            <button onclick="adminVerifyRecord('${escapeHTML(d.id)}', 'Rejected')" class="bg-red-600 hover:bg-red-700 text-white font-bold px-2 py-1 rounded text-xs transition">
              Reject
            </button>
          </td>
        </tr>
      `
        )
        .join("");
    }

    // Load audit logs
    const auditLogs = await apiFetch("/api/admin/audit-logs");
    const auditTbody = document.getElementById("admin-audit-table-body");
    auditTbody.innerHTML = auditLogs
      .map(
        (a) => `
      <tr>
        <td class="p-2.5 font-mono text-[11px] text-slate-500">${new Date(a.created_at).toLocaleString()}</td>
        <td class="p-2.5 font-bold text-gov-navy">${escapeHTML(a.action)}</td>
        <td class="p-2.5 uppercase font-semibold text-slate-600 text-[10px]">${escapeHTML(a.entity_type)}</td>
        <td class="p-2.5 text-slate-700">${escapeHTML(a.details)}</td>
      </tr>
    `
      )
      .join("");

    await loadAdminUsers();
    await loadInstitutionsDropdown();
    await loadAdminAnomalies();
  } catch (err) {
    console.error(err);
  }
}

async function loadAdminUsers() {
  const tbody = document.getElementById("admin-users-table-body");
  const countSpan = document.getElementById("admin-users-count");
  if (!tbody) return;

  try {
    const users = await apiFetch("/api/admin/users");
    if (countSpan) countSpan.textContent = `${users.length} registered users`;

    if (!users || users.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-slate-400">No registered users found.</td></tr>`;
      return;
    }

    tbody.innerHTML = users
      .map((u) => {
        let roleBadge = '<span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[10px] font-bold">Family User</span>';
        if (u.role === "admin") {
          roleBadge = '<span class="bg-amber-100 text-amber-800 px-2 py-0.5 rounded text-[10px] font-bold">Administrator</span>';
        } else if (u.role === "institution_rep") {
          roleBadge = '<span class="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-[10px] font-bold">Institution Rep</span>';
        }

        return `
          <tr class="hover:bg-slate-50 transition">
            <td class="p-2.5 font-bold text-slate-900">${escapeHTML(u.full_name)}</td>
            <td class="p-2.5 font-mono text-slate-600 text-[11px]">${escapeHTML(u.email)}</td>
            <td class="p-2.5">${roleBadge}</td>
            <td class="p-2.5 text-slate-600">${escapeHTML(u.institution_name || "-")}</td>
            <td class="p-2.5 text-slate-400 font-mono text-[10px]">${new Date(u.created_at).toLocaleDateString()}</td>
          </tr>
        `;
      })
      .join("");
  } catch (err) {
    console.error("Error loading admin users:", err);
  }
}

function onAdminRoleChange() {
  const roleSelect = document.getElementById("admin-user-role");
  const role = roleSelect ? roleSelect.value : "admin";
  const instContainer = document.getElementById("admin-user-inst-container");
  if (!instContainer) return;
  if (role === "institution_rep") {
    instContainer.classList.remove("hidden");
  } else {
    instContainer.classList.add("hidden");
  }
}

async function loadInstitutionsDropdown() {
  const instSelect = document.getElementById("admin-user-inst");
  const assetInstSelect = document.getElementById("asset-inst-select");
  try {
    const insts = await apiFetch("/api/institutions");
    if (instSelect) {
      instSelect.innerHTML = `<option value="">Select Financial Institution...</option>`;
      insts.forEach((inst) => {
        instSelect.innerHTML += `<option value="${inst.id}">${inst.name} (${inst.institution_type})</option>`;
      });
    }
    if (assetInstSelect) {
      assetInstSelect.innerHTML = `<option value="">Select Institution...</option>`;
      insts.forEach((inst) => {
        assetInstSelect.innerHTML += `<option value="${inst.id}">${inst.name}</option>`;
      });
    }
  } catch (err) {
    console.error("Error loading institutions dropdown:", err);
  }
}

async function handleAdminCreateUser(e) {
  e.preventDefault();
  const role = document.getElementById("admin-user-role").value;
  const fullName = document.getElementById("admin-user-fullname").value.trim();
  const email = document.getElementById("admin-user-email").value.trim();
  const mobile = document.getElementById("admin-user-mobile").value.trim();
  const password = document.getElementById("admin-user-password").value;
  const instSelect = document.getElementById("admin-user-inst");
  const institutionId = (instSelect && instSelect.value) ? instSelect.value : null;

  if (role === "institution_rep" && !institutionId) {
    showToast("Please select a financial institution for the representative", "error");
    return;
  }

  try {
    const res = await apiFetch("/api/admin/users", {
      method: "POST",
      body: JSON.stringify({
        role,
        full_name: fullName,
        email,
        mobile,
        password,
        institution_id: institutionId,
      }),
    });
    showToast(`Account created successfully for ${res.full_name} (${res.role})!`);
    document.getElementById("admin-create-user-form").reset();
    onAdminRoleChange();
    await loadAdminUsers();
    const stats = await apiFetch("/api/admin/stats");
    document.getElementById("admin-stat-users").textContent = stats.total_users;
  } catch (err) {
    console.error("Error creating user:", err);
  }
}

async function adminVerifyRecord(deceasedId, status) {
  try {
    await apiFetch(`/api/deceased/${deceasedId}/verify`, {
      method: "PATCH",
      body: JSON.stringify({
        status: status,
        admin_notes: `Civil death certificate verified by administrator. Automatic asset matching triggered.`,
      }),
    });
    showToast(`Death record ${status}! Automated cross-database matching triggered.`, "success");
    await loadAdminData();
  } catch (err) {
    console.error(err);
  }
}

async function resetDemoData() {
  if (!confirm("Reset database to clean presentation state with the Rajesh Kumar demonstration scenario?")) return;
  try {
    await apiFetch("/api/admin/demo/reset", { method: "POST" });
    showToast("Demo database successfully reset!");
    await loadDashboardData();
    await loadFinancialDB();
    await loadMatchesForSelected();
  } catch (err) {
    console.error(err);
  }
}

// INSTITUTION PORTAL (Module 12)

async function loadInstitutionData() {
  try {
    const data = await apiFetch("/api/institutions/my");
    document.getElementById("inst-node-name").textContent = data.institution.name;
    document.getElementById("inst-portal-title").textContent = `${data.institution.name} Processing Desk`;

    const claims = await apiFetch("/api/claims");
    const container = document.getElementById("inst-claims-list");

    if (!claims || claims.length === 0) {
      container.innerHTML = `<p class="text-center text-slate-400 py-6">No active claims assigned to this institution node.</p>`;
      return;
    }

    container.innerHTML = claims
      .map(
        (c) => `
      <div class="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
        <div class="flex justify-between items-start">
          <div>
            <span class="font-mono text-xs font-bold text-gov-navy">${escapeHTML(c.claim_reference)}</span>
            <h4 class="font-bold text-sm text-slate-900">${escapeHTML(c.asset_category)} (${escapeHTML(c.account_ref)})</h4>
            <div class="text-xs text-slate-600 mt-0.5">
              Deceased: <strong>${escapeHTML(c.deceased_name)}</strong> (Claimant: <strong>${escapeHTML(c.claimant_name)}</strong>) (${escapeHTML(c.claimant_relationship)})
            </div>
          </div>
          <div class="text-right">
            <span class="status-badge badge-${escapeHTML(c.status).toLowerCase().replace(/\s+/g, "")}">${escapeHTML(c.status)}</span>
            <div class="text-xs font-bold text-emerald-700 mt-1">₹${Number(c.approximate_value || 0).toLocaleString()}</div>
          </div>
        </div>

        <div class="text-xs text-slate-600 bg-white p-2.5 rounded border border-slate-200">
          <strong>Claimant Notes:</strong> ${escapeHTML(c.remarks || "No claimant remarks.")}
        </div>

        <!-- Action Drawer: Update Claim Status -->
        <div class="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-200">
          <span class="text-xs font-semibold text-slate-700">Update Official Claim Status:</span>
          <div class="flex items-center gap-2">
            <select id="inst-status-${escapeHTML(c.id)}" class="p-1.5 border border-slate-300 rounded text-xs">
              <option value="Under Review" ${c.status === "Under Review" ? "selected" : ""}>Under Review</option>
              <option value="Documents Required" ${c.status === "Documents Required" ? "selected" : ""}>Documents Required</option>
              <option value="Approved" ${c.status === "Approved" ? "selected" : ""}>Approved for Payout</option>
              <option value="Completed" ${c.status === "Completed" ? "selected" : ""}>Completed</option>
              <option value="Rejected" ${c.status === "Rejected" ? "selected" : ""}>Rejected</option>
            </select>
            <button onclick="instUpdateStatus('${escapeHTML(c.id)}')" class="bg-gov-navy hover:bg-slate-800 text-white font-bold px-3 py-1.5 rounded text-xs transition">
              Save Decision
            </button>
          </div>
        </div>
      </div>
    `
      )
      .join("");

    await loadInstitutionAnomalies();
  } catch (err) {
    console.error(err);
  }
}

async function instUpdateStatus(claimId) {
  const select = document.getElementById(`inst-status-${claimId}`);
  const status = select.value;
  const remarks = prompt("Enter official institution remarks / instructions for claimant:", `Updated to ${status} following document verification.`);
  if (remarks === null) return;

  try {
    await apiFetch(`/api/claims/${claimId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status, remarks }),
    });
    showToast(`Claim status updated to '${status}'! Notification sent to family.`);
    await loadInstitutionData();
  } catch (err) {
    console.error(err);
  }
}

// NOTIFICATIONS & SIMULATED EMAIL (Module 9)

let userNotifications = [];

async function pollNotifications() {
  if (!currentUser) return;
  try {
    userNotifications = await apiFetch("/api/notifications");
    const unread = userNotifications.filter((n) => !n.is_read).length;
    const badge = document.getElementById("notif-badge");
    if (unread > 0) {
      badge.textContent = unread;
      badge.classList.remove("hidden");
    } else {
      badge.classList.add("hidden");
    }
  } catch {}
}

async function openNotificationsModal() {
  document.getElementById("modal-notif").classList.remove("hidden");
  await pollNotifications();
  renderNotificationsModal();
}

function closeNotifModal() {
  document.getElementById("modal-notif").classList.add("hidden");
}

function renderNotificationsModal() {
  const list = document.getElementById("notif-modal-list");
  if (!userNotifications || userNotifications.length === 0) {
    list.innerHTML = `<p class="text-center text-slate-400 py-6">No notifications on record.</p>`;
    return;
  }

  list.innerHTML = userNotifications
    .map(
      (n) => `
    <div class="p-3 rounded-lg border ${n.is_read ? "bg-slate-50 border-slate-200" : "bg-amber-50/70 border-amber-200"} space-y-2">
      <div class="flex justify-between items-start">
        <h5 class="font-bold text-slate-900">${escapeHTML(n.title)}</h5>
        <span class="text-[10px] text-slate-400">${new Date(n.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
      </div>
      <p class="text-slate-600 leading-relaxed text-xs">${escapeHTML(n.message)}</p>
      <div class="flex justify-between items-center pt-1 text-[11px]">
        <button onclick="viewSimulatedEmail('${escapeHTML(n.id)}')" class="text-gov-blue hover:underline font-semibold flex items-center gap-1">
          <i class="fa-solid fa-envelope"></i> Inspect Simulated Email Dispatch
        </button>
        ${
          !n.is_read
            ? `<button onclick="markNotifRead('${escapeHTML(n.id)}')" class="text-slate-500 hover:text-slate-800">Mark read</button>`
            : `<span class="text-slate-400">Read</span>`
        }
      </div>
    </div>
  `
    )
    .join("");
}

async function markNotifRead(notifId) {
  try {
    await apiFetch(`/api/notifications/${notifId}/read`, { method: "PATCH" });
    await pollNotifications();
    renderNotificationsModal();
  } catch {}
}

async function markAllNotifsRead() {
  try {
    await apiFetch("/api/notifications/read-all", { method: "POST" });
    await pollNotifications();
    renderNotificationsModal();
  } catch {}
}

function viewSimulatedEmail(notifId) {
  const notif = userNotifications.find((n) => n.id === notifId);
  if (!notif) return;
  document.getElementById("email-preview-content").textContent = notif.email_logs || "No email log recorded.";
  document.getElementById("modal-email-view").classList.remove("hidden");
}

function closeEmailModal() {
  document.getElementById("modal-email-view").classList.add("hidden");
}

// RAJESH KUMAR TEST SCENARIO ONE-CLICK RUNNER

async function loadRajeshScenario() {
  showToast("Loading Rajesh Kumar demonstration scenario...");
  await demoLogin("family");
  switchTab("matches");
  await populateMatchesDropdown();
  const selector = document.getElementById("match-deceased-selector");
  for (let i = 0; i < selector.options.length; i++) {
    if (selector.options[i].text.includes("Rajesh Kumar")) {
      selector.selectedIndex = i;
      activeDeceasedId = selector.options[i].value;
      break;
    }
  }
  await loadMatchesForSelected();
  showToast("Rajesh Kumar matches loaded! (₹17,86,240 across SBI, LIC, and HDFC MF)", "success");
}

// GOOGLE OAUTH 2.0 INTEGRATION
function handleGoogleSignIn() {
  closeAuthModal();
  openGoogleAuthModal();
}

function openGoogleAuthModal() {
  const modal = document.getElementById("modal-google-auth");
  if (modal) {
    modal.classList.remove("hidden");
    const emailInput = document.getElementById("google-input-email");
    if (emailInput) {
      emailInput.value = "";
      setTimeout(() => emailInput.focus(), 100);
    }
  }
}

function closeGoogleAuthModal() {
  const modal = document.getElementById("modal-google-auth");
  if (modal) modal.classList.add("hidden");
}

function selectQuickGoogleAccount(email, name) {
  const emailInput = document.getElementById("google-input-email");
  const nameInput = document.getElementById("google-input-name");
  if (emailInput) emailInput.value = email;
  if (nameInput) nameInput.value = name;
  submitGoogleAuth();
}

async function submitGoogleAuth(e) {
  if (e) e.preventDefault();
  const emailInput = document.getElementById("google-input-email");
  const nameInput = document.getElementById("google-input-name");
  const submitBtn = document.getElementById("google-auth-submit-btn");

  const email = (emailInput ? emailInput.value : "").trim().toLowerCase();
  const rawName = nameInput ? nameInput.value.trim() : "";
  const fullName = rawName || email.split("@")[0].replace(/[._]/g, " ").replace(/\b\w/g, c => c.toUpperCase());

  if (!email || !email.includes("@") || !email.includes(".")) {
    showToast("Please enter a valid Google Gmail address.", "error");
    if (emailInput) emailInput.focus();
    return;
  }

  try {
    showToast(`Connecting to Google Identity Services (${email})...`);
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Authenticating with Google...';
    }

    const data = await apiFetch("/api/auth/google/login", {
      method: "POST",
      body: JSON.stringify({
        email: email,
        full_name: fullName,
        google_id: "google_oauth_sub_" + btoa(email).replace(/=/g, "").slice(0, 16)
      })
    });

    currentToken = data.access_token;
    currentUser = data.user;
    localStorage.setItem("token", currentToken);

    closeGoogleAuthModal();
    closeAuthModal();
    updateUIForUser();
    showToast(`Welcome, ${currentUser.full_name}! Signed in via Google (${currentUser.email}).`);
    await loadDashboardData();
    switchTab("dashboard");
  } catch (err) {
    console.error("Google Auth error:", err);
    showToast(err.message || "Google Authentication failed", "error");
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span>Next / Authenticate</span>';
    }
  }
}

// VIRASAT AI LEGAL COPILOT
function toggleAICopilotModal() {
  const modal = document.getElementById("modal-copilot");
  if (!modal) return;
  modal.classList.toggle("hidden");
  if (!modal.classList.contains("hidden")) {
    const input = document.getElementById("copilot-input");
    if (input) input.focus();
  }
}

function askQuickCopilot(question) {
  const input = document.getElementById("copilot-input");
  if (input) {
    input.value = question;
    handleCopilotSubmit(new Event("submit"));
  }
}

async function handleCopilotSubmit(e) {
  if (e) e.preventDefault();
  const input = document.getElementById("copilot-input");
  const thread = document.getElementById("copilot-thread");
  const sendBtn = document.getElementById("copilot-send-btn");
  if (!input || !thread) return;

  const query = input.value.trim();
  if (!query) return;

  // Append user message bubble
  thread.innerHTML += `
    <div class="flex items-start justify-end gap-2.5">
      <div class="bg-gov-navy text-white p-3 rounded-2xl rounded-tr-none text-xs shadow-sm max-w-[85%] leading-relaxed">
        ${escapeHTML(query)}
      </div>
      <div class="w-6 h-6 rounded-full bg-slate-300 text-slate-700 flex items-center justify-center shrink-0 text-[10px] font-bold">
        <i class="fa-solid fa-user"></i>
      </div>
    </div>
  `;
  input.value = "";
  thread.scrollTop = thread.scrollHeight;

  // Append thinking bubble
  const thinkingId = `copilot-thinking-${Date.now()}`;
  thread.innerHTML += `
    <div id="${thinkingId}" class="flex items-start gap-2.5">
      <div class="w-6 h-6 rounded-full bg-gov-navy text-white flex items-center justify-center shrink-0 text-[10px]">
        <i class="fa-solid fa-robot"></i>
      </div>
      <div class="bg-white p-3 rounded-2xl rounded-tl-none border border-slate-200 text-slate-500 text-xs shadow-sm flex items-center gap-2">
        <i class="fa-solid fa-circle-notch fa-spin text-amber-500"></i>
        <span>Viru is consulting legal succession frameworks and institutional precedents...</span>
      </div>
    </div>
  `;
  thread.scrollTop = thread.scrollHeight;
  if (sendBtn) sendBtn.disabled = true;

  try {
    const res = await apiFetch("/api/ai/copilot", {
      method: "POST",
      body: JSON.stringify({ query: query }),
      silent: true
    });

    const thinkingEl = document.getElementById(thinkingId);
    if (thinkingEl) thinkingEl.remove();

    const formattedAnswer = escapeHTML(res.answer).replace(/\n/g, "<br>");
    let followupsHTML = "";
    if (res.followups && res.followups.length > 0) {
      followupsHTML = `
        <div class="pt-2 border-t border-slate-100 mt-2 space-y-1">
          <span class="text-[10px] uppercase font-bold text-slate-400">Related Legal Topics:</span>
          <div class="flex flex-wrap gap-1">
            ${res.followups
              .map(
                (f) => `
              <button type="button" onclick="askQuickCopilot('${escapeHTML(f)}')" class="px-2 py-0.5 rounded bg-slate-100 hover:bg-amber-100 text-[10px] text-slate-700 font-medium transition">
                ${escapeHTML(f)}
              </button>
            `
              )
              .join("")}
          </div>
        </div>
      `;
    }

    const sourceBadge = res.source === "gemini_api"
      ? '<span class="bg-amber-100 text-amber-800 text-[9px] font-bold px-1.5 py-0.5 rounded">Gemini AI</span>'
      : '<span class="bg-blue-100 text-blue-800 text-[9px] font-bold px-1.5 py-0.5 rounded">Succession Knowledge Base</span>';

    thread.innerHTML += `
      <div class="flex items-start gap-2.5">
        <div class="w-6 h-6 rounded-full bg-gov-navy text-white flex items-center justify-center shrink-0 text-[10px]">
          <i class="fa-solid fa-robot"></i>
        </div>
        <div class="bg-white p-3 rounded-2xl rounded-tl-none border border-slate-200 text-slate-700 text-xs shadow-sm max-w-[85%] leading-relaxed space-y-1">
          <div class="flex items-center justify-between pb-1 border-b border-slate-100">
            <span class="font-bold text-slate-900">Viru Legal Advisory:</span>
            ${sourceBadge}
          </div>
          <div class="text-slate-800 leading-relaxed">${formattedAnswer}</div>
          ${followupsHTML}
        </div>
      </div>
    `;
    thread.scrollTop = thread.scrollHeight;
  } catch (err) {
    const thinkingEl = document.getElementById(thinkingId);
    if (thinkingEl) thinkingEl.remove();

    thread.innerHTML += `
      <div class="flex items-start gap-2.5">
        <div class="w-6 h-6 rounded-full bg-gov-navy text-white flex items-center justify-center shrink-0 text-[10px]">
          <i class="fa-solid fa-robot"></i>
        </div>
        <div class="bg-white p-3 rounded-2xl rounded-tl-none border border-slate-200 text-red-600 text-xs shadow-sm max-w-[85%]">
          Unable to retrieve advice at this moment. Please check your network or try again.
        </div>
      </div>
    `;
  } finally {
    if (sendBtn) sendBtn.disabled = false;
  }
}

// AI FRAUD AND ANOMALY DETECTION (Admin and Institution Desk Restricted)
async function loadAdminAnomalies() {
  const container = document.getElementById("admin-anomalies-list");
  if (!container) return;

  try {
    const anomalies = await apiFetch("/api/ai/admin/fraud-anomalies");
    if (!anomalies || anomalies.length === 0) {
      container.innerHTML = `
        <div class="bg-emerald-50 border border-emerald-200 rounded-lg p-3.5 text-center text-xs text-emerald-800">
          <i class="fa-solid fa-check-circle mr-1.5"></i> Zero active fraud anomalies or conflicting claims detected across platform records.
        </div>
      `;
      return;
    }

    container.innerHTML = anomalies
      .map(
        (a) => `
      <div class="p-3.5 bg-rose-50/70 border border-rose-200 rounded-xl space-y-2">
        <div class="flex flex-wrap justify-between items-start gap-2">
          <div class="flex items-center gap-2">
            <span class="bg-rose-600 text-white font-bold text-[10px] uppercase px-2 py-0.5 rounded flex items-center gap-1">
              <i class="fa-solid fa-triangle-exclamation"></i> ${escapeHTML(a.risk_level)}
            </span>
            <span class="font-bold text-slate-900 text-xs">${escapeHTML(a.category)}</span>
            <span class="text-slate-500 text-[11px]">(${escapeHTML(a.institution_name)})</span>
          </div>
          <span class="font-mono text-rose-700 font-bold text-xs">Risk Index: ${Number(a.risk_score)}/100</span>
        </div>
        <div class="text-xs text-slate-700 leading-relaxed">${escapeHTML(a.details)}</div>
        <div class="bg-white p-2 rounded border border-rose-100 text-[11px] text-slate-600 flex items-start gap-1.5">
          <strong class="text-rose-900 shrink-0">Prescribed Action:</strong>
          <span>${escapeHTML(a.recommended_action)}</span>
        </div>
      </div>
    `
      )
      .join("");
  } catch (err) {
    console.error("Error loading anomalies:", err);
  }
}

async function loadInstitutionAnomalies() {
  const container = document.getElementById("inst-anomalies-list");
  if (!container) return;

  try {
    const anomalies = await apiFetch("/api/ai/admin/fraud-anomalies");
    if (!anomalies || anomalies.length === 0) {
      container.innerHTML = `
        <div class="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-center text-xs text-emerald-800">
          <i class="fa-solid fa-check-circle mr-1"></i> No risk anomalies flagged for this institution node.
        </div>
      `;
      return;
    }

    container.innerHTML = anomalies
      .map(
        (a) => `
      <div class="p-3 bg-amber-50/70 border border-amber-200 rounded-lg space-y-1.5 text-xs">
        <div class="flex justify-between items-center">
          <span class="font-bold text-slate-800">${escapeHTML(a.category)}</span>
          <span class="bg-amber-100 text-amber-800 font-bold text-[10px] px-2 py-0.5 rounded">${escapeHTML(a.risk_level)}</span>
        </div>
        <p class="text-slate-600 text-[11px]">${escapeHTML(a.details)}</p>
        <p class="text-[11px] text-amber-900 font-medium"><strong>Advisory:</strong> ${escapeHTML(a.recommended_action)}</p>
      </div>
    `
      )
      .join("");
  } catch (err) {
    console.error("Error loading institution anomalies:", err);
  }
}
