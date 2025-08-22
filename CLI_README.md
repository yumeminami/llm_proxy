# LLM Proxy CLI 命令行工具

用于动态管理 Nginx 反向代理配置的 Python 命令行工具。

## 安装

使用 `uv` 管理 Python 环境和依赖：

```bash
# 安装 uv (如果还没有安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖并设置开发环境
uv sync

# 安装命令行工具
uv run pip install -e .
```

或者使用传统的 pip 安装：

```bash
pip install -e .
```

## 使用方法

### 1. 添加新的代理配置

```bash
# 基本用法
llm-proxy add --endpoint /claude --base-url https://api.anthropic.com

# 带名称的配置
llm-proxy add --endpoint /gpt --base-url https://api.openai.com --name "OpenAI GPT API"

# 强制覆盖已存在的配置
llm-proxy add --endpoint /claude --base-url https://api.anthropic.com --force
```

### 2. 列出所有代理配置

```bash
llm-proxy list
```

### 3. 删除代理配置

```bash
# 删除指定端点的代理
llm-proxy remove --endpoint /claude

# 强制删除（跳过确认）
llm-proxy remove --endpoint /claude --force
```

### 4. 查看服务状态

```bash
llm-proxy status
```

### 5. 重新加载 Nginx 配置

```bash
llm-proxy reload
```

## 示例场景

### 添加 Anthropic Claude API 代理

```bash
llm-proxy add --endpoint /claude --base-url https://api.anthropic.com --name "Claude API"
```

添加后，你可以通过以下方式访问：
- HTTP: `http://localhost/claude/v1/messages`
- HTTPS: `https://your-domain.com/claude/v1/messages` (配置 SSL 后)

### 添加 OpenAI API 代理

```bash
llm-proxy add --endpoint /gpt --base-url https://api.openai.com --name "OpenAI API"
```

### 添加自定义 API 代理

```bash
llm-proxy add --endpoint /custom --base-url https://api.custom.com --name "Custom API"
```

## 功能特性

- ✅ **动态配置**: 无需手动编辑 nginx.conf
- ✅ **重复检测**: 自动检测已存在的配置
- ✅ **自动重载**: 配置更改后自动重载 nginx
- ✅ **WebSocket 支持**: 自动配置 WebSocket 代理
- ✅ **HTTP/HTTPS**: 同时配置 HTTP 和 HTTPS 代理
- ✅ **容器管理**: 集成 Docker 容器操作
- ✅ **配置验证**: 自动验证 nginx 配置语法

## 注意事项

1. **工作目录**: 命令需要在包含 `docker-compose.yml` 和 `nginx/` 目录的项目根目录下运行

2. **Docker 要求**: 需要安装 Docker 和 docker-compose

3. **权限**: 可能需要 Docker 操作权限

4. **端点格式**: 
   - 端点会自动添加 `/` 前缀和后缀
   - 例如：`claude` → `/claude/`

5. **SSL 配置**: HTTPS 配置会自动添加到注释的 HTTPS server 块中，当你启用 SSL 时取消注释即可

## 开发

```bash
# 安装开发依赖
uv sync --dev

# 运行代码格式化
uv run black llm_proxy_cli/
uv run ruff check llm_proxy_cli/ --fix

# 运行测试
uv run pytest
```

## 故障排除

### 容器未运行

```bash
# 检查容器状态
llm-proxy status

# 手动启动容器
docker-compose up -d
```

### 配置语法错误

```bash
# 测试 nginx 配置
llm-proxy status  # 会显示配置是否有效

# 查看 nginx 日志
docker logs llm_proxy_nginx
```

### 权限问题

确保当前用户有 Docker 操作权限：

```bash
# 添加用户到 docker 组
sudo usermod -aG docker $USER

# 重新登录或刷新组权限
newgrp docker
```