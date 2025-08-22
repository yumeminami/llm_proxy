"""Main CLI interface for LLM Proxy management."""

import click
from rich.console import Console
from rich.table import Table

from .nginx_manager import NginxManager
from .docker_manager import DockerManager

console = Console()


@click.group()
@click.version_option()
def cli():
    """LLM Proxy CLI - Manage your proxy configurations dynamically."""
    pass


@cli.command()
@click.option(
    "--endpoint", 
    required=True, 
    help="Local endpoint path (e.g., /claude, /gpt)"
)
@click.option(
    "--base-url", 
    required=True, 
    help="Target base URL (e.g., https://api.anthropic.com)"
)
@click.option(
    "--name", 
    help="Optional name for the proxy configuration"
)
@click.option(
    "--force", 
    is_flag=True, 
    help="Force add even if configuration exists"
)
def add(endpoint: str, base_url: str, name: str = None, force: bool = False):
    """Add a new proxy configuration."""
    try:
        nginx_manager = NginxManager()
        docker_manager = DockerManager()
        
        # Validate inputs
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        if not endpoint.endswith('/'):
            endpoint = endpoint + '/'
        
        # Check if configuration already exists
        if not force and nginx_manager.proxy_exists(endpoint):
            console.print(f"[red]❌ Proxy configuration for '{endpoint}' already exists![/red]")
            console.print("[yellow]Use --force to override existing configuration.[/yellow]")
            return
        
        # Add the proxy configuration
        success = nginx_manager.add_proxy(endpoint, base_url, name)
        
        if success:
            console.print(f"[green]✅ Added proxy configuration:[/green]")
            console.print(f"  Endpoint: {endpoint}*")
            console.print(f"  Target: {base_url}/*")
            
            # Reload nginx configuration
            if docker_manager.reload_nginx():
                console.print("[green]✅ Nginx configuration reloaded successfully![/green]")
            else:
                console.print("[yellow]⚠️  Configuration added but nginx reload failed. You may need to restart manually.[/yellow]")
        else:
            console.print("[red]❌ Failed to add proxy configuration![/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


@cli.command()
def list():
    """List all proxy configurations."""
    try:
        nginx_manager = NginxManager()
        proxies = nginx_manager.list_proxies()
        
        if not proxies:
            console.print("[yellow]No proxy configurations found.[/yellow]")
            return
        
        table = Table(title="Proxy Configurations")
        table.add_column("Endpoint", style="cyan", no_wrap=True)
        table.add_column("Target URL", style="magenta")
        table.add_column("Name", style="green")
        
        for proxy in proxies:
            table.add_row(
                proxy['endpoint'], 
                proxy['target'], 
                proxy.get('name', 'N/A')
            )
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


@cli.command()
@click.option(
    "--endpoint", 
    required=True, 
    help="Endpoint to remove (e.g., /claude)"
)
@click.option(
    "--force", 
    is_flag=True, 
    help="Force remove without confirmation"
)
def remove(endpoint: str, force: bool = False):
    """Remove a proxy configuration."""
    try:
        nginx_manager = NginxManager()
        docker_manager = DockerManager()
        
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        if not endpoint.endswith('/'):
            endpoint = endpoint + '/'
        
        # Check if configuration exists
        if not nginx_manager.proxy_exists(endpoint):
            console.print(f"[red]❌ Proxy configuration for '{endpoint}' not found![/red]")
            return
        
        # Confirm removal
        if not force:
            if not click.confirm(f"Remove proxy configuration for '{endpoint}'?"):
                console.print("[yellow]Operation cancelled.[/yellow]")
                return
        
        # Remove the proxy configuration
        success = nginx_manager.remove_proxy(endpoint)
        
        if success:
            console.print(f"[green]✅ Removed proxy configuration for '{endpoint}'[/green]")
            
            # Reload nginx configuration
            if docker_manager.reload_nginx():
                console.print("[green]✅ Nginx configuration reloaded successfully![/green]")
            else:
                console.print("[yellow]⚠️  Configuration removed but nginx reload failed. You may need to restart manually.[/yellow]")
        else:
            console.print("[red]❌ Failed to remove proxy configuration![/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


@cli.command()
def status():
    """Show proxy service status."""
    try:
        docker_manager = DockerManager()
        nginx_manager = NginxManager()
        
        # Check Docker container status
        container_status = docker_manager.get_container_status()
        console.print(f"[bold]Container Status:[/bold] {container_status}")
        
        # Show proxy count
        proxies = nginx_manager.list_proxies()
        console.print(f"[bold]Active Proxies:[/bold] {len(proxies)}")
        
        # Test nginx configuration
        if docker_manager.test_nginx_config():
            console.print("[green]✅ Nginx configuration is valid[/green]")
        else:
            console.print("[red]❌ Nginx configuration has errors[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


@cli.command()
def reload():
    """Reload nginx configuration."""
    try:
        docker_manager = DockerManager()
        
        if docker_manager.reload_nginx():
            console.print("[green]✅ Nginx configuration reloaded successfully![/green]")
        else:
            console.print("[red]❌ Failed to reload nginx configuration![/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


if __name__ == "__main__":
    cli()