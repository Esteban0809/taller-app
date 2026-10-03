import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { api } from "../api.js";
import { Aviso, Cargando, EtiquetaEstado, Matricula } from "../components/Comunes.jsx";
import { euros, fecha } from "../utilidades.js";

export default function FichaVehiculo() {
  const { id } = useParams();
  const [vehiculo, setVehiculo] = useState(null);
  const [cliente, setCliente] = useState(null);
  const [historial, setHistorial] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function cargar() {
      try {
        const v = await api(`/vehiculos/${id}`);
        const [c, h] = await Promise.all([
          api(`/clientes/${v.cliente_id}`),
          api(`/reparaciones?vehiculo_id=${id}&limite=200`),
        ]);
        setVehiculo(v);
        setCliente(c);
        setHistorial(h);
      } catch (err) {
        setError(err.message);
      }
    }
    cargar();
  }, [id]);

  if (!vehiculo) return error ? <Aviso mensaje={error} /> : <Cargando />;

  const totalGastado = historial
    .filter((r) => r.estado === "entregado")
    .reduce((total, r) => total + (r.precio_final ?? 0), 0);

  return (
    <div className="pagina">
      <Link to="/clientes" className="volver">← Clientes</Link>

      <div className="ficha-mini">
        <Matricula valor={vehiculo.matricula} grande />
        <p>
          <strong>{[vehiculo.marca, vehiculo.modelo].filter(Boolean).join(" ") || "Vehículo"}</strong>
          {vehiculo.anio && ` · ${vehiculo.anio}`}
          <br />
          {vehiculo.kilometros != null && `${vehiculo.kilometros.toLocaleString("es-ES")} km · `}
          Dueño: <Link to={`/clientes/${cliente.id}`}>{cliente.nombre}</Link>
        </p>
      </div>

      <Link to={`/entrada?matricula=${vehiculo.matricula}`} className="boton boton-principal">
        ＋ Nueva reparación para este coche
      </Link>

      <h3>Historial · {historial.length} {historial.length === 1 ? "visita" : "visitas"} · {euros(totalGastado)}</h3>
      {historial.length === 0 ? (
        <p className="nota">Todavía no tiene reparaciones.</p>
      ) : (
        <ul className="lista-simple">
          {historial.map((r) => (
            <li key={r.id}>
              <Link to={`/reparaciones/${r.id}`} className="fila-historial">
                <span>
                  <small>{fecha(r.fecha_entrada)}</small>
                  <br />
                  {r.descripcion}
                </span>
                <span className="derecha">
                  <EtiquetaEstado estado={r.estado} />
                  <br />
                  <small>{euros(r.precio_final ?? r.presupuesto)}</small>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
