import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../auth.jsx";

export default function Layout() {
  const { usuario, salir } = useAuth();

  return (
    <div className="app">
      <header className="cabecera">
        <div>
          <strong className="cabecera-taller">🔧 {usuario.taller_nombre}</strong>
          <span className="cabecera-usuario">
            {usuario.nombre} · {usuario.rol === "propietario" ? "Propietario" : "Mecánico"}
          </span>
        </div>
        <button className="boton-texto" onClick={salir}>Salir</button>
      </header>

      <main className="contenido">
        <Outlet />
      </main>

      <nav className="menu">
        <NavLink to="/" end>
          <span aria-hidden="true">🏠</span>Taller
        </NavLink>
        <NavLink to="/entrada" className="menu-principal">
          <span aria-hidden="true">＋</span>Entrada
        </NavLink>
        <NavLink to="/clientes">
          <span aria-hidden="true">👥</span>Clientes
        </NavLink>
        {usuario.rol === "propietario" && (
          <NavLink to="/equipo">
            <span aria-hidden="true">🧑‍🔧</span>Equipo
          </NavLink>
        )}
      </nav>
    </div>
  );
}
