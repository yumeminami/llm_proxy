"""Nginx configuration management."""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse


class NginxManager:
    """Manages nginx configuration for proxy settings."""
    
    def __init__(self, config_path: str = None):
        """Initialize NginxManager with configuration path."""
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Default to nginx/nginx.conf relative to current working directory
            self.config_path = Path.cwd() / "nginx" / "nginx.conf"
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Nginx configuration file not found: {self.config_path}")
    
    def _read_config(self) -> str:
        """Read the nginx configuration file."""
        return self.config_path.read_text()
    
    def _write_config(self, content: str) -> bool:
        """Write content to nginx configuration file."""
        try:
            # Create backup
            backup_path = self.config_path.with_suffix('.conf.backup')
            backup_path.write_text(self._read_config())
            
            # Write new content
            self.config_path.write_text(content)
            return True
        except Exception as e:
            print(f"Error writing config: {e}")
            return False
    
    def _parse_upstream_name(self, base_url: str) -> str:
        """Generate upstream name from base URL."""
        parsed = urlparse(base_url)
        # Clean hostname and replace dots/hyphens with underscores
        clean_name = re.sub(r'[.-]', '_', parsed.hostname or 'unknown')
        return f"{clean_name}_upstream"
    
    def _generate_upstream_block(self, base_url: str, upstream_name: str) -> str:
        """Generate upstream configuration block."""
        parsed = urlparse(base_url)
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        
        return f"""    # Upstream for {base_url}
    upstream {upstream_name} {{
        server {parsed.hostname}:{port};
        keepalive 32;
    }}"""
    
    def _generate_location_block(self, endpoint: str, base_url: str, upstream_name: str, name: str = None) -> str:
        """Generate location configuration block."""
        parsed = urlparse(base_url)
        comment = f"# {name}" if name else f"# Proxy for {base_url}"
        
        # Determine if we need SSL
        proxy_pass_scheme = parsed.scheme
        ssl_config = ""
        if parsed.scheme == 'https':
            ssl_config = """
            proxy_ssl_server_name on;
            proxy_ssl_name """ + parsed.hostname + ";"
        
        # Handle base URL path - if base_url has a path, include it in rewrite rule
        base_path = parsed.path.rstrip('/') if parsed.path and parsed.path != '/' else ''
        proxy_pass_url = f"{proxy_pass_scheme}://{upstream_name}"
        
        # Generate rewrite rule based on whether base_url has a path
        if base_path:
            rewrite_rule = f"rewrite ^{re.escape(endpoint.rstrip('/'))}/(.*) {base_path}/$1 break;"
        else:
            rewrite_rule = f"rewrite ^{re.escape(endpoint.rstrip('/'))}/(.*) /$1 break;"
        
        return f"""        
        {comment}
        location {endpoint} {{
            # Remove {endpoint.rstrip('/')} prefix and pass to upstream
            {rewrite_rule}
            
            proxy_pass {proxy_pass_url};{ssl_config}
            
            # Headers for proper proxying
            proxy_set_header Host {parsed.hostname};
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            
            # Timeout settings
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # Buffer settings for streaming
            proxy_buffering off;
            proxy_cache_bypass $http_upgrade;
        }}"""
    
    def proxy_exists(self, endpoint: str) -> bool:
        """Check if a proxy configuration already exists for the endpoint."""
        config = self._read_config()
        # Look for location block with this endpoint
        pattern = rf'location\s+{re.escape(endpoint)}\s*{{'
        return bool(re.search(pattern, config))
    
    def add_proxy(self, endpoint: str, base_url: str, name: str = None) -> bool:
        """Add a new proxy configuration."""
        try:
            config = self._read_config()
            upstream_name = self._parse_upstream_name(base_url)
            
            # Store the original base_url as a comment in upstream for later retrieval
            upstream_comment = f"# Upstream for {base_url}"
            
            # Check if upstream already exists
            upstream_pattern = rf'upstream\s+{upstream_name}\s*{{'
            if not re.search(upstream_pattern, config):
                # Add upstream block after the existing upstreams
                upstream_block = self._generate_upstream_block(base_url, upstream_name)
                # Replace the comment to include full URL
                upstream_block = upstream_block.replace(f"# Upstream for {base_url}", upstream_comment)
                
                # Find the position to insert upstream (after last upstream or before first server)
                upstream_insert_pattern = r'(\s*# Upstream for [^\n]*\n\s*upstream [^}]+}\n)'
                matches = list(re.finditer(upstream_insert_pattern, config))
                
                if matches:
                    # Insert after last upstream
                    last_match = matches[-1]
                    insert_pos = last_match.end()
                else:
                    # Insert before first server block
                    server_pattern = r'\n(\s*# HTTP server)'
                    server_match = re.search(server_pattern, config)
                    if server_match:
                        insert_pos = server_match.start() + 1
                    else:
                        raise Exception("Could not find position to insert upstream")
                
                config = config[:insert_pos] + "\n" + upstream_block + "\n" + config[insert_pos:]
            
            # Add location blocks to both HTTP and HTTPS servers
            location_block = self._generate_location_block(endpoint, base_url, upstream_name, name)
            
            # Add to HTTP server (find the OpenAI location block and add after it)
            http_pattern = r'(# OpenAI API proxy\n\s*location /openai/ \{[^}]+\})'
            http_match = re.search(http_pattern, config, re.DOTALL)
            
            if http_match:
                insert_pos = http_match.end()
                config = config[:insert_pos] + location_block + config[insert_pos:]
            else:
                raise Exception("Could not find HTTP server section to insert location")
            
            # Add to HTTPS server (commented section) if it exists
            https_pattern = r'(#\s*# OpenAI API proxy \(same as HTTP\)\n\s*#\s*location /openai/ \{[^}]+\})'
            https_match = re.search(https_pattern, config, re.DOTALL)
            
            if https_match:
                # Generate commented version of location block for HTTPS
                https_location_block = "\n".join(f"    #{line}" for line in location_block.split("\n"))
                insert_pos = https_match.end()
                config = config[:insert_pos] + https_location_block + config[insert_pos:]
            
            return self._write_config(config)
        
        except Exception as e:
            print(f"Error adding proxy: {e}")
            return False
    
    def remove_proxy(self, endpoint: str) -> bool:
        """Remove a proxy configuration."""
        try:
            config = self._read_config()
            
            # Remove location block from HTTP server
            location_pattern = rf'\s*# [^\n]*\n\s*location\s+{re.escape(endpoint)}\s*\{{[^}}]+\}}'
            config = re.sub(location_pattern, '', config, flags=re.DOTALL)
            
            # Remove location block from HTTPS server (commented)
            https_location_pattern = rf'\s*#\s*# [^\n]*\n(\s*#\s*location\s+{re.escape(endpoint)}\s*\{{[^}}]+\}})'
            config = re.sub(https_location_pattern, '', config, flags=re.DOTALL | re.MULTILINE)
            
            # TODO: Optionally remove unused upstream blocks
            
            return self._write_config(config)
        
        except Exception as e:
            print(f"Error removing proxy: {e}")
            return False
    
    def list_proxies(self) -> List[Dict[str, str]]:
        """List all proxy configurations."""
        try:
            config = self._read_config()
            proxies = []
            
            # Find all location blocks (excluding /openai and /health)
            location_pattern = r'# ([^\n]*)\n\s*location\s+([^\s]+)\s*\{[^}]*proxy_pass\s+[^:]+://([^/;]+)[^}]*\}'
            matches = re.findall(location_pattern, config, re.DOTALL)
            
            for match in matches:
                comment, endpoint, upstream = match
                if endpoint not in ['/openai/', '/health']:
                    # Try to extract the original URL from upstream comment
                    upstream_comment_pattern = rf'# Upstream for ([^\n]+)\n\s*upstream\s+{re.escape(upstream)}'
                    upstream_comment_match = re.search(upstream_comment_pattern, config)
                    
                    if upstream_comment_match:
                        # Use the full URL from the comment
                        target_url = upstream_comment_match.group(1)
                    else:
                        # Fallback to reconstructing from server info
                        upstream_pattern = rf'upstream\s+{re.escape(upstream)}\s*\{{\s*server\s+([^;]+);'
                        upstream_match = re.search(upstream_pattern, config)
                        
                        if upstream_match:
                            server_info = upstream_match.group(1)
                            # Reconstruct URL (assuming https for port 443, http for others)
                            if ':443' in server_info:
                                target_url = f"https://{server_info.replace(':443', '')}"
                            else:
                                target_url = f"http://{server_info}"
                        else:
                            target_url = f"upstream://{upstream}"
                    
                    proxies.append({
                        'endpoint': endpoint,
                        'target': target_url,
                        'name': comment if not comment.startswith('Proxy for') else None
                    })
            
            return proxies
        
        except Exception as e:
            print(f"Error listing proxies: {e}")
            return []