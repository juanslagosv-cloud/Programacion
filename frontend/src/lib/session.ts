"use client";

// Sesión real de la aplicación: el JWT propio emitido por el backend tras
// validar el login (Google real o Mock, según IntegrationMode del backend,
// sección 4/19). Se guarda en localStorage por simplicidad de este esqueleto;
// como es un JWT de vida corta (60 min por defecto), su exposición a XSS tiene
// impacto acotado, pero una migración a cookie HttpOnly es una mejora futura
// razonable antes de producción (sección 19/81).
export interface Perfil {
  id: number;
  nombre: string;
  correo: string;
  roles: string[];
  permisos: string[];
}

export interface Sesion {
  token: string;
  perfil: Perfil;
}

const CLAVE = "cxp_sesion";

export function obtenerSesion(): Sesion | null {
  if (typeof window === "undefined") return null;
  try {
    const crudo = window.localStorage.getItem(CLAVE);
    return crudo ? (JSON.parse(crudo) as Sesion) : null;
  } catch {
    return null;
  }
}

export function guardarSesion(sesion: Sesion): void {
  window.localStorage.setItem(CLAVE, JSON.stringify(sesion));
}

export function cerrarSesion(): void {
  window.localStorage.removeItem(CLAVE);
}

/** Rol principal para elegir el menú (sección 78). Un usuario puede tener varios roles (punto 3); el esqueleto usa el primero. */
export function rolPrincipal(sesion: Sesion): string | undefined {
  return sesion.perfil.roles[0];
}
