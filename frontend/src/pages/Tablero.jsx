import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api.js";
import { Aviso, Cargando, EtiquetaEstado, Matricula } from "../components/Comunes.jsx";
import { ESTADOS, euros, siguienteEstado } from "../utilidades.js";

const ESTADOS_ACTIVOS = ESTADOS.filter((e) => e.valor !== "entregado");

export default function Tablero() {
  const [reparaciones, setReparaciones] = useState(null);
  const [resumen, setResumen] = useState(null);
  const [filtro, setFiltro] = useState("todos");
  const [error, setError] = useState("");
  const [avanzando, setAvanzando] = useState(null);

  const cargar = useCallback(async () => {
    try {
      const [lista, datosResumen] = await Promise.all([
        api("/reparaciones?activas=true&limite=200"),
        api("/reparaciones/resumen"),
      ]);
      setReparaciones(lista);
      setResumen(datosResumen);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    cargar();
  }, [cargar]);

  async function avanzar(reparacion) {
    const siguiente = siguienteEstado(reparacion.estado);
    if (!siguiente) return;

    setAvanzando(reparacion.id);
    try {
      await api(`/reparaciones/${reparacion.id}/estado`, {
        metodo: "PATCH",
        datos: { estado: siguiente.valor },
      });
      await cargar();
    } catch (err) {
      setError(err.message);
    } finally {
      setAvanzando(null);
    }
  }

  if (!reparaciones) return error ? <Aviso mensaje={error} /> : <Cargando />;

  const visibles = filtro === "todos"
    ? reparaciones
    : reparaciones.filter((r) => r.estado === filtro);

  return (
    <>
      <section className="resumen">
        <div className="tarjeta-dato">
          <span className="dato-numero">{resumen.en_taller}</span>
          <span className="dato-texto">En el taller</span>
        </div>
        <div className="tarjeta-dato dato-listo">
          <span className="dato-numero">{resumen.por_estado.listo}</span>
          <span className="dato-texto">Listos para entregar</span>
        </div>
        <div className="tarjeta-dato">
          <span className="dato-numero dato-dinero">{euros(resumen.facturado)}</span>
          <span className="dato-texto">Facturado</span>
        </div>
      </section>

      <div className="filtros">
        <button className={filtro === "todos" ? "activo" : ""} onClick={() => setFiltro("todos")}>
          Todos <span>{reparaciones.length}</span>
        </button>
        {ESTADOS_ACTIVOS.map((estado) => (
          <button
            key={estado.valor}
            className={filtro === estado.valor ? "activo" : ""}
            onClick={() => setFiltro(estado.valor)}
          >
            {estado.texto} <span>{resumen.por_estado[estado.valor]}</span>
          </button>
        ))}
      </div>

      <Aviso mensaje={error} />

      {visibles.length === 0 ? (
        <div className="vacio">
          <p>No hay coches {filtro === "todos" ? "en el taller" : "en este estado"}.</p>
          <Link to="/entrada" className="boton boton-principal">＋ Registrar entrada</Link>
        </div>
      ) : (
        <ul className="lista-reparaciones">
          {visibles.map((r) => {
            const siguiente = siguienteEstado(r.estado);
            return (
              <li key={r.id} className={`tarjeta-reparacion borde-${r.estado}`}>
                <Link to={`/reparaciones/${r.id}`} className="tarjeta-enlace">
                  <div className="tarjeta-cabecera">
                    <Matricula valor={r.vehiculo.matricula} />
                    <EtiquetaEstado estado={r.estado} />
                  </div>
                  <p className="tarjeta-coche">
                    {[r.vehiculo.marca, r.vehiculo.modelo].filter(Boolean).join(" ") || "Vehículo"}
                    {" · "}
                    {r.vehiculo.cliente.nombre}
                  </p>
                  <p className="tarjeta-descripcion">{r.descripcion}</p>
                  <p className="tarjeta-precio">Presupuesto: {euros(r.presupuesto)}</p>
                </Link>

                <div className="tarjeta-acciones">
                  {r.vehiculo.cliente.telefono && (
                    <a className="boton boton-secundario" href={`tel:${r.vehiculo.cliente.telefono}`}>
                      📞 Llamar
                    </a>
                  )}
                  {siguiente && (
                    <button
                      className={`boton boton-avanzar fondo-${siguiente.valor}`}
                      onClick={() => avanzar(r)}
                      disabled={avanzando === r.id}
                    >
                      {avanzando === r.id ? "…" : siguiente.valor === "entregado" ? "✓ Entregar" : `→ ${siguiente.texto}`}
                    </button>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}
