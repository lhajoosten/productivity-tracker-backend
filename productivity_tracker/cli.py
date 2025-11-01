import pathlib

import typer
import uvicorn
from alembic import command
from alembic.config import Config
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from productivity_tracker.versioning.utils import (
    get_active_versions,
    get_deprecated_versions,
)
from productivity_tracker.versioning.version import get_version_info
from productivity_tracker.versioning.versioning import (
    ALL_VERSIONS,
    CURRENT_VERSION,
    VERSION_FEATURES,
    Version,
    VersionStatus,
    get_all_features_up_to_version,
    is_feature_enabled,
)

app = typer.Typer()
console = Console()


@app.command()
def start():
    """Start the FastAPI development server."""
    uvicorn.run("productivity_tracker.main:app", reload=True)


@app.command()
def seed_rbac():
    """Seed initial roles and permissions into the database."""
    from productivity_tracker.scripts.seed_rbac import seed_rbac as run_seed

    run_seed()
    console.print("✅ RBAC data seeded successfully!", style="green")


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


@app.command()
def version():
    """Show current application version information."""
    version_info = get_version_info()

    panel = Panel.fit(
        f"""[bold blue]Productivity Tracker Backend[/bold blue]
[green]Version:[/green] {version_info["version"]}
[green]Release Date:[/green] {version_info["release_date"]}
[green]Release Name:[/green] {version_info.get("release_name", "N/A")}
[green]API Version:[/green] {CURRENT_VERSION}
        """,
        title="Version Information",
        border_style="blue",
    )
    console.print(panel)


@app.command()
def roadmap(
    version_filter: str | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show roadmap for specific version (e.g., 1.0, 1.1, 2.0)",
    ),
    features: bool = typer.Option(False, "--features", "-f", help="Show detailed feature list"),
):
    """Display development roadmap and feature status per VERSION_ROADMAP.md."""

    if version_filter:
        # Show specific version details
        from productivity_tracker.versioning.versioning import get_version_from_string

        api_version = get_version_from_string(version_filter)
        if not api_version:
            console.print(
                f"❌ Version {version_filter} not found. Available versions: {[str(v) for v in ALL_VERSIONS]}",
                style="red",
            )
            return

        _show_version_details(api_version)
        return

    # Show general roadmap overview
    console.print("\n🗺️  [bold blue]Productivity Tracker Development Roadmap[/bold blue]\n")

    # Current status
    version_info = get_version_info()
    current_panel = Panel.fit(
        f"""[green]Current Version:[/green] {version_info["version"]}
[green]API Version:[/green] {CURRENT_VERSION}
[green]Release Date:[/green] {version_info["release_date"]}
[green]Status:[/green] {CURRENT_VERSION.status.value.upper()}
        """,
        title="📊 Current Status",
        border_style="green",
    )
    console.print(current_panel)

    # Version overview table
    table = Table(title="🚀 Version Roadmap (per VERSION_ROADMAP.md)")
    table.add_column("Version", style="cyan", no_wrap=True, width=5)
    table.add_column("Status", style="magenta", width=10)
    table.add_column("Focus", style="white", width=35)
    table.add_column("Features Count", style="yellow", justify="center", no_wrap=False, width=8)

    # Version roadmap data based on VERSION_ROADMAP.md
    roadmap_data = [
        ("v1.0", "CURRENT", "Foundation - First Beta", 11),
        ("v1.1", "PLANNED", "Security & Validation Enhancement", 9),
        ("v1.2", "PLANNED", "Productivity Tracking Core", 7),
        ("v1.3", "PLANNED", "Analytics & Reporting", 12),
        ("v1.4", "PLANNED", "Collaboration & Communication", 9),
        ("v1.5", "PLANNED", "Performance & Scalability", 6),
        ("v1.6", "PLANNED", "Integration & Extensibility", 8),
        ("v2.0", "PLANNED", "Enterprise Features", 9),
        ("v2.1", "PLANNED", "AI & Machine Learning", 7),
        ("v2.2", "PLANNED", "Accessibility & i18n", 5),
        ("v2.3", "PLANNED", "Advanced Quality & Observability", 5),
    ]

    for ver_str, status, focus, feat_count in roadmap_data:
        table.add_row(ver_str, status, focus, str(feat_count))

    console.print(table)

    # Active versions info
    active_versions = get_active_versions()
    deprecated_versions = get_deprecated_versions()

    if active_versions:
        active_text = Text("\n🟢 Active API Versions: ")
        active_text.append(", ".join([str(v) for v in active_versions]), style="green")
        console.print(active_text)

    if deprecated_versions:
        deprecated_text = Text("⚠️  Deprecated API Versions: ")
        deprecated_text.append(", ".join([str(v) for v in deprecated_versions]), style="yellow")
        console.print(deprecated_text)

    console.print("\n📋 [cyan]For detailed roadmap see:[/cyan] docs/VERSION_ROADMAP.md")
    console.print("🔧 [cyan]Use --features flag to see feature list[/cyan]")
    console.print("🎯 [cyan]Use --version [VERSION] to see specific version details[/cyan]")

    if features:
        console.print("\n")
        _show_all_features()


def _show_version_details(version: Version):
    """Show detailed information for a specific version."""
    features = VERSION_FEATURES.get(version, set())
    all_features = get_all_features_up_to_version(version)

    console.print(f"\n🎯 [bold blue]Version {version} Details[/bold blue]\n")

    # Create status panel
    status_emoji = {
        VersionStatus.PLANNED: "📋",
        VersionStatus.IN_DEVELOPMENT: "🚧",
        VersionStatus.BETA: "🧪",
        VersionStatus.RC: "🎯",
        VersionStatus.ACTIVE: "✅",
        VersionStatus.MAINTENANCE: "🔧",
        VersionStatus.DEPRECATED: "⚠️",
        VersionStatus.EOL: "❌",
    }

    status_display = (
        f"{status_emoji.get(version.status, '❓')} {version.status.value.upper().replace('_', ' ')}"
    )

    panel_content = f"""[green]Status:[/green] {status_display}
[green]New Features in this version:[/green] {len(features)}
[green]Total Features (cumulative):[/green] {len(all_features)}
[green]API Prefix:[/green] {version.api_prefix}"""

    if version.release_date:
        panel_content += f"\n[green]Release Date:[/green] {version.release_date}"
    if version.eol_date:
        panel_content += f"\n[yellow]EOL Date:[/yellow] {version.eol_date}"
    if version.docs_url:
        panel_content += f"\n[green]Documentation:[/green] {version.docs_url}"

    panel = Panel.fit(
        panel_content,
        title=f"Version {version}",
        border_style="blue",
    )
    console.print(panel)

    # Feature table for new features in this version
    if features:
        table = Table(title=f"New Features Introduced in {version}")
        table.add_column("Feature", style="cyan")
        table.add_column("Status", style="magenta")

        for feature in sorted(features, key=lambda f: f.value):
            enabled = is_feature_enabled(feature, version=version)
            status = "Enabled" if enabled else "Disabled"
            table.add_row(feature.value.replace("_", " ").title(), status)

        console.print(table)
    else:
        console.print("[yellow]No new features in this version[/yellow]")


def _show_all_features():
    """Show feature status across all versions."""
    console.print("\n📊 [bold blue]Feature Status Across All Versions[/bold blue]\n")

    # Create table
    table = Table(title="Feature Availability Matrix")
    table.add_column("Feature", style="cyan", width=40)
    table.add_column("Introduced In", style="yellow", width=12)
    table.add_column("Status", style="magenta", width=15)

    # Collect all features with their introduction version
    feature_version_map = {}
    for version, features in VERSION_FEATURES.items():
        for feature in features:
            if feature not in feature_version_map:
                feature_version_map[feature] = version

    # Add rows sorted by feature name
    for feature in sorted(feature_version_map.keys(), key=lambda f: f.value):
        intro_version = feature_version_map[feature]
        enabled = is_feature_enabled(feature, version=CURRENT_VERSION)

        status = "✅ Available" if enabled else "📋 Planned"

        table.add_row(feature.value.replace("_", " ").title(), str(intro_version), status)

    console.print(table)

    # Summary
    total_features = len(feature_version_map)
    enabled_features = sum(
        1 for f in feature_version_map.keys() if is_feature_enabled(f, version=CURRENT_VERSION)
    )

    summary = Panel.fit(
        f"""[green]Total Features Defined:[/green] {total_features}
[green]Currently Available:[/green] {enabled_features}
[yellow]Planned for Future:[/yellow] {total_features - enabled_features}""",
        title="Feature Summary",
        border_style="green",
    )
    console.print(f"\n{summary}")


if __name__ == "__main__":
    app()
