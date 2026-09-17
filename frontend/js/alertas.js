(() => {
  async function init() {
    renderShell("alertas.html", "Alertas");
    const main = document.getElementById("alertas-main");
    try {
      const data = await api.get("/alertas");
      render(main, data);
    } catch (err) {
      handleApiError(err);
      main.innerHTML = '<p class="text-faint">No se pudieron cargar las alertas.</p>';
    }
  }

  function iconVacaciones() {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>';
  }
  function iconAsignacion() {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>';
  }
  function iconNomina() {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/></svg>';
  }
  function iconNovedad() {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>';
  }

  function render(main, data) {
    const totalAlertas =
      data.vacaciones.length + data.sobreasignacion.length + data.nomina.length + data.novedades_sin_procesar.length;

    if (totalAlertas === 0) {
      main.innerHTML = `
        <div class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          <p>No hay alertas activas por el momento.</p>
        </div>
      `;
      return;
    }

    main.innerHTML = `
      ${section(
        "Vacaciones por vencer",
        iconVacaciones(),
        data.vacaciones.length,
        data.vacaciones
          .map(
            (a) => `
        <div class="alert-item fade-up">
          <div class="alert-item-icon icon-${a.nivel}">${iconVacaciones()}</div>
          <div class="alert-item-body">
            <div class="alert-item-title">${escapeHtml(a.empleado_nombre)}</div>
            <div class="alert-item-desc">${a.dias_pendientes} días pendientes${
              a.meses_sin_tomar !== null ? ` · ${a.meses_sin_tomar} meses sin tomar vacaciones` : ""
            }</div>
          </div>
          <span class="badge ${a.nivel === "critico" ? "badge-danger" : "badge-warning"}">${a.nivel === "critico" ? "Crítico" : "Alerta"}</span>
        </div>`
          )
          .join("")
      )}

      ${section(
        "Sobre-asignación de personal",
        iconAsignacion(),
        data.sobreasignacion.length,
        data.sobreasignacion
          .map(
            (a) => `
        <div class="alert-item fade-up">
          <div class="alert-item-icon icon-${a.nivel}">${iconAsignacion()}</div>
          <div class="alert-item-body">
            <div class="alert-item-title">${escapeHtml(a.empleado_nombre)}</div>
            <div class="alert-item-desc">${a.porcentaje_total}% de participación total entre proyectos</div>
          </div>
          <span class="badge ${a.nivel === "critico" ? "badge-danger" : "badge-warning"}">${a.nivel === "critico" ? "Crítico" : "Alerta"}</span>
        </div>`
          )
          .join("")
      )}

      ${section(
        "Nómina y pagos",
        iconNomina(),
        data.nomina.length,
        data.nomina
          .map(
            (a) => `
        <div class="alert-item fade-up">
          <div class="alert-item-icon icon-${a.nivel}">${iconNomina()}</div>
          <div class="alert-item-body">
            <div class="alert-item-title">${escapeHtml(a.tipo)}</div>
            <div class="alert-item-desc">${escapeHtml(a.descripcion)}</div>
          </div>
        </div>`
          )
          .join("")
      )}

      ${section(
        "Novedades sin procesar",
        iconNovedad(),
        data.novedades_sin_procesar.length,
        data.novedades_sin_procesar
          .map(
            (n) => `
        <div class="alert-item fade-up">
          <div class="alert-item-icon icon-alerta">${iconNovedad()}</div>
          <div class="alert-item-body">
            <div class="alert-item-title">${escapeHtml(n.empleado_nombre)} · ${n.tipo}</div>
            <div class="alert-item-desc">${formatDate(n.fecha)}${n.detalle ? ` — ${escapeHtml(n.detalle)}` : ""}</div>
          </div>
        </div>`
          )
          .join("")
      )}
    `;
  }

  function section(title, icon, count, itemsHtml) {
    if (count === 0) return "";
    return `
      <div class="alert-group">
        <div class="alert-group-header">
          <div class="alert-item-icon icon-info" style="width:32px;height:32px;">${icon}</div>
          <div class="alert-group-title">${title}</div>
          <span class="alert-count">${count} elemento${count === 1 ? "" : "s"}</span>
        </div>
        ${itemsHtml}
      </div>
    `;
  }

  init();
})();
