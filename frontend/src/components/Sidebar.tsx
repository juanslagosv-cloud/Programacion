"use client";

import Link from "next/link";
import { menuParaRol, type Rol } from "@/lib/roles";

// Menú lateral (sección 78): "los módulos deben aparecer únicamente según
// permisos". El rol viene de la sesión real emitida por el backend tras el
// login (Fase 3); este archivo solo mapea nombre de rol -> secciones a
// mostrar. La autorización real de cada acción se vuelve a validar en el
// backend (PermisoRequeridoAttribute) sin importar lo que muestre este menú.
export default function Sidebar({ rol }: { rol: Rol }) {
  const secciones = menuParaRol(rol);

  return (
    <nav className="flex h-full w-60 flex-col gap-6 overflow-y-auto border-r border-slate-200 bg-white px-4 py-6">
      <div className="px-2 text-sm font-semibold text-slate-900">Cuentas por Pagar</div>
      {secciones.map((seccion) => (
        <div key={seccion.titulo}>
          <div className="px-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
            {seccion.titulo}
          </div>
          <ul className="mt-1 space-y-0.5">
            {seccion.items.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="block rounded-md px-2 py-1.5 text-sm text-slate-700 hover:bg-slate-100"
                >
                  {item.etiqueta}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}
