(() => {
  async function init() {
    renderShell("inicio.html", "Inicio");
    loadKpis();
    loadBirthdays();
    loadAlertasPreview();
  }

  async function loadKpis() {
    const host = document.getElementById("inicio-kpis");
    try {
      const [empleados, proyectos, vacantes, alertas] = await Promise.all([
        api.get("/empleados"),
        api.get("/proyectos"),
        api.get("/vacantes").catch(() => []),
        api.get("/alertas"),
      ]);
      const empleadosActivos = empleados.filter((e) => e.estado === "Activo").length;
      const proyectosActivos = proyectos.filter((p) => p.estado === "Activo" || p.estado === "Continuo").length;
      const vacantesAbiertas = vacantes.filter((v) => v.estado === "Abierta" || v.estado === "En proceso").length;
      const totalAlertas =
        alertas.vacaciones.length +
        alertas.sobreasignacion.length +
        alertas.nomina.length +
        alertas.novedades_sin_procesar.length +
        (alertas.expediente ? alertas.expediente.length : 0) +
        (alertas.aniversarios ? alertas.aniversarios.length : 0);

      host.innerHTML = `
        <div class="kpi-card fade-up">
          <div class="kpi-label">Empleados activos</div>
          <div class="kpi-value" id="kpi-empleados">0</div>
          <div class="kpi-sub">de ${empleados.length} en total</div>
        </div>
        <div class="kpi-card fade-up">
          <div class="kpi-label">Proyectos activos</div>
          <div class="kpi-value" id="kpi-proyectos">0</div>
          <div class="kpi-sub">de ${proyectos.length} en total</div>
        </div>
        <div class="kpi-card fade-up">
          <div class="kpi-label">Alertas pendientes</div>
          <div class="kpi-value" id="kpi-alertas">0</div>
          <div class="kpi-sub">vacaciones, nómina, expediente y más</div>
        </div>
        <div class="kpi-card fade-up">
          <div class="kpi-label">Vacantes abiertas</div>
          <div class="kpi-value" id="kpi-vacantes">0</div>
          <div class="kpi-sub">abiertas o en proceso</div>
        </div>
      `;
      animateNumber(document.getElementById("kpi-empleados"), empleadosActivos);
      animateNumber(document.getElementById("kpi-proyectos"), proyectosActivos);
      animateNumber(document.getElementById("kpi-alertas"), totalAlertas);
      animateNumber(document.getElementById("kpi-vacantes"), vacantesAbiertas);
    } catch (err) {
      handleApiError(err);
      host.innerHTML = `<p class="table-empty">No se pudieron cargar los indicadores.</p>`;
    }
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

  const NIVEL_PESO = { critico: 0, alerta: 1, info: 2 };
  const NIVEL_ICON = {
    critico: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
    alerta: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
    info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
  };

  function normalizarAlertas(data) {
    const items = [];
    data.vacaciones.forEach((a) =>
      items.push({
        titulo: a.empleado_nombre,
        descripcion: `${a.dias_pendientes} días de vacaciones pendientes`,
        nivel: a.nivel,
      })
    );
    data.sobreasignacion.forEach((a) =>
      items.push({
        titulo: a.empleado_nombre,
        descripcion: `${a.porcentaje_total}% de participación total entre proyectos`,
        nivel: a.nivel,
      })
    );
    data.nomina.forEach((a) =>
      items.push({ titulo: a.tipo, descripcion: a.descripcion, nivel: a.nivel })
    );
    data.novedades_sin_procesar.forEach((n) =>
      items.push({
        titulo: `${n.empleado_nombre} · ${n.tipo}`,
        descripcion: formatDate(n.fecha) + (n.detalle ? ` — ${n.detalle}` : ""),
        nivel: "alerta",
      })
    );
    (data.expediente || []).forEach((a) =>
      items.push({ titulo: `${a.empleado_nombre} · ${a.tipo}`, descripcion: a.descripcion, nivel: a.nivel })
    );
    (data.aniversarios || []).forEach((a) =>
      items.push({ titulo: a.empleado_nombre, descripcion: a.descripcion, nivel: a.nivel })
    );
    items.sort((a, b) => (NIVEL_PESO[a.nivel] ?? 1) - (NIVEL_PESO[b.nivel] ?? 1));
    return items;
  }

  async function loadAlertasPreview() {
    const host = document.getElementById("inicio-alertas");
    try {
      const data = await api.get("/alertas");
      const items = normalizarAlertas(data).slice(0, 6);
      if (!items.length) {
        host.innerHTML = `<p class="table-empty">No hay alertas activas por el momento.</p>`;
        return;
      }
      host.innerHTML = items
        .map(
          (a) => `
        <div class="alert-item fade-up">
          <div class="alert-item-icon icon-${a.nivel}">${NIVEL_ICON[a.nivel] || NIVEL_ICON.info}</div>
          <div class="alert-item-body">
            <div class="alert-item-title">${escapeHtml(a.titulo)}</div>
            <div class="alert-item-desc">${escapeHtml(a.descripcion)}</div>
          </div>
        </div>`
        )
        .join("");
    } catch (err) {
      handleApiError(err);
      host.innerHTML = `<p class="table-empty">No se pudieron cargar las alertas.</p>`;
    }
  }

  init();
})();
