# LLM Proxy - Nginx Reverse Proxy

Docker-based Nginx reverse proxy for LLM API requests.

## Start Proxy

```bash
docker-compose up -d
```

**Effect**:

- Access `http://localhost/openai/*` → Proxy to `https://api.openai.com/*`
- Access `http://localhost/health` → Health check
- Support WebSocket streaming

**Test**:

```bash
# Health check
curl http://localhost/health

# OpenAI API proxy (requires API key)
curl -H "Authorization: Bearer your-api-key" \
     http://localhost/openai/v1/models
```

## CLI Tool

### Install

```bash
uv sync && uv run pip install -e .
```

### Usage

```bash
# Add proxy: /claude → https://api.anthropic.com
llm-proxy add --endpoint /claude --base-url https://api.anthropic.com --name "Claude API"

# Add proxy with path: /v3 → https://cf.gpt.ge/v1
llm-proxy add --endpoint /v3 --base-url https://cf.gpt.ge/v1 --name "Custom API"

# List all proxies
llm-proxy list

# Remove proxy
llm-proxy remove --endpoint /claude

# Check status
llm-proxy status
```

**Parameters**:

- `--endpoint` Local path (e.g. `/claude`)
- `--base-url` Target API URL (e.g. `https://api.anthropic.com`)
- `--name` Optional name description
- `--force` Force overwrite existing configuration

## SSL Configuration

### 1. Prepare Certificates

```bash
mkdir ssl
# Place certificate files in ssl/ directory:
# ssl/cert.pem - SSL certificate
# ssl/key.pem - Private key
```

### 2. Enable HTTPS

Edit `nginx/nginx.conf`:

- Uncomment HTTPS server block
- Change `server_name your-domain.com` to your domain

Edit `docker-compose.yml`:

- Uncomment SSL volume mount: `- ./ssl:/etc/nginx/ssl:ro`

### 3. Restart Service

```bash
docker-compose down && docker-compose up -d
```

**Effect**: HTTPS access to `https://your-domain.com/openai/*` endpoints