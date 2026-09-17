(() => {
  const state = { empleados: [], periodo: null };

  function periodoActual() {
    const hoy = new Date();
    return `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, "0")}`;
  }

  async function init() {
    renderShell("nomina.html", "Nómina");
    try {
      state.empleados = await api.get("/empleados");
    } catch (err) {
      handleApiError(err);
    }
    fillPeriodos();
    loadResumen();
    loadNomina();
    bindFiltros();
    bindNuevaNomina();
  }

  function fillPeriodos() {
    const select = document.getElementById("f-periodo");
    const actual = periodoActual();
    const opciones = [];
    const [y, m] = actual.split("-").map(Number);
    for (let i = 0; i < 6; i++) {
      const date = new Date(y, m - 1 - i, 1);
      const val = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
      opciones.push(val);
    }
    select.innerHTML = opciones.map((p) => `<option value="${p}">${formatMonthPeriodo(p)}</option>`).join("");
    state.periodo = actual;
    select.value = actual;
  }

  function bindFiltros() {
    document.getElementById("f-periodo").addEventListener("change", (e) => {
      state.periodo = e.target.value;
      loadResumen();
      loadNomina();
    });
  }

  async function loadResumen() {
    const host = document.getElementById("nomina-kpis");
    try {
      const resumen = await api.get(`/nomina/resumen?periodo=${state.periodo}`);
      host.innerHTML = `
        <div class="kpi-card fade-up">
          <div class="kpi-label">Neto pagado a trabajadores</div>
          <div class="kpi-value" id="kpi-total">$0</div>
          <div class="kpi-sub">${formatMonthPeriodo(state.periodo)}</div>
        </div>
        <div class="kpi-card fade-up">
          <div class="kpi-label">Costo real para la empresa</div>
          <div class="kpi-value" id="kpi-costo">$0</div>
          <div class="kpi-sub">Carga prestacional: +${resumen.carga_prestacional}% sobre el neto</div>
        </div>
        <div class="kpi-card fade-up">
          <div class="kpi-label">Próximo pago</div>
          <div class="kpi-value" style="font-size:20px;">${resumen.proximo_pago ? formatDate(resumen.proximo_pago) : "—"}</div>
          <div class="kpi-sub">Fecha estimada de desembolso</div>
        </div>
        <div class="kpi-card fade-up">
          <div class="kpi-label">Novedades sin procesar</div>
          <div class="kpi-value" id="kpi-novedades">0</div>
          <div class="kpi-sub">Pueden afectar la nómina del período</div>
        </div>
      `;
      animateNumber(document.getElementById("kpi-total"), resumen.nomina_total_mes, { money: true });
      animateNumber(document.getElementById("kpi-costo"), resumen.costo_total_empleador, { money: true });
      animateNumber(document.getElementById("kpi-novedades"), resumen.novedades_sin_procesar);
    } catch (err) {
      handleApiError(err);
    }
  }

  async function loadNomina() {
    const tbody = document.getElementById("nomina-tbody");
    tbody.innerHTML = `<tr><td colspan="8" class="table-empty">Cargando nómina…</td></tr>`;
    try {
      const registros = await api.get(`/nomina?periodo=${state.periodo}`);
      renderTable(registros);
    } catch (err) {
      handleApiError(err);
      tbody.innerHTML = `<tr><td colspan="8" class="table-empty">No se pudo cargar la nómina.</td></tr>`;
    }
  }

  function renderTable(registros) {
    const tbody = document.getElementById("nomina-tbody");
    if (!registros.length) {
      tbody.innerHTML = `<tr><td colspan="8" class="table-empty">No hay registros de nómina para este período.</td></tr>`;
      return;
    }
    tbody.innerHTML = registros
      .map(
        (n) => `
      <tr>
        <td>
          <div class="person-name">${escapeHtml(n.empleado_nombre)}</div>
          ${n.novedades_mes > 0 ? `<span class="person-sub">${n.novedades_mes} novedad(es) este mes</span>` : ""}
        </td>
        <td>${formatMoney(n.salario_base)}</td>
        <td>
          ${formatMoney(n.auxilio_transporte + n.auxilio_movilidad)}
          <div class="person-sub">Transporte ${formatMoney(n.auxilio_transporte)} · Movilidad ${formatMoney(n.auxilio_movilidad)}</div>
        </td>
        <td>
          ${formatMoney(n.total_descuentos)}
          <div class="person-sub">Salud ${formatMoney(n.salud_empleado)} · Pensión ${formatMoney(n.pension_empleado)}</div>
        </td>
        <td><strong>${formatMoney(n.total)}</strong></td>
        <td>
          ${formatMoney(n.total_prestaciones)}
          <div class="person-sub">Prima ${formatMoney(n.prima)} · Cesantías ${formatMoney(n.cesantias)} · Vac. ${formatMoney(n.provision_vacaciones)} · Pensión ${formatMoney(n.pension_empleador)} · ARL ${formatMoney(n.arl)}</div>
        </td>
        <td><strong>${formatMoney(n.costo_empleador)}</strong></td>
        <td>
          <span class="badge ${n.pagada ? "badge-success" : "badge-neutral"}">${n.pagada ? "Pagada" : "Pendiente"}</span>
          <button class="list-item-remove write-only" data-eliminar="${n.id}" style="margin-left:6px;" title="Eliminar registro">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
          </button>
        </td>
      </tr>`
      )
      .join("");

    tbody.querySelectorAll("[data-eliminar]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (!confirm("¿Eliminar este registro de nómina?")) return;
        try {
          await api.del(`/nomina/${btn.dataset.eliminar}`);
          showToast("Registro eliminado");
          loadNomina();
          loadResumen();
        } catch (err) {
          handleApiError(err);
        }
      });
    });
  }

  function bindNuevaNomina() {
    document.getElementById("btn-nueva-nomina").addEventListener("click", () => {
      const overlay = openModal(`
        <div class="modal-header">
          <h3>Registrar nómina</h3>
          <button class="icon-btn" data-close-modal>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <form id="form-nomina">
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
                <label>Período (AAAA-MM)</label>
                <input type="month" name="periodo" value="${state.periodo}" required>
              </div>
              <div class="field">
                <label>Salario base</label>
                <input type="number" name="salario_base" min="0" required>
              </div>
            </div>
            <div class="field-row">
              <div class="field">
                <label>Auxilio de movilidad</label>
                <input type="number" name="auxilio_movilidad" min="0" value="0">
                <span class="text-faint" style="font-size:11px;">Lo define Ecodes para roles de campo</span>
              </div>
              <div class="field">
                <label>Otros descuentos</label>
                <input type="number" name="descuentos" min="0" value="0">
                <span class="text-faint" style="font-size:11px;">Préstamos, embargos, etc.</span>
              </div>
            </div>
            <div class="field">
              <label>Auxilio de transporte</label>
              <input type="number" name="auxilio_transporte" min="0" value="0">
              <span class="text-faint" style="font-size:11px;">Déjalo en 0 y el sistema aplica el valor de ley ($249.095) si el salario no supera 2 SMLMV ($3.501.810)</span>
            </div>
            <p class="text-faint" style="font-size:12px;">Las deducciones de salud y pensión (4% cada una) y las prestaciones que asume la empresa (prima, cesantías e intereses, vacaciones, pensión del empleador y ARL) se calculan automáticamente.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-close-modal>Cancelar</button>
            <button type="submit" class="btn btn-primary">Registrar nómina</button>
          </div>
        </form>
      `);
      overlay.querySelector("#form-nomina").addEventListener("submit", async (ev) => {
        ev.preventDefault();
        const fd = new FormData(ev.target);
        const payload = {
          empleado_id: Number(fd.get("empleado_id")),
          periodo: fd.get("periodo"),
          salario_base: Number(fd.get("salario_base")),
          auxilio_transporte: Number(fd.get("auxilio_transporte") || 0),
          auxilio_movilidad: Number(fd.get("auxilio_movilidad") || 0),
          descuentos: Number(fd.get("descuentos") || 0),
        };
        try {
          await api.post("/nomina", payload);
          showToast("Nómina registrada correctamente");
          closeModal();
          loadNomina();
          loadResumen();
        } catch (err) {
          handleApiError(err);
        }
      });
    });
  }

  init();
})();
