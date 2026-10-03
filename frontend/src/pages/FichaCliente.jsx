import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api } from "../api.js";
import { Aviso, Cargando, Matricula } from "../components/Comunes.jsx";
import { limpiar } from "../utilidades.js";

export default function FichaCliente() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [cliente, setCliente] = useState(null);
  const [datos, setDatos] = useState({});
  const [vehiculos, setVehiculos] = useState([]);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  useEffect(() => {
    Promise.all([api(`/clientes/${id}`), api(`/vehiculos?cliente_id=${id}`)])
      .then(([c, v]) => {
        setCliente(c);
        setDatos({ nombre: c.nombre, telefono: c.telefono ?? "", email: c.email ?? "", notas: c.notas ?? "" });
        setVehiculos(v);
      })
      .catch((err) => setError(err.message));
  }, [id]);

  async function guardar(e) {
    e.preventDefault();
    setError("");
    setMensaje("");
    try {
      setCliente(await api(`/clientes/${id}`, { metodo: "PATCH", datos: limpiar(datos) }));
      setMensaje("Cliente actualizado");
    } catch (err) {
      setError(err.message);
    }
  }

  async function eliminar() {
    if (!window.confirm(`¿Eliminar a ${cliente.nombre}?`)) return;
    try {
      await api(`/clientes/${id}`, { metodo: "DELETE" });
      navigate("/clientes");
    } catch (err) {
      setError(err.message);
    }
  }

  if (!cliente) return error ? <Aviso mensaje={error} /> : <Cargando />;

  const cambiar = (e) => setDatos({ ...datos, [e.target.name]: e.target.value });

  return (
    <div className="pagina">
      <Link to="/clientes" className="volver">← Clientes</Link>
      <h2>{cliente.nombre}</h2>
      {cliente.telefono && <a className="boton boton-secundario" href={`tel:${cliente.telefono}`}>📞 Llamar a {cliente.telefono}</a>}

      <h3>Vehículos</h3>
      {vehiculos.length === 0 ? (
        <p className="nota">Sin vehículos. Regístralo desde <Link to="/entrada">＋ Entrada</Link>.</p>
      ) : (
        <ul className="lista-simple">
          {vehiculos.map((v) => (
            <li key={v.id}>
              <Link to={`/vehiculos/${v.id}`} className="fila-historial">
                <span><Matricula valor={v.matricula} /> {[v.marca, v.modelo].filter(Boolean).join(" ")}</span>
                <span className="derecha">›</span>
              </Link>
            </li>
          ))}
        </ul>
      )}

      <h3>Datos</h3>
      <form onSubmit={guardar} className="formulario">
        <label>Nombre<input name="nombre" value={datos.nombre} onChange={cambiar} required minLength={2} /></label>
        <div className="fila">
          <label>Teléfono<input name="telefono" type="tel" value={datos.telefono} onChange={cambiar} /></label>
          <label>Email<input name="email" type="email" value={datos.email} onChange={cambiar} /></label>
        </div>
        <label>Notas<textarea name="notas" rows={2} value={datos.notas} onChange={cambiar} /></label>
        <Aviso mensaje={error} />
        <Aviso mensaje={mensaje} tipo="exito" />
        <button className="boton boton-principal">Guardar</button>
      </form>

      <button className="boton boton-peligro" onClick={eliminar}>Eliminar cliente</button>
    </div>
  );
}
