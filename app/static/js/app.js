const API_BASE = '/';

const state = {
  token: localStorage.getItem('ecodes_token') || '',
  role: localStorage.getItem('ecodes_role') || '',
  currentView: 'empleados',
  employees: [],
  projects: [],
  events: [],
  payroll: [],
  alerts: { vacaciones: [], sobreasignacion: [] },
};

function setToken(token, role) {
  state.token = token;
  state.role = role;
  localStorage.setItem('ecodes_token', token);
  localStorage.setItem('ecodes_role', role);
}

function clearToken() {
  localStorage.removeItem('ecodes_token');
  localStorage.removeItem('ecodes_role');
  state.token = '';
  state.role = '';
}

function apiFetch(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }

  return fetch(url, { ...options, headers }).then(async (response) => {
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.detail || 'Error de servidor');
    }
    return data;
  });
}

function formatCurrency(value) {
  const num = Number(value || 0);
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(num);
}

function escapeHtml(value = '') {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function renderPageTitle() {
  const map = {
    empleados: 'Empleados',
    proyectos: 'Proyectos',
    novedades: 'Novedades',
    nomina: 'Nómina',
    alertas: 'Alertas',
  };
  document.getElementById('pageTitle').textContent = map[state.currentView] || 'Ecodes';
}

function renderTopbarActions() {
  const slot = document.getElementById('topbarActionSlot');
  if (!slot) return;

  const actionMap = {
    empleados: state.role === 'Talento Humano' ? '<button class="btn btn-primary" id="addEmployeeBtn">Agregar empleado</button>' : '',
    proyectos: state.role === 'Talento Humano' ? '<button class="btn btn-primary" id="addProjectBtn">Agregar proyecto</button>' : '',
    novedades: state.role === 'Talento Humano' ? '<button class="btn btn-primary" id="addEventBtn">Registrar novedad</button>' : '',
    nomina: state.role === 'Talento Humano' ? '<button class="btn btn-primary" id="addPayrollBtn">Registrar novedad</button>' : '',
    alertas: '',
  };

  slot.innerHTML = actionMap[state.currentView] || '';

  const addEmployeeBtn = document.getElementById('addEmployeeBtn');
  if (addEmployeeBtn) addEmployeeBtn.addEventListener('click', () => openEmployeeForm());

  const addProjectBtn = document.getElementById('addProjectBtn');
  if (addProjectBtn) addProjectBtn.addEventListener('click', openProjectForm);

  const addEventBtn = document.getElementById('addEventBtn');
  if (addEventBtn) addEventBtn.addEventListener('click', openEventForm);

  const addPayrollBtn = document.getElementById('addPayrollBtn');
  if (addPayrollBtn) addPayrollBtn.addEventListener('click', () => openPayrollForm());
}

function toggleSidePanel(content = '') {
  const panel = document.getElementById('sidePanel');
  panel.innerHTML = content;
  panel.classList.toggle('hidden', !content);
}

function renderEmployees() {
  const content = document.getElementById('appContent');
  content.innerHTML = `
    <div class="panel-grid">
      <section class="widget">
        <div class="widget-header">
          <h3>Próximos cumpleaños</h3>
          <span class="pill">45 días</span>
        </div>
        <div class="birthday-list">
          <div class="birthday-row">
            <div class="avatar">AP</div>
            <div>
              <strong>Ana María Pérez</strong><br>
              <small>Analista Ambiental</small>
            </div>
            <span class="pill">Hoy</span>
          </div>
          <div class="birthday-row">
            <div class="avatar">CR</div>
            <div>
              <strong>Carlos Rojas</strong><br>
              <small>Monitoreo de Biodiversidad</small>
            </div>
            <span class="pill">Mañana</span>
          </div>
        </div>
      </section>

      <section class="table-card">
        <div class="table-tools">
          <div class="search-bar">
            <input id="searchEmployees" placeholder="Buscar empleado" />
            <select id="employeeStatusFilter">
              <option value="">Todos los estados</option>
              <option value="Activo">Activo</option>
              <option value="Inactivo">Inactivo</option>
            </select>
            <select id="employeeTypeFilter">
              <option value="">Todos</option>
              <option value="Profesional">Profesional</option>
              <option value="Técnico">Técnico</option>
              <option value="Operario">Operario</option>
              <option value="Administrativo">Administrativo</option>
            </select>
          </div>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Empleado</th>
                <th>Cargo</th>
                <th>Tipo</th>
                <th>Proyecto(s)</th>
                <th>% Total</th>
                <th>Antigüedad</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody id="employeeTableBody"></tbody>
          </table>
        </div>
      </section>
    </div>
  `;

  Promise.all([
    apiFetch('/empleados'),
    apiFetch('/proyectos')
  ]).then(([employees, projects]) => {
    state.employees = employees;
    state.projects = projects;
    renderEmployeeRows();
  }).catch(() => {
    document.getElementById('employeeTableBody').innerHTML = '<tr><td colspan="7">No fue posible cargar los empleados.</td></tr>';
  });

  document.getElementById('searchEmployees').addEventListener('input', renderEmployeeRows);
  document.getElementById('employeeStatusFilter').addEventListener('change', renderEmployeeRows);
  document.getElementById('employeeTypeFilter').addEventListener('change', renderEmployeeRows);
}

function renderEmployeeRows() {
  const tbody = document.getElementById('employeeTableBody');
  if (!tbody) return;

  const search = (document.getElementById('searchEmployees').value || '').toLowerCase();
  const status = document.getElementById('employeeStatusFilter').value;
  const type = document.getElementById('employeeTypeFilter').value;

  const filtered = state.employees.filter((emp) => {
    const nombre = String(emp?.nombre_completo || '').trim();
    const cargo = String(emp?.nombre_cargo || '').trim();
    const tipo = String(emp?.tipo_cargo || '').trim();
    const estado = String(emp?.estado || '').trim();

    const matchesSearch = !search || nombre.toLowerCase().includes(search) || cargo.toLowerCase().includes(search);
    const matchesStatus = !status || estado === status;
    const matchesType = !type || tipo === type;
    return matchesSearch && matchesStatus && matchesType;
  });

  if (!filtered.length) {
    tbody.innerHTML = '<tr><td colspan="7">Sin resultados</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map((emp) => {
    const total = emp.participaciones?.reduce((sum, p) => sum + Number(p.porcentaje || 0), 0) || 0;
    const projects = emp.participaciones?.map((p) => `${p.project_id} (${p.porcentaje}%)`).join(', ') || 'Sin asignación';
    return `
      <tr data-employee-id="${emp.id}">
        <td>
          <div class="birthday-row" style="padding:0; border:none; background:transparent; grid-template-columns: 42px 1fr;">
            <div class="avatar">${initials(emp.nombre_completo)}</div>
            <div><strong>${escapeHtml(emp.nombre_completo)}</strong><br><small>${escapeHtml(emp.nombre_cargo || 'Sin cargo')}</small></div>
          </div>
        </td>
        <td>${escapeHtml(emp.nombre_cargo || 'Sin cargo')}</td>
        <td>${escapeHtml(emp.tipo_cargo || 'Sin tipo')}</td>
        <td>${escapeHtml(projects)}</td>
        <td>${total.toFixed(0)}%</td>
        <td>${escapeHtml(emp.antiguedad || 'Sin fecha')}</td>
        <td><span class="badge ${emp.estado === 'Inactivo' ? 'inactive' : ''}">${escapeHtml(emp.estado || 'Activo')}</span></td>
      </tr>
    `;
  }).join('');

  tbody.querySelectorAll('tr[data-employee-id]').forEach((row) => {
    row.addEventListener('click', () => openEmployeeDetail(Number(row.dataset.employeeId)));
  });
}

function renderProjects() {
  const content = document.getElementById('appContent');
  content.innerHTML = `
    <section class="table-card">
      <div class="table-tools">
        <div class="search-bar">
          <input id="projectSearch" placeholder="Buscar proyecto" />
          <select id="projectStatusFilter">
            <option value="">Todos</option>
            <option value="Activo">Activo</option>
            <option value="Cierre">Cierre</option>
            <option value="Continuo">Continuo</option>
          </select>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Contratante</th>
              <th>Inicio</th>
              <th>Fin estimada</th>
              <th>Tamaño equipo</th>
              <th>Costo nómina/mes</th>
              <th>% rotación</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody id="projectTableBody"></tbody>
        </table>
      </div>
    </section>
  `;

  apiFetch('/proyectos').then((data) => {
    state.projects = data;
    renderProjectRows();
  }).catch(() => {
    document.getElementById('projectTableBody').innerHTML = '<tr><td colspan="8">No fue posible cargar los proyectos.</td></tr>';
  });

  document.getElementById('projectSearch').addEventListener('input', renderProjectRows);
  document.getElementById('projectStatusFilter').addEventListener('change', renderProjectRows);
}

function renderProjectRows() {
  const tbody = document.getElementById('projectTableBody');
  if (!tbody) return;
  const search = document.getElementById('projectSearch').value.toLowerCase();
  const status = document.getElementById('projectStatusFilter').value;
  const filtered = state.projects.filter((project) => {
    const matches = !search || project.nombre.toLowerCase().includes(search) || project.contratante.toLowerCase().includes(search);
    const matchesStatus = !status || project.estado === status;
    return matches && matchesStatus;
  });

  tbody.innerHTML = filtered.map((project) => {
    const people = project.participaciones?.length || 0;
    const totalParticipation = project.participaciones?.reduce((sum, p) => sum + Number(p.porcentaje || 0), 0) || 0;
    const cost = formatCurrency(project.presupuesto || 0);
    const rotation = people ? Math.min(100, Math.round((people * 15) / Math.max(1, people))) : 0;
    return `
      <tr data-project-id="${project.id}">
        <td>${escapeHtml(project.nombre)}</td>
        <td>${escapeHtml(project.contratante)}</td>
        <td>${escapeHtml(project.fecha_inicio || '-')}</td>
        <td>${escapeHtml(project.fecha_fin_estimada || '-')}</td>
        <td>${people}</td>
        <td>${cost}</td>
        <td>${rotation}%</td>
        <td><span class="badge">${escapeHtml(project.estado || 'Activo')}</span></td>
      </tr>
    `;
  }).join('');

  tbody.querySelectorAll('tr[data-project-id]').forEach((row) => {
    row.addEventListener('click', () => openProjectDetail(Number(row.dataset.projectId)));
  });
}

function renderEvents() {
  const content = document.getElementById('appContent');
  content.innerHTML = `
    <section class="table-card">
      <div class="table-tools">
        <div class="search-bar">
          <input id="eventSearch" placeholder="Buscar novedad" />
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Empleado</th>
              <th>Tipo</th>
              <th>Proyecto</th>
              <th>Fecha</th>
              <th>Detalle</th>
            </tr>
          </thead>
          <tbody id="eventTableBody"></tbody>
        </table>
      </div>
    </section>
  `;
  apiFetch('/novedades').then((data) => {
    state.events = data;
    renderEventRows();
  }).catch(() => {
    document.getElementById('eventTableBody').innerHTML = '<tr><td colspan="5">No fue posible cargar novedades.</td></tr>';
  });
  document.getElementById('eventSearch').addEventListener('input', renderEventRows);
}

function renderEventRows() {
  const tbody = document.getElementById('eventTableBody');
  if (!tbody) return;
  const search = document.getElementById('eventSearch').value.toLowerCase();
  const rows = state.events.filter((event) => {
    const employeeName = state.employees.find((e) => e.id === event.employee_id)?.nombre_completo || '';
    return !search || event.tipo.toLowerCase().includes(search) || employeeName.toLowerCase().includes(search);
  });
  tbody.innerHTML = rows.map((event) => `
    <tr>
      <td>${escapeHtml(state.employees.find((e) => e.id === event.employee_id)?.nombre_completo || event.employee_id)}</td>
      <td><span class="badge">${escapeHtml(event.tipo)}</span></td>
      <td>${escapeHtml(event.project_id || 'Sin proyecto')}</td>
      <td>${escapeHtml(event.fecha || '-')}</td>
      <td>${escapeHtml(event.detalle || '-')}</td>
    </tr>
  `).join('');
}

function renderPayroll() {
  const content = document.getElementById('appContent');
  content.innerHTML = `
    <div class="summary-grid">
      <div class="summary-card">
        <div class="kpi-label">Nómina total del mes</div>
        <div class="kpi-value">${formatCurrency(state.payroll.reduce((sum, row) => sum + Number(row.total || 0), 0))}</div>
        <div class="kpi-trend">Validación Colombia</div>
      </div>
      <div class="summary-card">
        <div class="kpi-label">Próximo pago</div>
        <div class="kpi-value">${new Date().toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })}</div>
        <div class="kpi-trend">14 días</div>
      </div>
      <div class="summary-card">
        <div class="kpi-label">Novedades sin procesar</div>
        <div class="kpi-value">${state.payroll.filter((row) => row.novedad_tipo && row.novedad_tipo !== 'Normal').length}</div>
        <div class="kpi-trend">Revisión requerida</div>
      </div>
    </div>
    <section class="table-card" style="margin-top: 24px;">
      <div class="table-tools">
        <div></div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Empleado</th>
              <th>Salario base</th>
              <th>Auxilio transporte</th>
              <th>Auxilio movilidad</th>
              <th>Descuentos</th>
              <th>Novedad</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody id="payrollTableBody"></tbody>
        </table>
      </div>
    </section>
  `;

  apiFetch('/nomina').then((data) => {
    state.payroll = data;
    renderPayrollRows();
  }).catch(() => {
    document.getElementById('payrollTableBody').innerHTML = '<tr><td colspan="7">No fue posible cargar nómina.</td></tr>';
  });

}

function renderPayrollRows() {
  const tbody = document.getElementById('payrollTableBody');
  if (!tbody) return;
  tbody.innerHTML = state.payroll.map((row) => {
    const employeeName = state.employees.find((e) => e.id === row.employee_id)?.nombre_completo || row.employee_id;
    return `
      <tr data-payroll-id="${row.id}">
        <td>${escapeHtml(employeeName)}</td>
        <td>${formatCurrency(row.salario_base)}</td>
        <td>${formatCurrency(row.auxilio_transporte)}</td>
        <td>${formatCurrency(row.auxilio_movilidad)}</td>
        <td>${formatCurrency(row.descuentos)}</td>
        <td>${escapeHtml(row.novedad_tipo || 'Normal')}</td>
        <td>${formatCurrency(row.total)}</td>
      </tr>
    `;
  }).join('');

  tbody.querySelectorAll('tr[data-payroll-id]').forEach((row) => {
    row.addEventListener('click', () => openPayrollForm(Number(row.dataset.payrollId)));
  });
}

function openPayrollForm(payrollId = null) {
  const payroll = payrollId ? state.payroll.find((item) => item.id === payrollId) : null;
  const employeeOptions = state.employees.map((emp) => `<option value="${emp.id}">${escapeHtml(emp.nombre_completo)}</option>`).join('');

  toggleSidePanel(`
    <div class="side-panel-header">
      <div><h2>${payroll ? 'Editar nómina' : 'Registrar novedad de nómina'}</h2></div>
      <button class="btn btn-ghost" onclick="document.getElementById('sidePanel').classList.add('hidden'); document.getElementById('sidePanel').innerHTML='';">Cerrar</button>
    </div>
    <div class="side-panel-body">
      <div class="detail-grid">
        <div class="field"><label>Empleado</label><select id="payrollEmployee">${employeeOptions}</select></div>
        <div class="field"><label>Periodo</label><input id="payrollPeriodo" value="${payroll?.periodo || new Date().toISOString().slice(0, 7)}" /></div>
        <div class="field"><label>Salario base</label><input id="payrollSalarioBase" type="number" value="${payroll?.salario_base || 1300000}" /></div>
        <div class="field"><label>Auxilio transporte</label><input id="payrollAuxTransporte" type="number" value="${payroll?.auxilio_transporte || 0}" /></div>
        <div class="field"><label>Auxilio movilidad</label><input id="payrollAuxMovilidad" type="number" value="${payroll?.auxilio_movilidad || 0}" /></div>
        <div class="field"><label>Descuentos</label><input id="payrollDescuentos" type="number" value="${payroll?.descuentos || 0}" /></div>
        <div class="field"><label>Tipo de novedad</label><select id="payrollNovedadTipo">
          <option value="Normal">Normal</option>
          <option value="Aumento salarial">Aumento salarial</option>
          <option value="Horas extras">Horas extras</option>
          <option value="Incapacidad">Incapacidad</option>
          <option value="Descuento">Descuento</option>
          <option value="Otro">Otro</option>
        </select></div>
        <div class="field" style="grid-column: 1 / -1;"><label>Detalle de la novedad</label><textarea id="payrollDetalle" rows="3">${escapeHtml(payroll?.novedad_detalle || '')}</textarea></div>
      </div>
      <div class="inline-actions" style="margin-top: 24px;">
        <button class="btn" onclick="submitPayrollForm(${payrollId || 'null'})">Guardar</button>
      </div>
    </div>
  `);

  const employeeSelect = document.getElementById('payrollEmployee');
  if (employeeSelect && payroll) employeeSelect.value = String(payroll.employee_id);
  const tipoSelect = document.getElementById('payrollNovedadTipo');
  if (tipoSelect && payroll) tipoSelect.value = payroll.novedad_tipo || 'Normal';
}

function submitPayrollForm(payrollId) {
  const payload = {
    employee_id: Number(document.getElementById('payrollEmployee').value),
    periodo: document.getElementById('payrollPeriodo').value,
    salario_base: Number(document.getElementById('payrollSalarioBase').value || 0),
    auxilio_transporte: Number(document.getElementById('payrollAuxTransporte').value || 0),
    auxilio_movilidad: Number(document.getElementById('payrollAuxMovilidad').value || 0),
    descuentos: Number(document.getElementById('payrollDescuentos').value || 0),
    novedad_tipo: document.getElementById('payrollNovedadTipo').value,
    novedad_detalle: document.getElementById('payrollDetalle').value.trim(),
  };

  if (payload.salario_base < 1300000) {
    alert('La nómina debe respetar el salario mínimo legal vigente en Colombia (SMMLV: $1.300.000).');
    return;
  }

  if (payload.auxilio_transporte > payload.salario_base) {
    alert('El auxilio de transporte no puede ser mayor al salario base.');
    return;
  }

  if (payload.descuentos > payload.salario_base + payload.auxilio_transporte + payload.auxilio_movilidad) {
    alert('Los descuentos no pueden superar la base liquidable del empleado.');
    return;
  }

  const method = payrollId ? 'PUT' : 'POST';
  const url = payrollId ? `/nomina/${payrollId}` : '/nomina';

  apiFetch(url, { method, body: JSON.stringify(payload) }).then(() => {
    toggleSidePanel('');
    renderPayroll();
  }).catch((err) => {
    alert(err.message);
  });
}

function renderAlerts() {
  const content = document.getElementById('appContent');
  content.innerHTML = `
    <div class="summary-grid">
      <div class="summary-card">
        <div class="kpi-label">Vacaciones por vencer</div>
        <div class="kpi-value" id="vacationMetric">0</div>
        <div class="kpi-trend">Próximo umbral de cumplimiento</div>
      </div>
      <div class="summary-card">
        <div class="kpi-label">Pagos próximos</div>
        <div class="kpi-value">2</div>
        <div class="kpi-trend">Cronograma de nómina</div>
      </div>
      <div class="summary-card">
        <div class="kpi-label">Sobre-asignación</div>
        <div class="kpi-value" id="overMetric">0</div>
        <div class="kpi-trend">Personal por encima de 90%</div>
      </div>
    </div>
    <div class="widget-grid" style="margin-top: 24px;">
      <section class="widget">
        <div class="widget-header"><h3>Vacaciones por vencer</h3></div>
        <div id="vacationList"></div>
      </section>
      <section class="widget">
        <div class="widget-header"><h3>Sobre-asignación</h3></div>
        <div id="overList"></div>
      </section>
    </div>
  `;

  Promise.all([
    apiFetch('/alertas/vacaciones'),
    apiFetch('/alertas/sobreasignacion'),
  ]).then(([vacationData, overData]) => {
    state.alerts.vacaciones = vacationData;
    state.alerts.sobreasignacion = overData;
    document.getElementById('vacationMetric').textContent = String(vacationData.length);
    document.getElementById('overMetric').textContent = String(overData.length);
    document.getElementById('vacationList').innerHTML = vacationData.length ? vacationData.map((item) => `<div class="list-item"><strong>${escapeHtml(item.employee_name)}</strong><br><small>${item.dias_pendientes} días pendientes</small></div>`).join('') : '<div class="list-item">Sin alertas de vacaciones</div>';
    document.getElementById('overList').innerHTML = overData.length ? overData.map((item) => `<div class="list-item"><strong>${escapeHtml(item.employee_name)}</strong><br><small>${item.total_porcentaje}% de participación</small></div>`).join('') : '<div class="list-item">Sin sobre-asignación</div>';
  }).catch(() => {
    document.getElementById('vacationList').innerHTML = '<div class="list-item">Sin alertas</div>';
    document.getElementById('overList').innerHTML = '<div class="list-item">Sin alertas</div>';
  });
}

function initials(name) {
  const words = String(name || 'E')
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2);

  if (!words.length) return 'E';

  return words
    .map((word) => word.charAt(0).toUpperCase())
    .join('');
}

function openEmployeeDetail(id) {
  const employee = state.employees.find((item) => item.id === id);
  if (!employee) return;
  const participations = employee.participaciones || [];
  toggleSidePanel(`
    <div class="side-panel-header">
      <div>
        <h2>${escapeHtml(employee.nombre_completo || 'Empleado')}</h2>
        <small>${escapeHtml(employee.nombre_cargo || 'Sin cargo')}</small>
      </div>
      <button class="btn btn-ghost" onclick="document.getElementById('sidePanel').classList.add('hidden'); document.getElementById('sidePanel').innerHTML='';">Cerrar</button>
    </div>
    <div class="side-panel-body">
      <div class="detail-grid">
        <div class="field"><label>Nombre completo</label><input value="${escapeHtml(employee.nombre_completo)}" readonly /></div>
        <div class="field"><label>Género</label><input value="${escapeHtml(employee.genero || '')}" readonly /></div>
        <div class="field"><label>Tipo de cargo</label><input value="${escapeHtml(employee.tipo_cargo || '')}" readonly /></div>
        <div class="field"><label>Estado</label><input value="${escapeHtml(employee.estado)}" readonly /></div>
        <div class="field"><label>Fecha de ingreso</label><input value="${escapeHtml(employee.fecha_ingreso || '')}" readonly /></div>
        <div class="field"><label>Antigüedad</label><input value="${escapeHtml(employee.antiguedad || '')}" readonly /></div>
      </div>
      <div class="section">
        <h3>Formación académica</h3>
        <div class="list-stack">
          ${(employee.formaciones || []).map((f) => `<div class="list-item"><strong>${escapeHtml(f.titulo)}</strong><br><small>${escapeHtml(f.institucion)} · ${f.anio}</small></div>`).join('') || '<div class="list-item">Sin información</div>'}
        </div>
      </div>
      <div class="section">
        <h3>Experiencia laboral</h3>
        <div class="list-stack">
          ${(employee.experiencias || []).map((e) => `<div class="list-item"><strong>${escapeHtml(e.empresa)}</strong><br><small>${escapeHtml(e.cargo)} · ${escapeHtml(e.periodo)}</small></div>`).join('') || '<div class="list-item">Sin información</div>'}
        </div>
      </div>
      <div class="section">
        <h3>Proyectos asignados</h3>
        <div class="list-stack">
          ${participations.length ? participations.map((p) => `<div class="list-item"><strong>Proyecto ${p.project_id}</strong><br><small>${p.porcentaje}% de dedicación</small></div>`).join('') : '<div class="list-item">Sin asignaciones</div>'}
        </div>
      </div>
      <div class="inline-actions" style="margin-top: 24px;">
        ${state.role === 'Talento Humano' ? '<button class="btn" onclick="openEmployeeForm(' + employee.id + ')">Editar</button>' : ''}
      </div>
    </div>
  `);
}

function calculateAgeFromBirthdate(value) {
  if (!value) return '';
  const birthDate = new Date(value);
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDifference = today.getMonth() - birthDate.getMonth();
  if (monthDifference < 0 || (monthDifference === 0 && today.getDate() < birthDate.getDate())) {
    age -= 1;
  }
  return `${age} años`;
}

function addStudyRow() {
  const container = document.getElementById('studyRows');
  if (!container) return;
  const index = container.dataset.index ? Number(container.dataset.index) : 0;
  container.dataset.index = String(index + 1);
  const row = document.createElement('div');
  row.className = 'list-item';
  row.style.marginTop = '12px';
  row.innerHTML = `
    <div class="field" style="margin-bottom: 10px;">
      <label>Título / especialización</label>
      <input data-study-field="titulo" placeholder="Ej: Especialización en GIS" />
    </div>
    <div class="field" style="margin-bottom: 10px;">
      <label>Universidad / institución</label>
      <input data-study-field="institucion" placeholder="Ej: Universidad Nacional" />
    </div>
    <div class="field">
      <label>Año</label>
      <input data-study-field="anio" type="number" min="1950" max="2100" placeholder="2024" />
    </div>
  `;
  container.appendChild(row);
}

function addExperienceRow() {
  const container = document.getElementById('experienceRows');
  if (!container) return;
  const row = document.createElement('div');
  row.className = 'list-item';
  row.style.marginTop = '12px';
  row.innerHTML = `
    <div class="field" style="margin-bottom: 10px;">
      <label>Empresa</label>
      <input data-experience-field="empresa" placeholder="Ej: Ecodes" />
    </div>
    <div class="field" style="margin-bottom: 10px;">
      <label>Cargo</label>
      <input data-experience-field="cargo" placeholder="Ej: Analista Ambiental" />
    </div>
    <div class="field">
      <label>Período</label>
      <input data-experience-field="periodo" placeholder="Ej: 2018-2021" />
    </div>
  `;
  container.appendChild(row);
}

function openEmployeeForm(employeeId = null) {
  const employee = employeeId ? state.employees.find((item) => item.id === employeeId) : null;
  const studies = employee?.formaciones?.length ? employee.formaciones : [{ titulo: '', institucion: '', anio: new Date().getFullYear() }];
  const experiences = employee?.experiencias?.length ? employee.experiencias : [{ empresa: '', cargo: '', periodo: '' }];

  const selectedProjectId = employee?.participaciones?.[0]?.project_id || '';
  const projectOptions = state.projects.map((project) => `
    <option value="${project.id}">${escapeHtml(project.nombre)}</option>
  `).join('');

  toggleSidePanel(`
    <div class="side-panel-header">
      <div><h2>${employee ? 'Editar empleado' : 'Nuevo empleado'}</h2></div>
      <button class="btn btn-ghost" onclick="document.getElementById('sidePanel').classList.add('hidden'); document.getElementById('sidePanel').innerHTML='';">Cerrar</button>
    </div>
    <div class="side-panel-body">
      <div class="detail-grid">
        <div class="field"><label>Nombre completo</label><input id="empNombre" value="${escapeHtml(employee?.nombre_completo || '')}" /></div>
        <div class="field"><label>Género</label><select id="empGenero">
          <option value="">Seleccione</option>
          <option value="Femenino">Femenino</option>
          <option value="Masculino">Masculino</option>
          <option value="Otro">Otro</option>
        </select></div>
        <div class="field"><label>Dirección</label><input id="empDireccion" value="${escapeHtml(employee?.direccion || '')}" /></div>
        <div class="field"><label>Fecha de nacimiento</label><input id="empNacimiento" type="date" value="${employee?.fecha_nacimiento || ''}" /></div>
        <div class="field"><label>Edad</label><input id="empEdad" readonly value="${employee?.fecha_nacimiento ? calculateAgeFromBirthdate(employee.fecha_nacimiento) : ''}" /></div>
        <div class="field"><label>Nivel educativo</label><select id="empNivel">
          <option value="">Seleccione</option>
          <option value="Bachillerato">Bachillerato</option>
          <option value="Técnico">Técnico</option>
          <option value="Tecnólogo">Tecnólogo</option>
          <option value="Profesional">Profesional</option>
          <option value="Especialización">Especialización</option>
          <option value="Maestría">Maestría</option>
          <option value="Doctorado">Doctorado</option>
        </select></div>
        <div class="field"><label>Cargo</label><input id="empCargo" value="${escapeHtml(employee?.nombre_cargo || '')}" /></div>
        <div class="field"><label>Tipo de cargo</label><select id="empTipo"><option value="Profesional">Profesional</option><option value="Técnico">Técnico</option><option value="Operario">Operario</option><option value="Administrativo">Administrativo</option></select></div>
        <div class="field"><label>Proyecto</label><select id="empProyecto"><option value="">Sin proyecto</option>${projectOptions}</select></div>
        <div class="field"><label>% Participación</label><input id="empParticipacion" type="number" min="1" max="100" step="1" value="${employee?.participaciones?.[0]?.porcentaje || 100}" /></div>
        <div class="field"><label>Fecha de ingreso</label><input id="empIngreso" type="date" value="${employee?.fecha_ingreso || ''}" /></div>
        <div class="field"><label>Estado</label><select id="empEstado"><option value="Activo">Activo</option><option value="Inactivo">Inactivo</option></select></div>
      </div>

      <div class="section">
        <h3>Formación académica</h3>
        <div id="studyRows">
          ${studies.map((study) => `
            <div class="list-item" style="margin-top: 12px;">
              <div class="field" style="margin-bottom: 10px;">
                <label>Título / especialización</label>
                <input data-study-field="titulo" value="${escapeHtml(study.titulo || '')}" placeholder="Ej: Especialización en GIS" />
              </div>
              <div class="field" style="margin-bottom: 10px;">
                <label>Universidad / institución</label>
                <input data-study-field="institucion" value="${escapeHtml(study.institucion || '')}" placeholder="Ej: Universidad Nacional" />
              </div>
              <div class="field">
                <label>Año</label>
                <input data-study-field="anio" type="number" min="1950" max="2100" value="${study.anio || ''}" placeholder="2024" />
              </div>
            </div>
          `).join('')}
        </div>
        <div class="inline-actions" style="margin-top: 12px;">
          <button type="button" class="btn btn-secondary" onclick="addStudyRow()">Agregar estudio</button>
        </div>
      </div>

      <div class="section">
        <h3>Experiencia laboral</h3>
        <div id="experienceRows">
          ${experiences.map((exp) => `
            <div class="list-item" style="margin-top: 12px;">
              <div class="field" style="margin-bottom: 10px;">
                <label>Empresa</label>
                <input data-experience-field="empresa" value="${escapeHtml(exp.empresa || '')}" placeholder="Ej: Ecodes" />
              </div>
              <div class="field" style="margin-bottom: 10px;">
                <label>Cargo</label>
                <input data-experience-field="cargo" value="${escapeHtml(exp.cargo || '')}" placeholder="Ej: Analista Ambiental" />
              </div>
              <div class="field">
                <label>Período</label>
                <input data-experience-field="periodo" value="${escapeHtml(exp.periodo || '')}" placeholder="Ej: 2018-2021" />
              </div>
            </div>
          `).join('')}
        </div>
        <div class="inline-actions" style="margin-top: 12px;">
          <button type="button" class="btn btn-secondary" onclick="addExperienceRow()">Agregar experiencia</button>
        </div>
      </div>

      <div class="inline-actions" style="margin-top: 24px;">
        <button class="btn" onclick="submitEmployeeForm(${employeeId || 'null'})">Guardar</button>
      </div>
    </div>
  `);

  const tipoSelect = document.getElementById('empTipo');
  if (tipoSelect && employee) tipoSelect.value = employee.tipo_cargo || 'Profesional';
  const estadoSelect = document.getElementById('empEstado');
  if (estadoSelect && employee) estadoSelect.value = employee.estado || 'Activo';
  const nivelSelect = document.getElementById('empNivel');
  if (nivelSelect && employee) nivelSelect.value = employee.nivel_educativo || '';
  const generoSelect = document.getElementById('empGenero');
  if (generoSelect) generoSelect.value = employee?.genero || '';
  const proyectoSelect = document.getElementById('empProyecto');
  if (proyectoSelect) proyectoSelect.value = selectedProjectId || '';

  const birthInput = document.getElementById('empNacimiento');
  const ageInput = document.getElementById('empEdad');
  if (birthInput && ageInput) {
    birthInput.addEventListener('input', () => {
      ageInput.value = calculateAgeFromBirthdate(birthInput.value);
    });
  }
}

function submitEmployeeForm(employeeId) {
  const readStudyRows = () => Array.from(document.querySelectorAll('#studyRows .list-item')).map((item) => {
    const titulo = item.querySelector('[data-study-field="titulo"]')?.value?.trim();
    const institucion = item.querySelector('[data-study-field="institucion"]')?.value?.trim();
    const anioValue = item.querySelector('[data-study-field="anio"]')?.value;

    if (!titulo && !institucion && !anioValue) return null;
    return {
      titulo: titulo || '',
      institucion: institucion || '',
      anio: Number(anioValue || 0),
    };
  }).filter(Boolean);

  const readExperienceRows = () => Array.from(document.querySelectorAll('#experienceRows .list-item')).map((item) => {
    const empresa = item.querySelector('[data-experience-field="empresa"]')?.value?.trim();
    const cargo = item.querySelector('[data-experience-field="cargo"]')?.value?.trim();
    const periodo = item.querySelector('[data-experience-field="periodo"]')?.value?.trim();

    if (!empresa && !cargo && !periodo) return null;
    return {
      empresa: empresa || '',
      cargo: cargo || '',
      periodo: periodo || '',
    };
  }).filter(Boolean);

  const selectedProjectId = document.getElementById('empProyecto')?.value;
  const selectedParticipation = Number(document.getElementById('empParticipacion')?.value || 0);

  const payload = {
    nombre_completo: document.getElementById('empNombre').value.trim(),
    genero: document.getElementById('empGenero').value,
    direccion: document.getElementById('empDireccion').value.trim(),
    fecha_nacimiento: document.getElementById('empNacimiento').value || null,
    nivel_educativo: document.getElementById('empNivel').value,
    nombre_cargo: document.getElementById('empCargo').value.trim(),
    tipo_cargo: document.getElementById('empTipo').value,
    fecha_ingreso: document.getElementById('empIngreso').value || null,
    estado: document.getElementById('empEstado').value,
    formaciones: readStudyRows(),
    experiencias: readExperienceRows(),
    participaciones: selectedProjectId ? [{ project_id: Number(selectedProjectId), porcentaje: Number.isFinite(selectedParticipation) ? selectedParticipation : 0 }] : [],
  };

  if (!payload.nombre_completo || !payload.nombre_cargo) {
    alert('Debe completar al menos el nombre y el cargo del empleado.');
    return;
  }

  const method = employeeId ? 'PUT' : 'POST';
  const url = employeeId ? `/empleados/${employeeId}` : '/empleados';
  apiFetch(url, { method, body: JSON.stringify(payload) }).then(() => {
    toggleSidePanel('');
    renderEmployees();
  }).catch((err) => {
    alert(err.message);
  });
}

function openProjectDetail(id) {
  const project = state.projects.find((item) => item.id === id);
  if (!project) return;
  toggleSidePanel(`
    <div class="side-panel-header">
      <div><h2>${escapeHtml(project.nombre)}</h2><small>${escapeHtml(project.contratante)}</small></div>
      <button class="btn btn-ghost" onclick="document.getElementById('sidePanel').classList.add('hidden'); document.getElementById('sidePanel').innerHTML='';">Cerrar</button>
    </div>
    <div class="side-panel-body">
      <div class="detail-grid">
        <div class="field"><label>Contratante</label><input value="${escapeHtml(project.contratante)}" readonly /></div>
        <div class="field"><label>Estado</label><input value="${escapeHtml(project.estado)}" readonly /></div>
        <div class="field"><label>Inicio</label><input value="${escapeHtml(project.fecha_inicio || '')}" readonly /></div>
        <div class="field"><label>Fin estimada</label><input value="${escapeHtml(project.fecha_fin_estimada || '')}" readonly /></div>
      </div>
      <div class="section">
        <h3>Participaciones</h3>
        <div class="list-stack">
          ${(project.participaciones || []).map((p) => `<div class="list-item"><strong>Empleado ${p.employee_id}</strong><br><small>${p.porcentaje}% de participación</small></div>`).join('') || '<div class="list-item">Sin participaciones</div>'}
        </div>
      </div>
      ${state.role === 'Talento Humano' ? '<div class="inline-actions" style="margin-top: 24px;"><button class="btn" onclick="openProjectForm(' + project.id + ')">Editar</button></div>' : ''}
    </div>
  `);
}

function openProjectForm(projectId = null) {
  const project = projectId ? state.projects.find((item) => item.id === projectId) : null;
  toggleSidePanel(`
    <div class="side-panel-header">
      <div><h2>${project ? 'Editar proyecto' : 'Nuevo proyecto'}</h2></div>
      <button class="btn btn-ghost" onclick="document.getElementById('sidePanel').classList.add('hidden'); document.getElementById('sidePanel').innerHTML='';">Cerrar</button>
    </div>
    <div class="side-panel-body">
      <div class="detail-grid">
        <div class="field"><label>Nombre</label><input id="projNombre" value="${escapeHtml(project?.nombre || '')}" /></div>
        <div class="field"><label>Contratante</label><input id="projContratante" value="${escapeHtml(project?.contratante || '')}" /></div>
        <div class="field"><label>Fecha inicio</label><input id="projInicio" type="date" value="${project?.fecha_inicio || ''}" /></div>
        <div class="field"><label>Fecha fin</label><input id="projFin" type="date" value="${project?.fecha_fin_estimada || ''}" /></div>
        <div class="field"><label>Estado</label><select id="projEstado"><option value="Activo">Activo</option><option value="Cierre">Cierre</option><option value="Continuo">Continuo</option></select></div>
        <div class="field"><label>Presupuesto</label><input id="projPresupuesto" type="number" value="${project?.presupuesto || 0}" /></div>
      </div>
      <div class="inline-actions" style="margin-top: 24px;">
        <button class="btn" onclick="submitProjectForm(${projectId || 'null'})">Guardar</button>
      </div>
    </div>
  `);
  if (project) document.getElementById('projEstado').value = project.estado || 'Activo';
}

function submitProjectForm(projectId) {
  const payload = {
    nombre: document.getElementById('projNombre').value,
    contratante: document.getElementById('projContratante').value,
    fecha_inicio: document.getElementById('projInicio').value,
    fecha_fin_estimada: document.getElementById('projFin').value,
    estado: document.getElementById('projEstado').value,
    presupuesto: Number(document.getElementById('projPresupuesto').value || 0),
  };
  const method = projectId ? 'PUT' : 'POST';
  const url = projectId ? `/proyectos/${projectId}` : '/proyectos';
  apiFetch(url, { method, body: JSON.stringify(payload) }).then(() => {
    toggleSidePanel('');
    renderProjects();
  }).catch((err) => {
    alert(err.message);
  });
}

function openEventForm() {
  toggleSidePanel(`
    <div class="side-panel-header">
      <div><h2>Registrar novedad</h2></div>
      <button class="btn btn-ghost" onclick="document.getElementById('sidePanel').classList.add('hidden'); document.getElementById('sidePanel').innerHTML='';">Cerrar</button>
    </div>
    <div class="side-panel-body">
      <div class="detail-grid">
        <div class="field"><label>Empleado ID</label><input id="eventEmployeeId" value="1" /></div>
        <div class="field"><label>Tipo</label><select id="eventType"><option>Ingreso</option><option>Salida</option><option>Cambio de proyecto</option><option>Incapacidad</option><option>Otro</option></select></div>
        <div class="field"><label>Proyecto ID (opcional)</label><input id="eventProjectId" value="" /></div>
        <div class="field"><label>Fecha</label><input id="eventDate" type="date" /></div>
      </div>
      <div class="field" style="margin-top: 16px;"><label>Detalle</label><textarea id="eventDetail" rows="4"></textarea></div>
      <div class="inline-actions" style="margin-top: 24px;"><button class="btn" onclick="submitEventForm()">Guardar</button></div>
    </div>
  `);
}

function submitEventForm() {
  const payload = {
    employee_id: Number(document.getElementById('eventEmployeeId').value),
    project_id: document.getElementById('eventProjectId').value ? Number(document.getElementById('eventProjectId').value) : null,
    tipo: document.getElementById('eventType').value,
    fecha: document.getElementById('eventDate').value,
    detalle: document.getElementById('eventDetail').value,
  };
  apiFetch('/novedades', { method: 'POST', body: JSON.stringify(payload) }).then(() => {
    toggleSidePanel('');
    renderEvents();
  }).catch((err) => {
    alert(err.message);
  });
}

function setupNavigation() {
  document.querySelectorAll('.nav-item').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.nav-item').forEach((item) => item.classList.remove('active'));
      button.classList.add('active');
      state.currentView = button.dataset.view;
      renderPageTitle();
      toggleSidePanel('');
      renderTopbarActions();
      switch (state.currentView) {
        case 'empleados': renderEmployees(); break;
        case 'proyectos': renderProjects(); break;
        case 'novedades': renderEvents(); break;
        case 'nomina': renderPayroll(); break;
        case 'alertas': renderAlerts(); break;
      }
    });
  });
}

function handleLoginSubmit(event) {
  event.preventDefault();
  const form = new FormData(event.target);
  const role = form.get('role');
  const email = form.get('email');
  const password = form.get('password');

  const payload = { email, password, role };
  fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).then(async (response) => {
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Credenciales inválidas');
    }
    if (role !== data.role) {
      throw new Error('El rol seleccionado no coincide con el usuario autenticado');
    }
    setToken(data.access_token, data.role);
    window.location.href = '/ecodesTH/app';
  }).catch((error) => {
    document.getElementById('loginError').textContent = error.message;
    document.getElementById('loginInfo').textContent = '';
  });
}

function setupLogin() {
  const form = document.getElementById('loginForm');
  if (!form) return;
  form.addEventListener('submit', handleLoginSubmit);

  const roleSelect = document.getElementById('role');
  roleSelect.addEventListener('change', () => {
    const role = roleSelect.value;
    const email = role === 'Talento Humano' ? 'juans.lagosv@gmail.com' : 'admin@ecodes.com';
    document.getElementById('email').value = email;
    document.getElementById('password').value = role === 'Talento Humano' ? 'ecodes123' : 'admin123';
    document.getElementById('loginError').textContent = '';
    document.getElementById('loginInfo').textContent = '';
  });
}

function applyInitialState() {
  if (window.location.pathname === '/login') {
    setupLogin();
    return;
  }
  if (!state.token) {
    window.location.href = '/ecodesTH/login';
    return;
  }
  setupNavigation();
  renderPageTitle();
  renderEmployees();
  document.getElementById('exportExcelBtn').addEventListener('click', async () => {
    if (!state.token) {
      window.location.href = '/ecodesTH/login';
      return;
    }

    try {
      const response = await fetch('/exportar/excel', {
        headers: {
          Authorization: `Bearer ${state.token}`,
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'No se pudo exportar el archivo');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'ecodes_hr_export.xlsx';
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      alert(error.message || 'No se pudo exportar a Excel.');
    }
  });
  document.getElementById('logoutBtn').addEventListener('click', () => {
    clearToken();
    window.location.href = '/ecodesTH/login';
  });
  renderTopbarActions();
}

document.addEventListener('DOMContentLoaded', applyInitialState);
