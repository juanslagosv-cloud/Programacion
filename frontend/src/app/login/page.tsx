"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ROLES, type Rol } from "@/lib/roles";
import { guardarSesion } from "@/lib/session";

// Pantalla de login (sección 4). "Continuar con Google" está simulado: en la
// Fase 3 este botón invocará Google Identity Services, enviará el id_token al
// backend (IAuthProvider) y este validará que el correo exista y esté Activo
// en la tabla Usuarios antes de emitir la sesión — el login de Google por sí
// solo nunca basta. El selector de rol es solo de demostración, porque el RBAC
// real (sección 8) todavía vive en el backend, no en este esqueleto de frontend.
export default function LoginPage() {
  const router = useRouter();
  const [nombre, setNombre] = useState("Laura Gómez");
  const [correo, setCorreo] = useState("laura.gomez@empresa.com");
  const [rol, setRol] = useState<Rol>("Solicitante");

  function continuarConGoogle() {
    guardarSesion({ nombre, correo, rol });
    router.push("/dashboard");
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-xl font-semibold text-slate-900">Cuentas por Pagar</h1>
        <p className="mt-1 text-sm text-slate-500">
          Sistema de gestión documental, aprobaciones, contabilidad y tesorería.
        </p>

        <div className="mt-6 space-y-3">
          <div>
            <label className="block text-xs font-medium text-slate-600">Nombre (demo)</label>
            <input
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600">Correo corporativo (demo)</label>
            <input
              value={correo}
              onChange={(e) => setCorreo(e.target.value)}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600">Rol (solo demostración)</label>
            <select
              value={rol}
              onChange={(e) => setRol(e.target.value as Rol)}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={continuarConGoogle}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-md bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800"
        >
          Continuar con Google
        </button>

        <p className="mt-3 text-center text-xs text-slate-400">
          Login simulado (Fase 1/2). La integración real con Google OAuth llega en la Fase 3.
        </p>
      </div>
    </div>
  );
}
