# Frontend Overview

This directory contains the Vite frontend. It loads data from the FastAPI backend with browser `fetch` calls, stores the current page data in a small shared state object, and renders HTML into the page.

## Directory Responsibilities

| Directory | Responsibility |
| --- | --- |
| `src/` | Browser application source code loaded by Vite. |
| `src/api/` | Backend API calls grouped by domain concept. |
| `src/state/` | Shared frontend state used by rendering functions. |
| `src/ui/` | DOM rendering, form submission handlers, and interaction logic. |

## Frontend Data Flow

The frontend follows this loading flow:

```text
main.js
  -> API modules
  -> fetchJson()
  -> Vite proxy /api/*
  -> FastAPI backend
  -> JSON response
  -> state/store.js
  -> ui/render.js
  -> browser DOM
```

The frontend follows this form submission flow:

```text
User submits form
  -> ui/forms.js
  -> API module POST request
  -> FastAPI backend
  -> PostgreSQL insert
  -> reload frontend data
  -> update state
  -> re-render DOM
```

## Main Frontend Files

| File | Role |
| --- | --- |
| `src/main.js` | Starts the frontend, loads initial API data, stores it, and renders the page. |
| `src/api/client.js` | Shared `fetchJson` helper for JSON requests and error handling. |
| `src/api/*.js` | Domain-specific API functions such as listing or creating books and authors. |
| `src/state/store.js` | Shared state for nationalities, categories, authors, and books. |
| `src/ui/render.js` | Converts state and API results into DOM output. |
| `src/ui/forms.js` | Handles form submissions and button interactions. |
| `src/styles.css` | Tailwind entrypoint and project CSS. |

## Adding Or Changing A Frontend Feature

Use this order when adding a new frontend feature:

1. Add or update API functions in `src/api/`.
2. Add any required state fields in `src/state/store.js`.
3. Update rendering logic in `src/ui/render.js`.
4. Add form or button handlers in `src/ui/forms.js`.
5. Wire the loading or interaction flow from `src/main.js` if needed.
6. Update `index.html` when the page needs new containers, forms, or controls.

## Local Browser Behavior

With the default Docker Compose setup, open the frontend at `http://localhost:8080`.

The browser calls paths such as `/api/books`. Vite proxies those `/api/*` requests to the FastAPI container, so frontend code does not need to know the backend container hostname.
