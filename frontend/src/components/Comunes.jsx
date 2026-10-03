import { textoEstado } from "../utilidades.js";

export function Matricula({ valor, grande = false }) {
  return (
    <span className={`matricula ${grande ? "matricula-grande" : ""}`}>
      <span className="matricula-pais">E</span>
      {valor}
    </span>
  );
}

export function EtiquetaEstado({ estado }) {
  return <span className={`estado estado-${estado}`}>{textoEstado(estado)}</span>;
}

export function Aviso({ mensaje, tipo = "error" }) {
  if (!mensaje) return null;
  return <div className={`aviso aviso-${tipo}`} role="alert">{mensaje}</div>;
}

export function Cargando() {
  return <p className="cargando">Cargando…</p>;
}
