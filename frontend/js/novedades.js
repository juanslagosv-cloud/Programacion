(() => {
  const state = { empleados: [], proyectos: [], filtros: {} };

  async function init() {
    renderShell("novedades.html", "Novedades");
    try {
      [state.empleados, state.proyectos] = await Promise.all([
        api.get("/empleados"),
        api.get("/proyectos"),
      ]);
    } catch (err) {
      handleApiError(err);
    }
    loadNovedades();
    bindFilters();
    bindNuevaNovedad();
  }

  function bindFilters() {
    document.getElementById("f-tipo").addEventListener("change", (e) => {
      state.filtros.tipo = e.target.value;
      loadNovedades();
    });
    document.getElementById("f-procesada").addEventListener("change", (e) => {
      state.filtros.procesada = e.target.value;
      loadNovedades();
    });
  }

  async function loadNovedades() {
    const tbody = document.getElementById("novedades-tbody");
    tbody.innerHTML = `<tr><td colspan="7" class="table-empty">Cargando novedades…</td></tr>`;
    const params = new URLSearchParams();
    Object.entries(state.filtros).forEach(([k, v]) => v !== "" && v !== undefined && params.set(k, v));
    try {
      const novedades = await api.get(`/novedades?${params.toString()}`);
      renderTable(novedades);
    } catch (err) {
      handleApiError(err);
      tbody.innerHTML = `<tr><td colspan="7" class="table-empty">No se pudieron cargar las novedades.</td></tr>`;
    }
  }

  function tipoBadgeClass(tipo) {
    if (tipo === "Ingreso") return "badge-success";
    if (tipo === "Salida") return "badge-danger";
    if (tipo === "Incapacidad") return "badge-warning";
    return "badge-info";
  }

  function renderTable(novedades) {
    const tbody = document.getElementById("novedades-tbody");
    if (!novedades.length) {
      tbody.innerHTML = `<tr><td colspan="7" class="table-empty">No hay novedades con estos filtros.</td></tr>`;
      return;
    }
    tbody.innerHTML = novedades
      .map(
        (n) => `
      <tr data-id="${n.id}">
        <td><div class="person-name">${escapeHtml(n.empleado_nombre)}</div></td>
        <td><span class="badge ${tipoBadgeClass(n.tipo)}">${n.tipo}</span></td>
        <td>${n.proyecto_nombre ? escapeHtml(n.proyecto_nombre) : '<span class="text-faint">—</span>'}</td>
        <td>${formatDate(n.fecha)}</td>
        <td class="text-muted">${n.detalle ? escapeHtml(n.detalle) : "—"}</td>
        <td>
          <span class="badge ${n.procesada ? "badge-success" : "badge-warning"}">
            <span class="badge-dot"></span>${n.procesada ? "Procesada" : "Sin procesar"}
          </span>
        </td>
        <td>
          ${!n.procesada ? `<button class="btn btn-secondary btn-sm write-only" data-procesar="${n.id}">Marcar procesada</button>` : ""}
        </td>
      </tr>`
      )
      .join("");

    tbody.querySelectorAll("[data-procesar]").forEach((btn) => {
      btn.addEventListener("click", async (ev) => {
        ev.stopPropagation();
        try {
          await api.put(`/novedades/${btn.dataset.procesar}/procesar`, {});
          showToast("Novedad marcada como procesada");
          loadNovedades();
        } catch (err) {
          handleApiError(err);
        }
      });
    });
  }

  function bindNuevaNovedad() {
    document.getElementById("btn-nueva-novedad").addEventListener("click", () => {
      const overlay = openModal(`
        <div class="modal-header">
          <h3>Registrar novedad</h3>
          <button class="icon-btn" data-close-modal>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <form id="form-novedad">
          <div class="modal-body">
            <div class="field">
              <label>Empleado</label>
              <select name="empleado_id" required>
                <option value="">Selecciona un empleado</option>
                ${state.empleados.map((e) => `<option value="${e.id}">${escapeHtml(e.nombre_completo)}</option>`).join("")}
              </select>
            </div>
            <div class="field-row">
              <div class="field">
                <label>Tipo de novedad</label>
                <select name="tipo" required>
                  <option>Ingreso</option>
                  <option>Salida</option>
                  <option>Cambio de proyecto</option>
                  <option>Incapacidad</option>
                  <option>Otro</option>
                </select>
              </div>
              <div class="field">
                <label>Fecha</label>
                <input type="date" name="fecha" required>
              </div>
            </div>
            <div class="field">
              <label>Proyecto relacionado (opcional)</label>
              <select name="proyecto_id">
                <option value="">Ninguno</option>
                ${state.proyectos.map((p) => `<option value="${p.id}">${escapeHtml(p.nombre)}</option>`).join("")}
              </select>
            </div>
            <div class="field">
              <label>Detalle</label>
              <textarea name="detalle" placeholder="Describe la novedad..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
            <button type="submit" class="btn btn-primary">Registrar</button>
          </div>
        </form>
      `);
      overlay.querySelector("#form-novedad").addEventListener("submit", async (ev) => {
        ev.preventDefault();
        const fd = new FormData(ev.target);
        const payload = {
          empleado_id: Number(fd.get("empleado_id")),
          tipo: fd.get("tipo"),
          fecha: fd.get("fecha"),
          detalle: fd.get("detalle") || null,
        };
        if (fd.get("proyecto_id")) payload.proyecto_id = Number(fd.get("proyecto_id"));
        try {
          await api.post("/novedades", payload);
          showToast("Novedad registrada correctamente");
          closeModal();
          loadNovedades();
        } catch (err) {
          handleApiError(err);
        }
      });
    });
  }

  init();
})();
