[![PyPI version](https://img.shields.io/pypi/v/backend-dash.svg)](https://pypi.org/project/backend-dash/)
[![Pepy Total Downloads](https://img.shields.io/pepy/dt/backend-dash)](https://pepy.tech/project/backend-dash)
[![License](https://img.shields.io/pypi/l/backend-dash.svg)](https://github.com/prathamdmehta/backend-dash/blob/main/LICENSE)
[![Python versions](https://img.shields.io/pypi/pyversions/backend-dash.svg)](https://pypi.org/project/backend-dash/)

# backend-dash

A CLI that generates ready-to-code FastAPI backend projects with SQLAlchemy, SQLite, PostgreSQL, MySQL, Alembic migrations, CRUD examples, tests, and optional JWT + Google OAuth authentication.

## Features

- Scaffold a complete FastAPI backend in seconds.
- Supports `--db=sqlite|postgres|mysql` with SQLite as the default.
- Generates a working SQLAlchemy setup and DB session wiring.
- Adds an example CRUD resource so you can start from real code, not boilerplate.
- Includes tests for the generated project.
- Adds Alembic migrations for PostgreSQL and MySQL.
- Keeps SQLite simple with `create_all` for zero-config local development.
- Optional `--auth` mode adds JWT + Google OAuth auth support.
- Clear validation for unsupported database values.
- Clean `.env.example` setup for local development and migrations.

## Installation

### One-off usage

```bash
uvx backend-dash init "My API"
```

### Install locally

```bash
pip install backend-dash
backend-dash init "My API"
```

### Editable install for development

```bash
git clone https://github.com/prathamdmehta/backend-dash.git
cd backend-dash
pip install -e . --break-system-packages
```

## Usage

Create a new project:

```bash
backend-dash init "Demo Project"
```

Create a project with auth:

```bash
backend-dash init "Demo Project Auth" --auth
```

Choose a database:

```bash
backend-dash init "My API" --db=sqlite
backend-dash init "My API" --db=postgres
backend-dash init "My API" --db=mysql
```

Combine database and auth:

```bash
backend-dash init "My API" --db=postgres --auth
```

Add Docker support:

```bash
backend-dash init "My API" --db=postgres --docker
```

This generates a `Dockerfile`, `docker-compose.yml`, and `.dockerignore`. For
`--db=postgres`/`--db=mysql`, the compose file includes the database service
too (with a healthcheck, so the app waits for the DB to actually be ready),
and Alembic migrations run automatically on container start. For the SQLite
default, it's just the app container with the DB file mounted as a volume.

```bash
cd my_api
cp .env.example .env
docker compose up --build
```

## What gets generated

### Base project

- FastAPI app structure.
- SQLAlchemy session and base model wiring.
- Example item resource with CRUD routes.
- Pydantic schemas and models.
- Pytest test setup.

### With `--auth`

- Repository layer with a generic `BaseRepository` and `UserRepository`.
- Auth service for registration, login, JWT issuance, and Google token exchange.
- Validation with proper schema constraints.
- Centralized error handling with a consistent error response shape.
- Auth routes for register, login, me, Google login, and Google callback.

## Database support

### SQLite

SQLite is the default and uses `create_all` for a simple local setup.

### PostgreSQL

For PostgreSQL, the scaffold uses Alembic migrations and real schema management.

### MySQL

For MySQL, the scaffold also uses Alembic migrations and the correct MySQL driver setup.

## Migrations

For PostgreSQL and MySQL, the project generates Alembic configuration and an `env.py` wired to `DATABASE_URL` and your app metadata.

Typical workflow:

```bash
alembic revision --autogenerate -m "create initial tables"
alembic upgrade head
```

The generated `.env.example` includes the right migration flow so you can move from scaffold to production-style schema management quickly.

## Project structure

```bash
my_api/
├── app/
├── tests/
├── alembic/
├── alembic.ini
└── .env.example
```

If `--auth` is enabled, additional auth-related modules are included inside the app structure.

## Example

Generate a new API project:

```bash
backend-dash init "Orders API" --db=postgres --auth
```

This creates a FastAPI backend with database wiring, migrations, tests, and authentication already in place, so you can start on business logic immediately.

## Development

```bash
git clone https://github.com/prathamdmehta/backend-dash.git
cd backend-dash
pip install -e . --break-system-packages
```

Then run the CLI locally:

```bash
backend-dash init "Demo Project"
```

## License

MIT
