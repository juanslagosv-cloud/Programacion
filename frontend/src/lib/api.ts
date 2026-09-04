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
