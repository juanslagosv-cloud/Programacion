/* Utilidades comunes de interfaz — Ecodes Talento Humano */

function requireAuth() {
  const session = getSession();
  if (!session) {
    window.location.href = "index.html";
    return null;
  }
  return session;
}

function isReadOnly() {
  const session = getSession();
  return !session || session.rol === "administrativo";
}

function initials(name) {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/);
  const letters = parts.length > 1 ? [parts[0][0], parts[1][0]] : [parts[0][0]];
  return letters.join("").toUpperCase();
}

function avatarHtml(name, fotoUrl, size) {
  const style = size ? `style="width:${size}px;height:${size}px;font-size:${Math.round(size * 0.36)}px"` : "";
  if (fotoUrl) {
    return `<img class="avatar" ${style} src="${fotoUrl}" alt="${escapeHtml(name)}">`;
  }
  return `<span class="avatar" ${style}>${initials(name)}</span>`;
}

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatMoney(value) {
  const n = Number(value || 0);
  return n.toLocaleString("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 });
}

function formatDate(value) {
  if (!value) return "—";
  const d = new Date(value + "T00:00:00");
  return d.toLocaleDateString("es-CO", { day: "2-digit", month: "short", year: "numeric" });
}

function formatMonthPeriodo(periodo) {
  if (!periodo) return "—";
  const [y, m] = periodo.split("-");
  const d = new Date(Number(y), Number(m) - 1, 1);
  return d.toLocaleDateString("es-CO", { month: "long", year: "numeric" });
}

function antiguedadTexto(meses) {
  const años = Math.floor(meses / 12);
  const resto = meses % 12;
  if (años === 0) return `${resto} mes${resto === 1 ? "" : "es"}`;
  if (resto === 0) return `${años} año${años === 1 ? "" : "s"}`;
  return `${años}a ${resto}m`;
}

function debounce(fn, delay = 300) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), delay);
  };
}

function animateNumber(el, endValue, opts = {}) {
  const isMoney = opts.money;
  const duration = opts.duration || 800;
  const start = performance.now();
  const from = 0;
  function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = from + (endValue - from) * eased;
    el.textContent = isMoney ? formatMoney(current) : Math.round(current).toLocaleString("es-CO");
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function showToast(message, type = "success") {
  let stack = document.querySelector(".toast-stack");
  if (!stack) {
    stack = document.createElement("div");
    stack.className = "toast-stack";
    document.body.appendChild(stack);
  }
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  stack.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

function handleApiError(err) {
  console.error(err);
  showToast(err.detail || err.message || "Ocurrió un error", "error");
}

/* ---------------------------------------------------------------------
   Shell: sidebar + topbar
   --------------------------------------------------------------------- */

const NAV_ITEMS = [
  {
    page: "empleados.html",
    label: "Empleados",
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
  },
  {
    page: "proyectos.html",
    label: "Proyectos",
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
  },
  {
    page: "novedades.html",
    label: "Novedades",
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M12 18v-6"/><path d="M9 15h6"/></svg>',
  },
  {
    page: "nomina.html",
    label: "Nómina",
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/><path d="M6 15h4"/></svg>',
  },
  {
    page: "alertas.html",
    label: "Alertas",
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
  },
];

function renderShell(activePage, pageTitle) {
  const session = requireAuth();
  if (!session) return;

  document.getElementById("sidebar-slot").innerHTML = `
    <aside class="sidebar">
      <div class="brand">
        <img src="assets/logo.svg" class="brand-mark" alt="Ecodes">
        <div class="brand-text">
          <span class="brand-name">Ecodes</span>
          <span class="brand-sub">Colombia · Perú · Argentina</span>
        </div>
      </div>
      <nav class="nav-group">
        ${NAV_ITEMS.map(
          (item) => `
          <a class="nav-link ${item.page === activePage ? "active" : ""}" href="${item.page}">
            ${item.icon}
            <span>${item.label}</span>
          </a>`
        ).join("")}
      </nav>
      <div class="sidebar-footer">
        <div class="user-chip">
          ${avatarHtml(session.nombre, null, 32)}
          <div class="user-meta">
            <div class="user-name">${escapeHtml(session.nombre)}</div>
            <div class="user-role">${session.rol === "talento_humano" ? "Talento Humano" : "Administrativo"}</div>
          </div>
          <button class="logout-btn" id="logout-btn" title="Cerrar sesión">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          </button>
        </div>
      </div>
    </aside>
  `;

  document.getElementById("topbar-slot").innerHTML = `
    <header class="topbar">
      <h1 class="topbar-title">${pageTitle}</h1>
      <div class="topbar-actions">
        <button class="btn btn-secondary btn-sm" id="export-excel-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Exportar a Excel
        </button>
      </div>
    </header>
  `;

  document.getElementById("logout-btn").addEventListener("click", () => {
    clearSession();
    window.location.href = "index.html";
  });

  document.getElementById("export-excel-btn").addEventListener("click", async (e) => {
    const btn = e.currentTarget;
    const original = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = "Generando…";
    try {
      await api.exportarExcel();
      showToast("Archivo Excel generado correctamente");
    } catch (err) {
      handleApiError(err);
    } finally {
      btn.disabled = false;
      btn.innerHTML = original;
    }
  });

  if (isReadOnly()) {
    document.body.classList.add("read-only");
  }
}

/* ---------------------------------------------------------------------
   Panel lateral genérico
   --------------------------------------------------------------------- */

function ensurePanelHost() {
  let overlay = document.getElementById("panel-overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "panel-overlay";
    overlay.className = "overlay";
    document.body.appendChild(overlay);
    overlay.addEventListener("click", closeSidePanel);
  }
  let panel = document.getElementById("side-panel");
  if (!panel) {
    panel = document.createElement("aside");
    panel.id = "side-panel";
    panel.className = "side-panel";
    document.body.appendChild(panel);
  }
  return { overlay, panel };
}

function openSidePanel(html) {
  const { overlay, panel } = ensurePanelHost();
  panel.innerHTML = html;
  requestAnimationFrame(() => {
    overlay.classList.add("open");
    panel.classList.add("open");
  });
  const closeBtn = panel.querySelector("[data-close-panel]");
  if (closeBtn) closeBtn.addEventListener("click", closeSidePanel);
}

function closeSidePanel() {
  const overlay = document.getElementById("panel-overlay");
  const panel = document.getElementById("side-panel");
  if (overlay) overlay.classList.remove("open");
  if (panel) panel.classList.remove("open");
}

/* ---------------------------------------------------------------------
   Modal genérico
   --------------------------------------------------------------------- */

function openModal(html, id = "generic-modal") {
  let overlay = document.getElementById(id);
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = id;
    overlay.className = "modal-overlay";
    document.body.appendChild(overlay);
  }
  overlay.innerHTML = `<div class="modal">${html}</div>`;
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeModal(id);
  });
  requestAnimationFrame(() => overlay.classList.add("open"));
  overlay.querySelectorAll("[data-close-modal]").forEach((btn) =>
    btn.addEventListener("click", () => closeModal(id))
  );
  return overlay;
}

function closeModal(id = "generic-modal") {
  const overlay = document.getElementById(id);
  if (overlay) {
    overlay.classList.remove("open");
    setTimeout(() => overlay.remove(), 200);
  }
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeSidePanel();
    document.querySelectorAll(".modal-overlay.open").forEach((m) => closeModal(m.id));
  }
});
