(() => {
  const state = { empleados: [], empleadosTodos: [], proyectos: [], empresas: [], filtros: {} };

  async function init() {
    renderShell("empleados.html", "Empleados");

    try {
      [state.proyectos, state.empresas, state.empleadosTodos] = await Promise.all([
        api.get("/proyectos"),
        api.get("/empresas"),
        api.get("/empleados"),
      ]);
    } catch (err) {
      handleApiError(err);
    }
    fillProyectoFilter();
    fillEmpresaFilter();

    loadBirthdays();
    loadEmpleados();
    bindFilters();
    bindNuevoEmpleado();
    bindGestionEmpresas();
  }

  function fillEmpresaFilter() {
    const select = document.getElementById("f-empresa");
    state.empresas.forEach((emp) => {
      const opt = document.createElement("option");
      opt.value = emp.id;
      opt.textContent = emp.nombre;
      select.appendChild(opt);
    });
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
    document.getElementById("f-empresa").addEventListener("change", (e) => {
      state.filtros.empresa_id = e.target.value;
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
              ${e.empresa_nombre
                ? `<span class="badge badge-info" style="margin-top:4px;">${escapeHtml(e.empresa_nombre)}</span>`
                : `<span class="badge badge-danger" style="margin-top:4px;">Sin empresa asignada</span>`}
            </div>
          </div>
        </td>
        <td>
          ${escapeHtml(e.nombre_cargo)}
          <div class="person-sub">${e.numero_documento ? `${e.tipo_documento} ${escapeHtml(e.numero_documento)}` : "Sin documento"}</div>
        </td>
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

  function estadoContratoBadgeClass(estado) {
    if (estado === "Activo") return "badge-success";
    if (estado === "Vencido") return "badge-danger";
    if (estado === "Suspendido") return "badge-warning";
    return "badge-neutral";
  }

  function contratoCardHtml(c) {
    const modificacionesHtml = c.modificaciones.length
      ? c.modificaciones
          .map(
            (m) => `
          <div class="list-item" style="padding-left:14px;">
            <div>
              <div class="list-item-main">${m.tipo}${m.nueva_fecha_fin ? ` · nueva fecha fin: ${formatDate(m.nueva_fecha_fin)}` : ""}</div>
              <div class="list-item-sub">${formatDate(m.fecha)} — ${escapeHtml(m.detalle)}</div>
            </div>
            <button class="list-item-remove write-only" data-remove-modificacion="${m.id}">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
            </button>
          </div>`
          )
          .join("")
      : "";

    return `
      <div class="list-item" style="flex-direction:column;align-items:stretch;gap:10px;margin-bottom:10px;">
        <div class="flex" style="justify-content:space-between;align-items:flex-start;">
          <div>
            <div class="list-item-main">${c.tipo_contrato} · ${escapeHtml(c.cargo_contractual)}</div>
            <div class="list-item-sub">${formatDate(c.fecha_inicio)} → ${c.fecha_fin ? formatDate(c.fecha_fin) : "Indefinido"} · ${c.duracion}</div>
          </div>
          <div class="flex gap-8" style="flex-wrap:wrap;justify-content:flex-end;">
            <span class="badge ${estadoContratoBadgeClass(c.estado)}"><span class="badge-dot"></span>${c.estado}</span>
            ${c.vencido ? '<span class="badge badge-danger">Vencido</span>' : ""}
          </div>
        </div>
        <div class="info-grid">
          <div class="info-item"><div class="label">Salario</div><div class="value">${formatMoney(c.salario)}</div></div>
          <div class="info-item"><div class="label">Modalidad</div><div class="value">${c.modalidad}</div></div>
          <div class="info-item"><div class="label">Proyecto</div><div class="value">${escapeHtml(c.proyecto_nombre) || "—"}</div></div>
          <div class="info-item"><div class="label">Centro de costos</div><div class="value">${escapeHtml(c.centro_costos) || "—"}</div></div>
          <div class="info-item"><div class="label">Período de prueba</div><div class="value">${c.periodo_prueba_dias != null ? `${c.periodo_prueba_dias} días` : "—"}</div></div>
        </div>
        ${modificacionesHtml}
        <div class="flex gap-8 write-only" style="flex-wrap:wrap;">
          <button class="btn btn-ghost btn-sm" data-prorroga-contrato="${c.id}">+ Prórroga</button>
          <button class="btn btn-ghost btn-sm" data-otrosi-contrato="${c.id}">+ Otrosí</button>
          <button class="btn btn-ghost btn-sm" data-editar-contrato="${c.id}">Editar</button>
          <button class="btn btn-ghost btn-sm" data-eliminar-contrato="${c.id}" style="color:var(--danger-text);">Eliminar</button>
        </div>
      </div>
    `;
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
            <div class="info-item"><div class="label">Empresa</div><div class="value">${escapeHtml(e.empresa_nombre) || "Sin asignar"}</div></div>
            <div class="info-item"><div class="label">Documento</div><div class="value">${e.tipo_documento} ${escapeHtml(e.numero_documento) || "—"}</div></div>
            <div class="info-item"><div class="label">Género</div><div class="value">${e.genero}</div></div>
            <div class="info-item"><div class="label">Fecha de nacimiento</div><div class="value">${formatDate(e.fecha_nacimiento)}</div></div>
            <div class="info-item"><div class="label">Nivel educativo</div><div class="value">${e.nivel_educativo}</div></div>
            <div class="info-item"><div class="label">Tipo de cargo</div><div class="value">${e.tipo_cargo}</div></div>
            <div class="info-item"><div class="label">Periodicidad de pago</div><div class="value">${e.periodicidad_pago}</div></div>
            <div class="info-item"><div class="label">Fecha de ingreso</div><div class="value">${formatDate(e.fecha_ingreso)}</div></div>
            <div class="info-item"><div class="label">Antigüedad</div><div class="value">${antiguedadTexto(e.antiguedad_meses)}</div></div>
            <div class="info-item" style="grid-column:1/-1;"><div class="label">Dirección</div><div class="value">${[escapeHtml(e.direccion), escapeHtml(e.ciudad)].filter(Boolean).join(", ") || "—"}</div></div>
          </div>
        </div>

        <div class="panel-section">
          <div class="panel-section-title">Información personal y organizacional</div>
          <div class="info-grid">
            <div class="info-item"><div class="label">Estado civil</div><div class="value">${e.estado_civil || "—"}</div></div>
            <div class="info-item"><div class="label">Área</div><div class="value">${escapeHtml(e.area) || "—"}</div></div>
            <div class="info-item"><div class="label">Cargo</div><div class="value">${escapeHtml(e.nombre_cargo)}</div></div>
            <div class="info-item"><div class="label">Jefe inmediato</div><div class="value">${escapeHtml(e.jefe_inmediato_nombre) || "—"}</div></div>
            <div class="info-item" style="grid-column:1/-1;"><div class="label">Contacto de emergencia</div><div class="value">${
              e.contacto_emergencia_nombre
                ? `${escapeHtml(e.contacto_emergencia_nombre)}${e.contacto_emergencia_parentesco ? ` (${escapeHtml(e.contacto_emergencia_parentesco)})` : ""} · ${escapeHtml(e.contacto_emergencia_telefono) || "sin teléfono"}`
                : "—"
            }</div></div>
          </div>
        </div>

        <div class="panel-section">
          <div class="panel-section-title">Afiliaciones y datos bancarios</div>
          <div class="info-grid">
            <div class="info-item"><div class="label">EPS</div><div class="value">${escapeHtml(e.eps) || "—"}</div></div>
            <div class="info-item"><div class="label">AFP</div><div class="value">${escapeHtml(e.afp) || "—"}</div></div>
            <div class="info-item"><div class="label">ARL</div><div class="value">${escapeHtml(e.arl) || "—"}</div></div>
            <div class="info-item"><div class="label">Nivel de riesgo ARL</div><div class="value">${e.nivel_riesgo_arl || "—"}</div></div>
            <div class="info-item"><div class="label">Caja de compensación</div><div class="value">${escapeHtml(e.caja_compensacion) || "—"}</div></div>
            <div class="info-item"><div class="label">Fondo de cesantías</div><div class="value">${escapeHtml(e.fondo_cesantias) || "—"}</div></div>
            <div class="info-item"><div class="label">Banco</div><div class="value">${escapeHtml(e.banco) || "—"}</div></div>
            <div class="info-item"><div class="label">Tipo de cuenta</div><div class="value">${e.tipo_cuenta || "—"}</div></div>
            <div class="info-item"><div class="label">Número de cuenta</div><div class="value">${escapeHtml(e.numero_cuenta) || "—"}</div></div>
          </div>
        </div>

        <div class="panel-section">
          <div class="panel-section-title">
            Historial contractual
            <button class="btn btn-ghost btn-sm write-only" id="btn-nuevo-contrato">+ Nuevo contrato</button>
          </div>
          <div id="lista-contratos">
            ${
              e.contratos.length
                ? e.contratos.map((c) => contratoCardHtml(c)).join("")
                : '<p class="text-faint">Sin contratos registrados.</p>'
            }
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
          <div class="panel-section-title">Documentos</div>
          <p class="text-muted" style="font-size:12.5px;margin-bottom:10px;">
            Certificado laboral en PDF con el nombre, el documento, el cargo y la fecha de ingreso.
          </p>
          <div class="field" style="max-width:220px;margin-bottom:10px;">
            <label>Fecha de expedición</label>
            <input type="date" id="cert-fecha" value="${todayIso()}" min="${e.fecha_ingreso || ""}" max="${todayIso()}">
          </div>
          <div class="flex gap-8" style="flex-wrap:wrap;">
            <button class="btn btn-secondary btn-sm" data-certificado="sin">Sin salario</button>
            <button class="btn btn-secondary btn-sm" data-certificado="con">Con salario</button>
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

    document.querySelectorAll("[data-certificado]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const conSalario = btn.dataset.certificado === "con";
        const fechaExpedicion = document.getElementById("cert-fecha").value || undefined;
        const textoOriginal = btn.textContent;
        btn.disabled = true;
        btn.textContent = "Generando…";
        try {
          await api.descargarCertificado(e.id, conSalario, fechaExpedicion);
          showToast("Certificado generado");
        } catch (err) {
          handleApiError(err);
        } finally {
          btn.disabled = false;
          btn.textContent = textoOriginal;
        }
      });
    });

    bindContratosEvents(e);

    document.getElementById("btn-editar-empleado").addEventListener("click", () => openEditModal(e));
    document.getElementById("btn-eliminar-empleado").addEventListener("click", async () => {
      if (!confirm(`¿Eliminar a ${e.nombre_completo}? Esta acción no se puede deshacer.`)) return;
      try {
        await api.del(`/empleados/${e.id}`);
        showToast("Empleado eliminado");
        closeSidePanel();
        loadEmpleados();
        state.empleadosTodos = await api.get("/empleados");
      } catch (err) {
        handleApiError(err);
      }
    });
  }

  /* ------------------------------------------------------------------
     Historial contractual
     ------------------------------------------------------------------ */

  function bindContratosEvents(e) {
    const btnNuevo = document.getElementById("btn-nuevo-contrato");
    if (btnNuevo) btnNuevo.addEventListener("click", () => openContratoForm(e, null));

    document.querySelectorAll("[data-editar-contrato]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const contrato = e.contratos.find((c) => c.id === Number(btn.dataset.editarContrato));
        openContratoForm(e, contrato);
      });
    });

    document.querySelectorAll("[data-eliminar-contrato]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (!confirm("¿Eliminar este contrato? Esta acción no se puede deshacer.")) return;
        try {
          await api.del(`/contratos/${btn.dataset.eliminarContrato}`);
          showToast("Contrato eliminado");
          openEmpleadoPanel(e.id);
        } catch (err) {
          handleApiError(err);
        }
      });
    });

    document.querySelectorAll("[data-prorroga-contrato]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const contrato = e.contratos.find((c) => c.id === Number(btn.dataset.prorrogaContrato));
        openModificacionForm(contrato, "Prórroga", e);
      });
    });

    document.querySelectorAll("[data-otrosi-contrato]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const contrato = e.contratos.find((c) => c.id === Number(btn.dataset.otrosiContrato));
        openModificacionForm(contrato, "Otrosí", e);
      });
    });

    document.querySelectorAll("[data-remove-modificacion]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        try {
          await api.del(`/modificaciones/${btn.dataset.removeModificacion}`);
          showToast("Modificación eliminada");
          openEmpleadoPanel(e.id);
        } catch (err) {
          handleApiError(err);
        }
      });
    });
  }

  function contratoFormHtml(empleado, c = {}) {
    const tipo = c.tipo_contrato || "Término indefinido";
    const modalidad = c.modalidad || "Presencial";
    const estado = c.estado || "Activo";
    const proyectoId = c.proyecto_id ?? "";
    return `
      <div class="field-row">
        <div class="field">
          <label>Tipo de contrato</label>
          <select name="tipo_contrato">
            ${["Término fijo", "Término indefinido", "Obra o labor", "Prestación de servicios", "Aprendizaje"]
              .map((t) => `<option ${t === tipo ? "selected" : ""}>${t}</option>`)
              .join("")}
          </select>
        </div>
        <div class="field">
          <label>Cargo contractual</label>
          <input type="text" name="cargo_contractual" value="${escapeHtml(c.cargo_contractual) || escapeHtml(empleado.nombre_cargo) || ""}" required>
        </div>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Fecha inicial</label>
          <input type="date" name="fecha_inicio" value="${c.fecha_inicio || ""}" required>
        </div>
        <div class="field">
          <label>Fecha final</label>
          <input type="date" name="fecha_fin" value="${c.fecha_fin || ""}">
          <span class="text-faint" style="font-size:11px;">Vacío para término indefinido</span>
        </div>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Período de prueba (días)</label>
          <input type="number" name="periodo_prueba_dias" min="0" value="${c.periodo_prueba_dias ?? ""}">
        </div>
        <div class="field">
          <label>Salario</label>
          <input type="number" name="salario" min="0" value="${c.salario ?? ""}" required>
        </div>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Proyecto</label>
          <select name="proyecto_id">
            <option value="">Sin proyecto asociado</option>
            ${state.proyectos
              .map((p) => `<option value="${p.id}" ${String(p.id) === String(proyectoId) ? "selected" : ""}>${escapeHtml(p.nombre)}</option>`)
              .join("")}
          </select>
        </div>
        <div class="field">
          <label>Centro de costos</label>
          <input type="text" name="centro_costos" value="${escapeHtml(c.centro_costos) || ""}">
        </div>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Modalidad</label>
          <select name="modalidad">
            ${["Presencial", "Híbrido", "Remoto"].map((m) => `<option ${m === modalidad ? "selected" : ""}>${m}</option>`).join("")}
          </select>
        </div>
        <div class="field">
          <label>Estado</label>
          <select name="estado">
            ${["Activo", "Vencido", "Suspendido", "Terminado"].map((s) => `<option ${s === estado ? "selected" : ""}>${s}</option>`).join("")}
          </select>
        </div>
      </div>
    `;
  }

  function openContratoForm(empleado, existing) {
    const esEdicion = !!existing;
    const overlay = openModal(`
      <div class="modal-header">
        <h3>${esEdicion ? "Editar contrato" : "Nuevo contrato"}</h3>
        <button class="icon-btn" data-close-modal>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <form id="form-contrato">
        <div class="modal-body">${contratoFormHtml(empleado, existing || {})}</div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
          <button type="submit" class="btn btn-primary">${esEdicion ? "Guardar cambios" : "Crear contrato"}</button>
        </div>
      </form>
    `);
    overlay.querySelector("#form-contrato").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const payload = Object.fromEntries(fd.entries());
      payload.salario = Number(payload.salario);
      payload.periodo_prueba_dias = payload.periodo_prueba_dias ? Number(payload.periodo_prueba_dias) : null;
      payload.proyecto_id = payload.proyecto_id ? Number(payload.proyecto_id) : null;
      payload.centro_costos = (payload.centro_costos || "").trim() || null;
      if (!payload.fecha_fin) payload.fecha_fin = null;
      try {
        if (esEdicion) {
          await api.put(`/contratos/${existing.id}`, payload);
          showToast("Contrato actualizado");
        } else {
          payload.empleado_id = empleado.id;
          await api.post("/contratos", payload);
          showToast("Contrato creado");
        }
        closeModal();
        openEmpleadoPanel(empleado.id);
      } catch (err) {
        handleApiError(err);
      }
    });
  }

  function openModificacionForm(contrato, tipo, empleado) {
    const overlay = openModal(`
      <div class="modal-header">
        <h3>${tipo === "Prórroga" ? "Registrar prórroga" : "Registrar otrosí"}</h3>
        <button class="icon-btn" data-close-modal>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <form id="form-modificacion">
        <div class="modal-body">
          <input type="hidden" name="tipo" value="${tipo}">
          <div class="field">
            <label>Fecha</label>
            <input type="date" name="fecha" value="${todayIso()}" required>
          </div>
          <div class="field">
            <label>Detalle</label>
            <textarea name="detalle" rows="3" required placeholder="¿Qué cambia?"></textarea>
          </div>
          ${
            tipo === "Prórroga"
              ? `<div class="field">
                  <label>Nueva fecha final</label>
                  <input type="date" name="nueva_fecha_fin" value="${contrato.fecha_fin || ""}" required>
                  <span class="text-faint" style="font-size:11px;">Reemplaza la fecha final del contrato.</span>
                </div>`
              : ""
          }
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
          <button type="submit" class="btn btn-primary">Guardar</button>
        </div>
      </form>
    `);
    overlay.querySelector("#form-modificacion").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const payload = Object.fromEntries(fd.entries());
      if (!payload.nueva_fecha_fin) delete payload.nueva_fecha_fin;
      try {
        await api.post(`/contratos/${contrato.id}/modificaciones`, payload);
        showToast(tipo === "Prórroga" ? "Prórroga registrada" : "Otrosí registrado");
        closeModal();
        openEmpleadoPanel(empleado.id);
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

  function sanearPayloadEmpleado(payload) {
    payload.vacaciones_dias_pendientes = Number(payload.vacaciones_dias_pendientes || 0);
    payload.numero_documento = (payload.numero_documento || "").trim() || null;
    payload.empresa_id = payload.empresa_id ? Number(payload.empresa_id) : null;
    payload.jefe_inmediato_id = payload.jefe_inmediato_id ? Number(payload.jefe_inmediato_id) : null;
    payload.estado_civil = payload.estado_civil || null;
    [
      "numero_cuenta", "eps", "afp", "arl", "caja_compensacion", "fondo_cesantias", "banco",
      "ciudad", "contacto_emergencia_nombre", "contacto_emergencia_telefono",
      "contacto_emergencia_parentesco", "area",
    ].forEach((campo) => {
      payload[campo] = (payload[campo] || "").trim() || null;
    });
    return payload;
  }

  function empleadoFormHtml(e = {}) {
    const gen = e.genero || "Femenino";
    const nivel = e.nivel_educativo || "Profesional";
    const tipo = e.tipo_cargo || "Profesional";
    const periodicidad = e.periodicidad_pago || "Mensual";
    const tipoDoc = e.tipo_documento || "CC";
    const estado = e.estado || "Activo";
    const empresaId = e.empresa_id ?? "";
    const tipoCuenta = e.tipo_cuenta || "Ahorros";
    const nivelRiesgo = e.nivel_riesgo_arl || "I";
    return `
      <div class="field">
        <label>Empresa</label>
        <select name="empresa_id" required>
          <option value="" disabled ${empresaId === "" ? "selected" : ""}>Selecciona una empresa</option>
          ${state.empresas
            .map((emp) => `<option value="${emp.id}" ${String(emp.id) === String(empresaId) ? "selected" : ""}>${escapeHtml(emp.nombre)}</option>`)
            .join("")}
        </select>
        <span class="text-faint" style="font-size:11px;">De qué empresa depende esta persona (Ecodes, Envsol, u otra registrada)</span>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Tipo de documento</label>
          <select name="tipo_documento">
            ${["CC", "CE", "PA", "PEP"].map((t) => `<option ${t === tipoDoc ? "selected" : ""}>${t}</option>`).join("")}
          </select>
        </div>
        <div class="field">
          <label>Número de documento</label>
          <input type="text" name="numero_documento" value="${escapeHtml(e.numero_documento) || ""}">
          <span class="text-faint" style="font-size:11px;">Necesario para emitir el certificado laboral</span>
        </div>
      </div>
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
      <div class="field-row">
        <div class="field">
          <label>Dirección</label>
          <input type="text" name="direccion" value="${escapeHtml(e.direccion) || ""}">
        </div>
        <div class="field">
          <label>Ciudad</label>
          <input type="text" name="ciudad" value="${escapeHtml(e.ciudad) || ""}">
        </div>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Estado civil</label>
          <select name="estado_civil">
            <option value="">Sin especificar</option>
            ${["Soltero(a)", "Casado(a)", "Unión libre", "Separado(a)", "Viudo(a)"]
              .map((c) => `<option ${c === e.estado_civil ? "selected" : ""}>${c}</option>`)
              .join("")}
          </select>
        </div>
        <div class="field">
          <label>Área</label>
          <input type="text" name="area" value="${escapeHtml(e.area) || ""}" placeholder="Ej. Operaciones - Restauración">
        </div>
      </div>
      <div class="field">
        <label>Jefe inmediato</label>
        <select name="jefe_inmediato_id">
          <option value="">Sin jefe asignado</option>
          ${state.empleadosTodos
            .filter((jefe) => jefe.id !== e.id)
            .map((jefe) => `<option value="${jefe.id}" ${String(jefe.id) === String(e.jefe_inmediato_id ?? "") ? "selected" : ""}>${escapeHtml(jefe.nombre_completo)}</option>`)
            .join("")}
        </select>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Contacto de emergencia</label>
          <input type="text" name="contacto_emergencia_nombre" value="${escapeHtml(e.contacto_emergencia_nombre) || ""}" placeholder="Nombre">
        </div>
        <div class="field">
          <label>Parentesco</label>
          <input type="text" name="contacto_emergencia_parentesco" value="${escapeHtml(e.contacto_emergencia_parentesco) || ""}" placeholder="Ej. Madre, Esposo(a)">
        </div>
      </div>
      <div class="field">
        <label>Teléfono de emergencia</label>
        <input type="text" name="contacto_emergencia_telefono" value="${escapeHtml(e.contacto_emergencia_telefono) || ""}">
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
      <div class="field-row">
        <div class="field">
          <label>EPS</label>
          <input type="text" name="eps" value="${escapeHtml(e.eps) || ""}" placeholder="Ej. EPS Sura">
        </div>
        <div class="field">
          <label>AFP</label>
          <input type="text" name="afp" value="${escapeHtml(e.afp) || ""}" placeholder="Ej. Porvenir">
        </div>
      </div>
      <div class="field-row">
        <div class="field">
          <label>ARL</label>
          <input type="text" name="arl" value="${escapeHtml(e.arl) || ""}" placeholder="Ej. ARL Sura">
        </div>
        <div class="field">
          <label>Nivel de riesgo ARL</label>
          <select name="nivel_riesgo_arl">
            ${["I", "II", "III", "IV", "V"].map((n) => `<option ${n === nivelRiesgo ? "selected" : ""}>${n}</option>`).join("")}
          </select>
          <span class="text-faint" style="font-size:11px;">De esto depende la tasa de ARL que paga la empresa en la nómina.</span>
        </div>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Caja de compensación</label>
          <input type="text" name="caja_compensacion" value="${escapeHtml(e.caja_compensacion) || ""}" placeholder="Ej. Compensar">
        </div>
        <div class="field">
          <label>Fondo de cesantías</label>
          <input type="text" name="fondo_cesantias" value="${escapeHtml(e.fondo_cesantias) || ""}" placeholder="Ej. Porvenir">
        </div>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Banco</label>
          <input type="text" name="banco" value="${escapeHtml(e.banco) || ""}" placeholder="Ej. Bancolombia">
        </div>
        <div class="field">
          <label>Tipo de cuenta</label>
          <select name="tipo_cuenta">
            ${["Ahorros", "Corriente"].map((t) => `<option ${t === tipoCuenta ? "selected" : ""}>${t}</option>`).join("")}
          </select>
        </div>
      </div>
      <div class="field">
        <label>Número de cuenta</label>
        <input type="text" name="numero_cuenta" value="${escapeHtml(e.numero_cuenta) || ""}">
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
        const payload = sanearPayloadEmpleado(Object.fromEntries(fd.entries()));
        if (!payload.vacaciones_ultima_toma) delete payload.vacaciones_ultima_toma;
        try {
          await api.post("/empleados", payload);
          showToast("Empleado creado correctamente");
          closeModal();
          loadEmpleados();
          state.empleadosTodos = await api.get("/empleados");
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
      const payload = sanearPayloadEmpleado(Object.fromEntries(fd.entries()));
      if (!payload.vacaciones_ultima_toma) payload.vacaciones_ultima_toma = null;
      try {
        await api.put(`/empleados/${e.id}`, payload);
        showToast("Empleado actualizado");
        closeModal();
        loadEmpleados();
        openEmpleadoPanel(e.id);
        state.empleadosTodos = await api.get("/empleados");
      } catch (err) {
        handleApiError(err);
      }
    });
  }

  /* ------------------------------------------------------------------
     Gestión de empresas (Ecodes, Envsol, o las que hagan falta)
     ------------------------------------------------------------------ */

  function empresaFormHtml(emp = {}) {
    return `
      <div class="field">
        <label>Nombre / razón social</label>
        <input type="text" name="nombre" value="${escapeHtml(emp.nombre) || ""}" required>
      </div>
      <div class="field-row">
        <div class="field">
          <label>NIT</label>
          <input type="text" name="nit" value="${escapeHtml(emp.nit) || ""}" required>
        </div>
        <div class="field">
          <label>Ciudad</label>
          <input type="text" name="ciudad" value="${escapeHtml(emp.ciudad) || "Bogotá D.C."}" required>
        </div>
      </div>
      <div class="field">
        <label>Dirección</label>
        <input type="text" name="direccion" value="${escapeHtml(emp.direccion) || ""}">
      </div>
      <div class="field-row">
        <div class="field">
          <label>Teléfono</label>
          <input type="text" name="telefono" value="${escapeHtml(emp.telefono) || ""}">
        </div>
        <div class="field">
          <label>Correo</label>
          <input type="email" name="correo" value="${escapeHtml(emp.correo) || ""}">
        </div>
      </div>
      <p class="text-faint" style="font-size:11.5px;margin:4px 0 8px;">
        Quien firma el certificado laboral de esta empresa:
      </p>
      <div class="field-row">
        <div class="field">
          <label>Nombre de quien firma</label>
          <input type="text" name="firmante_nombre" value="${escapeHtml(emp.firmante_nombre) || ""}" required>
        </div>
        <div class="field">
          <label>Cargo de quien firma</label>
          <input type="text" name="firmante_cargo" value="${escapeHtml(emp.firmante_cargo) || "Directora de Talento Humano"}" required>
        </div>
      </div>
      <label class="flex gap-8" style="align-items:center;font-size:13px;font-weight:500;">
        <input type="checkbox" name="activa" ${emp.activa === false ? "" : "checked"} style="width:auto;">
        Empresa activa (aparece para asignar a empleados y proyectos nuevos)
      </label>
    `;
  }

  function openEmpresaForm(emp) {
    const esEdicion = !!emp;
    const overlay = openModal(`
      <div class="modal-header">
        <h3>${esEdicion ? "Editar empresa" : "Nueva empresa"}</h3>
        <button class="icon-btn" data-close-modal>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <form id="form-empresa">
        <div class="modal-body">${empresaFormHtml(emp || {})}</div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
          <button type="submit" class="btn btn-primary">${esEdicion ? "Guardar cambios" : "Crear empresa"}</button>
        </div>
      </form>
    `);
    overlay.querySelector("#form-empresa").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const payload = Object.fromEntries(fd.entries());
      payload.activa = fd.has("activa");
      try {
        if (esEdicion) {
          await api.put(`/empresas/${emp.id}`, payload);
          showToast("Empresa actualizada");
        } else {
          await api.post("/empresas", payload);
          showToast("Empresa creada");
        }
        // Ojo: NO se llama closeModal() aquí. openGestionEmpresas() reutiliza el
        // mismo overlay (mismo id "generic-modal") para mostrar la lista
        // actualizada; si se cerrara primero, el remove() diferido de
        // closeModal() borraría también el modal recién abierto.
        state.empresas = await api.get("/empresas");
        document.getElementById("f-empresa").innerHTML = '<option value="">Todas las empresas</option>';
        fillEmpresaFilter();
        openGestionEmpresas();
        loadEmpleados();
      } catch (err) {
        handleApiError(err);
      }
    });
  }

  function renderListaEmpresas() {
    const host = document.getElementById("lista-empresas");
    if (!host) return;
    host.innerHTML = state.empresas.length
      ? state.empresas
          .map(
            (emp) => `
      <div class="list-item">
        <div>
          <div class="list-item-main">
            ${escapeHtml(emp.nombre)}
            ${emp.activa ? "" : '<span class="badge badge-neutral" style="margin-left:6px;">Inactiva</span>'}
          </div>
          <div class="list-item-sub">
            NIT ${escapeHtml(emp.nit)} · ${emp.total_empleados} empleado(s) · ${emp.total_proyectos} proyecto(s)
          </div>
        </div>
        <div class="flex gap-8">
          <button class="btn btn-secondary btn-sm write-only" data-editar-empresa="${emp.id}">Editar</button>
          <button class="list-item-remove write-only" data-eliminar-empresa="${emp.id}" title="Eliminar empresa">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
          </button>
        </div>
      </div>`
          )
          .join("")
      : '<p class="text-faint">No hay empresas registradas todavía.</p>';

    if (isReadOnly()) document.body.classList.add("read-only");

    host.querySelectorAll("[data-editar-empresa]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const emp = state.empresas.find((x) => x.id === Number(btn.dataset.editarEmpresa));
        openEmpresaForm(emp);
      });
    });
    host.querySelectorAll("[data-eliminar-empresa]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const emp = state.empresas.find((x) => x.id === Number(btn.dataset.eliminarEmpresa));
        if (!confirm(`¿Eliminar «${emp.nombre}»? Solo es posible si no tiene empleados ni proyectos asignados.`)) return;
        try {
          await api.del(`/empresas/${emp.id}`);
          showToast("Empresa eliminada");
          state.empresas = await api.get("/empresas");
          renderListaEmpresas();
        } catch (err) {
          handleApiError(err);
        }
      });
    });
  }

  function openGestionEmpresas() {
    const overlay = openModal(`
      <div class="modal-header">
        <h3>Empresas</h3>
        <button class="icon-btn" data-close-modal>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="modal-body">
        <p class="text-muted" style="font-size:13px;margin-bottom:14px;">
          El sistema atiende a más de una empresa a la vez. Estos son sus datos de
          identificación: los que salen impresos en el certificado laboral de cada empleado.
        </p>
        <button class="btn btn-primary btn-sm write-only" id="btn-nueva-empresa" style="margin-bottom:12px;">+ Agregar empresa</button>
        <div id="lista-empresas"></div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-close-modal>Cerrar</button>
      </div>
    `);
    renderListaEmpresas();
    overlay.querySelector("#btn-nueva-empresa")?.addEventListener("click", () => openEmpresaForm(null));
  }

  function bindGestionEmpresas() {
    document.getElementById("btn-empresas").addEventListener("click", openGestionEmpresas);
  }

  init();
})();
