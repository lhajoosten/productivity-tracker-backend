"""
CLI Tool for Productivity Tracker

Development and management commands.
"""

import typer
import uvicorn
from alembic import command
from alembic.config import Config
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from productivity_tracker.core.database import get_db
from productivity_tracker.database.entities.feature_flag import FeatureFlag
from productivity_tracker.database.entities.version import Version as VersionEntity
from productivity_tracker.versioning import __version__

app = typer.Typer(help="Productivity Tracker CLI")
console = Console()


# ==============================================================================
# SERVER
# ==============================================================================


@app.command()
def start(
    port: int = 3456,
    host: str = "api.localhost",
    reload: bool = True,
):
    """Start the FastAPI development server."""
    console.print(
        Panel.fit(
            f"[bold cyan]Starting Productivity Tracker API[/bold cyan]\n"
            f"Version: {__version__}\n"
            f"URL: https://{host}:{port}",
            border_style="cyan",
        )
    )

    uvicorn.run(
        "productivity_tracker.main:app",
        reload=reload,
        port=port,
        host=host,
        log_level="info",
        ssl_keyfile="../certs/api.localhost-key.pem",
        ssl_certfile="../certs/api.localhost.pem",
    )


# ==============================================================================
# DATABASE
# ==============================================================================


@app.command()
def migrate(message: str = "Auto migration"):
    """Create a new database migration."""
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, message=message, autogenerate=True)
    console.print(f"✅ Migration created: {message}", style="green")


@app.command()
def upgrade():
    """Apply all pending database migrations."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    console.print("✅ Database upgraded to latest", style="green")


@app.command()
def downgrade(revision: str = "-1"):
    """Downgrade database by one revision."""
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, revision)
    console.print(f"✅ Database downgraded to {revision}", style="green")


# ==============================================================================
# SEEDING
# ==============================================================================


@app.command()
def seed_rbac():
    """Seed initial roles and permissions."""
    from productivity_tracker.scripts.seed_rbac import seed_rbac as run_seed

    run_seed()
    console.print("✅ RBAC data seeded successfully!", style="green")


@app.command()
def seed_test_data():
    """Seed test data for development."""
    from productivity_tracker.scripts.seed_test_data import seed_test_data as run_seed

    run_seed()
    console.print("✅ Test data seeded successfully!", style="green")


@app.command()
def seed_versions():
    """Seed versions and feature flags from versions.json."""
    from productivity_tracker.scripts.seed_versions import main as run_seed

    run_seed()


@app.command()
def validate_versions():
    """Validate versions.json structure."""
    from productivity_tracker.scripts.validate_versions import main as run_validate

    exit(run_validate())


# ==============================================================================
# VERSIONING INFO
# ==============================================================================


@app.command()
def version():
    """Show current application version."""
    from productivity_tracker.versioning import get_version_info

    info = get_version_info()

    table = Table(title="Version Information", show_header=False)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Version", info["version"])
    table.add_row("Release Date", str(info["release_date"]))
    table.add_row("Release Name", info["release_name"])

    console.print(table)


@app.command()
def versions():
    """List all versions in database."""
    db = next(get_db())

    try:
        all_versions = (
            db.query(VersionEntity)
            .order_by(
                VersionEntity.major.desc(), VersionEntity.minor.desc(), VersionEntity.patch.desc()
            )
            .all()
        )

        if not all_versions:
            console.print(
                "[yellow]No versions found in database. Run 'seed-versions' first.[/yellow]"
            )
            return

        table = Table(title="All Versions")
        table.add_column("Version", style="cyan")
        table.add_column("Name", style="white", width=45)
        table.add_column("Status", style="magenta")
        table.add_column("Release Date", style="green", width=12)
        table.add_column("Features", style="blue")

        for v in all_versions:
            feature_count = (
                db.query(FeatureFlag)
                .filter(FeatureFlag.version_id == v.id, FeatureFlag.enabled)
                .count()
            )

            status_color = {
                "active": "bold green",
                "planned": "yellow",
                "deprecated": "red",
                "beta": "cyan",
                "alpha": "magenta",
            }.get(v.status, "white")

            table.add_row(
                v.version,
                v.name[:50],
                f"[{status_color}]{v.status}[/{status_color}]",
                v.release_date.strftime("%Y-%m-%d") if v.release_date else "—",
                str(feature_count),
            )

        console.print(table)

        # Show active version
        active = db.query(VersionEntity).filter(VersionEntity.status == "active").first()
        if active:
            console.print(
                f"\n[bold green]Active Version:[/bold green] {active.version} - {active.name}"
            )

    finally:
        db.close()


@app.command()
def features(version: str = None):
    """List features for a version (defaults to active)."""
    db = next(get_db())

    try:
        if version:
            ver = db.query(VersionEntity).filter(VersionEntity.version == version).first()
            if not ver:
                console.print(f"[red]Version '{version}' not found[/red]")
                return
        else:
            ver = db.query(VersionEntity).filter(VersionEntity.status == "active").first()
            if not ver:
                console.print(
                    "[yellow]No active version found. Run 'seed-versions' first.[/yellow]"
                )
                return

        flags = (
            db.query(FeatureFlag)
            .filter(FeatureFlag.version_id == ver.id, FeatureFlag.enabled)
            .all()
        )

        table = Table(title=f"Features for {ver.version}")
        table.add_column("Feature Key", style="cyan")
        table.add_column("Name", style="white", width=30)
        table.add_column("Category", style="magenta")
        table.add_column("Enabled", style="green")

        for f in flags:
            table.add_row(
                f.feature_key, f.feature_name, f.category or "—", "✓" if f.enabled else "✗"
            )

        console.print(table)
        console.print(f"\n[bold]Total Features:[/bold] {len(flags)}")

    finally:
        db.close()


@app.command()
def health():
    """Check versioning system health."""
    db = next(get_db())

    try:
        total_versions = db.query(VersionEntity).count()
        active_version = db.query(VersionEntity).filter(VersionEntity.status == "active").first()
        total_features = db.query(FeatureFlag).count()

        table = Table(title="Versioning System Health")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Total Versions", str(total_versions))
        table.add_row(
            "Active Version", active_version.version if active_version else "[red]None[/red]"
        )
        table.add_row("Total Feature Flags", str(total_features))

        if active_version:
            active_features = (
                db.query(FeatureFlag)
                .filter(FeatureFlag.version_id == active_version.id, FeatureFlag.enabled)
                .count()
            )
            table.add_row("Active Version Features", str(active_features))

        console.print(table)

        if not active_version:
            console.print("\n[bold red]⚠️  No active version found![/bold red]")
            console.print(
                "[yellow]Run 'seed-versions' to initialize the versioning system.[/yellow]"
            )
        else:
            console.print("\n[bold green]✓ Versioning system is healthy[/bold green]")

    finally:
        db.close()


# ==============================================================================
# USER MANAGEMENT
# ==============================================================================


@app.command()
def create_superuser():
    """Create a superuser account."""
    from productivity_tracker.scripts.create_super_user import (
        create_super_user as run_create,
    )

    run_create()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    app()
