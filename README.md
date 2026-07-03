# Dashboard Franquicia

Dashboard estadístico de turnos de atención construido con FastAPI + PostgreSQL + Next.js.

## Requisitos

- Docker y Docker Compose
- Node.js 18+
- Python 3.12+

---

## Levantar el proyecto (modo desarrollo)

### 1. Base de datos con Docker

```bash
docker-compose up -d db
```

Esto levanta PostgreSQL en `localhost:5432`.

### 2. Backend (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend disponible en: http://localhost:8000
Documentación API: http://localhost:8000/docs

### 3. Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Frontend disponible en: http://localhost:3000

---

## Levantar todo con Docker Compose

```bash
docker-compose up --build
```

---

## Estructura del proyecto

```
backend/
  app/
    models/       → Modelos SQLAlchemy (turnos, cargas)
    schemas/      → Schemas Pydantic (validación)
    routers/      → Endpoints FastAPI
    services/     → Lógica de negocio (procesador Excel, estadísticas)
    main.py       → Punto de entrada
    database.py   → Conexión PostgreSQL
    config.py     → Variables de entorno

frontend/
  app/            → Páginas Next.js (dashboard, upload, historial)
  components/     → Componentes reutilizables (gráficas, KPIs, filtros)
  lib/api.ts      → Cliente HTTP hacia el backend
```

## Variables de entorno

### Backend (.env)
```
DATABASE_URL=postgresql://admin:admin123@localhost:5432/dashboard_franquicia
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```
