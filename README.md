# LLM Proxy - Nginx Reverse Proxy

A Docker-based Nginx reverse proxy for LLM APIs with dynamic configuration management.

## Features

- ✅ Reverse proxy `/openai/*` to `https://api.openai.com/*`
- ✅ WebSocket support for streaming responses
- ✅ HTTP and HTTPS support
- ✅ SSL certificate configuration ready
- ✅ Docker containerized deployment
- ✅ Health check endpoint
- ✅ Dynamic proxy management via CLI tool

## Quick Start

1. Start the service:

```bash
docker compose up -d
```

2. Test the proxy:

```bash
# Health check
curl http://localhost/health

# Test OpenAI proxy (requires API key)
curl -H "Authorization: Bearer your-api-key" \
     http://localhost/openai/v1/models
```

## CLI Tool

The project includes a Python command-line tool for dynamic proxy management:

### Install CLI Tool

```bash
# Using uv (recommended)
uv sync
uv run pip install -e .

# Or using traditional pip
pip install -e .
```

### Usage Examples

```bash
# Add new proxy
llm-proxy add --endpoint /claude --base-url https://api.anthropic.com

# List all proxies
llm-proxy list

# Check service status
llm-proxy status

# Remove proxy
llm-proxy remove --endpoint /claude
```

For detailed CLI usage, see [CLI_README.md](CLI_README.md)

## SSL Certificate Configuration

When you have a domain and SSL certificates:

1. Create SSL certificate directory:

```bash
mkdir ssl
```

2. Place certificate files in ssl directory:
   - `ssl/cert.pem` - SSL certificate
   - `ssl/key.pem` - Private key

3. Edit `nginx/nginx.conf`:
   - Uncomment the HTTPS server block
   - Update `server_name` with your domain

4. Edit `docker-compose.yml`:
   - Uncomment the SSL volume mount line

5. Restart the service:

```bash
docker-compose down
docker-compose up -d
```

## Project Structure

```
llm_proxy/
├── docker-compose.yml          # Docker Compose configuration
├── nginx/
│   └── nginx.conf             # Nginx configuration file
├── llm_proxy_cli/            # Python CLI tool
│   ├── __init__.py
│   ├── main.py              # Main CLI interface
│   ├── nginx_manager.py     # Nginx configuration management
│   └── docker_manager.py    # Docker container management
├── ssl/                      # SSL certificates directory (create when needed)
├── logs/                     # Nginx logs directory
├── pyproject.toml           # Project configuration
├── .pre-commit-config.yaml  # Pre-commit hooks
├── Makefile                 # Development commands
└── README.md               # Documentation
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
make dev-install

# Or manually
uv sync --dev
uv run pre-commit install
```

### Available Commands

```bash
make help          # Show all available commands
make lint          # Run linting
make format        # Format code
make test          # Run tests
make docker-up     # Start Docker containers
make docker-down   # Stop Docker containers
```

### Code Quality

The project uses:

- **Black** for code formatting
- **Ruff** for linting and import sorting
- **MyPy** for type checking
- **Pre-commit** hooks for automated quality checks

### CLI Tool Features

- **Dynamic Configuration**: Add/remove proxies without manual nginx.conf editing
- **Duplicate Detection**: Automatically detects existing configurations
- **Auto Reload**: Automatically reloads nginx after configuration changes
- **WebSocket Support**: Automatically configures WebSocket proxying
- **HTTP/HTTPS**: Configures both HTTP and HTTPS proxies
- **Container Management**: Integrated Docker container operations
- **Configuration Validation**: Automatic nginx configuration syntax validation

## Usage Examples

### HTTP Requests

```bash
curl -H "Authorization: Bearer sk-your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Hello"}]}' \
     http://localhost/openai/v1/chat/completions
```

### HTTPS Requests (after SSL setup)

```bash
curl -H "Authorization: Bearer sk-your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Hello"}]}' \
     https://your-domain.com/openai/v1/chat/completions
```

### Adding Custom API Proxies

```bash
# Add Anthropic Claude API
llm-proxy add --endpoint /claude --base-url https://api.anthropic.com --name "Claude API"

# Add custom API
llm-proxy add --endpoint /custom --base-url https://api.custom.com --name "Custom API"

# Test the new proxy
curl -H "Authorization: Bearer your-key" \
     http://localhost/claude/v1/messages
```

## Notes

- Ensure you have valid API keys for the services you're proxying
- SSL certificate configuration is optional; you can use HTTP without certificates
- WebSocket support is pre-configured for streaming responses
- Log files are saved in the `logs/` directory
- The CLI tool must be run from the project root directory containing `docker-compose.yml`

## Troubleshooting

### Container Not Running

```bash
# Check container status
llm-proxy status

# Start container manually
docker-compose up -d
```

### Configuration Syntax Errors

```bash
# Test nginx configuration
llm-proxy status  # Shows if configuration is valid

# View nginx logs
docker logs llm_proxy_nginx
```

### Permission Issues

Make sure your user has Docker permissions:

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Refresh group membership
newgrp docker
```

## License

This project is open source. Please check the LICENSE file for details.