const BASE = import.meta.env.VITE_API_URL || "/api";
const CLAVE_TOKEN = "taller_token";

export const tokenGuardado = () => localStorage.getItem(CLAVE_TOKEN);

export function guardarToken(token) {
  if (token) localStorage.setItem(CLAVE_TOKEN, token);
  else localStorage.removeItem(CLAVE_TOKEN);
}

export class ErrorApi extends Error {
  constructor(status, mensaje) {
    super(mensaje);
    this.status = status;
  }
}

function mensajeDeError(detalle) {
  if (!detalle) return "Ha ocurrido un error inesperado";
  if (typeof detalle === "string") return detalle;
  if (Array.isArray(detalle)) {
    return detalle.map((e) => `${e.loc?.at(-1) ?? ""}: ${e.msg}`).join(" · ");
  }
  return "Ha ocurrido un error inesperado";
}

// publica: true para login/registro. No envían token y un 401 ahí significa
// "credenciales incorrectas", no "sesión caducada", así que no cierran la sesión.
export async function api(ruta, { metodo = "GET", datos, publica = false } = {}) {
  const cabeceras = { "Content-Type": "application/json" };
  const token = publica ? null : tokenGuardado();
  if (token) cabeceras.Authorization = `Bearer ${token}`;

  let respuesta;
  try {
    respuesta = await fetch(`${BASE}${ruta}`, {
      method: metodo,
      headers: cabeceras,
      body: datos ? JSON.stringify(datos) : undefined,
    });
  } catch {
    throw new ErrorApi(0, "No se puede conectar con el servidor. ¿Está arrancado el backend?");
  }

  if (respuesta.status === 204) return null;

  const cuerpo = await respuesta.json().catch(() => null);

  if (!respuesta.ok) {
    if (respuesta.status === 401 && token) {
      guardarToken(null);
      window.dispatchEvent(new Event("sesion-caducada"));
    }
    throw new ErrorApi(respuesta.status, mensajeDeError(cuerpo?.detail));
  }

  return cuerpo;
}
