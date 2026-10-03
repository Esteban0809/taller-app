export const ESTADOS = [
  { valor: "recibido", texto: "Recibido" },
  { valor: "diagnostico", texto: "Diagnóstico" },
  { valor: "esperando_piezas", texto: "Esperando piezas" },
  { valor: "en_reparacion", texto: "En reparación" },
  { valor: "listo", texto: "Listo" },
  { valor: "entregado", texto: "Entregado" },
];

export const textoEstado = (valor) =>
  ESTADOS.find((e) => e.valor === valor)?.texto ?? valor;

export function siguienteEstado(valor) {
  const indice = ESTADOS.findIndex((e) => e.valor === valor);
  return indice >= 0 && indice < ESTADOS.length - 1 ? ESTADOS[indice + 1] : null;
}

export const euros = (cantidad) =>
  Number(cantidad ?? 0).toLocaleString("es-ES", { style: "currency", currency: "EUR" });

export const fecha = (texto) =>
  texto ? new Date(texto).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" }) : "—";

export const normalizarMatricula = (matricula) =>
  matricula.replace(/[\s-]/g, "").toUpperCase();

// Convierte "" en null y textos numéricos en números antes de enviar a la API
export function limpiar(datos, camposNumericos = []) {
  const resultado = {};
  for (const [campo, valor] of Object.entries(datos)) {
    if (valor === "" || valor === undefined) continue;
    resultado[campo] = camposNumericos.includes(campo) ? Number(valor) : valor;
  }
  return resultado;
}
