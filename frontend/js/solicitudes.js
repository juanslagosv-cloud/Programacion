(() => {
  const state = { solicitudes: [], empleados: [], proyectos: [], filtros: {} };

  const TIPOS_CON_RANGO = [
    "Vacaciones", "Incapacidad", "Permiso", "Licencia remunerada", "Licencia no remunerada",
    "Calamidad doméstica", "Trabajo remoto", "Ausencia", "Suspensión",
  ];
  const TIPOS_CAMBIO_VALOR = ["Cambio salarial", "Cambio de cargo"];

  async function init() {
    renderShell("solicitudes.html", "Solicitudes");
    try {
      [state.empleados, state.proyectos] = await Promise.all([
        api.get("/empleados"),
        api.get("/proyectos"),
      ]);
    } catch (err) {
      handleApiError(err);
    }
    loadSolicitudes();
    bindFilters();
    bindNuevaSolicitud();
  }

  function bindFilters() {
    document.getElementById("f-tipo").addEventListener("change", (e) => {
      state.filtros.tipo = e.target.value;
      loadSolicitudes();
    });
    document.getElementById("f-estado").addEventListener("change", (e) => {
      state.filtros.estado = e.target.value;
      loadSolicitudes();
    });
  }

  // El backend filtra por estado_jefe/estado_th por separado; aquí se traduce
  // la etiqueta compuesta que ve el usuario a esos dos parámetros.
  function paramsDeFiltroEstado(estado) {
    switch (estado) {
      case "pendiente_jefe": return { estado_jefe: "Pendiente" };
      case "rechazada_jefe": return { estado_jefe: "Rechazado" };
      case "pendiente_th": return { estado_jefe: "Aprobado", estado_th: "Pendiente" };
      case "rechazada_th": return { estado_th: "Rechazado" };
      case "aprobada": return { estado_th: "Aprobado" };
      default: return {};
    }
  }

  async function loadSolicitudes() {
    const tbody = document.getElementById("solicitudes-tbody");
    tbody.innerHTML = `<tr><td colspan="7" class="table-empty">Cargando solicitudes…</td></tr>`;
    const params = new URLSearchParams();
    if (state.filtros.tipo) params.set("tipo", state.filtros.tipo);
    Object.entries(paramsDeFiltroEstado(state.filtros.estado)).forEach(([k, v]) => params.set(k, v));
    try {
      const solicitudes = await api.get(`/solicitudes?${params.toString()}`);
      state.solicitudes = solicitudes;
      renderTable(solicitudes);
    } catch (err) {
      handleApiError(err);
      tbody.innerHTML = `<tr><td colspan="7" class="table-empty">No se pudieron cargar las solicitudes.</td></tr>`;
    }
  }

  function estadoBadgeClass(estado) {
    if (estado === "Aprobado") return "badge-success";
    if (estado === "Rechazado") return "badge-danger";
    return "badge-warning";
  }

  function estadoGeneralBadgeClass(estadoGeneral) {
    if (estadoGeneral === "Aprobada") return "badge-success";
    if (estadoGeneral.startsWith("Rechazada")) return "badge-danger";
    return "badge-warning";
  }

  function rangoFechasTexto(s) {
    if (!s.fecha_fin) {
      return formatDate(s.fecha_inicio) + (s.horas ? ` · ${s.horas} h` : "");
    }
    return `${formatDate(s.fecha_inicio)} → ${formatDate(s.fecha_fin)}` + (s.dias_solicitados ? ` · ${s.dias_solicitados} día(s)` : "");
  }

  function renderTable(solicitudes) {
    const tbody = document.getElementById("solicitudes-tbody");
    if (!solicitudes.length) {
      tbody.innerHTML = `<tr><td colspan="7" class="table-empty">No hay solicitudes con estos filtros.</td></tr>`;
      return;
    }
    tbody.innerHTML = solicitudes
      .map(
        (s) => `
      <tr data-id="${s.id}">
        <td><div class="person-name">${escapeHtml(s.empleado_nombre)}</div></td>
        <td><span class="badge badge-info">${s.tipo}</span></td>
        <td class="text-muted">${rangoFechasTexto(s)}</td>
        <td>
          <span class="badge ${estadoBadgeClass(s.estado_jefe)}"><span class="badge-dot"></span>${s.estado_jefe}</span>
          <div class="person-sub">${s.jefe_inmediato_nombre ? escapeHtml(s.jefe_inmediato_nombre) : "Sin jefe asignado"}</div>
        </td>
        <td><span class="badge ${estadoBadgeClass(s.estado_th)}"><span class="badge-dot"></span>${s.estado_th}</span></td>
        <td><span class="badge ${estadoGeneralBadgeClass(s.estado_general)}">${s.estado_general}</span></td>
        <td><button class="btn btn-secondary btn-sm" data-ver="${s.id}">Ver</button></td>
      </tr>`
      )
      .join("");

    tbody.querySelectorAll("[data-ver]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const s = state.solicitudes.find((x) => x.id === Number(btn.dataset.ver));
        openDetalleSolicitud(s);
      });
    });
  }

  function tipoRequiereCampo(tipo, lista) {
    return lista.includes(tipo);
  }

  function actualizarCamposCondicionales(form) {
    const tipo = form.querySelector('[name="tipo"]').value;
    form.querySelector("#campo-fecha-fin").classList.toggle("hidden", !tipoRequiereCampo(tipo, TIPOS_CON_RANGO));
    form.querySelector("#campo-horas").classList.toggle("hidden", tipo !== "Horas extras");
    form.querySelector("#campo-valor-propuesto").classList.toggle("hidden", !tipoRequiereCampo(tipo, TIPOS_CAMBIO_VALOR));
    form.querySelector("#campo-proyecto-propuesto").classList.toggle("hidden", tipo !== "Cambio de proyecto");
  }

  function bindNuevaSolicitud() {
    document.getElementById("btn-nueva-solicitud").addEventListener("click", () => {
      const overlay = openModal(`
        <div class="modal-header">
          <h3>Registrar solicitud</h3>
          <button class="icon-btn" data-close-modal>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <form id="form-solicitud">
          <div class="modal-body">
            <div class="field">
              <label>Empleado</label>
              <select name="empleado_id" required>
                <option value="">Selecciona un empleado</option>
                ${state.empleados.map((e) => `<option value="${e.id}">${escapeHtml(e.nombre_completo)}</option>`).join("")}
              </select>
            </div>
            <div class="field">
              <label>Tipo de solicitud</label>
              <select name="tipo" required>
                <option>Vacaciones</option>
                <option>Incapacidad</option>
                <option>Permiso</option>
                <option>Licencia remunerada</option>
                <option>Licencia no remunerada</option>
                <option>Calamidad doméstica</option>
                <option>Trabajo remoto</option>
                <option>Horas extras</option>
                <option>Ausencia</option>
                <option>Suspensión</option>
                <option>Cambio salarial</option>
                <option>Cambio de cargo</option>
                <option>Cambio de proyecto</option>
              </select>
            </div>
            <div class="field-row">
              <div class="field">
                <label>Fecha inicial</label>
                <input type="date" name="fecha_inicio" required>
              </div>
              <div class="field" id="campo-fecha-fin">
                <label>Fecha final</label>
                <input type="date" name="fecha_fin">
              </div>
            </div>
            <div class="field hidden" id="campo-horas">
              <label>Horas</label>
              <input type="number" name="horas" min="0" step="0.5">
            </div>
            <div class="field hidden" id="campo-valor-propuesto">
              <label>Valor propuesto</label>
              <input type="text" name="valor_propuesto" placeholder="Ej. De $4.200.000 a $4.800.000, o el nuevo cargo">
            </div>
            <div class="field hidden" id="campo-proyecto-propuesto">
              <label>Proyecto propuesto</label>
              <select name="proyecto_propuesto_id">
                <option value="">Selecciona un proyecto</option>
                ${state.proyectos.map((p) => `<option value="${p.id}">${escapeHtml(p.nombre)}</option>`).join("")}
              </select>
            </div>
            <div class="field">
              <label>Motivo</label>
              <textarea name="motivo" required placeholder="Justificación de la solicitud..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
            <button type="submit" class="btn btn-primary">Registrar</button>
          </div>
        </form>
      `);
      const form = overlay.querySelector("#form-solicitud");
      form.querySelector('[name="tipo"]').addEventListener("change", () => actualizarCamposCondicionales(form));
      actualizarCamposCondicionales(form);

      form.addEventListener("submit", async (ev) => {
        ev.preventDefault();
        const fd = new FormData(ev.target);
        const payload = {
          empleado_id: Number(fd.get("empleado_id")),
          tipo: fd.get("tipo"),
          fecha_inicio: fd.get("fecha_inicio"),
          fecha_fin: fd.get("fecha_fin") || null,
          horas: fd.get("horas") ? Number(fd.get("horas")) : null,
          valor_propuesto: (fd.get("valor_propuesto") || "").trim() || null,
          proyecto_propuesto_id: fd.get("proyecto_propuesto_id") ? Number(fd.get("proyecto_propuesto_id")) : null,
          motivo: fd.get("motivo"),
        };
        try {
          await api.post("/solicitudes", payload);
          showToast("Solicitud registrada correctamente");
          closeModal();
          loadSolicitudes();
        } catch (err) {
          handleApiError(err);
        }
      });
    });
  }

  function seccionDecision(titulo, estado, comentario, fechaRespuesta, puedeDecidir, onDecidir) {
    let cuerpo;
    if (estado === "Pendiente" && puedeDecidir) {
      cuerpo = `
        <div class="field">
          <label>Comentario (opcional)</label>
          <textarea id="comentario-${onDecidir}" placeholder="Observaciones..."></textarea>
        </div>
        <div class="flex gap-8 write-only">
          <button class="btn btn-primary btn-sm" data-decidir="${onDecidir}" data-aprobar="true">Aprobar</button>
          <button class="btn btn-danger btn-sm" data-decidir="${onDecidir}" data-aprobar="false">Rechazar</button>
        </div>`;
    } else if (estado === "Pendiente") {
      cuerpo = `<p class="text-faint">Esperando la decisión del jefe inmediato.</p>`;
    } else {
      cuerpo = `
        <div class="info-grid">
          <div class="info-item"><div class="label">Fecha de respuesta</div><div class="value">${formatDate(fechaRespuesta)}</div></div>
          <div class="info-item" style="grid-column:1/-1;"><div class="label">Comentario</div><div class="value">${comentario ? escapeHtml(comentario) : "—"}</div></div>
        </div>`;
    }
    return `
      <div class="panel-section">
        <div class="panel-section-title">${titulo} <span class="badge ${estadoBadgeClass(estado)}"><span class="badge-dot"></span>${estado}</span></div>
        ${cuerpo}
      </div>`;
  }

  function openDetalleSolicitud(s) {
    const puedeDecidirJefe = s.estado_jefe === "Pendiente";
    const puedeDecidirTh = s.estado_jefe === "Aprobado" && s.estado_th === "Pendiente";
    const overlay = openModal(`
      <div class="modal-header">
        <h3>${s.tipo} · ${escapeHtml(s.empleado_nombre)}</h3>
        <button class="icon-btn" data-close-modal>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="modal-body">
        <div class="info-grid">
          <div class="info-item"><div class="label">Fecha de la solicitud</div><div class="value">${formatDate(s.fecha_solicitud)}</div></div>
          <div class="info-item"><div class="label">Fechas</div><div class="value">${rangoFechasTexto(s)}</div></div>
          ${s.valor_propuesto ? `<div class="info-item" style="grid-column:1/-1;"><div class="label">Valor propuesto</div><div class="value">${escapeHtml(s.valor_propuesto)}</div></div>` : ""}
          ${s.proyecto_propuesto_nombre ? `<div class="info-item" style="grid-column:1/-1;"><div class="label">Proyecto propuesto</div><div class="value">${escapeHtml(s.proyecto_propuesto_nombre)}</div></div>` : ""}
          <div class="info-item" style="grid-column:1/-1;"><div class="label">Motivo</div><div class="value">${escapeHtml(s.motivo)}</div></div>
        </div>
        ${seccionDecision("Decisión del jefe inmediato" + (s.jefe_inmediato_nombre ? ` (${escapeHtml(s.jefe_inmediato_nombre)})` : " (sin jefe asignado)"), s.estado_jefe, s.jefe_comentario, s.jefe_fecha_respuesta, puedeDecidirJefe, "jefe")}
        ${seccionDecision("Decisión de Talento Humano", s.estado_th, s.th_comentario, s.th_fecha_respuesta, puedeDecidirTh, "th")}
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-danger btn-sm write-only" id="btn-eliminar-solicitud">Eliminar</button>
        <button type="button" class="btn btn-secondary" data-close-modal>Cerrar</button>
      </div>
    `);

    overlay.querySelectorAll("[data-decidir]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const etapa = btn.dataset.decidir;
        const aprobar = btn.dataset.aprobar === "true";
        const comentario = overlay.querySelector(`#comentario-${etapa}`).value.trim() || null;
        try {
          await api.post(`/solicitudes/${s.id}/decision-${etapa}`, { aprobar, comentario });
          showToast(aprobar ? "Solicitud aprobada" : "Solicitud rechazada");
          closeModal();
          loadSolicitudes();
        } catch (err) {
          handleApiError(err);
        }
      });
    });

    document.getElementById("btn-eliminar-solicitud").addEventListener("click", async () => {
      if (!confirm("¿Eliminar esta solicitud? Esta acción no se puede deshacer.")) return;
      try {
        await api.del(`/solicitudes/${s.id}`);
        showToast("Solicitud eliminada");
        closeModal();
        loadSolicitudes();
      } catch (err) {
        handleApiError(err);
      }
    });
  }

  init();
})();
