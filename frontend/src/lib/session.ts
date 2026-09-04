"use client";

import type { Rol } from "./roles";

// Sesión de demostración en localStorage (Fase 1/2 del frontend). En la Fase 3
// esto se reemplaza por el JWT emitido por el backend tras validar el login de
// Google (IAuthProvider), como describe la sección 4 de la propuesta técnica:
// "la autenticación debe estar desacoplada del resto de la aplicación".
export interface SesionDemo {
  correo: string;
  nombre: string;
  rol: Rol;
}

const CLAVE = "cxp_sesion_demo";

export function obtenerSesion(): SesionDemo | null {
  if (typeof window === "undefined") return null;
  try {
    const crudo = window.localStorage.getItem(CLAVE);
    return crudo ? (JSON.parse(crudo) as SesionDemo) : null;
  } catch {
    return null;
  }
}

export function guardarSesion(sesion: SesionDemo): void {
  window.localStorage.setItem(CLAVE, JSON.stringify(sesion));
}

export function cerrarSesion(): void {
  window.localStorage.removeItem(CLAVE);
}
