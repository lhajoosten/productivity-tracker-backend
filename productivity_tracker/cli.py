import pathlib

import typer
import uvicorn
from alembic import command
from alembic.config import Config

app = typer.Typer()


@app.command()
def start():
    """Start the FastAPI development server."""
    uvicorn.run("productivity_tracker.main:app", reload=True)


@app.command()
def seed_rbac():
    """Seed initial roles and permissions into the database."""
    from productivity_tracker.scripts.seed_rbac import seed_rbac as run_seed

    run_seed()


@app.command()
def create_superuser():
    """Create a new super user."""
    from productivity_tracker.scripts.create_super_user import (
        create_super_user as run_create_super_user,
    )

    run_create_super_user()


def _alembic_cfg(alembic_ini: str) -> Config:
    cfg = Config(alembic_ini)
    project_root = pathlib.Path(__file__).resolve().parent.parent
    cfg.set_main_option("script_location", str(project_root / "migrations"))
    return cfg


@app.command()
def migrate(alembic_ini: str = "alembic.ini"):
    """Run Alembic migrations (upgrade to head)."""
    cfg = _alembic_cfg(alembic_ini)
    command.upgrade(cfg, "head")
    typer.echo("Alembic: migrations applied (head)")


@app.command()
def downgrade(
    revision: str = typer.Argument(..., help="revision id or migration filename"),
    alembic_ini: str = "alembic.ini",
):
    """Reset Alembic migrations (downgrade to revision). Accepts either a revision id or a migration filename."""
    cfg = _alembic_cfg(alembic_ini)
    project_root = pathlib.Path(__file__).resolve().parent.parent
    versions_dir = project_root / "migrations" / "versions"

    def resolve_revision_token(token: str) -> str:
        # If user supplied a filename, strip extension and extract leading revision hash.
        t = token
        if t.endswith(".py"):
            t = t[:-3]
        # If a file with that exact name exists in versions, use it.
        if (versions_dir / f"{t}.py").exists():
            return (versions_dir / f"{t}.py").name.split("_", 1)[0]
        # If token contains an underscore assume it's '<rev>_name' and extract rev
        if "_" in t:
            return t.split("_", 1)[0]
        # Try to find any file that starts with the given token
        if versions_dir.exists():
            for f in versions_dir.iterdir():
                if f.name.startswith(t):
                    return f.name.split("_", 1)[0]
        # Fallback: return token as-is
        return t

    target_rev = resolve_revision_token(revision)
    command.downgrade(cfg, target_rev)
    typer.echo(f"Alembic: migrations reset to {target_rev}")


@app.command()
def new_migration(
    filename: str = typer.Argument(..., help="migration message/name"),
    rev_id: str | None = typer.Option(
        None, help="explicit revision id to use for the new migration"
    ),
    autogenerate: bool = typer.Option(
        True, help="use autogenerate (set --no-autogenerate to disable)"
    ),
    alembic_ini: str = "alembic.ini",
):
    """Create new Alembic migration. Accepts optional rev_id and can be run as a poetry console script."""
    # Normalize filename (Typer's ArgumentInfo may be passed if the function is invoked directly
    # as a console script). Try .default, then fallback to sys.argv.
    if not isinstance(filename, str):
        filename = getattr(filename, "default", None)
        if not isinstance(filename, str):
            import sys

            if len(sys.argv) > 1:
                filename = sys.argv[1]
            else:
                raise typer.BadParameter("filename is required")

    # Normalize rev_id (Typer OptionInfo can be passed directly)
    if not isinstance(rev_id, str | type(None)):
        rev_id = getattr(rev_id, "default", None)
        if not isinstance(rev_id, str | type(None)):
            rev_id = None

    # Normalize autogenerate
    if not isinstance(autogenerate, bool):
        autogenerate = bool(getattr(autogenerate, "default", True))

    cfg = _alembic_cfg(alembic_ini)
    command.revision(cfg, autogenerate=autogenerate, message=filename, rev_id=rev_id)
    typer.echo(
        f"Alembic: migration created: {filename} (rev_id={rev_id}, autogenerate={autogenerate})"
    )


if __name__ == "__main__":
    app()
