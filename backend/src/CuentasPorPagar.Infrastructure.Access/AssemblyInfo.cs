using System.Runtime.Versioning;

// Declara explícitamente que este ensamblado completo solo se soporta en Windows
// (sección 4/61: conexión OLE DB a Access requiere el Access Database Engine
// Redistributable, disponible únicamente en Windows). Esto hace que el analizador
// de compatibilidad de plataforma (CA1416) deje de advertir sobre el uso de
// System.Data.OleDb dentro de este proyecto, ya que toda la superficie del
// ensamblado queda marcada como Windows-only.
[assembly: SupportedOSPlatform("windows")]
