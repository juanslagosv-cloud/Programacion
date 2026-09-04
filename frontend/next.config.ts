import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Next dev solo permite por defecto recursos HMR desde "localhost"; sin esto,
  // acceder por 127.0.0.1 (u otro host) bloquea silenciosamente la hidratación
  // de React en desarrollo (sin error visible en el navegador).
  allowedDevOrigins: ["localhost", "127.0.0.1"],
};

export default nextConfig;
