(() => {
  const state = { proyectos: [], empleados: [], filtros: {} };

  async function init() {
    renderShell("proyectos.html", "Proyectos");
    try {
      state.empleados = await api.get("/empleados");
    } catch (err) {
      handleApiError(err);
    }
    loadProyectos();
    bindFilters();
    bindNuevoProyecto();
  }

  function bindFilters() {
    document.getElementById("f-buscar").addEventListener(
      "input",
      debounce((e) => {
        state.filtros.q = e.target.value.trim();
        loadProyectos();
      }, 350)
    );
    document.getElementById("f-estado").addEventListener("change", (e) => {
      state.filtros.estado = e.target.value;
      loadProyectos();
    });
  }

  async function loadProyectos() {
    const tbody = document.getElementById("proyectos-tbody");
    tbody.innerHTML = `<tr><td colspan="8" class="table-empty">Cargando proyectos…</td></tr>`;
    const params = new URLSearchParams();
    Object.entries(state.filtros).forEach(([k, v]) => v && params.set(k, v));
    try {
      const proyectos = await api.get(`/proyectos?${params.toString()}`);
      state.proyectos = proyectos;
      renderTable(proyectos);
    } catch (err) {
      handleApiError(err);
      tbody.innerHTML = `<tr><td colspan="8" class="table-empty">No se pudieron cargar los proyectos.</td></tr>`;
    }
  }

  function estadoBadgeClass(estado) {
    if (estado === "Activo") return "badge-success";
    if (estado === "Continuo") return "badge-info";
    return "badge-neutral";
  }

  function renderTable(proyectos) {
    const tbody = document.getElementById("proyectos-tbody");
    if (!proyectos.length) {
      tbody.innerHTML = `<tr><td colspan="8" class="table-empty">No se encontraron proyectos con estos filtros.</td></tr>`;
      return;
    }
    tbody.innerHTML = proyectos
      .map(
        (p) => `
      <tr data-id="${p.id}">
        <td><div class="person-name">${escapeHtml(p.nombre)}</div></td>
        <td>${escapeHtml(p.contratante)}</td>
        <td>${formatDate(p.fecha_inicio)}</td>
        <td>${p.fecha_fin ? formatDate(p.fecha_fin) : "—"}</td>
        <td>${p.tamano_equipo} persona${p.tamano_equipo === 1 ? "" : "s"}</td>
        <td>${formatMoney(p.costo_nomina_mes)}</td>
        <td>
          <span class="badge ${p.porcentaje_rotacion >= 30 ? "badge-danger" : p.porcentaje_rotacion > 0 ? "badge-warning" : "badge-neutral"}">
            ${p.porcentaje_rotacion}%
          </span>
        </td>
        <td><span class="badge ${estadoBadgeClass(p.estado)}"><span class="badge-dot"></span>${p.estado}</span></td>
      </tr>`
      )
      .join("");

    tbody.querySelectorAll("tr[data-id]").forEach((row) => {
      row.addEventListener("click", () => openProyectoPanel(Number(row.dataset.id)));
    });
  }

  async function openProyectoPanel(id) {
    let proyecto;
    try {
      proyecto = await api.get(`/proyectos/${id}`);
    } catch (err) {
      handleApiError(err);
      return;
    }
    renderProyectoPanel(proyecto);
  }

  function renderProyectoPanel(p) {
    const empleadosDisponibles = state.empleados.filter(
      (e) => !p.participaciones.some((part) => part.empleado_id === e.id)
    );

    const html = `
      <div class="side-panel-header">
        <div>
          <div class="panel-profile-name">${escapeHtml(p.nombre)}</div>
          <div class="panel-profile-role">${escapeHtml(p.contratante)}</div>
          <span class="badge ${estadoBadgeClass(p.estado)}" style="margin-top:6px;"><span class="badge-dot"></span>${p.estado}</span>
        </div>
        <button class="icon-btn" data-close-panel>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>

      <div class="side-panel-body">
        <div class="panel-section">
          <div class="panel-section-title">
            Información general
            <button class="btn btn-secondary btn-sm write-only" id="btn-editar-proyecto">Editar</button>
          </div>
          <div class="info-grid">
            <div class="info-item"><div class="label">Fecha de inicio</div><div class="value">${formatDate(p.fecha_inicio)}</div></div>
            <div class="info-item"><div class="label">Fecha de fin estimada</div><div class="value">${p.fecha_fin ? formatDate(p.fecha_fin) : "—"}</div></div>
            <div class="info-item"><div class="label">Presupuesto</div><div class="value">${formatMoney(p.presupuesto)}</div></div>
            <div class="info-item"><div class="label">Costo nómina/mes</div><div class="value">${formatMoney(p.costo_nomina_mes)}</div></div>
            <div class="info-item"><div class="label">Tamaño del equipo</div><div class="value">${p.tamano_equipo}</div></div>
            <div class="info-item"><div class="label">% Rotación</div><div class="value">${p.porcentaje_rotacion}%</div></div>
          </div>
        </div>

        <div class="panel-section">
          <div class="panel-section-title">
            Equipo asignado
            <button class="btn btn-ghost btn-sm write-only" data-toggle="form-agregar-persona">+ Agregar persona</button>
          </div>
          <form id="form-agregar-persona" class="hidden" style="margin-bottom:12px;">
            <div class="field-row" style="align-items:end;">
              <select name="empleado_id" required>
                <option value="">Selecciona un empleado</option>
                ${empleadosDisponibles.map((e) => `<option value="${e.id}">${escapeHtml(e.nombre_completo)}</option>`).join("")}
              </select>
              <input type="number" placeholder="% dedicación" name="porcentaje" min="1" max="100" required>
            </div>
            <button type="submit" class="btn btn-primary btn-sm">Agregar al equipo</button>
          </form>
          <div id="lista-equipo">
            ${
              p.participaciones.length
                ? p.participaciones
                    .map(
                      (part) => `
              <div class="list-item">
                <div class="person-cell">
                  ${avatarHtml(part.empleado_nombre, null, 30)}
                  <div>
                    <div class="list-item-main">${escapeHtml(part.empleado_nombre)}</div>
                    <div class="list-item-sub">${part.porcentaje}% de dedicación</div>
                  </div>
                </div>
                <button class="list-item-remove write-only" data-remove-participacion="${part.id}">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
                </button>
              </div>`
                    )
                    .join("")
                : '<p class="text-faint">Sin personas asignadas.</p>'
            }
          </div>
        </div>
      </div>

      <div class="side-panel-footer write-only">
        <button class="btn btn-danger btn-sm" id="btn-eliminar-proyecto">Eliminar proyecto</button>
      </div>
    `;

    openSidePanel(html);
    if (isReadOnly()) document.body.classList.add("read-only");
    bindPanelEvents(p);
  }

  function bindPanelEvents(p) {
    document.querySelectorAll("[data-toggle]").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.getElementById(btn.dataset.toggle).classList.toggle("hidden");
      });
    });

    const form = document.getElementById("form-agregar-persona");
    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(form);
      try {
        await api.post("/participaciones", {
          empleado_id: Number(fd.get("empleado_id")),
          proyecto_id: p.id,
          porcentaje: Number(fd.get("porcentaje")),
        });
        showToast("Persona agregada al proyecto");
        openProyectoPanel(p.id);
        loadProyectos();
      } catch (err) {
        handleApiError(err);
      }
    });

    document.querySelectorAll("[data-remove-participacion]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        try {
          await api.del(`/participaciones/${btn.dataset.removeParticipacion}`);
          openProyectoPanel(p.id);
          loadProyectos();
        } catch (err) {
          handleApiError(err);
        }
      });
    });

    document.getElementById("btn-editar-proyecto").addEventListener("click", () => openEditModal(p));
    document.getElementById("btn-eliminar-proyecto").addEventListener("click", async () => {
      if (!confirm(`¿Eliminar el proyecto "${p.nombre}"? Esta acción no se puede deshacer.`)) return;
      try {
        await api.del(`/proyectos/${p.id}`);
        showToast("Proyecto eliminado");
        closeSidePanel();
        loadProyectos();
      } catch (err) {
        handleApiError(err);
      }
    });
  }

  function proyectoFormHtml(p = {}) {
    const estado = p.estado || "Activo";
    return `
      <div class="field">
        <label>Nombre del proyecto</label>
        <input type="text" name="nombre" value="${escapeHtml(p.nombre) || ""}" required>
      </div>
      <div class="field">
        <label>Contratante / cliente</label>
        <input type="text" name="contratante" value="${escapeHtml(p.contratante) || ""}" required>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Fecha de inicio</label>
          <input type="date" name="fecha_inicio" value="${p.fecha_inicio || ""}" required>
        </div>
        <div class="field">
          <label>Fecha de fin estimada</label>
          <input type="date" name="fecha_fin" value="${p.fecha_fin || ""}">
        </div>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Presupuesto (COP)</label>
          <input type="number" name="presupuesto" min="0" value="${p.presupuesto ?? 0}" required>
        </div>
        <div class="field">
          <label>Estado</label>
          <select name="estado">
            ${["Activo", "Continuo", "Cierre"].map((s) => `<option ${s === estado ? "selected" : ""}>${s}</option>`).join("")}
          </select>
        </div>
      </div>
    `;
  }

  function bindNuevoProyecto() {
    document.getElementById("btn-nuevo-proyecto").addEventListener("click", () => {
      const overlay = openModal(`
        <div class="modal-header">
          <h3>Crear proyecto</h3>
          <button class="icon-btn" data-close-modal>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <form id="form-nuevo-proyecto">
          <div class="modal-body">${proyectoFormHtml()}</div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
            <button type="submit" class="btn btn-primary">Crear proyecto</button>
          </div>
        </form>
      `);
      overlay.querySelector("#form-nuevo-proyecto").addEventListener("submit", async (ev) => {
        ev.preventDefault();
        const fd = new FormData(ev.target);
        const payload = Object.fromEntries(fd.entries());
        payload.presupuesto = Number(payload.presupuesto || 0);
        if (!payload.fecha_fin) delete payload.fecha_fin;
        try {
          await api.post("/proyectos", payload);
          showToast("Proyecto creado correctamente");
          closeModal();
          loadProyectos();
        } catch (err) {
          handleApiError(err);
        }
      });
    });
  }

  function openEditModal(p) {
    const overlay = openModal(`
      <div class="modal-header">
        <h3>Editar proyecto</h3>
        <button class="icon-btn" data-close-modal>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <form id="form-editar-proyecto">
        <div class="modal-body">${proyectoFormHtml(p)}</div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
          <button type="submit" class="btn btn-primary">Guardar cambios</button>
        </div>
      </form>
    `);
    overlay.querySelector("#form-editar-proyecto").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const payload = Object.fromEntries(fd.entries());
      payload.presupuesto = Number(payload.presupuesto || 0);
      if (!payload.fecha_fin) payload.fecha_fin = null;
      try {
        await api.put(`/proyectos/${p.id}`, payload);
        showToast("Proyecto actualizado");
        closeModal();
        loadProyectos();
        openProyectoPanel(p.id);
      } catch (err) {
        handleApiError(err);
      }
    });
  }

  init();
})();
