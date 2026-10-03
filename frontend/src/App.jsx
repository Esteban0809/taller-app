import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "./auth.jsx";
import { Cargando } from "./components/Comunes.jsx";
import Layout from "./components/Layout.jsx";
import Clientes from "./pages/Clientes.jsx";
import DetalleReparacion from "./pages/DetalleReparacion.jsx";
import Equipo from "./pages/Equipo.jsx";
import FichaCliente from "./pages/FichaCliente.jsx";
import FichaVehiculo from "./pages/FichaVehiculo.jsx";
import Login from "./pages/Login.jsx";
import NuevaEntrada from "./pages/NuevaEntrada.jsx";
import Tablero from "./pages/Tablero.jsx";

export default function App() {
  const { usuario, cargando } = useAuth();

  if (cargando) return <Cargando />;
  if (!usuario) return <Login />;

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Tablero />} />
        <Route path="/entrada" element={<NuevaEntrada />} />
        <Route path="/clientes" element={<Clientes />} />
        <Route path="/clientes/:id" element={<FichaCliente />} />
        <Route path="/vehiculos/:id" element={<FichaVehiculo />} />
        <Route path="/reparaciones/:id" element={<DetalleReparacion />} />
        {usuario.rol === "propietario" && <Route path="/equipo" element={<Equipo />} />}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
