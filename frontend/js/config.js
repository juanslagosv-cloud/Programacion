/* Configuración de entorno — Ecodes Talento Humano
 *
 * Normalmente NO hay que tocar este archivo.
 *
 * El sistema se conecta solo a la API en los dos casos habituales:
 *
 *   1. Instalación en el servidor local de la empresa: el mismo programa
 *      sirve las pantallas y la API, así que se usan rutas relativas y
 *      funciona igual desde cualquier computador de la oficina.
 *   2. Desarrollo, abriendo el frontend con Live Server o
 *      "python -m http.server": la API se busca en el puerto 8000.
 *
 * Solo hay que llenar API_EN_PRODUCCION en el tercer caso: cuando las
 * pantallas y la API viven en dominios distintos (por ejemplo, frontend en
 * Vercel y backend en Render). Sin barra "/" al final.
 */

const API_EN_PRODUCCION = "";

// Puertos típicos de un servidor estático de desarrollo.
const PUERTOS_DE_DESARROLLO = ["5500", "5501", "8080", "8096", "8098", "3000"];

window.ECODES_API_BASE = (function () {
  if (API_EN_PRODUCCION) return API_EN_PRODUCCION;

  const puerto = window.location.port;
  if (window.location.protocol === "file:" || PUERTOS_DE_DESARROLLO.includes(puerto)) {
    return "http://localhost:8000";
  }

  // Mismo servidor que entregó esta página: rutas relativas.
  return "";
})();
