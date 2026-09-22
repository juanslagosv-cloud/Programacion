/* Cliente API — Ecodes Talento Humano */

const API_BASE = window.ECODES_API_BASE || "http://localhost:8000";

class ApiError extends Error {
  constructor(status, detail) {
    super(typeof detail === "string" ? detail : "Error de la solicitud");
    this.status = status;
    this.detail = detail;
  }
}

function getToken() {
  return localStorage.getItem("ecodes_token");
}

function getSession() {
  const raw = localStorage.getItem("ecodes_user");
  return raw ? JSON.parse(raw) : null;
}

function setSession(token, user) {
  localStorage.setItem("ecodes_token", token);
  localStorage.setItem("ecodes_user", JSON.stringify(user));
}

function clearSession() {
  localStorage.removeItem("ecodes_token");
  localStorage.removeItem("ecodes_user");
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    clearSession();
    window.location.href = "index.html";
    throw new ApiError(401, "Sesión expirada");
  }

  if (!res.ok) {
    let detail = "Error inesperado";
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch (_) {}
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return null;
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return res.json();
  return res;
}

const api = {
  login: (payload) =>
    fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  get: (path) => apiFetch(path, { method: "GET" }),
  post: (path, body) => apiFetch(path, { method: "POST", body: JSON.stringify(body) }),
  put: (path, body) => apiFetch(path, { method: "PUT", body: JSON.stringify(body) }),
  del: (path) => apiFetch(path, { method: "DELETE" }),

  async descargarCertificado(empleadoId, incluirSalario) {
    const token = getToken();
    const res = await fetch(
      `${API_BASE}/empleados/${empleadoId}/certificado-laboral?incluir_salario=${incluirSalario}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    if (!res.ok) {
      // El backend explica el motivo (por ejemplo, que no hay nómina registrada).
      let detalle = "No se pudo generar el certificado";
      try {
        const data = await res.json();
        if (data && data.detail) detalle = data.detail;
      } catch (_) {
        /* la respuesta no era JSON: se queda el mensaje genérico */
      }
      throw new ApiError(res.status, detalle);
    }
    const blob = await res.blob();
    const nombre = (res.headers.get("Content-Disposition") || "").match(/filename="(.+?)"/);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = nombre ? nombre[1] : "certificado_laboral.pdf";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  },

  async exportarExcel() {
    const token = getToken();
    const res = await fetch(`${API_BASE}/exportar/excel`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new ApiError(res.status, "No se pudo exportar el archivo");
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "ecodes_talento_humano.xlsx";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  },
};
