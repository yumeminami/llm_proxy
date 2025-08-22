# LLM Proxy - Nginx反向代理

基于Docker的Nginx反向代理，用于代理各种LLM API请求。

## 启动代理

```bash
docker-compose up -d
```

**效果**：
- 访问 `http://localhost/openai/*` → 代理到 `https://api.openai.com/*`
- 访问 `http://localhost/health` → 健康检查
- 支持WebSocket流式响应

**测试**：
```bash
# 健康检查
curl http://localhost/health

# OpenAI API代理（需要API密钥）
curl -H "Authorization: Bearer your-api-key" \
     http://localhost/openai/v1/models
```

## 命令行工具

### 安装
```bash
uv sync && uv run pip install -e .
```

### 使用

```bash
# 添加代理：/claude → https://api.anthropic.com
llm-proxy add --endpoint /claude --base-url https://api.anthropic.com --name "Claude API"

# 添加带路径的代理：/v3 → https://cf.gpt.ge/v1
llm-proxy add --endpoint /v3 --base-url https://cf.gpt.ge/v1 --name "Custom API"

# 列出所有代理
llm-proxy list

# 删除代理
llm-proxy remove --endpoint /claude

# 查看状态
llm-proxy status
```

**参数说明**：
- `--endpoint` 本地路径（如 `/claude`）
- `--base-url` 目标API地址（如 `https://api.anthropic.com`）
- `--name` 可选的名称描述
- `--force` 强制覆盖已存在的配置

## SSL配置

### 1. 准备证书
```bash
mkdir ssl
# 将证书文件放入 ssl/ 目录：
# ssl/cert.pem - SSL证书
# ssl/key.pem - 私钥
```

### 2. 启用HTTPS
编辑 `nginx/nginx.conf`：
- 取消注释 HTTPS server 块
- 修改 `server_name your-domain.com` 为你的域名

编辑 `docker-compose.yml`：
- 取消注释 SSL 卷挂载行：`- ./ssl:/etc/nginx/ssl:ro`

### 3. 重启服务
```bash
docker-compose down && docker-compose up -d
```

**效果**：HTTPS访问 `https://your-domain.com/openai/*` 等端点