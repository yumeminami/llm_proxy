# LLM Proxy - Nginx反向代理

这个项目实现了一个基于Docker的Nginx反向代理，用于代理OpenAI API请求。

## 功能特性

- ✅ 反向代理 `/openai/*` 到 `https://api.openai.com/*`
- ✅ 支持WebSocket连接
- ✅ 支持HTTP和HTTPS
- ✅ 预配置SSL证书支持
- ✅ Docker容器化部署
- ✅ 健康检查

## 快速开始

1. 启动服务：

```bash
docker-compose up -d
```

2. 测试代理：

```bash
# 测试健康检查
curl http://localhost/health

# 测试OpenAI代理（需要API密钥）
curl -H "Authorization: Bearer your-api-key" \
     http://localhost/openai/v1/models
```

## SSL证书配置

当你有域名和SSL证书时：

1. 创建SSL证书目录：

```bash
mkdir ssl
```

2. 将证书文件放入ssl目录：
   - `ssl/cert.pem` - SSL证书
   - `ssl/key.pem` - 私钥

3. 编辑 `nginx/nginx.conf`：
   - 取消注释HTTPS server块
   - 更新 `server_name` 为你的域名

4. 编辑 `docker-compose.yml`：
   - 取消注释SSL卷挂载行

5. 重启服务：

```bash
docker-compose down
docker-compose up -d
```

## 项目结构

```text
llm_proxy/
├── docker-compose.yml      # Docker Compose配置
├── nginx/
│   └── nginx.conf         # Nginx配置文件
├── ssl/                   # SSL证书目录（需要时创建）
├── logs/                  # Nginx日志目录
├── .env.example          # 环境变量示例
└── README.md             # 说明文档
```

## 使用示例

### HTTP请求

```bash
curl -H "Authorization: Bearer sk-your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Hello"}]}' \
     http://localhost/openai/v1/chat/completions
```

### HTTPS请求（配置SSL后）

```bash
curl -H "Authorization: Bearer sk-your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Hello"}]}' \
     https://your-domain.com/openai/v1/chat/completions
```

## 命令行工具

项目包含了一个 Python 命令行工具用于动态管理代理配置：

### 安装 CLI 工具

```bash
# 使用 uv 管理依赖
uv sync
uv run pip install -e .

# 或使用传统 pip
pip install -e .
```

### 使用示例

```bash
# 添加新的代理
llm-proxy add --endpoint /claude --base-url https://api.anthropic.com

# 列出所有代理
llm-proxy list

# 查看服务状态
llm-proxy status

# 删除代理
llm-proxy remove --endpoint /claude
```

详细使用方法请参考 [CLI_README.md](CLI_README.md)

## 开发

### 开发环境设置

```bash
# 安装开发依赖
make dev-install

# 或手动安装
uv sync --dev
uv run pre-commit install
```

### 可用命令

```bash
make help          # 显示所有可用命令
make lint          # 运行代码检查
make format        # 格式化代码
make test          # 运行测试
make docker-up     # 启动Docker容器
make docker-down   # 停止Docker容器
```

## 注意事项

- 确保你有有效的OpenAI API密钥
- SSL证书配置是可选的，没有证书时可以使用HTTP
- WebSocket支持已预配置，适用于流式响应
- 日志文件会保存在 `logs/` 目录中
