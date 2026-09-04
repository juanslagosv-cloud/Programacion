import type { Perfil } from "./session";

// El frontend nunca habla con Access, Drive ni Gmail directamente (sección 3/61):
// todo pasa por esta API HTTP, que es el único cliente configurado en la app.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5238";

export interface EstadoSistema {
  dataProvider: string;
  integrationMode: string;
  ambiente: string;
}

export async function obtenerEstadoSistema(): Promise<EstadoSistema | null> {
  try {
    const respuesta = await fetch(`${API_URL}/api/sistema/estado`, { cache: "no-store" });
    if (!respuesta.ok) return null;
    return (await respuesta.json()) as EstadoSistema;
  } catch {
    // La API puede no estar disponible (backend apagado, red, etc.): el dashboard
    // debe seguir renderizando en vez de romperse (mismo principio de resiliencia
    // aplicado a Drive/Gmail en el backend, sección 71/72).
    return null;
  }
}

export class ErrorDeAutenticacion extends Error {}

/**
 * Login (sección 4). `tokenExterno` es el id_token real de Google Identity
 * Services cuando el backend corre con IntegrationMode=google, o
 * "mock:{correo}:{nombre}" cuando corre en modo mock (ver MockAuthProvider).
 * El backend decide si el usuario existe y está activo — este cliente nunca
 * asume que el login es válido solo porque Google lo aceptó.
 */
export async function iniciarSesion(tokenExterno: string): Promise<{ token: string; perfil: Perfil }> {
  const respuesta = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: tokenExterno }),
  });

  if (!respuesta.ok) {
    const cuerpo = await respuesta.json().catch(() => null);
    throw new ErrorDeAutenticacion(cuerpo?.error ?? "No fue posible iniciar sesión.");
  }

  return respuesta.json();
}

export async function obtenerPerfil(token: string): Promise<Perfil | null> {
  const respuesta = await fetch(`${API_URL}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!respuesta.ok) return null;
  return respuesta.json();
}
