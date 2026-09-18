/* Configuración de entorno — Ecodes Talento Humano
 *
 * Este es el ÚNICO archivo que hay que tocar para conectar el frontend
 * publicado con el backend publicado.
 *
 * Después de desplegar el backend en Render, copia la URL que te da
 * (algo como https://ecodes-th-api.onrender.com) y pégala abajo en
 * API_EN_PRODUCCION. No pongas una barra "/" al final.
 */

const API_EN_PRODUCCION = "https://ecodes-th-api.onrender.com";

window.ECODES_API_BASE = (function () {
  const host = window.location.hostname;
  // Trabajando en tu computador: el backend corre en el puerto 8000.
  if (host === "localhost" || host === "127.0.0.1" || host === "") {
    return "http://localhost:8000";
  }
  // Publicado (Vercel u otro hosting): el backend vive en otro dominio.
  return API_EN_PRODUCCION;
})();
