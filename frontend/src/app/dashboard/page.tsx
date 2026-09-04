"use client";

import { useEffect, useState } from "react";
import { obtenerEstadoSistema, type EstadoSistema } from "@/lib/api";
import { accesosRapidosParaRol, comoRolConocido } from "@/lib/roles";
import { obtenerSesion, rolPrincipal, type Sesion } from "@/lib/session";

// Dashboard personalizado por rol (sección 5): "Hola, [Nombre]" + accesos rápidos
// según el rol activo, ahora con datos reales del backend (perfil + permisos
// devueltos por POST /api/auth/login, Fase 3). La tarjeta de estado del sistema
// demuestra la conexión real Frontend -> API (nunca Frontend -> Access/Drive
// directamente, sección 3/61).
export default function DashboardPage() {
  const [sesion, setSesion] = useState<Sesion | null>(null);
  const [estado, setEstado] = useState<EstadoSistema | null | undefined>(undefined);

  useEffect(() => {
    // Igual que en dashboard/layout.tsx: localStorage no existe durante el
    // render de servidor, por lo que la sesión solo puede leerse en un efecto.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setSesion(obtenerSesion());
    obtenerEstadoSistema().then(setEstado);
  }, []);

  if (!sesion) return null;

  const rol = comoRolConocido(rolPrincipal(sesion));

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-semibold text-slate-900">Hola, {sesion.perfil.nombre}</h1>
      <p className="mt-1 text-sm text-slate-500">Rol activo: {rol}</p>

      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {accesosRapidosParaRol(rol).map((acceso) => (
          <div
            key={acceso}
            className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700 shadow-sm"
          >
            {acceso}
          </div>
        ))}
      </div>

      <div className="mt-8 rounded-lg border border-slate-200 bg-white p-4">
        <h2 className="text-sm font-semibold text-slate-900">Permisos otorgados por el backend</h2>
        <p className="mt-1 text-xs text-slate-400">
          Verificados de nuevo en cada endpoint (sección 3/81) — este listado es
          solo informativo, no la fuente de la autorización.
        </p>
        <div className="mt-2 flex flex-wrap gap-1.5">
          {sesion.perfil.permisos.map((p) => (
            <span key={p} className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
              {p}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-4 rounded-lg border border-slate-200 bg-white p-4">
        <h2 className="text-sm font-semibold text-slate-900">Estado de la API</h2>
        {estado === undefined && <p className="mt-1 text-sm text-slate-500">Consultando…</p>}
        {estado === null && (
          <p className="mt-1 text-sm text-red-600">
            No se pudo conectar con el backend. Verifique que la API esté corriendo
            (ver backend/src/CuentasPorPagar.Api) y NEXT_PUBLIC_API_URL.
          </p>
        )}
        {estado && (
          <dl className="mt-2 grid grid-cols-3 gap-2 text-sm">
            <div>
              <dt className="text-slate-400">Proveedor de datos</dt>
              <dd className="font-medium text-slate-800">{estado.dataProvider}</dd>
            </div>
            <div>
              <dt className="text-slate-400">Modo de integración</dt>
              <dd className="font-medium text-slate-800">{estado.integrationMode}</dd>
            </div>
            <div>
              <dt className="text-slate-400">Ambiente</dt>
              <dd className="font-medium text-slate-800">{estado.ambiente}</dd>
            </div>
          </dl>
        )}
      </div>
    </div>
  );
}
