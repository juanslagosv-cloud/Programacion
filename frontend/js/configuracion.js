(() => {
  const state = { parametros: [], codigos: [], filtros: {} };

  const UNIDADES = ["Porcentaje", "Pesos", "Días", "Horas", "Semanas", "Meses", "Número", "Hora del día"];

  async function init() {
    renderShell("configuracion.html", "Configuración");
    try {
      state.codigos = await api.get("/parametros-legales/codigos");
    } catch (err) {
      handleApiError(err);
    }
    fillCodigosDatalist();
    bindFiltros();
    bindNuevaVigencia();
    loadParametros();
  }

  function fillCodigosDatalist() {
    document.getElementById("lista-codigos").innerHTML = state.codigos
      .map((c) => `<option value="${escapeHtml(c.codigo)}">${escapeHtml(c.nombre)}</option>`)
      .join("");
  }

  function bindFiltros() {
    document.getElementById("f-codigo").addEventListener(
      "input",
      debounce((e) => {
        state.filtros.codigo = e.target.value.trim();
        loadParametros();
      }, 350)
    );
    document.getElementById("f-anio").addEventListener("change", (e) => {
      state.filtros.anio = e.target.value;
      loadParametros();
    });
    document.getElementById("f-pendiente").addEventListener("change", (e) => {
      state.filtros.pendiente_verificacion = e.target.value;
      loadParametros();
    });
  }

  function bindNuevaVigencia() {
    document.getElementById("btn-nueva-vigencia").addEventListener("click", () => openVigenciaForm(null));
  }

  function fillAnioFilter() {
    const select = document.getElementById("f-anio");
    const actual = select.value;
    const anios = [...new Set(state.parametros.map((p) => p.anio))].sort((a, b) => b - a);
    select.innerHTML =
      '<option value="">Todos los años</option>' +
      anios.map((a) => `<option value="${a}">${a}</option>`).join("");
    select.value = actual;
  }

  async function loadParametros() {
    const tbody = document.getElementById("parametros-tbody");
    tbody.innerHTML = `<tr><td colspan="6" class="table-empty">Cargando parámetros…</td></tr>`;
    const params = new URLSearchParams();
    Object.entries(state.filtros).forEach(([k, v]) => v !== undefined && v !== "" && params.set(k, v));
    try {
      state.parametros = await api.get(`/parametros-legales?${params.toString()}`);
      fillAnioFilter();
      renderBanner();
      renderTable();
    } catch (err) {
      handleApiError(err);
      tbody.innerHTML = `<tr><td colspan="6" class="table-empty">No se pudieron cargar los parámetros.</td></tr>`;
    }
  }

  function renderBanner() {
    const banner = document.getElementById("banner-pendientes");
    const pendientes = state.parametros.filter((p) => p.pendiente_verificacion && p.activo);
    if (!pendientes.length) {
      banner.classList.add("hidden");
      return;
    }
    document.getElementById("texto-pendientes").textContent =
      `${pendientes.length} parámetro(s) pendiente(s) de verificación legal — confírmalos o corrígelos antes de usarlos para una nómina real.`;
    banner.classList.remove("hidden");
  }

  function fmtValor(p) {
    if (p.unidad === "Porcentaje") return (p.valor * 100).toLocaleString("es-CO", { maximumFractionDigits: 4 }) + "%";
    if (p.unidad === "Pesos") return money(p.valor);
    if (p.unidad === "Hora del día") {
      const h = Math.floor(p.valor);
      const esPm = h >= 12;
      const h12 = h % 12 === 0 ? 12 : h % 12;
      return `${h12}:00 ${esPm ? "p.m." : "a.m."}`;
    }
    return `${p.valor} ${p.unidad.toLowerCase()}`;
  }

  function money(n) {
    return "$ " + Math.round(n || 0).toLocaleString("es-CO");
  }

  function renderTable() {
    const tbody = document.getElementById("parametros-tbody");
    if (!state.parametros.length) {
      tbody.innerHTML = `<tr><td colspan="6" class="table-empty">No hay parámetros con estos filtros.</td></tr>`;
      return;
    }
    tbody.innerHTML = state.parametros
      .map((p) => {
        const hoy = todayIso();
        const esHistorica = p.fecha_fin_vigencia && p.fecha_fin_vigencia < hoy;
        let estadoBadge;
        if (!p.activo) {
          estadoBadge = '<span class="badge badge-neutral"><span class="badge-dot"></span>Inactivo</span>';
        } else if (esHistorica) {
          estadoBadge = '<span class="badge badge-neutral"><span class="badge-dot"></span>Histórica</span>';
        } else if (p.vigente_actualmente) {
          estadoBadge = '<span class="badge badge-success"><span class="badge-dot"></span>Vigente</span>';
        } else {
          estadoBadge = '<span class="badge badge-info"><span class="badge-dot"></span>Futura</span>';
        }
        const badgePendiente = p.pendiente_verificacion
          ? '<span class="badge badge-warning" style="margin-left:6px;" title="Pendiente de verificación legal">⚠ Por verificar</span>'
          : "";
        return `
      <tr data-id="${p.id}">
        <td>
          <div class="person-name">${escapeHtml(p.nombre)}</div>
          <div class="text-faint" style="font-size:11.5px;">${escapeHtml(p.codigo)}</div>
        </td>
        <td><b>${fmtValor(p)}</b></td>
        <td>${formatDate(p.fecha_inicio_vigencia)} – ${p.fecha_fin_vigencia ? formatDate(p.fecha_fin_vigencia) : "indefinido"}</td>
        <td style="max-width:220px;">${p.norma ? escapeHtml(p.norma) : '<span class="text-faint">—</span>'}</td>
        <td>${estadoBadge}${badgePendiente}</td>
        <td class="flex gap-8 write-only">
          <button class="btn btn-secondary btn-sm" data-editar="${p.id}">Editar</button>
          <button class="list-item-remove" data-eliminar="${p.id}" title="Eliminar esta vigencia">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
          </button>
        </td>
      </tr>`;
      })
      .join("");

    if (isReadOnly()) document.body.classList.add("read-only");

    tbody.querySelectorAll("[data-editar]").forEach((btn) => {
      btn.addEventListener("click", () => {
        openEditarForm(state.parametros.find((p) => p.id === Number(btn.dataset.editar)));
      });
    });
    tbody.querySelectorAll("[data-eliminar]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const p = state.parametros.find((x) => x.id === Number(btn.dataset.eliminar));
        if (!confirm(`¿Eliminar esta vigencia de «${p.nombre}» (${formatDate(p.fecha_inicio_vigencia)})? Solo se puede eliminar la más reciente de su código.`)) return;
        try {
          await api.del(`/parametros-legales/${p.id}`);
          showToast("Vigencia eliminada");
          loadParametros();
        } catch (err) {
          handleApiError(err);
        }
      });
    });
  }

  function vigenciaFormHtml(p = {}) {
    return `
      <div class="field">
        <label>Código (identificador único, en snake_case)</label>
        <input type="text" name="codigo" list="lista-codigos" value="${escapeHtml(p.codigo) || ""}" required ${p.id ? "readonly" : ""}>
      </div>
      <div class="field">
        <label>Nombre</label>
        <input type="text" name="nombre" value="${escapeHtml(p.nombre) || ""}" required>
      </div>
      <div class="field">
        <label>Descripción (opcional)</label>
        <textarea name="descripcion" rows="2">${escapeHtml(p.descripcion) || ""}</textarea>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Valor</label>
          <input type="number" step="any" name="valor" value="${p.valor ?? ""}" required>
        </div>
        <div class="field">
          <label>Unidad</label>
          <select name="unidad" required>
            ${UNIDADES.map((u) => `<option ${p.unidad === u ? "selected" : ""}>${u}</option>`).join("")}
          </select>
        </div>
      </div>
      <p class="text-faint" style="font-size:11.5px;margin:-4px 0 4px;">
        Si la unidad es "Porcentaje", el valor se guarda como fracción (0.04 = 4%). Si es "Hora del día",
        en formato 24 horas (19 = 7:00 p.m.).
      </p>
      <div class="field-row">
        <div class="field">
          <label>Inicio de vigencia</label>
          <input type="date" name="fecha_inicio_vigencia" value="${p.fecha_inicio_vigencia || ""}" required>
        </div>
        <div class="field">
          <label>Fin de vigencia (vacío = indefinida)</label>
          <input type="date" name="fecha_fin_vigencia" value="${p.fecha_fin_vigencia || ""}">
        </div>
      </div>
      <div class="field">
        <label>Año</label>
        <input type="number" name="anio" value="${p.anio || new Date().getFullYear()}" required>
      </div>
      <div class="field">
        <label>Norma relacionada (opcional)</label>
        <input type="text" name="norma" value="${escapeHtml(p.norma) || ""}">
      </div>
      <div class="field">
        <label>Observaciones (opcional)</label>
        <textarea name="observaciones" rows="2">${escapeHtml(p.observaciones) || ""}</textarea>
      </div>
      <label class="flex gap-8" style="align-items:center;font-size:13px;font-weight:500;margin-top:4px;">
        <input type="checkbox" name="pendiente_verificacion" ${p.pendiente_verificacion !== false ? "checked" : ""} style="width:auto;">
        Pendiente de verificación legal
      </label>
    `;
  }

  function openVigenciaForm(p) {
    const overlay = openModal(`
      <div class="modal-header">
        <h3>Nueva vigencia</h3>
        <button class="icon-btn" data-close-modal>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <form id="form-vigencia">
        <div class="modal-body">${vigenciaFormHtml(p || {})}</div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
          <button type="submit" class="btn btn-primary">Crear vigencia</button>
        </div>
      </form>
    `);
    overlay.querySelector("#form-vigencia").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const payload = {
        codigo: fd.get("codigo").trim(),
        nombre: fd.get("nombre"),
        descripcion: fd.get("descripcion") || null,
        valor: Number(fd.get("valor")),
        unidad: fd.get("unidad"),
        fecha_inicio_vigencia: fd.get("fecha_inicio_vigencia"),
        fecha_fin_vigencia: fd.get("fecha_fin_vigencia") || null,
        anio: Number(fd.get("anio")),
        norma: fd.get("norma") || null,
        observaciones: fd.get("observaciones") || null,
        pendiente_verificacion: fd.has("pendiente_verificacion"),
      };
      try {
        await api.post("/parametros-legales", payload);
        showToast("Vigencia creada");
        closeModal();
        state.codigos = await api.get("/parametros-legales/codigos");
        fillCodigosDatalist();
        loadParametros();
      } catch (err) {
        handleApiError(err);
      }
    });
  }

  function openEditarForm(p) {
    const overlay = openModal(`
      <div class="modal-header">
        <h3>Editar metadatos — ${escapeHtml(p.nombre)}</h3>
        <button class="icon-btn" data-close-modal>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <form id="form-editar">
        <div class="modal-body">
          <p class="text-faint" style="font-size:12px;margin-bottom:12px;">
            Solo se pueden editar el nombre, la descripción, la norma, las observaciones y el estado.
            El valor y las fechas de vigencia no se editan: si cambiaron, crea una nueva vigencia en vez
            de modificar esta, para no alterar cómo se calculó una nómina que ya la haya usado.
          </p>
          <div class="field">
            <label>Nombre</label>
            <input type="text" name="nombre" value="${escapeHtml(p.nombre)}" required>
          </div>
          <div class="field">
            <label>Descripción</label>
            <textarea name="descripcion" rows="2">${escapeHtml(p.descripcion) || ""}</textarea>
          </div>
          <div class="field">
            <label>Norma relacionada</label>
            <input type="text" name="norma" value="${escapeHtml(p.norma) || ""}">
          </div>
          <div class="field">
            <label>Observaciones</label>
            <textarea name="observaciones" rows="3">${escapeHtml(p.observaciones) || ""}</textarea>
          </div>
          <label class="flex gap-8" style="align-items:center;font-size:13px;font-weight:500;margin-top:6px;">
            <input type="checkbox" name="pendiente_verificacion" ${p.pendiente_verificacion ? "checked" : ""} style="width:auto;">
            Pendiente de verificación legal
          </label>
          <label class="flex gap-8" style="align-items:center;font-size:13px;font-weight:500;margin-top:6px;">
            <input type="checkbox" name="activo" ${p.activo ? "checked" : ""} style="width:auto;">
            Activo (si se desmarca, el motor de cálculo deja de usar esta vigencia)
          </label>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
          <button type="submit" class="btn btn-primary">Guardar cambios</button>
        </div>
      </form>
    `);
    overlay.querySelector("#form-editar").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const payload = {
        nombre: fd.get("nombre"),
        descripcion: fd.get("descripcion") || null,
        norma: fd.get("norma") || null,
        observaciones: fd.get("observaciones") || null,
        pendiente_verificacion: fd.has("pendiente_verificacion"),
        activo: fd.has("activo"),
      };
      try {
        await api.put(`/parametros-legales/${p.id}`, payload);
        showToast("Parámetro actualizado");
        closeModal();
        loadParametros();
      } catch (err) {
        handleApiError(err);
      }
    });
  }

  init();
})();
