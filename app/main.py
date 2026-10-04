from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, clientes, reparaciones, seguimiento, vehiculos

app = FastAPI(title="Taller App", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(vehiculos.router)
app.include_router(reparaciones.router)
app.include_router(seguimiento.router)


@app.get("/")
def inicio():
    return {
        "app": "Taller App",
        "version": "0.1",
        "status": "online"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
