import { createContext, useCallback, useContext, useEffect, useState } from "react";

import { api, guardarToken, tokenGuardado } from "./api.js";

const ContextoAuth = createContext(null);

export function ProveedorAuth({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [cargando, setCargando] = useState(true);

  const cargarUsuario = useCallback(async () => {
    if (!tokenGuardado()) {
      setUsuario(null);
      setCargando(false);
      return;
    }

    try {
      setUsuario(await api("/auth/me"));
    } catch {
      guardarToken(null);
      setUsuario(null);
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    cargarUsuario();

    const alCaducar = () => setUsuario(null);
    window.addEventListener("sesion-caducada", alCaducar);
    return () => window.removeEventListener("sesion-caducada", alCaducar);
  }, [cargarUsuario]);

  async function entrar(token) {
    guardarToken(token);
    await cargarUsuario();
  }

  function salir() {
    guardarToken(null);
    setUsuario(null);
  }

  return (
    <ContextoAuth.Provider value={{ usuario, cargando, entrar, salir }}>
      {children}
    </ContextoAuth.Provider>
  );
}

export const useAuth = () => useContext(ContextoAuth);
