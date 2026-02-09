"""
Database Management CLI

Command-line interface for database operations including
initialization, migrations, health checks, and maintenance.
"""

import asyncio
import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from app.core.database_init import initialize_database, check_database_status
from app.core.migrations import MigrationManager, get_migration_status, run_migrations
from app.core.database import get_database_info, DatabaseHealthCheck
from app.core.connection_pool import get_pool_manager

console = Console()


@click.group()
def database():
    """Database management commands."""
    pass


@database.command()
@click.option('--force', is_flag=True, help='Force recreate all tables')
@click.option('--seed', is_flag=True, help='Seed initial data')
def init(force: bool, seed: bool):
    """Initialize database with tables and initial data."""
    
    async def _init():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing database...", total=None)
            
            try:
                result = await initialize_database(force_recreate=force)
                progress.update(task, description="Database initialized successfully!")
                
                # Display results
                console.print("\n[bold green]Database Initialization Results:[/bold green]")
                
                for component, details in result.items():
                    if isinstance(details, dict):
                        status = details.get('status', 'unknown')
                        color = 'green' if status == 'success' else 'red'
                        console.print(f"  {component}: [{color}]{status}[/{color}]")
                        
                        if 'actions' in details:
                            for action in details['actions']:
                                console.print(f"    ✓ {action}")
                        
                        if 'error' in details:
                            console.print(f"    ✗ {details['error']}", style="red")
                
            except Exception as e:
                progress.update(task, description=f"Failed: {e}")
                console.print(f"\n[bold red]Error:[/bold red] {e}")
                raise click.Abort()
    
    asyncio.run(_init())


@database.command()
def status():
    """Check database connection status and health."""
    
    async def _status():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Checking database status...", total=None)
            
            try:
                # Get database info
                db_info = await get_database_info()
                health_check = await DatabaseHealthCheck.full_health_check()
                
                progress.update(task, description="Status check completed!")
                
                # Create status table
                table = Table(title="Database Status")
                table.add_column("Component", style="cyan")
                table.add_column("Status", style="magenta")
                table.add_column("Details", style="green")
                
                # SQL Database
                sql_status = db_info['sql_database']
                sql_health = health_check['sql_database']
                
                if sql_status['connected']:
                    status_text = "✓ Connected"
                    details = f"Type: {sql_status['type']}, URL: {sql_status['url']}"
                    if sql_health.get('pool_status'):
                        pool = sql_health['pool_status']
                        details += f"\nPool: {pool['checked_out']}/{pool['size']} active"
                else:
                    status_text = "✗ Disconnected"
                    details = sql_health.get('error', 'Unknown error')
                
                table.add_row("SQL Database", status_text, details)
                
                # MongoDB
                mongo_status = db_info['mongodb']
                mongo_health = health_check['mongodb']
                
                if mongo_status['connected']:
                    status_text = "✓ Connected"
                    details = f"URL: {mongo_status['url']}"
                    if mongo_health.get('server_version'):
                        details += f"\nVersion: {mongo_health['server_version']}"
                elif mongo_status['url']:
                    status_text = "✗ Disconnected"
                    details = mongo_health.get('error', 'Unknown error')
                else:
                    status_text = "Not configured"
                    details = "MongoDB URL not set"
                
                table.add_row("MongoDB", status_text, details)
                
                console.print(table)
                
            except Exception as e:
                progress.update(task, description=f"Failed: {e}")
                console.print(f"\n[bold red]Error:[/bold red] {e}")
                raise click.Abort()
    
    asyncio.run(_status())


@database.command()
def migrations():
    """Show migration status and history."""
    
    async def _migrations():
        try:
            status = await get_migration_status()
            
            console.print("[bold blue]Migration Status:[/bold blue]")
            
            if 'sql' in status:
                sql_status = status['sql']
                
                # Current status
                panel_content = f"""
Current Revision: {sql_status.get('current_revision', 'None')}
Head Revision: {sql_status.get('head_revision', 'None')}
Needs Migration: {'Yes' if sql_status.get('needs_migration') else 'No'}
Up to Date: {'Yes' if sql_status.get('is_up_to_date') else 'No'}
                """.strip()
                
                console.print(Panel(panel_content, title="SQL Database"))
                
                # Migration history
                if sql_status.get('history'):
                    table = Table(title="Migration History")
                    table.add_column("Revision", style="cyan")
                    table.add_column("Down Revision", style="yellow")
                    table.add_column("Description", style="green")
                    table.add_column("Date", style="magenta")
                    
                    for migration in sql_status['history'][:10]:  # Show last 10
                        table.add_row(
                            migration.get('revision', 'N/A'),
                            migration.get('down_revision', 'N/A'),
                            migration.get('doc', 'N/A'),
                            str(migration.get('create_date', 'N/A'))
                        )
                    
                    console.print(table)
            
            if 'mongodb' in status:
                mongo_status = status['mongodb']
                applied = mongo_status.get('applied_migrations', [])
                
                console.print(f"\n[bold blue]MongoDB Migrations:[/bold blue]")
                console.print(f"Applied migrations: {len(applied)}")
                
                if applied:
                    for migration in applied:
                        console.print(f"  ✓ {migration}")
                
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise click.Abort()
    
    asyncio.run(_migrations())


@database.command()
@click.option('--message', '-m', required=True, help='Migration message')
@click.option('--autogenerate/--no-autogenerate', default=True, help='Auto-generate migration')
def create_migration(message: str, autogenerate: bool):
    """Create a new database migration."""
    
    try:
        migration_manager = MigrationManager()
        result = migration_manager.create_migration(message, autogenerate)
        
        if result == "success":
            console.print(f"[green]✓[/green] Migration created: {message}")
        else:
            console.print(f"[red]✗[/red] Failed to create migration: {result}")
            raise click.Abort()
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@database.command()
@click.option('--revision', default='head', help='Target revision (default: head)')
@click.option('--backup/--no-backup', default=True, help='Create backup before migration')
def migrate(revision: str, backup: bool):
    """Run database migrations."""
    
    async def _migrate():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running migrations...", total=None)
            
            try:
                if backup:
                    progress.update(task, description="Creating backup...")
                    migration_manager = MigrationManager()
                    backup_file = await migration_manager.backup_before_migration()
                    if backup_file:
                        console.print(f"[green]✓[/green] Backup created: {backup_file}")
                
                progress.update(task, description="Running migrations...")
                result = await run_migrations()
                
                progress.update(task, description="Migrations completed!")
                
                console.print("\n[bold green]Migration Results:[/bold green]")
                for component, details in result.items():
                    console.print(f"  {component}: {details}")
                
            except Exception as e:
                progress.update(task, description=f"Failed: {e}")
                console.print(f"\n[bold red]Error:[/bold red] {e}")
                raise click.Abort()
    
    asyncio.run(_migrate())


@database.command()
def pool_stats():
    """Show connection pool statistics."""
    
    async def _pool_stats():
        try:
            from app.core.database import async_engine
            
            if not async_engine:
                console.print("[yellow]Database not initialized[/yellow]")
                return
            
            pool_manager = get_pool_manager()
            health_status = pool_manager.get_pool_health_status(async_engine)
            
            # Health status panel
            status_color = {
                'healthy': 'green',
                'moderate': 'yellow',
                'warning': 'orange',
                'critical': 'red'
            }.get(health_status['health_status'], 'white')
            
            panel_content = f"""
Health Status: [{status_color}]{health_status['health_status'].upper()}[/{status_color}]
Utilization: {health_status['utilization_percentage']}%
Error Rate: {health_status['error_rate_percentage']}%
            """.strip()
            
            console.print(Panel(panel_content, title="Pool Health"))
            
            # Metrics table
            metrics = health_status['metrics']
            table = Table(title="Connection Pool Metrics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Pool Size", str(metrics['pool_size']))
            table.add_row("Max Overflow", str(metrics['max_overflow']))
            table.add_row("Checked Out", str(metrics['checked_out']))
            table.add_row("Checked In", str(metrics['checked_in']))
            table.add_row("Overflow", str(metrics['overflow']))
            table.add_row("Invalid", str(metrics['invalid']))
            
            console.print(table)
            
            # Statistics
            stats = health_status['statistics']
            stats_table = Table(title="Connection Statistics")
            stats_table.add_column("Statistic", style="cyan")
            stats_table.add_column("Value", style="magenta")
            
            stats_table.add_row("Total Connections", str(stats['total_connections']))
            stats_table.add_row("Active Connections", str(stats['active_connections']))
            stats_table.add_row("Failed Connections", str(stats['failed_connections']))
            stats_table.add_row("Peak Connections", str(stats['peak_connections']))
            stats_table.add_row("Total Requests", str(stats['total_requests']))
            stats_table.add_row("Avg Connection Time", f"{stats['average_connection_time_ms']} ms")
            
            console.print(stats_table)
            
            # Recommendations
            if health_status['recommendations']:
                console.print("\n[bold yellow]Recommendations:[/bold yellow]")
                for rec in health_status['recommendations']:
                    console.print(f"  • {rec}")
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise click.Abort()
    
    asyncio.run(_pool_stats())


@database.command()
@click.confirmation_option(prompt='Are you sure you want to reset the database?')
def reset():
    """Reset database (drop and recreate all tables)."""
    
    async def _reset():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Resetting database...", total=None)
            
            try:
                result = await initialize_database(force_recreate=True)
                progress.update(task, description="Database reset completed!")
                
                console.print("[bold green]✓[/bold green] Database reset successfully")
                
            except Exception as e:
                progress.update(task, description=f"Failed: {e}")
                console.print(f"\n[bold red]Error:[/bold red] {e}")
                raise click.Abort()
    
    asyncio.run(_reset())


if __name__ == '__main__':
    database()