import { useCallback, useEffect, useState } from "react";

import { api } from "../api.js";
import { Aviso, Cargando, Matricula } from "../components/Comunes.jsx";
import { ESTADOS, euros, fecha } from "../utilidades.js";

const RECARGA_MS = 30000;

// Página pública que abre el cliente desde el enlace de WhatsApp. Sin login.
// Se pinta fuera de <Routes> (no pasa por el login), así que recibe el token por props
export default function Seguimiento({ token }) {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState("");
  const [aprobando, setAprobando] = useState(false);

  const cargar = useCallback(async () => {
    try {
      setDatos(await api(`/seguimiento/${token}`, { publica: true }));
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }, [token]);

  useEffect(() => {
    cargar();
    const intervalo = setInterval(cargar, RECARGA_MS);
    return () => clearInterval(intervalo);
  }, [cargar]);

  async function aprobar() {
    if (!window.confirm(`¿Apruebas el presupuesto de ${euros(datos.presupuesto)}?`)) return;
    setAprobando(true);
    try {
      setDatos(await api(`/seguimiento/${token}/aprobar`, { metodo: "POST", publica: true }));
    } catch (err) {
      setError(err.message);
    } finally {
      setAprobando(false);
    }
  }

  if (!datos) {
    return (
      <div className="seguimiento">
        {error ? <Aviso mensaje={error} /> : <Cargando />}
      </div>
    );
  }

  const actual = ESTADOS.findIndex((e) => e.valor === datos.estado);
  const terminada = ["listo", "entregado"].includes(datos.estado);
  const puedeAprobar = datos.presupuesto > 0 && !datos.presupuesto_aprobado_at && !terminada;

  return (
    <div className="seguimiento">
      <p className="seguimiento-taller">{datos.taller_nombre}</p>
      <p className="nota">Hola {datos.cliente_nombre} 👋</p>

      <div className={`seguimiento-estado fondo-${datos.estado}`}>
        <span>Tu vehículo está</span>
        <strong>{ESTADOS[actual]?.texto ?? datos.estado}</strong>
      </div>

      <div className="ficha-mini">
        <Matricula valor={datos.matricula} grande />
        <p>
          <strong>{datos.vehiculo || "Vehículo"}</strong>
          <br />
          <small>Entrada: {fecha(datos.fecha_entrada)}</small>
        </p>
      </div>

      {datos.presupuesto > 0 && (
        <section className="caja seguimiento-presupuesto">
          <h3>Presupuesto</h3>
          <p className="seguimiento-importe">{euros(datos.presupuesto)}</p>
          <p className="nota">{datos.descripcion}</p>
          {puedeAprobar && (
            <button className="boton boton-principal" onClick={aprobar} disabled={aprobando}>
              {aprobando ? "Aprobando…" : "✅ Aprobar presupuesto"}
            </button>
          )}
          {datos.presupuesto_aprobado_at && (
            <Aviso tipo="exito" mensaje={`Aprobado el ${fecha(datos.presupuesto_aprobado_at)}. ¡Gracias!`} />
          )}
        </section>
      )}

      <Aviso mensaje={error} />

      <ol className="seguimiento-pasos">
        {ESTADOS.map((e, i) => (
          <li key={e.valor} className={i < actual ? "hecho" : i === actual ? "actual" : ""}>
            {e.texto}
          </li>
        ))}
      </ol>

      {datos.taller_telefono && (
        <a className="boton boton-secundario" href={`tel:${datos.taller_telefono}`}>
          📞 Llamar al taller
        </a>
      )}
    </div>
  );
}
