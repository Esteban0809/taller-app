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

export const enlaceSeguimiento = (token) => `${window.location.origin}/s/${token}`;

// wa.me necesita el número con prefijo de país y sin símbolos
export function telefonoWhatsApp(telefono) {
  let digitos = (telefono ?? "").replace(/\D/g, "");
  if (digitos.startsWith("00")) digitos = digitos.slice(2);
  if (digitos.length === 9) digitos = `34${digitos}`; // móvil español sin prefijo
  return digitos;
}

export function mensajeWhatsApp(reparacion) {
  const { vehiculo } = reparacion;
  const nombre = vehiculo.cliente.nombre.split(" ")[0];
  const coche = [vehiculo.marca, vehiculo.modelo].filter(Boolean).join(" ") || vehiculo.matricula;
  const enlace = enlaceSeguimiento(reparacion.token_seguimiento);
  const pendienteAprobar = reparacion.presupuesto > 0 && !reparacion.presupuesto_aprobado_at;

  const textos = {
    recibido: `Hola ${nombre}, hemos recibido tu ${coche}. Puedes seguir la reparación aquí: ${enlace}`,
    diagnostico: `Hola ${nombre}, estamos revisando tu ${coche}. Te avisamos en cuanto sepamos qué tiene: ${enlace}`,
    esperando_piezas: `Hola ${nombre}, estamos esperando las piezas para tu ${coche}. Síguelo aquí: ${enlace}`,
    en_reparacion: `Hola ${nombre}, ya estamos reparando tu ${coche}. Síguelo aquí: ${enlace}`,
    listo: `¡Hola ${nombre}! Tu ${coche} ya está listo para recoger 🚗✅ ${enlace}`,
    entregado: `Gracias por confiar en nosotros, ${nombre}. ¡Buen viaje!`,
  };

  const texto = pendienteAprobar && ["diagnostico", "esperando_piezas"].includes(reparacion.estado)
    ? `Hola ${nombre}, ya tenemos el presupuesto de tu ${coche}: ${euros(reparacion.presupuesto)}. Puedes verlo y aprobarlo aquí: ${enlace}`
    : textos[reparacion.estado];

  return `https://wa.me/${telefonoWhatsApp(vehiculo.cliente.telefono)}?text=${encodeURIComponent(texto)}`;
}
