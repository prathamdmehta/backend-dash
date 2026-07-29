import re
import shutil
from pathlib import Path

import typer
from jinja2 import Environment, FileSystemLoader

app = typer.Typer(
    help="Scaffold a FastAPI + SQLAlchemy backend so you can skip the boilerplate."
)

TEMPLATES_ROOT = Path(__file__).parent / "templates"
VALID_DBS = ("sqlite", "postgres", "mysql")


def slugify(name: str) -> str:
    """Turn 'My Cool API' into 'my_cool_api' for use as a folder name."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip()).strip("_").lower()
    return slug or "backend_project"


def render_template(template_dir: Path, target_dir: Path, context: dict) -> None:
    env = Environment(loader=FileSystemLoader(str(template_dir)), keep_trailing_newline=True)

    for src_path in sorted(template_dir.rglob("*")):
        if src_path.is_dir():
            continue

        rel_path = src_path.relative_to(template_dir)
        rel_str = rel_path.as_posix()
        is_template = rel_str.endswith(".j2")
        out_rel = Path(rel_str[:-3]) if is_template else rel_path
        out_path = target_dir / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if is_template:
            rendered = env.get_template(rel_str).render(**context)
            out_path.write_text(rendered, encoding="utf-8")
        else:
            shutil.copy2(src_path, out_path)


@app.command()
def init(
    project_name: str = typer.Argument(..., help="Human-readable project name, e.g. 'My API'"),
    directory: str = typer.Option(
        None,
        "--dir",
        help="Folder to create the project in. Defaults to a slugified version of the project name.",
    ),
    auth: bool = typer.Option(
        False,
        "--auth",
        help="Include JWT + Google OAuth authentication (repository pattern, service layer, "
        "centralized error handling, login/register/me routes).",
    ),
    db: str = typer.Option(
        "sqlite",
        "--db",
        help="Database backend: sqlite (default, zero setup), postgres, or mysql "
        "(both include Alembic migrations instead of auto-created tables).",
    ),
    docker: bool = typer.Option(
        False,
        "--docker",
        help="Include a Dockerfile and docker-compose.yml (with the db service included "
        "for --db=postgres/mysql, migrations run automatically on container start).",
    ),
):
    """
    Generate a new FastAPI + SQLAlchemy + SQLite backend project.
    """
    db = db.lower()
    if db not in VALID_DBS:
        typer.secho(f"--db must be one of {VALID_DBS}, got '{db}'.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    project_slug = slugify(directory or project_name)
    target_dir = Path.cwd() / project_slug

    if target_dir.exists() and any(target_dir.iterdir()):
        typer.secho(f"'{project_slug}' already exists and is not empty. Aborting.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    context = {"project_name": project_name, "project_slug": project_slug, "auth": auth, "db": db}

    render_template(TEMPLATES_ROOT / "fastapi_sqlite", target_dir, context)
    if auth:
        render_template(TEMPLATES_ROOT / "fastapi_sqlite_auth", target_dir, context)
    if db in ("postgres", "mysql"):
        render_template(TEMPLATES_ROOT / "db_migrations", target_dir, context)
    if docker:
        render_template(TEMPLATES_ROOT / "docker", target_dir, context)

    typer.secho(f"\n✅ Created '{project_name}' in ./{project_slug}\n", fg=typer.colors.GREEN, bold=True)
    typer.echo("Next steps:")
    typer.echo(f"  cd {project_slug}")
    typer.echo("  cp .env.example .env")
    if docker:
        typer.echo("  docker compose up --build")
        if db in ("postgres", "mysql"):
            typer.echo(f"  # migrations run automatically on container start (edit .env for real {db} creds first)")
    else:
        typer.echo("  pip install -r requirements.txt   # or: uv pip install -r requirements.txt")
        if db in ("postgres", "mysql"):
            typer.echo(f"  # edit .env with your real {db} credentials, then:")
            typer.echo('  alembic revision --autogenerate -m "initial tables"')
            typer.echo("  alembic upgrade head")
        if auth:
            typer.echo("  # (optional) set GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET in .env for Google login")
        typer.echo("  uvicorn app.main:app --reload")
    if auth:
        typer.echo("\nAuth endpoints: POST /api/v1/auth/register, POST /api/v1/auth/login, "
                    "GET /api/v1/auth/me, GET /api/v1/auth/google/login")


@app.command()
def version():
    """Print the fastapi-scaffolder version."""
    from fastapi_scaffolder import __version__

    typer.echo(__version__)


def main():
    app()


if __name__ == "__main__":
    main()
