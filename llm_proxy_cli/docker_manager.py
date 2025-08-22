"""Docker container management for nginx proxy."""

import subprocess
from pathlib import Path


class DockerManager:
    """Manages Docker operations for the nginx container."""

    def __init__(self, container_name: str = "llm_proxy_nginx"):
        """Initialize DockerManager with container name."""
        self.container_name = container_name
        self.project_root = Path.cwd()

    def _run_docker_command(self, command: list[str]) -> tuple[bool, str]:
        """Run a docker command and return success status and output."""
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
        except FileNotFoundError:
            return False, "Docker not found. Please install Docker."

    def _run_docker_compose_command(self, command: list[str]) -> tuple[bool, str]:
        """Run a docker-compose command and return success status and output."""
        full_command = ["docker-compose"] + command
        return self._run_docker_command(full_command)

    def get_container_status(self) -> str:
        """Get the status of the nginx container."""
        success, output = self._run_docker_command([
            "docker", "ps", "-f", f"name={self.container_name}", 
            "--format", "table {{.Status}}"
        ])
        
        if success and output.strip():
            lines = output.strip().split('\n')
            if len(lines) > 1:  # Skip header
                return lines[1]
            else:
                return "Not running"
        else:
            return "Not found"

    def container_exists(self) -> bool:
        """Check if the container exists (running or stopped)."""
        success, output = self._run_docker_command([
            "docker", "ps", "-a", "-f", f"name={self.container_name}", 
            "--format", "{{.Names}}"
        ])
        
        return success and self.container_name in output

    def container_is_running(self) -> bool:
        """Check if the container is currently running."""
        success, output = self._run_docker_command([
            "docker", "ps", "-f", f"name={self.container_name}", 
            "--format", "{{.Names}}"
        ])
        
        return success and self.container_name in output

    def start_container(self) -> bool:
        """Start the nginx container using docker-compose."""
        success, output = self._run_docker_compose_command(["up", "-d"])
        if not success:
            print(f"Failed to start container: {output}")
        return success

    def stop_container(self) -> bool:
        """Stop the nginx container using docker-compose."""
        success, output = self._run_docker_compose_command(["down"])
        if not success:
            print(f"Failed to stop container: {output}")
        return success

    def restart_container(self) -> bool:
        """Restart the nginx container using docker-compose."""
        success, output = self._run_docker_compose_command(["restart"])
        if not success:
            print(f"Failed to restart container: {output}")
        return success

    def reload_nginx(self) -> bool:
        """Reload nginx configuration without restarting the container."""
        if not self.container_is_running():
            # If container is not running, try to start it
            print("Container not running, starting...")
            return self.start_container()
        
        # Reload nginx configuration
        success, output = self._run_docker_command([
            "docker", "exec", self.container_name, 
            "nginx", "-s", "reload"
        ])
        
        if not success:
            print(f"Failed to reload nginx: {output}")
            # Try restarting the container as fallback
            print("Attempting container restart as fallback...")
            return self.restart_container()
        
        return success

    def test_nginx_config(self) -> bool:
        """Test nginx configuration for syntax errors."""
        if not self.container_is_running():
            # Test config by starting a temporary container
            success, output = self._run_docker_command([
                "docker", "run", "--rm", "-v", 
                f"{self.project_root}/nginx/nginx.conf:/etc/nginx/nginx.conf:ro",
                "nginx:alpine", "nginx", "-t"
            ])
        else:
            # Test config in running container
            success, output = self._run_docker_command([
                "docker", "exec", self.container_name, 
                "nginx", "-t"
            ])
        
        if not success:
            print(f"Nginx configuration test failed: {output}")
        
        return success

    def get_nginx_logs(self, lines: int = 50) -> str:
        """Get nginx logs from the container."""
        if not self.container_is_running():
            return "Container is not running"
        
        success, output = self._run_docker_command([
            "docker", "logs", "--tail", str(lines), self.container_name
        ])
        
        return output if success else f"Failed to get logs: {output}"

    def ensure_container_running(self) -> bool:
        """Ensure the container is running, start if needed."""
        if self.container_is_running():
            return True
        
        print("Starting nginx container...")
        return self.start_container()