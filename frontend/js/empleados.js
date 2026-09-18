(() => {
  const state = { empleados: [], proyectos: [], filtros: {} };

  async function init() {
    renderShell("empleados.html", "Empleados");

    try {
      state.proyectos = await api.get("/proyectos");
    } catch (err) {
      handleApiError(err);
    }
    fillProyectoFilter();

    loadBirthdays();
    loadEmpleados();
    bindFilters();
    bindNuevoEmpleado();
  }

  function fillProyectoFilter() {
    const select = document.getElementById("f-proyecto");
    state.proyectos.forEach((p) => {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = p.nombre;
      select.appendChild(opt);
    });
  }

  function bindFilters() {
    document.getElementById("f-buscar").addEventListener(
      "input",
      debounce((e) => {
        state.filtros.q = e.target.value.trim();
        loadEmpleados();
      }, 350)
    );
    document.getElementById("f-estado").addEventListener("change", (e) => {
      state.filtros.estado = e.target.value;
      loadEmpleados();
    });
    document.getElementById("f-proyecto").addEventListener("change", (e) => {
      state.filtros.proyecto_id = e.target.value;
      loadEmpleados();
    });
    document.getElementById("f-tipo-cargo").addEventListener("change", (e) => {
      state.filtros.tipo_cargo = e.target.value;
      loadEmpleados();
    });
  }

  async function loadBirthdays() {
    const host = document.getElementById("birthday-widget");
    try {
      const cumpleanos = await api.get("/empleados/cumpleanos?dias=45");
      if (!cumpleanos.length) {
        host.innerHTML = "";
        return;
      }
      host.innerHTML = `
        <div class="birthday-widget fade-up">
          <div class="birthday-widget-title">
            🎂 Próximos cumpleaños
          </div>
          <div class="birthday-scroll">
            ${cumpleanos
              .map(
                (c) => `
              <div class="birthday-card">
                ${avatarHtml(c.nombre_completo, c.foto_url, 40)}
                <div>
                  <div class="birthday-name">${escapeHtml(c.nombre_completo)} ${
                  c.etiqueta ? `<span class="birthday-tag">${c.etiqueta}</span>` : ""
                }</div>
                  <div class="birthday-role">${escapeHtml(c.nombre_cargo)}</div>
                  <div class="birthday-date">${formatDate(c.proxima_fecha)}</div>
                </div>
              </div>`
              )
              .join("")}
          </div>
        </div>
      `;
    } catch (err) {
      host.innerHTML = "";
    }
  }

  async function loadEmpleados() {
    const tbody = document.getElementById("empleados-tbody");
    tbody.innerHTML = `<tr><td colspan="8" class="table-empty">Cargando empleados…</td></tr>`;

    const params = new URLSearchParams();
    Object.entries(state.filtros).forEach(([k, v]) => {
      if (v) params.set(k, v);
    });

    try {
      const empleados = await api.get(`/empleados?${params.toString()}`);
      state.empleados = empleados;
      renderTable(empleados);
    } catch (err) {
      handleApiError(err);
      tbody.innerHTML = `<tr><td colspan="8" class="table-empty">No se pudieron cargar los empleados.</td></tr>`;
    }
  }

  function renderTable(empleados) {
    const tbody = document.getElementById("empleados-tbody");
    if (!empleados.length) {
      tbody.innerHTML = `<tr><td colspan="8" class="table-empty">No se encontraron empleados con estos filtros.</td></tr>`;
      return;
    }
    tbody.innerHTML = empleados
      .map(
        (e) => `
      <tr data-id="${e.id}">
        <td>
          <div class="person-cell">
            ${avatarHtml(e.nombre_completo, e.foto_url)}
            <div>
              <div class="person-name">${escapeHtml(e.nombre_completo)}</div>
              <div class="person-sub">${escapeHtml(e.nombre_cargo)}</div>
            </div>
          </div>
        </td>
        <td>${escapeHtml(e.nombre_cargo)}</td>
        <td><span class="badge badge-neutral">${e.tipo_cargo}</span></td>
        <td><span class="badge ${e.periodicidad_pago === "Quincenal" ? "badge-info" : "badge-neutral"}">${e.periodicidad_pago}</span></td>
        <td>${e.proyectos.length ? e.proyectos.map((p) => `<div class="person-sub">${escapeHtml(p)}</div>`).join("") : '<span class="text-faint">Sin asignar</span>'}</td>
        <td>
          <div class="flex gap-8" style="align-items:center;">
            <div class="progress-track"><div class="progress-fill" style="width:${Math.min(e.porcentaje_total, 100)}%"></div></div>
            <span class="text-muted" style="font-size:12px;">${e.porcentaje_total}%</span>
          </div>
        </td>
        <td>${antiguedadTexto(e.antiguedad_meses)}</td>
        <td>
          <span class="badge ${e.estado === "Activo" ? "badge-success" : "badge-neutral"}">
            <span class="badge-dot"></span>${e.estado}
          </span>
        </td>
      </tr>`
      )
      .join("");

    tbody.querySelectorAll("tr[data-id]").forEach((row) => {
      row.addEventListener("click", () => openEmpleadoPanel(Number(row.dataset.id)));
    });
  }

  /* ------------------------------------------------------------------
     Panel lateral: ficha del empleado
     ------------------------------------------------------------------ */

  async function openEmpleadoPanel(id) {
    let empleado;
    try {
      empleado = await api.get(`/empleados/${id}`);
    } catch (err) {
      handleApiError(err);
      return;
    }
    renderEmpleadoPanel(empleado);
  }

  function renderEmpleadoPanel(e) {
    const proyectosDisponibles = state.proyectos.filter(
      (p) => !e.participaciones.some((part) => part.proyecto_id === p.id)
    );

    const html = `
      <div class="side-panel-header">
        <div class="panel-profile">
          ${avatarHtml(e.nombre_completo, e.foto_url, 56)}
          <div>
            <div class="panel-profile-name">${escapeHtml(e.nombre_completo)}</div>
            <div class="panel-profile-role">${escapeHtml(e.nombre_cargo)}</div>
            <span class="badge ${e.estado === "Activo" ? "badge-success" : "badge-neutral"}" style="margin-top:6px;">
              <span class="badge-dot"></span>${e.estado}
            </span>
          </div>
        </div>
        <button class="icon-btn" data-close-panel>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>

      <div class="side-panel-body">
        <div class="panel-section">
          <div class="panel-section-title">
            Información general
            <button class="btn btn-secondary btn-sm write-only" id="btn-editar-empleado">Editar</button>
          </div>
          <div class="info-grid">
            <div class="info-item"><div class="label">Género</div><div class="value">${e.genero}</div></div>
            <div class="info-item"><div class="label">Fecha de nacimiento</div><div class="value">${formatDate(e.fecha_nacimiento)}</div></div>
            <div class="info-item"><div class="label">Nivel educativo</div><div class="value">${e.nivel_educativo}</div></div>
            <div class="info-item"><div class="label">Tipo de cargo</div><div class="value">${e.tipo_cargo}</div></div>
            <div class="info-item"><div class="label">Periodicidad de pago</div><div class="value">${e.periodicidad_pago}</div></div>
            <div class="info-item"><div class="label">Fecha de ingreso</div><div class="value">${formatDate(e.fecha_ingreso)}</div></div>
            <div class="info-item"><div class="label">Antigüedad</div><div class="value">${antiguedadTexto(e.antiguedad_meses)}</div></div>
            <div class="info-item" style="grid-column:1/-1;"><div class="label">Dirección</div><div class="value">${escapeHtml(e.direccion) || "—"}</div></div>
          </div>
        </div>

        <div class="panel-section">
          <div class="panel-section-title">
            Formación académica
            <button class="btn btn-ghost btn-sm write-only" data-toggle="form-estudio">+ Agregar</button>
          </div>
          <form id="form-estudio" class="hidden" style="margin-bottom:12px;">
            <div class="field-row">
              <input type="text" placeholder="Título" name="titulo" required>
              <input type="text" placeholder="Institución" name="institucion" required>
            </div>
            <div class="field-row" style="align-items:end;">
              <input type="number" placeholder="Año" name="anio" min="1950" max="2100" required>
              <button type="submit" class="btn btn-primary btn-sm">Guardar</button>
            </div>
          </form>
          <div id="lista-estudios">
            ${
              e.estudios.length
                ? e.estudios
                    .map(
                      (s) => `
              <div class="list-item">
                <div>
                  <div class="list-item-main">${escapeHtml(s.titulo)}</div>
                  <div class="list-item-sub">${escapeHtml(s.institucion)} · ${s.anio}</div>
                </div>
                <button class="list-item-remove write-only" data-remove-estudio="${s.id}">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
                </button>
              </div>`
                    )
                    .join("")
                : '<p class="text-faint">Sin formación registrada.</p>'
            }
          </div>
        </div>

        <div class="panel-section">
          <div class="panel-section-title">
            Experiencia laboral
            <button class="btn btn-ghost btn-sm write-only" data-toggle="form-experiencia">+ Agregar</button>
          </div>
          <form id="form-experiencia" class="hidden" style="margin-bottom:12px;">
            <div class="field-row">
              <input type="text" placeholder="Empresa" name="empresa" required>
              <input type="text" placeholder="Cargo" name="cargo" required>
            </div>
            <div class="field-row" style="align-items:end;">
              <input type="text" placeholder="Período (ej. 2019 - 2021)" name="periodo" required>
              <button type="submit" class="btn btn-primary btn-sm">Guardar</button>
            </div>
          </form>
          <div id="lista-experiencia">
            ${
              e.experiencias.length
                ? e.experiencias
                    .map(
                      (x) => `
              <div class="list-item">
                <div>
                  <div class="list-item-main">${escapeHtml(x.cargo)} · ${escapeHtml(x.empresa)}</div>
                  <div class="list-item-sub">${escapeHtml(x.periodo)}</div>
                </div>
                <button class="list-item-remove write-only" data-remove-experiencia="${x.id}">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
                </button>
              </div>`
                    )
                    .join("")
                : '<p class="text-faint">Sin experiencia registrada.</p>'
            }
          </div>
        </div>

        <div class="panel-section">
          <div class="panel-section-title">
            Proyectos asignados (${e.porcentaje_total}% del tiempo)
            <button class="btn btn-ghost btn-sm write-only" data-toggle="form-participacion">+ Asignar</button>
          </div>
          <form id="form-participacion" class="hidden" style="margin-bottom:12px;">
            <div class="field-row" style="align-items:end;">
              <select name="proyecto_id" required>
                <option value="">Selecciona un proyecto</option>
                ${proyectosDisponibles.map((p) => `<option value="${p.id}">${escapeHtml(p.nombre)}</option>`).join("")}
              </select>
              <input type="number" placeholder="% dedicación" name="porcentaje" min="1" max="100" required>
            </div>
            <button type="submit" class="btn btn-primary btn-sm">Asignar al proyecto</button>
          </form>
          <div id="lista-participaciones">
            ${
              e.participaciones.length
                ? e.participaciones
                    .map(
                      (p) => `
              <div class="list-item">
                <div>
                  <div class="list-item-main">${escapeHtml(p.proyecto_nombre)}</div>
                  <div class="list-item-sub">${p.porcentaje}% de dedicación</div>
                </div>
                <button class="list-item-remove write-only" data-remove-participacion="${p.id}">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
                </button>
              </div>`
                    )
                    .join("")
                : '<p class="text-faint">Sin proyectos asignados.</p>'
            }
          </div>
        </div>

        <div class="panel-section">
          <div class="panel-section-title">Vacaciones</div>
          <div class="info-grid">
            <div class="info-item"><div class="label">Última toma</div><div class="value">${formatDate(e.vacaciones_ultima_toma)}</div></div>
            <div class="info-item"><div class="label">Días pendientes</div><div class="value">${e.vacaciones_dias_pendientes} días</div></div>
          </div>
        </div>

        <div class="panel-section">
          <div class="panel-section-title">Historial de movimientos</div>
          <div id="lista-historial"><p class="text-faint">Cargando…</p></div>
        </div>
      </div>

      <div class="side-panel-footer write-only">
        <button class="btn btn-danger btn-sm" id="btn-eliminar-empleado">Eliminar empleado</button>
      </div>
    `;

    openSidePanel(html);
    if (isReadOnly()) document.body.classList.add("read-only");

    bindPanelEvents(e);
    loadHistorial(e.id);
  }

  function bindPanelEvents(e) {
    document.querySelectorAll("[data-toggle]").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.getElementById(btn.dataset.toggle).classList.toggle("hidden");
      });
    });

    const formEstudio = document.getElementById("form-estudio");
    formEstudio.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(formEstudio);
      try {
        await api.post(`/empleados/${e.id}/estudios`, {
          titulo: fd.get("titulo"),
          institucion: fd.get("institucion"),
          anio: Number(fd.get("anio")),
        });
        showToast("Formación académica agregada");
        openEmpleadoPanel(e.id);
      } catch (err) {
        handleApiError(err);
      }
    });

    const formExperiencia = document.getElementById("form-experiencia");
    formExperiencia.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(formExperiencia);
      try {
        await api.post(`/empleados/${e.id}/experiencia`, {
          empresa: fd.get("empresa"),
          cargo: fd.get("cargo"),
          periodo: fd.get("periodo"),
        });
        showToast("Experiencia laboral agregada");
        openEmpleadoPanel(e.id);
      } catch (err) {
        handleApiError(err);
      }
    });

    const formParticipacion = document.getElementById("form-participacion");
    formParticipacion.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(formParticipacion);
      try {
        await api.post("/participaciones", {
          empleado_id: e.id,
          proyecto_id: Number(fd.get("proyecto_id")),
          porcentaje: Number(fd.get("porcentaje")),
        });
        showToast("Empleado asignado al proyecto");
        openEmpleadoPanel(e.id);
        loadEmpleados();
      } catch (err) {
        handleApiError(err);
      }
    });

    document.querySelectorAll("[data-remove-estudio]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        try {
          await api.del(`/empleados/${e.id}/estudios/${btn.dataset.removeEstudio}`);
          openEmpleadoPanel(e.id);
        } catch (err) {
          handleApiError(err);
        }
      });
    });

    document.querySelectorAll("[data-remove-experiencia]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        try {
          await api.del(`/empleados/${e.id}/experiencia/${btn.dataset.removeExperiencia}`);
          openEmpleadoPanel(e.id);
        } catch (err) {
          handleApiError(err);
        }
      });
    });

    document.querySelectorAll("[data-remove-participacion]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        try {
          await api.del(`/participaciones/${btn.dataset.removeParticipacion}`);
          openEmpleadoPanel(e.id);
          loadEmpleados();
        } catch (err) {
          handleApiError(err);
        }
      });
    });

    document.getElementById("btn-editar-empleado").addEventListener("click", () => openEditModal(e));
    document.getElementById("btn-eliminar-empleado").addEventListener("click", async () => {
      if (!confirm(`¿Eliminar a ${e.nombre_completo}? Esta acción no se puede deshacer.`)) return;
      try {
        await api.del(`/empleados/${e.id}`);
        showToast("Empleado eliminado");
        closeSidePanel();
        loadEmpleados();
      } catch (err) {
        handleApiError(err);
      }
    });
  }

  async function loadHistorial(empleadoId) {
    const host = document.getElementById("lista-historial");
    if (!host) return;
    try {
      const novedades = await api.get(`/novedades?empleado_id=${empleadoId}`);
      host.innerHTML = novedades.length
        ? novedades
            .map(
              (n) => `
          <div class="list-item">
            <div>
              <div class="list-item-main">${n.tipo}${n.proyecto_nombre ? ` · ${escapeHtml(n.proyecto_nombre)}` : ""}</div>
              <div class="list-item-sub">${formatDate(n.fecha)}${n.detalle ? ` — ${escapeHtml(n.detalle)}` : ""}</div>
            </div>
          </div>`
            )
            .join("")
        : '<p class="text-faint">Sin movimientos registrados.</p>';
    } catch (err) {
      host.innerHTML = '<p class="text-faint">No se pudo cargar el historial.</p>';
    }
  }

  /* ------------------------------------------------------------------
     Modales: crear / editar empleado
     ------------------------------------------------------------------ */

  function empleadoFormHtml(e = {}) {
    const gen = e.genero || "Femenino";
    const nivel = e.nivel_educativo || "Profesional";
    const tipo = e.tipo_cargo || "Profesional";
    const periodicidad = e.periodicidad_pago || "Mensual";
    const estado = e.estado || "Activo";
    return `
      <div class="field-row">
        <div class="field">
          <label>Nombre completo</label>
          <input type="text" name="nombre_completo" value="${escapeHtml(e.nombre_completo) || ""}" required>
        </div>
        <div class="field">
          <label>Género</label>
          <select name="genero">
            ${["Femenino", "Masculino", "Otro"].map((g) => `<option ${g === gen ? "selected" : ""}>${g}</option>`).join("")}
          </select>
        </div>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Fecha de nacimiento</label>
          <input type="date" name="fecha_nacimiento" value="${e.fecha_nacimiento || ""}" required>
        </div>
        <div class="field">
          <label>Fecha de ingreso</label>
          <input type="date" name="fecha_ingreso" value="${e.fecha_ingreso || ""}" required>
        </div>
      </div>
      <div class="field">
        <label>Dirección</label>
        <input type="text" name="direccion" value="${escapeHtml(e.direccion) || ""}">
      </div>
      <div class="field-row">
        <div class="field">
          <label>Nivel educativo</label>
          <select name="nivel_educativo">
            ${["Bachiller", "Técnico", "Tecnólogo", "Profesional", "Especialización", "Maestría"]
              .map((n) => `<option ${n === nivel ? "selected" : ""}>${n}</option>`)
              .join("")}
          </select>
        </div>
        <div class="field">
          <label>Tipo de cargo</label>
          <select name="tipo_cargo">
            ${["Profesional", "Técnico", "Operario", "Administrativo"]
              .map((t) => `<option ${t === tipo ? "selected" : ""}>${t}</option>`)
              .join("")}
          </select>
        </div>
      </div>
      <div class="field">
        <label>Nombre del cargo</label>
        <input type="text" name="nombre_cargo" value="${escapeHtml(e.nombre_cargo) || ""}" required>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Estado</label>
          <select name="estado">
            ${["Activo", "Inactivo"].map((s) => `<option ${s === estado ? "selected" : ""}>${s}</option>`).join("")}
          </select>
        </div>
        <div class="field">
          <label>Periodicidad de pago</label>
          <select name="periodicidad_pago">
            ${["Mensual", "Quincenal"].map((p) => `<option ${p === periodicidad ? "selected" : ""}>${p}</option>`).join("")}
          </select>
          <span class="text-faint" style="font-size:11px;">Mensual: se paga el último día del mes. Quincenal: el 15 y el último día.</span>
        </div>
      </div>
      <div class="field">
        <label>Días de vacaciones pendientes</label>
        <input type="number" name="vacaciones_dias_pendientes" min="0" value="${e.vacaciones_dias_pendientes ?? 0}">
      </div>
      <div class="field">
        <label>Última toma de vacaciones</label>
        <input type="date" name="vacaciones_ultima_toma" value="${e.vacaciones_ultima_toma || ""}">
      </div>
    `;
  }

  function bindNuevoEmpleado() {
    document.getElementById("btn-nuevo-empleado").addEventListener("click", () => {
      const overlay = openModal(`
        <div class="modal-header">
          <h3>Agregar empleado</h3>
          <button class="icon-btn" data-close-modal>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <form id="form-nuevo-empleado">
          <div class="modal-body">${empleadoFormHtml()}</div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
            <button type="submit" class="btn btn-primary">Guardar empleado</button>
          </div>
        </form>
      `);
      overlay.querySelector("#form-nuevo-empleado").addEventListener("submit", async (ev) => {
        ev.preventDefault();
        const fd = new FormData(ev.target);
        const payload = Object.fromEntries(fd.entries());
        payload.vacaciones_dias_pendientes = Number(payload.vacaciones_dias_pendientes || 0);
        if (!payload.vacaciones_ultima_toma) delete payload.vacaciones_ultima_toma;
        try {
          await api.post("/empleados", payload);
          showToast("Empleado creado correctamente");
          closeModal();
          loadEmpleados();
        } catch (err) {
          handleApiError(err);
        }
      });
    });
  }

  function openEditModal(e) {
    const overlay = openModal(`
      <div class="modal-header">
        <h3>Editar empleado</h3>
        <button class="icon-btn" data-close-modal>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <form id="form-editar-empleado">
        <div class="modal-body">${empleadoFormHtml(e)}</div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
          <button type="submit" class="btn btn-primary">Guardar cambios</button>
        </div>
      </form>
    `);
    overlay.querySelector("#form-editar-empleado").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const payload = Object.fromEntries(fd.entries());
      payload.vacaciones_dias_pendientes = Number(payload.vacaciones_dias_pendientes || 0);
      if (!payload.vacaciones_ultima_toma) payload.vacaciones_ultima_toma = null;
      try {
        await api.put(`/empleados/${e.id}`, payload);
        showToast("Empleado actualizado");
        closeModal();
        loadEmpleados();
        openEmpleadoPanel(e.id);
      } catch (err) {
        handleApiError(err);
      }
    });
  }

  init();
})();
