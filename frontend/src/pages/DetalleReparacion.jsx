import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api } from "../api.js";
import { useAuth } from "../auth.jsx";
import { Aviso, Cargando, EtiquetaEstado, Matricula } from "../components/Comunes.jsx";
import { ESTADOS, euros, fecha, limpiar } from "../utilidades.js";

export default function DetalleReparacion() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { usuario } = useAuth();

  const [reparacion, setReparacion] = useState(null);
  const [datos, setDatos] = useState({ descripcion: "", presupuesto: "", precio_final: "" });
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  function rellenar(r) {
    setReparacion(r);
    setDatos({
      descripcion: r.descripcion,
      presupuesto: r.presupuesto ?? "",
      precio_final: r.precio_final ?? "",
    });
  }

  useEffect(() => {
    api(`/reparaciones/${id}`).then(rellenar).catch((err) => setError(err.message));
  }, [id]);

  async function cambiarEstado(estado) {
    setError("");
    try {
      rellenar(await api(`/reparaciones/${id}/estado`, { metodo: "PATCH", datos: { estado } }));
    } catch (err) {
      setError(err.message);
    }
  }

  async function guardar(e) {
    e.preventDefault();
    setError("");
    setMensaje("");
    try {
      rellenar(await api(`/reparaciones/${id}`, {
        metodo: "PATCH",
        datos: limpiar(datos, ["presupuesto", "precio_final"]),
      }));
      setMensaje("Cambios guardados");
    } catch (err) {
      setError(err.message);
    }
  }

  async function eliminar() {
    if (!window.confirm("¿Eliminar esta reparación? No se puede deshacer.")) return;
    try {
      await api(`/reparaciones/${id}`, { metodo: "DELETE" });
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  if (!reparacion) return error ? <Aviso mensaje={error} /> : <Cargando />;

  const { vehiculo } = reparacion;

  return (
    <div className="pagina">
      <Link to="/" className="volver">← Taller</Link>

      <div className="ficha-mini">
        <Link to={`/vehiculos/${vehiculo.id}`}><Matricula valor={vehiculo.matricula} grande /></Link>
        <p>
          <strong>{[vehiculo.marca, vehiculo.modelo].filter(Boolean).join(" ") || "Vehículo"}</strong>
          <br />
          <Link to={`/clientes/${vehiculo.cliente.id}`}>{vehiculo.cliente.nombre}</Link>
          {vehiculo.cliente.telefono && <> · <a href={`tel:${vehiculo.cliente.telefono}`}>{vehiculo.cliente.telefono}</a></>}
        </p>
      </div>

      <p className="nota">
        Entrada: {fecha(reparacion.fecha_entrada)}
        {reparacion.kilometros_entrada != null && ` · ${reparacion.kilometros_entrada.toLocaleString("es-ES")} km`}
        {reparacion.fecha_entrega && ` · Entregado: ${fecha(reparacion.fecha_entrega)}`}
      </p>

      <h3>Estado <EtiquetaEstado estado={reparacion.estado} /></h3>
      <div className="selector-estados">
        {ESTADOS.map((e) => (
          <button
            key={e.valor}
            className={`fondo-${e.valor} ${reparacion.estado === e.valor ? "actual" : ""}`}
            onClick={() => cambiarEstado(e.valor)}
            disabled={reparacion.estado === e.valor}
          >
            {e.texto}
          </button>
        ))}
      </div>

      <form onSubmit={guardar} className="formulario">
        <label>
          Trabajo
          <textarea
            rows={4}
            value={datos.descripcion}
            onChange={(e) => setDatos({ ...datos, descripcion: e.target.value })}
            required
            minLength={3}
          />
        </label>
        <div className="fila">
          <label>
            Presupuesto (€)
            <input type="number" min="0" step="0.01" value={datos.presupuesto} onChange={(e) => setDatos({ ...datos, presupuesto: e.target.value })} />
          </label>
          <label>
            Precio final (€)
            <input type="number" min="0" step="0.01" value={datos.precio_final} onChange={(e) => setDatos({ ...datos, precio_final: e.target.value })} placeholder={euros(datos.presupuesto)} />
          </label>
        </div>

        <Aviso mensaje={error} />
        <Aviso mensaje={mensaje} tipo="exito" />
        <button className="boton boton-principal">Guardar cambios</button>
      </form>

      {usuario.rol === "propietario" && (
        <button className="boton boton-peligro" onClick={eliminar}>Eliminar reparación</button>
      )}
    </div>
  );
}
