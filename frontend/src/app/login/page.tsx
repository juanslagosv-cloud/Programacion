"use client";

import Script from "next/script";
import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { ErrorDeAutenticacion, iniciarSesion } from "@/lib/api";
import { guardarSesion } from "@/lib/session";

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

// Usuarios de ejemplo sembrados por el backend en modo Mock (sección 88,
// DemoDataSeeder) — uno por rol, todos activos. Se usan aquí solo para no
// obligar a escribir un correo de memoria durante el desarrollo; el rol real
// de cada uno vive en el backend (RBAC, sección 8), no se elige a mano.
const USUARIOS_DEMO = [
  { nombre: "Laura Gómez", correo: "laura.gomez@empresa.com", rol: "Solicitante" },
  { nombre: "Andrés Ruiz", correo: "andres.ruiz@empresa.com", rol: "Revisor" },
  { nombre: "Carlos Pérez", correo: "carlos.perez@empresa.com", rol: "Aprobador" },
  { nombre: "Andrea Rojas", correo: "andrea.rojas@empresa.com", rol: "Contabilidad" },
  { nombre: "Diego Sánchez", correo: "diego.sanchez@empresa.com", rol: "Tesorería" },
  { nombre: "Marta Londoño", correo: "marta.londono@empresa.com", rol: "Auditor" },
  { nombre: "Admin Sistema", correo: "admin@empresa.com", rol: "Administrador" },
];

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: { client_id: string; callback: (resp: { credential: string }) => void }) => void;
          renderButton: (parent: HTMLElement, options: Record<string, unknown>) => void;
        };
      };
    };
  }
}

// Pantalla de login (sección 4). Con NEXT_PUBLIC_GOOGLE_CLIENT_ID configurado,
// usa el botón real de Google Identity Services; el id_token que devuelve se
// envía tal cual a POST /api/auth/login (requiere que el backend corra con
// IntegrationMode=google). Sin esa variable, se ofrece iniciar sesión como uno
// de los usuarios de demostración, enviando "mock:{correo}:{nombre}" — formato
// que MockAuthProvider entiende (backend en IntegrationMode=mock, el default).
export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState<string | null>(null);

  const completarLogin = useCallback(
    async (tokenExterno: string, etiqueta: string) => {
      setError(null);
      setCargando(etiqueta);
      try {
        const { token, perfil } = await iniciarSesion(tokenExterno);
        guardarSesion({ token, perfil });
        router.push("/dashboard");
      } catch (e) {
        setError(e instanceof ErrorDeAutenticacion ? e.message : "No fue posible conectar con la API.");
      } finally {
        setCargando(null);
      }
    },
    [router]
  );

  const inicializarGoogle = useCallback(() => {
    if (!GOOGLE_CLIENT_ID || !window.google) return;
    window.google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback: (resp) => void completarLogin(resp.credential, "Google"),
    });
    const contenedor = document.getElementById("boton-google");
    if (contenedor) {
      window.google.accounts.id.renderButton(contenedor, { theme: "outline", size: "large", width: 300 });
    }
  }, [completarLogin]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      {GOOGLE_CLIENT_ID && (
        <Script src="https://accounts.google.com/gsi/client" strategy="afterInteractive" onLoad={inicializarGoogle} />
      )}

      <div className="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-xl font-semibold text-slate-900">Cuentas por Pagar</h1>
        <p className="mt-1 text-sm text-slate-500">
          Sistema de gestión documental, aprobaciones, contabilidad y tesorería.
        </p>

        {error && (
          <div className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
        )}

        {GOOGLE_CLIENT_ID ? (
          <div className="mt-6 flex justify-center" id="boton-google" />
        ) : (
          <div className="mt-6">
            <p className="text-xs font-medium text-slate-600">
              Iniciar sesión como (usuarios de demostración, modo Mock):
            </p>
            <div className="mt-2 space-y-1.5">
              {USUARIOS_DEMO.map((u) => (
                <button
                  key={u.correo}
                  disabled={cargando !== null}
                  onClick={() => completarLogin(`mock:${u.correo}:${u.nombre}`, u.correo)}
                  className="flex w-full items-center justify-between rounded-md border border-slate-200 px-3 py-2 text-left text-sm hover:bg-slate-50 disabled:opacity-50"
                >
                  <span>
                    <span className="font-medium text-slate-800">{u.nombre}</span>{" "}
                    <span className="text-slate-400">· {u.correo}</span>
                  </span>
                  <span className="text-xs text-slate-500">
                    {cargando === u.correo ? "Ingresando…" : u.rol}
                  </span>
                </button>
              ))}
            </div>
            <p className="mt-3 text-center text-xs text-slate-400">
              Login real contra el backend (JWT + RBAC, Fase 3). El botón de
              Google aparece automáticamente al configurar
              NEXT_PUBLIC_GOOGLE_CLIENT_ID.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
