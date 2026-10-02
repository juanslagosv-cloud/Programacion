(() => {
  const state = { areas: [], cargos: [], vacantes: [], empresas: [], filtros: { areas: {}, cargos: {}, vacantes: {} } };

  async function init() {
    renderShell("organigrama.html", "Organigrama");
    try {
      state.empresas = await api.get("/empresas");
    } catch (err) {
      handleApiError(err);
    }
    fillEmpresaSelects();
    bindTabs();
    bindFiltros();
    bindBotonesNuevo();
    loadAreas();
  }

  function fillEmpresaSelects() {
    ["f-areas-empresa", "f-cargos-empresa"].forEach((id) => {
      const select = document.getElementById(id);
      state.empresas.forEach((emp) => {
        const opt = document.createElement("option");
        opt.value = emp.id;
        opt.textContent = emp.nombre;
        select.appendChild(opt);
      });
    });
  }

  function bindTabs() {
    const tabs = document.querySelectorAll(".subtab-btn");
    tabs.forEach((btn) => {
      btn.addEventListener("click", () => {
        tabs.forEach((b) => b.classList.toggle("active", b === btn));
        ["areas", "cargos", "vacantes", "jefaturas", "dependencias"].forEach((name) => {
          document.getElementById(`view-${name}`).classList.toggle("hidden", name !== btn.dataset.tab);
        });
        if (btn.dataset.tab === "cargos" && !state.cargos.length) loadCargos();
        if (btn.dataset.tab === "vacantes" && !state.vacantes.length) loadVacantes();
        if (btn.dataset.tab === "jefaturas") loadJefaturas();
        if (btn.dataset.tab === "dependencias") loadDependencias();
      });
    });
  }

  function bindFiltros() {
    document.getElementById("f-areas-empresa").addEventListener("change", (e) => {
      state.filtros.areas.empresa_id = e.target.value;
      loadAreas();
    });
    document.getElementById("f-cargos-empresa").addEventListener("change", (e) => {
      state.filtros.cargos.empresa_id = e.target.value;
      loadCargos();
    });
    document.getElementById("f-vacantes-estado").addEventListener("change", (e) => {
      state.filtros.vacantes.estado = e.target.value;
      loadVacantes();
    });
  }

  function bindBotonesNuevo() {
    document.getElementById("btn-nueva-area").addEventListener("click", () => openAreaForm(null));
    document.getElementById("btn-nuevo-cargo").addEventListener("click", () => openCargoForm(null));
    document.getElementById("btn-nueva-vacante").addEventListener("click", () => openVacanteForm(null));
  }

  function nombreEmpresa(id) {
    const emp = state.empresas.find((e) => e.id === id);
    return emp ? emp.nombre : "—";
  }

  /* --------------------------------------------------------------------- Áreas */

  async function loadAreas() {
    const tbody = document.getElementById("areas-tbody");
    tbody.innerHTML = `<tr><td colspan="6" class="table-empty">Cargando áreas…</td></tr>`;
    const params = new URLSearchParams();
    Object.entries(state.filtros.areas).forEach(([k, v]) => v && params.set(k, v));
    try {
      state.areas = await api.get(`/areas?${params.toString()}`);
      renderAreasTable();
    } catch (err) {
      handleApiError(err);
      tbody.innerHTML = `<tr><td colspan="6" class="table-empty">No se pudieron cargar las áreas.</td></tr>`;
    }
  }

  function renderAreasTable() {
    const tbody = document.getElementById("areas-tbody");
    if (!state.areas.length) {
      tbody.innerHTML = `<tr><td colspan="6" class="table-empty">No hay áreas registradas todavía.</td></tr>`;
      return;
    }
    tbody.innerHTML = state.areas
      .map(
        (a) => `
      <tr data-id="${a.id}">
        <td><div class="person-name">${escapeHtml(a.nombre)}</div></td>
        <td>${escapeHtml(nombreEmpresa(a.empresa_id))}</td>
        <td>${a.area_padre_nombre ? escapeHtml(a.area_padre_nombre) : '<span class="text-faint">Raíz</span>'}</td>
        <td>${a.responsable_nombre ? escapeHtml(a.responsable_nombre) : '<span class="text-faint">Sin asignar</span>'}</td>
        <td>${a.total_empleados}</td>
        <td class="flex gap-8 write-only">
          <button class="btn btn-secondary btn-sm" data-editar-area="${a.id}">Editar</button>
          <button class="list-item-remove" data-eliminar-area="${a.id}" title="Eliminar área">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
          </button>
        </td>
      </tr>`
      )
      .join("");

    if (isReadOnly()) document.body.classList.add("read-only");

    tbody.querySelectorAll("[data-editar-area]").forEach((btn) => {
      btn.addEventListener("click", () => {
        openAreaForm(state.areas.find((a) => a.id === Number(btn.dataset.editarArea)));
      });
    });
    tbody.querySelectorAll("[data-eliminar-area]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const a = state.areas.find((x) => x.id === Number(btn.dataset.eliminarArea));
        if (!confirm(`¿Eliminar el área «${a.nombre}»?`)) return;
        try {
          await api.del(`/areas/${a.id}`);
          showToast("Área eliminada");
          loadAreas();
        } catch (err) {
          handleApiError(err);
        }
      });
    });
  }

  function areaFormHtml(a = {}) {
    const empresaId = a.empresa_id || (state.empresas[0] && state.empresas[0].id) || "";
    const padresDisponibles = state.areas.filter((x) => x.id !== a.id && x.empresa_id === Number(empresaId));
    const responsablesOpts = window.__empleadosCache || [];
    return `
      <div class="field">
        <label>Nombre del área</label>
        <input type="text" name="nombre" value="${escapeHtml(a.nombre) || ""}" required>
      </div>
      <div class="field">
        <label>Empresa</label>
        <select name="empresa_id" id="area-empresa-select" required>
          ${state.empresas.map((emp) => `<option value="${emp.id}" ${Number(empresaId) === emp.id ? "selected" : ""}>${escapeHtml(emp.nombre)}</option>`).join("")}
        </select>
      </div>
      <div class="field">
        <label>Depende de (opcional)</label>
        <select name="area_padre_id">
          <option value="">Ninguna (es un área raíz)</option>
          ${padresDisponibles.map((p) => `<option value="${p.id}" ${a.area_padre_id === p.id ? "selected" : ""}>${escapeHtml(p.nombre)}</option>`).join("")}
        </select>
      </div>
      <div class="field">
        <label>Responsable (opcional)</label>
        <select name="responsable_id">
          <option value="">Sin asignar</option>
          ${responsablesOpts.map((e) => `<option value="${e.id}" ${a.responsable_id === e.id ? "selected" : ""}>${escapeHtml(e.nombre_completo)}</option>`).join("")}
        </select>
      </div>
    `;
  }

  async function ensureEmpleadosCache() {
    if (!window.__empleadosCache) {
      window.__empleadosCache = await api.get("/empleados");
    }
  }

  async function openAreaForm(a) {
    await ensureEmpleadosCache();
    const esEdicion = !!a;
    const overlay = openModal(`
      <div class="modal-header">
        <h3>${esEdicion ? "Editar área" : "Nueva área"}</h3>
        <button class="icon-btn" data-close-modal>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <form id="form-area">
        <div class="modal-body">${areaFormHtml(a || {})}</div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
          <button type="submit" class="btn btn-primary">${esEdicion ? "Guardar cambios" : "Crear área"}</button>
        </div>
      </form>
    `);
    overlay.querySelector("#form-area").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const payload = {
        nombre: fd.get("nombre"),
        empresa_id: Number(fd.get("empresa_id")),
        area_padre_id: fd.get("area_padre_id") ? Number(fd.get("area_padre_id")) : null,
        responsable_id: fd.get("responsable_id") ? Number(fd.get("responsable_id")) : null,
      };
      try {
        if (esEdicion) {
          await api.put(`/areas/${a.id}`, payload);
          showToast("Área actualizada");
        } else {
          await api.post("/areas", payload);
          showToast("Área creada");
        }
        closeModal();
        loadAreas();
      } catch (err) {
        handleApiError(err);
      }
    });
  }

  /* --------------------------------------------------------------------- Cargos */

  async function loadCargos() {
    const tbody = document.getElementById("cargos-tbody");
    tbody.innerHTML = `<tr><td colspan="5" class="table-empty">Cargando cargos…</td></tr>`;
    const params = new URLSearchParams();
    Object.entries(state.filtros.cargos).forEach(([k, v]) => v && params.set(k, v));
    if (!state.areas.length) {
      try {
        state.areas = await api.get("/areas");
      } catch (err) {
        /* se maneja abajo */
      }
    }
    try {
      state.cargos = await api.get(`/cargos?${params.toString()}`);
      renderCargosTable();
    } catch (err) {
      handleApiError(err);
      tbody.innerHTML = `<tr><td colspan="5" class="table-empty">No se pudieron cargar los cargos.</td></tr>`;
    }
  }

  function renderCargosTable() {
    const tbody = document.getElementById("cargos-tbody");
    if (!state.cargos.length) {
      tbody.innerHTML = `<tr><td colspan="5" class="table-empty">No hay cargos registrados todavía.</td></tr>`;
      return;
    }
    tbody.innerHTML = state.cargos
      .map(
        (c) => `
      <tr data-id="${c.id}">
        <td><div class="person-name">${escapeHtml(c.nombre)}</div></td>
        <td>${escapeHtml(nombreEmpresa(c.empresa_id))}</td>
        <td>${c.area_nombre ? escapeHtml(c.area_nombre) : '<span class="text-faint">Sin asignar</span>'}</td>
        <td>${c.cargo_superior_nombre ? escapeHtml(c.cargo_superior_nombre) : '<span class="text-faint">Ninguno</span>'}</td>
        <td class="flex gap-8 write-only">
          <button class="btn btn-secondary btn-sm" data-editar-cargo="${c.id}">Editar</button>
          <button class="list-item-remove" data-eliminar-cargo="${c.id}" title="Eliminar cargo">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
          </button>
        </td>
      </tr>`
      )
      .join("");

    if (isReadOnly()) document.body.classList.add("read-only");

    tbody.querySelectorAll("[data-editar-cargo]").forEach((btn) => {
      btn.addEventListener("click", () => {
        openCargoForm(state.cargos.find((c) => c.id === Number(btn.dataset.editarCargo)));
      });
    });
    tbody.querySelectorAll("[data-eliminar-cargo]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const c = state.cargos.find((x) => x.id === Number(btn.dataset.eliminarCargo));
        if (!confirm(`¿Eliminar el cargo «${c.nombre}»?`)) return;
        try {
          await api.del(`/cargos/${c.id}`);
          showToast("Cargo eliminado");
          loadCargos();
        } catch (err) {
          handleApiError(err);
        }
      });
    });
  }

  function cargoFormHtml(c = {}) {
    const empresaId = c.empresa_id || (state.empresas[0] && state.empresas[0].id) || "";
    const areasDisponibles = state.areas.filter((a) => a.empresa_id === Number(empresaId));
    const superioresDisponibles = state.cargos.filter((x) => x.id !== c.id && x.empresa_id === Number(empresaId));
    return `
      <div class="field">
        <label>Nombre del cargo</label>
        <input type="text" name="nombre" value="${escapeHtml(c.nombre) || ""}" required>
      </div>
      <div class="field">
        <label>Empresa</label>
        <select name="empresa_id" required>
          ${state.empresas.map((emp) => `<option value="${emp.id}" ${Number(empresaId) === emp.id ? "selected" : ""}>${escapeHtml(emp.nombre)}</option>`).join("")}
        </select>
      </div>
      <div class="field">
        <label>Área (opcional)</label>
        <select name="area_id">
          <option value="">Sin asignar</option>
          ${areasDisponibles.map((a) => `<option value="${a.id}" ${c.area_id === a.id ? "selected" : ""}>${escapeHtml(a.nombre)}</option>`).join("")}
        </select>
      </div>
      <div class="field">
        <label>Depende de (opcional)</label>
        <select name="cargo_superior_id">
          <option value="">Ninguno</option>
          ${superioresDisponibles.map((s) => `<option value="${s.id}" ${c.cargo_superior_id === s.id ? "selected" : ""}>${escapeHtml(s.nombre)}</option>`).join("")}
        </select>
      </div>
    `;
  }

  async function openCargoForm(c) {
    if (!state.areas.length) {
      try {
        state.areas = await api.get("/areas");
      } catch (err) {
        /* se continúa sin áreas si falla */
      }
    }
    const esEdicion = !!c;
    const overlay = openModal(`
      <div class="modal-header">
        <h3>${esEdicion ? "Editar cargo" : "Nuevo cargo"}</h3>
        <button class="icon-btn" data-close-modal>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <form id="form-cargo">
        <div class="modal-body">${cargoFormHtml(c || {})}</div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
          <button type="submit" class="btn btn-primary">${esEdicion ? "Guardar cambios" : "Crear cargo"}</button>
        </div>
      </form>
    `);
    overlay.querySelector("#form-cargo").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const payload = {
        nombre: fd.get("nombre"),
        empresa_id: Number(fd.get("empresa_id")),
        area_id: fd.get("area_id") ? Number(fd.get("area_id")) : null,
        cargo_superior_id: fd.get("cargo_superior_id") ? Number(fd.get("cargo_superior_id")) : null,
      };
      try {
        if (esEdicion) {
          await api.put(`/cargos/${c.id}`, payload);
          showToast("Cargo actualizado");
        } else {
          await api.post("/cargos", payload);
          showToast("Cargo creado");
        }
        closeModal();
        loadCargos();
      } catch (err) {
        handleApiError(err);
      }
    });
  }

  /* --------------------------------------------------------------------- Vacantes */

  function vacanteBadgeClass(estado) {
    if (estado === "Abierta") return "badge-info";
    if (estado === "En proceso") return "badge-warning";
    return "badge-neutral";
  }

  async function loadVacantes() {
    const tbody = document.getElementById("vacantes-tbody");
    tbody.innerHTML = `<tr><td colspan="7" class="table-empty">Cargando vacantes…</td></tr>`;
    const params = new URLSearchParams();
    Object.entries(state.filtros.vacantes).forEach(([k, v]) => v && params.set(k, v));
    try {
      state.vacantes = await api.get(`/vacantes?${params.toString()}`);
      renderVacantesTable();
    } catch (err) {
      handleApiError(err);
      tbody.innerHTML = `<tr><td colspan="7" class="table-empty">No se pudieron cargar las vacantes.</td></tr>`;
    }
  }

  function renderVacantesTable() {
    const tbody = document.getElementById("vacantes-tbody");
    if (!state.vacantes.length) {
      tbody.innerHTML = `<tr><td colspan="7" class="table-empty">No hay vacantes con estos filtros.</td></tr>`;
      return;
    }
    tbody.innerHTML = state.vacantes
      .map(
        (v) => `
      <tr data-id="${v.id}">
        <td><div class="person-name">${escapeHtml(v.titulo)}</div></td>
        <td>${escapeHtml(nombreEmpresa(v.empresa_id))}</td>
        <td>${[v.area_nombre, v.cargo_nombre].filter(Boolean).map(escapeHtml).join(" · ") || "—"}</td>
        <td>${formatDate(v.fecha_apertura)}</td>
        <td>${v.dias_abierta} día(s)</td>
        <td><span class="badge ${vacanteBadgeClass(v.estado)}"><span class="badge-dot"></span>${v.estado}</span></td>
        <td class="flex gap-8 write-only">
          <button class="btn btn-secondary btn-sm" data-editar-vacante="${v.id}">Editar</button>
          <button class="list-item-remove" data-eliminar-vacante="${v.id}" title="Eliminar vacante">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
          </button>
        </td>
      </tr>`
      )
      .join("");

    if (isReadOnly()) document.body.classList.add("read-only");

    tbody.querySelectorAll("[data-editar-vacante]").forEach((btn) => {
      btn.addEventListener("click", () => {
        openVacanteForm(state.vacantes.find((v) => v.id === Number(btn.dataset.editarVacante)));
      });
    });
    tbody.querySelectorAll("[data-eliminar-vacante]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const v = state.vacantes.find((x) => x.id === Number(btn.dataset.eliminarVacante));
        if (!confirm(`¿Eliminar la vacante «${v.titulo}»?`)) return;
        try {
          await api.del(`/vacantes/${v.id}`);
          showToast("Vacante eliminada");
          loadVacantes();
        } catch (err) {
          handleApiError(err);
        }
      });
    });
  }

  function vacanteFormHtml(v = {}) {
    const empresaId = v.empresa_id || (state.empresas[0] && state.empresas[0].id) || "";
    const areasDisponibles = state.areas.filter((a) => a.empresa_id === Number(empresaId));
    const cargosDisponibles = state.cargos.filter((c) => c.empresa_id === Number(empresaId));
    return `
      <div class="field">
        <label>Título de la vacante</label>
        <input type="text" name="titulo" value="${escapeHtml(v.titulo) || ""}" required>
      </div>
      <div class="field">
        <label>Empresa</label>
        <select name="empresa_id" required>
          ${state.empresas.map((emp) => `<option value="${emp.id}" ${Number(empresaId) === emp.id ? "selected" : ""}>${escapeHtml(emp.nombre)}</option>`).join("")}
        </select>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Área (opcional)</label>
          <select name="area_id">
            <option value="">Sin asignar</option>
            ${areasDisponibles.map((a) => `<option value="${a.id}" ${v.area_id === a.id ? "selected" : ""}>${escapeHtml(a.nombre)}</option>`).join("")}
          </select>
        </div>
        <div class="field">
          <label>Cargo (opcional)</label>
          <select name="cargo_id">
            <option value="">Sin asignar</option>
            ${cargosDisponibles.map((c) => `<option value="${c.id}" ${v.cargo_id === c.id ? "selected" : ""}>${escapeHtml(c.nombre)}</option>`).join("")}
          </select>
        </div>
      </div>
      <div class="field">
        <label>Motivo de la vacante</label>
        <textarea name="motivo" rows="2">${escapeHtml(v.motivo) || ""}</textarea>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Salario ofrecido (opcional)</label>
          <input type="number" name="salario_ofrecido" min="0" value="${v.salario_ofrecido || ""}">
        </div>
        <div class="field">
          <label>Estado</label>
          <select name="estado">
            <option value="Abierta" ${!v.estado || v.estado === "Abierta" ? "selected" : ""}>Abierta</option>
            <option value="En proceso" ${v.estado === "En proceso" ? "selected" : ""}>En proceso</option>
            <option value="Cerrada" ${v.estado === "Cerrada" ? "selected" : ""}>Cerrada</option>
          </select>
        </div>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Fecha de apertura</label>
          <input type="date" name="fecha_apertura" value="${v.fecha_apertura || todayIso()}">
        </div>
        <div class="field">
          <label>Cierre esperado (opcional)</label>
          <input type="date" name="fecha_cierre_esperada" value="${v.fecha_cierre_esperada || ""}">
        </div>
      </div>
      <div class="field">
        <label>Notas (opcional)</label>
        <textarea name="notas" rows="2">${escapeHtml(v.notas) || ""}</textarea>
      </div>
    `;
  }

  async function openVacanteForm(v) {
    if (!state.areas.length) {
      try {
        state.areas = await api.get("/areas");
      } catch (err) {
        /* continúa sin áreas */
      }
    }
    if (!state.cargos.length) {
      try {
        state.cargos = await api.get("/cargos");
      } catch (err) {
        /* continúa sin cargos */
      }
    }
    const esEdicion = !!v;
    const overlay = openModal(`
      <div class="modal-header">
        <h3>${esEdicion ? "Editar vacante" : "Nueva vacante"}</h3>
        <button class="icon-btn" data-close-modal>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <form id="form-vacante">
        <div class="modal-body">${vacanteFormHtml(v || {})}</div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
          <button type="submit" class="btn btn-primary">${esEdicion ? "Guardar cambios" : "Crear vacante"}</button>
        </div>
      </form>
    `);
    overlay.querySelector("#form-vacante").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const payload = {
        titulo: fd.get("titulo"),
        empresa_id: Number(fd.get("empresa_id")),
        area_id: fd.get("area_id") ? Number(fd.get("area_id")) : null,
        cargo_id: fd.get("cargo_id") ? Number(fd.get("cargo_id")) : null,
        motivo: fd.get("motivo") || null,
        salario_ofrecido: fd.get("salario_ofrecido") ? Number(fd.get("salario_ofrecido")) : null,
        estado: fd.get("estado"),
        fecha_apertura: fd.get("fecha_apertura") || null,
        fecha_cierre_esperada: fd.get("fecha_cierre_esperada") || null,
        fecha_cierre_real: v && v.fecha_cierre_real ? v.fecha_cierre_real : (fd.get("estado") === "Cerrada" ? todayIso() : null),
        notas: fd.get("notas") || null,
      };
      try {
        if (esEdicion) {
          await api.put(`/vacantes/${v.id}`, payload);
          showToast("Vacante actualizada");
        } else {
          await api.post("/vacantes", payload);
          showToast("Vacante creada");
        }
        closeModal();
        loadVacantes();
      } catch (err) {
        handleApiError(err);
      }
    });
  }

  /* --------------------------------------------------------------------- Jefaturas y Dependencias (árboles de solo lectura) */

  function nodoJefaturaHtml(n) {
    return `
      <div class="org-node">
        <div class="org-node-card">
          ${avatarHtml(n.nombre, n.foto_url, 30)}
          <div>
            <div class="org-node-title">${escapeHtml(n.nombre)}</div>
            <div class="org-node-sub">${escapeHtml(n.nombre_cargo)}${n.reportes.length ? ` · ${n.reportes.length} persona(s) a cargo` : ""}</div>
          </div>
        </div>
        ${n.reportes.length ? `<div class="org-node-children">${n.reportes.map(nodoJefaturaHtml).join("")}</div>` : ""}
      </div>
    `;
  }

  async function loadJefaturas() {
    const host = document.getElementById("jefaturas-tree");
    host.innerHTML = '<p class="text-faint">Cargando…</p>';
    try {
      const arbol = await api.get("/organigrama/jefaturas");
      host.innerHTML = arbol.length
        ? arbol.map(nodoJefaturaHtml).join("")
        : '<p class="text-faint">No hay empleados registrados todavía.</p>';
    } catch (err) {
      handleApiError(err);
      host.innerHTML = '<p class="text-faint">No se pudo cargar el árbol de jefaturas.</p>';
    }
  }

  function nodoAreaHtml(n) {
    return `
      <div class="org-node">
        <div class="org-node-card">
          <div>
            <div class="org-node-title">${escapeHtml(n.nombre)}</div>
            <div class="org-node-sub">
              ${n.responsable_nombre ? `Responsable: ${escapeHtml(n.responsable_nombre)} · ` : ""}${n.total_empleados} empleado(s)
            </div>
          </div>
        </div>
        ${n.subareas.length ? `<div class="org-node-children">${n.subareas.map(nodoAreaHtml).join("")}</div>` : ""}
      </div>
    `;
  }

  async function loadDependencias() {
    const host = document.getElementById("dependencias-tree");
    host.innerHTML = '<p class="text-faint">Cargando…</p>';
    try {
      const arbol = await api.get("/organigrama/dependencias");
      host.innerHTML = arbol.length
        ? arbol.map(nodoAreaHtml).join("")
        : '<p class="text-faint">No hay áreas registradas todavía.</p>';
    } catch (err) {
      handleApiError(err);
      host.innerHTML = '<p class="text-faint">No se pudo cargar el árbol de dependencias.</p>';
    }
  }

  init();
})();
