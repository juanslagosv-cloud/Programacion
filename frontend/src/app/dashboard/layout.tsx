"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import { cerrarSesion, obtenerSesion, type SesionDemo } from "@/lib/session";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [sesion, setSesion] = useState<SesionDemo | null | undefined>(undefined);

  useEffect(() => {
    const actual = obtenerSesion();
    if (!actual) {
      router.replace("/login");
      return;
    }
    // localStorage solo existe en el cliente: la sesión no puede conocerse durante
    // el render de servidor, así que este efecto (no un initializer de useState)
    // evita el desajuste de hidratación entre servidor y cliente.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setSesion(actual);
  }, [router]);

  if (!sesion) return null;

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar rol={sesion.rol} />
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
          <div className="text-sm text-slate-500">
            {sesion.rol} · {sesion.correo}
          </div>
          <button
            onClick={() => {
              cerrarSesion();
              router.replace("/login");
            }}
            className="text-sm text-slate-500 hover:text-slate-900"
          >
            Cerrar sesión
          </button>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
