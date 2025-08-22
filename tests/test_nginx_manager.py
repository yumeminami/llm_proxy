"""Tests for nginx_manager module."""

import pytest
from pathlib import Path
from llm_proxy_cli.nginx_manager import NginxManager


class TestNginxManager:
    """Test cases for NginxManager class."""

    def test_parse_upstream_name(self):
        """Test upstream name generation."""
        manager = NginxManager.__new__(NginxManager)  # Create without __init__
        
        assert manager._parse_upstream_name("https://api.openai.com") == "api_openai_com_upstream"
        assert manager._parse_upstream_name("https://api.anthropic.com") == "api_anthropic_com_upstream"
        assert manager._parse_upstream_name("http://localhost:8080") == "localhost_upstream"

    def test_proxy_exists_detection(self, tmp_path):
        """Test proxy existence detection."""
        # Create a temporary nginx config
        config_file = tmp_path / "nginx.conf"
        config_content = """
        location /openai/ {
            proxy_pass https://openai_api;
        }
        
        location /claude/ {
            proxy_pass https://claude_api;
        }
        """
        config_file.write_text(config_content)
        
        manager = NginxManager(str(config_file))
        
        assert manager.proxy_exists("/openai/")
        assert manager.proxy_exists("/claude/")
        assert not manager.proxy_exists("/gpt/")