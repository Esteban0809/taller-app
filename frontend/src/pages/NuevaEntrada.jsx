import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { api } from "../api.js";
import { Aviso, Matricula } from "../components/Comunes.jsx";
import { limpiar, normalizarMatricula } from "../utilidades.js";

export default function NuevaEntrada() {
  const navigate = useNavigate();
  const [parametros] = useSearchParams();

  const [paso, setPaso] = useState("matricula");
  const [matricula, setMatricula] = useState(parametros.get("matricula") ?? "");
  const [vehiculo, setVehiculo] = useState(null);
  const [cliente, setCliente] = useState(null);
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  // Paso 2: datos del coche y del cliente nuevo
  const [datosVehiculo, setDatosVehiculo] = useState({ marca: "", modelo: "", anio: "", kilometros: "" });
  const [tipoCliente, setTipoCliente] = useState("nuevo");
  const [datosCliente, setDatosCliente] = useState({ nombre: "", telefono: "", email: "" });
  const [busqueda, setBusqueda] = useState("");
  const [encontrados, setEncontrados] = useState([]);
  const [clienteElegido, setClienteElegido] = useState(null);

  // Paso 3: la reparación
  const [datosReparacion, setDatosReparacion] = useState({ descripcion: "", presupuesto: "", kilometros_entrada: "" });

  useEffect(() => {
    if (tipoCliente !== "existente" || busqueda.length < 2) {
      setEncontrados([]);
      return;
    }
    const temporizador = setTimeout(async () => {
      try {
        setEncontrados(await api(`/clientes?buscar=${encodeURIComponent(busqueda)}&limite=8`));
      } catch (err) {
        setError(err.message);
      }
    }, 250);
    return () => clearTimeout(temporizador);
  }, [busqueda, tipoCliente]);

  async function buscarMatricula(e) {
    e.preventDefault();
    setError("");
    const buscada = normalizarMatricula(matricula);
    setMatricula(buscada);

    try {
      const coincidencias = await api(`/vehiculos?matricula=${encodeURIComponent(buscada)}`);
      const exacto = coincidencias.find((v) => v.matricula === buscada);

      if (exacto) {
        setVehiculo(exacto);
        setCliente(await api(`/clientes/${exacto.cliente_id}`));
        setDatosReparacion((d) => ({ ...d, kilometros_entrada: exacto.kilometros ?? "" }));
        setPaso("reparacion");
      } else {
        setPaso("vehiculo");
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function crearVehiculo(e) {
    e.preventDefault();
    setError("");
    setEnviando(true);

    try {
      let duenio = clienteElegido;
      if (tipoCliente === "nuevo") {
        duenio = await api("/clientes", { metodo: "POST", datos: limpiar(datosCliente) });
      }
      if (!duenio) throw new Error("Elige un cliente de la lista");

      const nuevo = await api("/vehiculos", {
        metodo: "POST",
        datos: {
          cliente_id: duenio.id,
          matricula,
          ...limpiar(datosVehiculo, ["anio", "kilometros"]),
        },
      });

      setVehiculo(nuevo);
      setCliente(duenio);
      setDatosReparacion((d) => ({ ...d, kilometros_entrada: nuevo.kilometros ?? "" }));
      setPaso("reparacion");
    } catch (err) {
      setError(err.message);
    } finally {
      setEnviando(false);
    }
  }

  async function crearReparacion(e) {
    e.preventDefault();
    setError("");
    setEnviando(true);

    try {
      await api("/reparaciones", {
        metodo: "POST",
        datos: {
          vehiculo_id: vehiculo.id,
          ...limpiar(datosReparacion, ["presupuesto", "kilometros_entrada"]),
        },
      });
      navigate("/");
    } catch (err) {
      setError(err.message);
      setEnviando(false);
    }
  }

  const cambiarEn = (setter) => (e) => setter((d) => ({ ...d, [e.target.name]: e.target.value }));

  return (
    <div className="pagina">
      <h2>Nueva entrada</h2>

      {paso === "matricula" && (
        <form onSubmit={buscarMatricula} className="formulario">
          <label>
            Matrícula
            <input
              className="input-matricula"
              value={matricula}
              onChange={(e) => setMatricula(e.target.value.toUpperCase())}
              placeholder="1234ABC"
              required
              minLength={4}
              autoFocus
            />
          </label>
          <Aviso mensaje={error} />
          <button className="boton boton-principal">Buscar</button>
        </form>
      )}

      {paso === "vehiculo" && (
        <form onSubmit={crearVehiculo} className="formulario">
          <p className="nota">
            <Matricula valor={matricula} /> no está registrado. Añádelo:
          </p>

          <fieldset>
            <legend>Vehículo</legend>
            <div className="fila">
              <label>Marca<input name="marca" value={datosVehiculo.marca} onChange={cambiarEn(setDatosVehiculo)} /></label>
              <label>Modelo<input name="modelo" value={datosVehiculo.modelo} onChange={cambiarEn(setDatosVehiculo)} /></label>
            </div>
            <div className="fila">
              <label>Año<input name="anio" type="number" min="1900" max="2100" value={datosVehiculo.anio} onChange={cambiarEn(setDatosVehiculo)} /></label>
              <label>Kilómetros<input name="kilometros" type="number" min="0" value={datosVehiculo.kilometros} onChange={cambiarEn(setDatosVehiculo)} /></label>
            </div>
          </fieldset>

          <fieldset>
            <legend>Cliente</legend>
            <div className="pestanas pestanas-pequenas">
              <button type="button" className={tipoCliente === "nuevo" ? "activa" : ""} onClick={() => setTipoCliente("nuevo")}>
                Cliente nuevo
              </button>
              <button type="button" className={tipoCliente === "existente" ? "activa" : ""} onClick={() => setTipoCliente("existente")}>
                Ya es cliente
              </button>
            </div>

            {tipoCliente === "nuevo" ? (
              <>
                <label>Nombre<input name="nombre" value={datosCliente.nombre} onChange={cambiarEn(setDatosCliente)} required minLength={2} /></label>
                <div className="fila">
                  <label>Teléfono<input name="telefono" type="tel" value={datosCliente.telefono} onChange={cambiarEn(setDatosCliente)} /></label>
                  <label>Email<input name="email" type="email" value={datosCliente.email} onChange={cambiarEn(setDatosCliente)} /></label>
                </div>
              </>
            ) : (
              <>
                <label>
                  Buscar cliente
                  <input value={busqueda} onChange={(e) => { setBusqueda(e.target.value); setClienteElegido(null); }} placeholder="Nombre o teléfono" />
                </label>
                <ul className="lista-simple">
                  {encontrados.map((c) => (
                    <li key={c.id}>
                      <button
                        type="button"
                        className={clienteElegido?.id === c.id ? "elegido" : ""}
                        onClick={() => setClienteElegido(c)}
                      >
                        {c.nombre} {c.telefono && <small>· {c.telefono}</small>}
                      </button>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </fieldset>

          <Aviso mensaje={error} />
          <div className="fila-botones">
            <button type="button" className="boton boton-secundario" onClick={() => setPaso("matricula")}>Atrás</button>
            <button className="boton boton-principal" disabled={enviando}>Continuar</button>
          </div>
        </form>
      )}

      {paso === "reparacion" && (
        <form onSubmit={crearReparacion} className="formulario">
          <div className="ficha-mini">
            <Matricula valor={vehiculo.matricula} grande />
            <p>
              <strong>{[vehiculo.marca, vehiculo.modelo].filter(Boolean).join(" ") || "Vehículo"}</strong>
              <br />
              {cliente?.nombre} {cliente?.telefono && `· ${cliente.telefono}`}
            </p>
          </div>

          <label>
            ¿Qué le pasa?
            <textarea
              name="descripcion"
              rows={4}
              value={datosReparacion.descripcion}
              onChange={cambiarEn(setDatosReparacion)}
              placeholder="Ej.: ruido al frenar, cambio de aceite y filtros…"
              required
              minLength={3}
              autoFocus
            />
          </label>
          <div className="fila">
            <label>Presupuesto (€)<input name="presupuesto" type="number" min="0" step="0.01" value={datosReparacion.presupuesto} onChange={cambiarEn(setDatosReparacion)} /></label>
            <label>Km a la entrada<input name="kilometros_entrada" type="number" min="0" value={datosReparacion.kilometros_entrada} onChange={cambiarEn(setDatosReparacion)} /></label>
          </div>

          <Aviso mensaje={error} />
          <button className="boton boton-principal" disabled={enviando}>
            {enviando ? "Guardando…" : "Registrar entrada"}
          </button>
        </form>
      )}
    </div>
  );
}
