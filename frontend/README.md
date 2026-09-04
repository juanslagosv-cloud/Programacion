# Frontend — Cuentas por Pagar

Next.js (App Router) + TypeScript + Tailwind CSS. Esqueleto de la Fase 1
(sección 78/84 de [../docs/00-propuesta-tecnica-funcional.md](../docs/00-propuesta-tecnica-funcional.md)):
login simulado, layout con menú lateral filtrado por rol y verificación de
conectividad con la API.

**El navegador nunca habla con Access, Drive ni Gmail directamente** (sección
3/61): solo consume `backend/` vía `NEXT_PUBLIC_API_URL`.

## Ejecutar

```bash
npm install
cp .env.local.example .env.local   # ajustar NEXT_PUBLIC_API_URL si es necesario
npm run dev
```

Abrir http://localhost:3000 (usar `localhost`, no `127.0.0.1`: Next dev
bloquea por defecto los recursos de desarrollo desde otros orígenes — ver
`allowedDevOrigins` en `next.config.ts`).

## Qué es real y qué es simulado en este esqueleto

- `src/app/login/page.tsx`: **"Continuar con Google" está simulado.** Guarda
  una sesión de demostración en `localStorage` (`src/lib/session.ts`) y
  permite elegir un rol manualmente. En la Fase 3 esto se reemplaza por Google
  Identity Services + el JWT emitido por el backend tras validar el `id_token`.
- `src/lib/roles.ts`: mapa **estático** de menú/dashboard por rol (secciones 5
  y 78). En la Fase 3 la fuente de verdad pasa a ser el backend (RBAC, sección
  8) — nunca confiar solo en este archivo para autorización real.
- `src/lib/api.ts`: cliente HTTP real hacia el backend (`/api/sistema/estado`
  ya está conectado end-to-end).

## Pendiente (fases siguientes)

Formularios de solicitud, bandejas de aprobación/contabilidad/tesorería,
expediente digital, notificaciones y reportes (Fases 5 en adelante).
