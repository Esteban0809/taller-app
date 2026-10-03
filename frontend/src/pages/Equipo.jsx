import { useEffect, useState } from "react";

import { api } from "../api.js";
import { Aviso } from "../components/Comunes.jsx";

export default function Equipo() {
  const [usuarios, setUsuarios] = useState([]);
  const [nuevo, setNuevo] = useState({ nombre: "", email: "", password: "", rol: "mecanico" });
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  useEffect(() => {
    api("/usuarios").then(setUsuarios).catch((err) => setError(err.message));
  }, []);

  async function crear(e) {
    e.preventDefault();
    setError("");
    setMensaje("");
    try {
      const creado = await api("/usuarios", { metodo: "POST", datos: nuevo });
      setUsuarios([...usuarios, creado]);
      setNuevo({ nombre: "", email: "", password: "", rol: "mecanico" });
      setMensaje(`${creado.nombre} ya puede entrar con su email y contraseña`);
    } catch (err) {
      setError(err.message);
    }
  }

  const cambiar = (e) => setNuevo({ ...nuevo, [e.target.name]: e.target.value });

  return (
    <div className="pagina">
      <h2>Equipo</h2>
      <ul className="lista-simple">
        {usuarios.map((u) => (
          <li key={u.id} className="fila-historial">
            <span><strong>{u.nombre}</strong><br /><small>{u.email}</small></span>
            <span className="derecha"><small>{u.rol === "propietario" ? "Propietario" : "Mecánico"}</small></span>
          </li>
        ))}
      </ul>

      <h3>Añadir persona</h3>
      <form onSubmit={crear} className="formulario">
        <label>Nombre<input name="nombre" value={nuevo.nombre} onChange={cambiar} required minLength={2} /></label>
        <label>Email<input name="email" type="email" value={nuevo.email} onChange={cambiar} required autoComplete="off" /></label>
        <label>Contraseña inicial<input name="password" type="password" value={nuevo.password} onChange={cambiar} required minLength={8} autoComplete="new-password" /></label>
        <label>
          Rol
          <select name="rol" value={nuevo.rol} onChange={cambiar}>
            <option value="mecanico">Mecánico</option>
            <option value="propietario">Propietario</option>
          </select>
        </label>
        <Aviso mensaje={error} />
        <Aviso mensaje={mensaje} tipo="exito" />
        <button className="boton boton-principal">Añadir</button>
      </form>
    </div>
  );
}
