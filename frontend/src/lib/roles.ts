// Roles iniciales del sistema (sección 3) y el menú/dashboard que le corresponde a
// cada uno (secciones 5 y 78). Esto es un mapa ESTÁTICO de demostración para el
// esqueleto de frontend: en la Fase 3 los permisos reales vendrán del backend
// (RBAC, sección 8) y este archivo se reemplaza por la respuesta de /api/auth/me.
// El backend SIEMPRE vuelve a validar el permiso — ocultar un botón aquí nunca
// es la única barrera (regla explícita de la sección 3/81).

export type Rol =
  | "Solicitante"
  | "Revisor"
  | "Aprobador"
  | "Contabilidad"
  | "Tesoreria"
  | "Auditor"
  | "Administrador";

export const ROLES: Rol[] = [
  "Solicitante",
  "Revisor",
  "Aprobador",
  "Contabilidad",
  "Tesoreria",
  "Auditor",
  "Administrador",
];

/** El backend (DemoDataSeeder) usa estos mismos nombres de rol — casteo seguro con fallback. */
export function comoRolConocido(nombreRol: string | undefined): Rol {
  return (ROLES as string[]).includes(nombreRol ?? "") ? (nombreRol as Rol) : "Solicitante";
}

export interface ItemMenu {
  etiqueta: string;
  href: string;
}

export interface SeccionMenu {
  titulo: string;
  items: ItemMenu[];
}

/** Estructura de menú lateral (sección 78), filtrada por rol. */
export function menuParaRol(rol: Rol): SeccionMenu[] {
  const secciones: SeccionMenu[] = [
    { titulo: "Inicio", items: [{ etiqueta: "Inicio", href: "/dashboard" }] },
  ];

  if (rol === "Solicitante" || rol === "Administrador") {
    secciones.push({
      titulo: "Solicitudes",
      items: [
        { etiqueta: "Nueva solicitud", href: "/dashboard/solicitudes/nueva" },
        { etiqueta: "Mis solicitudes", href: "/dashboard/solicitudes/mias" },
        { etiqueta: "Devueltas", href: "/dashboard/solicitudes/devueltas" },
      ],
    });
  }

  if (rol === "Aprobador" || rol === "Administrador") {
    secciones.push({
      titulo: "Aprobaciones",
      items: [
        { etiqueta: "Pendientes", href: "/dashboard/aprobaciones/pendientes" },
        { etiqueta: "Historial", href: "/dashboard/aprobaciones/historial" },
      ],
    });
  }

  if (rol === "Contabilidad" || rol === "Administrador") {
    secciones.push({
      titulo: "Contabilidad",
      items: [
        { etiqueta: "Pendientes de causación", href: "/dashboard/contabilidad/pendientes" },
        { etiqueta: "Causadas", href: "/dashboard/contabilidad/causadas" },
        { etiqueta: "Devueltas", href: "/dashboard/contabilidad/devueltas" },
      ],
    });
  }

  if (rol === "Tesoreria" || rol === "Administrador") {
    secciones.push({
      titulo: "Tesorería",
      items: [
        { etiqueta: "Pendientes", href: "/dashboard/tesoreria/pendientes" },
        { etiqueta: "Programados", href: "/dashboard/tesoreria/programados" },
        { etiqueta: "Pagados", href: "/dashboard/tesoreria/pagados" },
      ],
    });
  }

  secciones.push({
    titulo: "Documentos",
    items: [{ etiqueta: "Buscar expediente", href: "/dashboard/documentos/buscar" }],
  });

  if (rol === "Auditor" || rol === "Administrador") {
    secciones.push({
      titulo: "Auditoría",
      items: [{ etiqueta: "Historial de auditoría", href: "/dashboard/auditoria" }],
    });
  }

  secciones.push({ titulo: "Reportes", items: [{ etiqueta: "Reportes", href: "/dashboard/reportes" }] });

  if (rol === "Administrador") {
    secciones.push({
      titulo: "Administración",
      items: [
        { etiqueta: "Usuarios y roles", href: "/dashboard/admin/usuarios" },
        { etiqueta: "Empresas", href: "/dashboard/admin/empresas" },
        { etiqueta: "Proveedores", href: "/dashboard/admin/proveedores" },
        { etiqueta: "Flujos de aprobación", href: "/dashboard/admin/flujos" },
        { etiqueta: "Configuración general", href: "/dashboard/admin/configuracion" },
      ],
    });
  }

  return secciones;
}

/** Accesos rápidos del dashboard por rol (ejemplos de la sección 5). */
export function accesosRapidosParaRol(rol: Rol): string[] {
  switch (rol) {
    case "Solicitante":
      return ["Nueva solicitud", "Mis solicitudes", "Solicitudes devueltas", "Solicitudes pagadas"];
    case "Aprobador":
      return ["Pendientes de mi aprobación", "Próximas a vencer", "Aprobadas por mí", "Historial"];
    case "Contabilidad":
      return ["Pendientes de causación", "Devueltas", "Causadas hoy", "Próximas a vencer"];
    case "Tesoreria":
      return ["Pendientes de pago", "Pagos programados hoy", "Vencidos", "Próximos a vencer", "Pagados hoy"];
    case "Administrador":
      return ["Usuarios", "Empresas", "Proveedores", "Flujos", "Configuración", "Auditoría"];
    case "Revisor":
      return ["Pendientes de revisión", "Revisadas hoy"];
    case "Auditor":
      return ["Historial de auditoría", "Expedientes cerrados"];
  }
}
