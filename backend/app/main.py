from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import turno, carga, venta  # noqa: F401 - necesario para create_all
from app.routers import upload, estadisticas, cargas, filtros, turnos, ventas, auth
from app.middleware.auth import auth_middleware

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dashboard Franquicia API",
    description="API para gestión y análisis de turnos de atención",
    version="1.0.0",
)

app.middleware("http")(auth_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(upload.router, prefix="/api", tags=["Carga de Excel"])
app.include_router(estadisticas.router, prefix="/api/stats", tags=["Estadísticas"])
app.include_router(cargas.router, prefix="/api/cargas", tags=["Historial de Cargas"])
app.include_router(filtros.router, prefix="/api/filtros", tags=["Filtros"])
app.include_router(turnos.router, prefix="/api/turnos", tags=["Turnos"])
app.include_router(ventas.router, prefix="/api/ventas", tags=["Ventas"])


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "mensaje": "Dashboard Franquicia API funcionando"}
