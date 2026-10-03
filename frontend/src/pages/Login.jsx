import { useState } from "react";

import { api } from "../api.js";
import { useAuth } from "../auth.jsx";
import { Aviso } from "../components/Comunes.jsx";

export default function Login() {
  const { entrar } = useAuth();
  const [modo, setModo] = useState("login");
  const [datos, setDatos] = useState({ taller_nombre: "", nombre: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  const cambiar = (e) => setDatos({ ...datos, [e.target.name]: e.target.value });

  async function enviar(e) {
    e.preventDefault();
    setError("");
    setEnviando(true);

    try {
      const respuesta = modo === "login"
        ? await api("/auth/login", { metodo: "POST", publica: true, datos: { email: datos.email, password: datos.password } })
        : await api("/auth/registro", { metodo: "POST", publica: true, datos });
      await entrar(respuesta.access_token);
    } catch (err) {
      setError(err.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="login">
      <div className="login-caja">
        <h1>🔧 Taller App</h1>
        <p className="login-lema">Tu taller, en el bolsillo.</p>

        <div className="pestanas">
          <button className={modo === "login" ? "activa" : ""} onClick={() => setModo("login")}>
            Entrar
          </button>
          <button className={modo === "registro" ? "activa" : ""} onClick={() => setModo("registro")}>
            Registrar taller
          </button>
        </div>

        <form onSubmit={enviar} className="formulario">
          {modo === "registro" && (
            <>
              <label>
                Nombre del taller
                <input name="taller_nombre" value={datos.taller_nombre} onChange={cambiar} required minLength={2} />
              </label>
              <label>
                Tu nombre
                <input name="nombre" value={datos.nombre} onChange={cambiar} required minLength={2} />
              </label>
            </>
          )}
          <label>
            Email
            <input name="email" type="email" value={datos.email} onChange={cambiar} required autoComplete="email" />
          </label>
          <label>
            Contraseña
            <input
              name="password"
              type="password"
              value={datos.password}
              onChange={cambiar}
              required
              minLength={modo === "registro" ? 8 : undefined}
              autoComplete={modo === "login" ? "current-password" : "new-password"}
            />
          </label>

          <Aviso mensaje={error} />

          <button className="boton boton-principal" disabled={enviando}>
            {enviando ? "Un momento…" : modo === "login" ? "Entrar" : "Crear mi taller"}
          </button>
        </form>
      </div>
    </div>
  );
}
