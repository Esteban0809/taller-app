import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api.js";
import { Aviso } from "../components/Comunes.jsx";
import { limpiar } from "../utilidades.js";

export default function Clientes() {
  const [clientes, setClientes] = useState([]);
  const [buscar, setBuscar] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [nuevo, setNuevo] = useState({ nombre: "", telefono: "", email: "", notas: "" });
  const [error, setError] = useState("");

  useEffect(() => {
    const temporizador = setTimeout(async () => {
      try {
        const consulta = buscar ? `?buscar=${encodeURIComponent(buscar)}&limite=200` : "?limite=200";
        setClientes(await api(`/clientes${consulta}`));
      } catch (err) {
        setError(err.message);
      }
    }, 250);
    return () => clearTimeout(temporizador);
  }, [buscar]);

  async function crear(e) {
    e.preventDefault();
    setError("");
    try {
      const creado = await api("/clientes", { metodo: "POST", datos: limpiar(nuevo) });
      setClientes([creado, ...clientes]);
      setNuevo({ nombre: "", telefono: "", email: "", notas: "" });
      setMostrarFormulario(false);
    } catch (err) {
      setError(err.message);
    }
  }

  const cambiar = (e) => setNuevo({ ...nuevo, [e.target.name]: e.target.value });

  return (
    <div className="pagina">
      <div className="titulo-con-boton">
        <h2>Clientes</h2>
        <button className="boton boton-secundario" onClick={() => setMostrarFormulario(!mostrarFormulario)}>
          {mostrarFormulario ? "Cancelar" : "＋ Nuevo"}
        </button>
      </div>

      {mostrarFormulario && (
        <form onSubmit={crear} className="formulario caja">
          <label>Nombre<input name="nombre" value={nuevo.nombre} onChange={cambiar} required minLength={2} autoFocus /></label>
          <div className="fila">
            <label>Teléfono<input name="telefono" type="tel" value={nuevo.telefono} onChange={cambiar} /></label>
            <label>Email<input name="email" type="email" value={nuevo.email} onChange={cambiar} /></label>
          </div>
          <label>Notas<textarea name="notas" rows={2} value={nuevo.notas} onChange={cambiar} /></label>
          <button className="boton boton-principal">Guardar cliente</button>
        </form>
      )}

      <input
        className="buscador"
        value={buscar}
        onChange={(e) => setBuscar(e.target.value)}
        placeholder="🔍 Buscar por nombre, teléfono o email"
      />

      <Aviso mensaje={error} />

      <ul className="lista-simple">
        {clientes.map((c) => (
          <li key={c.id}>
            <Link to={`/clientes/${c.id}`} className="fila-historial">
              <span><strong>{c.nombre}</strong><br /><small>{c.telefono || c.email || "Sin contacto"}</small></span>
              <span className="derecha">›</span>
            </Link>
          </li>
        ))}
      </ul>
      {clientes.length === 0 && <p className="nota">No hay clientes{buscar && " con esa búsqueda"}.</p>}
    </div>
  );
}
