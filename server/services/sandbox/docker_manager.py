"""Docker manager for code execution sandbox."""

from typing import Dict, Any, Optional
import docker
import os

class DockerManager:
    """Manage Docker containers for code execution."""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            print(f"Failed to connect to Docker: {e}")
            self.client = None
    
    def create_container(self, image: str, command: str, **kwargs) -> Optional[Any]:
        """Create a new container."""
        if not self.client:
            return None
        
        try:
            container = self.client.containers.create(
                image=image,
                command=command,
                **kwargs
            )
            return container
        except Exception as e:
            print(f"Failed to create container: {e}")
            return None
    
    def start_container(self, container_id: str) -> bool:
        """Start a container."""
        if not self.client:
            return False
        
        try:
            container = self.client.containers.get(container_id)
            container.start()
            return True
        except Exception as e:
            print(f"Failed to start container: {e}")
            return False
    
    def stop_container(self, container_id: str) -> bool:
        """Stop a container."""
        if not self.client:
            return False
        
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            return True
        except Exception as e:
            print(f"Failed to stop container: {e}")
            return False
    
    def remove_container(self, container_id: str) -> bool:
        """Remove a container."""
        if not self.client:
            return False
        
        try:
            container = self.client.containers.get(container_id)
            container.remove()
            return True
        except Exception as e:
            print(f"Failed to remove container: {e}")
            return False
    
    def get_container_logs(self, container_id: str) -> str:
        """Get container logs."""
        if not self.client:
            return ""
        
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs()
            return logs.decode('utf-8')
        except Exception as e:
            print(f"Failed to get logs: {e}")
            return ""

