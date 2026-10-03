# Taller App

Multi-tenant SaaS backend for small car repair shops: customers, vehicles and repair orders, with each workshop seeing only its own data.

## Features

- **Workshop sign-up**: creates the workshop and its owner account in one step
- **JWT authentication** with Argon2 password hashing
- **Roles**: owner (`propietario`) and mechanic (`mecanico`)
- **Customers → vehicles → repairs** with full history per licence plate
- **Repair workflow**: `recibido → diagnostico → esperando_piezas → en_reparacion → listo → entregado`
- **Dashboard summary**: repairs by status, cars currently in the shop, total invoiced
- **Tenant isolation**: every query is scoped by `taller_id`, covered by tests

## Stack

FastAPI · SQLAlchemy 2.0 · Alembic · MySQL · Pydantic v2 · pytest · Docker · GitHub Actions

## Architecture

```
app/
├── routers/       HTTP layer (endpoints)
├── services/      business rules
├── repositories/  database access (always filtered by taller_id)
├── models/        SQLAlchemy models
├── schemas/       Pydantic request/response models
└── core/          security (JWT, hashing) and auth dependencies
```

## Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env          # fill in DB_PASSWORD and JWT_SECRET
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

Interactive API docs: http://localhost:8000/docs

## Tests

```bash
.venv/bin/pytest -q
```

Tests run against an in-memory SQLite database, so no MySQL is needed.

## Run with Docker

```bash
docker compose up --build
docker compose exec api alembic upgrade head
```
