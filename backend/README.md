# Backend Overview

This directory contains the FastAPI application. It receives browser requests, validates input with DTOs, uses SQLModel sessions to query PostgreSQL, and returns JSON responses to the frontend.

## Directory Responsibilities

| Directory | Responsibility |
| --- | --- |
| `app/` | FastAPI application package and startup wiring. |
| `app/db/` | Database connection, SQLModel table schema, and DTO definitions. |
| `app/routes/` | HTTP endpoints grouped by domain concept. |
| `app/crud/` | Database reads, inserts, and response-shaping helpers. |
| `app/utils/` | Supporting helpers such as seed data and ID validation. |

## Backend Data Flow

The backend follows this request flow:

```text
HTTP request
  -> FastAPI route
  -> DTO validation
  -> CRUD function
  -> SQLModel session
  -> PostgreSQL
  -> SQLModel object
  -> response DTO
  -> JSON response
```

For example, creating a book goes through this path:

```text
POST /api/books
  -> routes/books.py
  -> BookCreate DTO
  -> validate author_id and category_id
  -> crud/books.py
  -> Book table model
  -> PostgreSQL insert
  -> BookRead DTO
  -> JSON response
```

## Main Backend Files

| File | Role |
| --- | --- |
| `app/main.py` | Creates the FastAPI app, registers routers, creates tables on startup, and seeds demo data. |
| `app/db/config.py` | Loads environment values, builds the database URL, creates the SQLModel engine, and provides request sessions. |
| `app/db/schema.py` | Defines database tables and relationships. |
| `app/db/dto.py` | Defines request and response shapes used by API routes. |
| `app/routes/*.py` | Defines API endpoints and HTTP-level validation. |
| `app/crud/*.py` | Defines database queries, inserts, and conversion from table models to response DTOs. |

## Adding Or Changing A Backend Entity

Use this order when adding a new backend concept:

1. Define or update the table model in `app/db/schema.py`.
2. Define request and response DTOs in `app/db/dto.py`.
3. Add CRUD functions in `app/crud/`.
4. Add route handlers in `app/routes/`.
5. Register the router in `app/main.py`.
6. Add or update seed data in `app/utils/seed.py` if the demo should start with sample records.

## Local API Behavior

When Docker Compose starts the backend, `app/main.py` runs the lifespan startup logic. The startup creates missing tables and inserts demo records if the database is empty.

The API documentation is available at `http://localhost:8000/docs` with the default environment values.
