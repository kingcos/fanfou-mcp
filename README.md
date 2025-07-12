# 饭否 MCP 服务器

基于 FastMCP 构建的饭否（Fanfou）MCP 服务器，提供饭否相关的工具和服务。

## 功能特性

- 🛠️ 基于 FastMCP 框架构建
- 🔧 提供饭否相关的工具函数
- 📡 支持 MCP (Model Context Protocol) 协议
- 🐍 使用 Python 3.11+ 开发

## 安装和运行

### 前提条件

- Python 3.11+
- uv 包管理器
- 饭否账号和 API 密钥

### 安装依赖

```bash
# 安装依赖
uv sync
```

### 运行服务器

```bash
# 直接运行
python main.py

# 或者使用 uv
uv run main.py
```

## 客户端配置

### MCP 配置

#### 方式1：使用 OAuth Token（推荐）

```json
{
  "mcpServers": {
    "fanfou-mcp": {
      "command": "uv",
      "args": ["--directory", "/path/to/your/fanfou-mcp/main.py", "run", "python", "main.py"],
      "env": {
        "FANFOU_API_KEY": "your_api_key_here",
        "FANFOU_API_SECRET": "your_api_secret_here",
        "FANFOU_OAUTH_TOKEN": "your_oauth_token_here",
        "FANFOU_OAUTH_TOKEN_SECRET": "your_oauth_token_secret_here"
      }
    }
  }
}
```

#### 方式2：使用用户名密码（首次登录）

```json
{
  "mcpServers": {
    "fanfou-mcp": {
      "command": "uv",
      "args": ["--directory", "/path/to/your/fanfou-mcp/main.py", "run", "python", "main.py"],
      "env": {
        "FANFOU_API_KEY": "your_api_key_here",
        "FANFOU_API_SECRET": "your_api_secret_here",
        "FANFOU_USERNAME": "your_username_here",
        "FANFOU_PASSWORD": "your_password_here"
      }
    }
  }
}
```

**注意**: 
- 请将 `/path/to/your/fanfou-mcp/main.py` 替换为你项目的实际路径
- **推荐使用方式1**：OAuth Token 方式避免每次都需要登录
- **首次使用**：如果没有 OAuth Token，请先使用方式2，系统会自动生成并显示 OAuth Token，然后切换到方式1
- 请将环境变量中的占位符替换为你的实际饭否 API 凭据

## 可用工具

### generate_oauth_token

生成 OAuth Token

**功能:**
- 使用用户名密码生成 OAuth Token
- 用于后续免密登录，避免重复输入用户名密码

**前提条件:**
- 需要设置 `FANFOU_USERNAME` 和 `FANFOU_PASSWORD` 环境变量

**返回:**
- 包含 OAuth Token 信息的字典
- 控制台会显示详细的 Token 信息和使用说明

### get_user_timeline

获取用户时间线

**参数:**
- `max_id` (str, 可选): 最大 ID，用于分页，默认为空字符串
- `count` (int, 可选): 获取数量，默认 10 条

**返回:**
- 用户时间线列表，包含以下字段：
  - `饭否内容`: 饭否消息内容
  - `图片链接`: 如果有图片，返回图片的大图链接

### get_home_timeline

获取首页时间线

**参数:**
- `count` (int, 可选): 获取数量，默认 20 条
- `max_id` (str, 可选): 最大 ID，用于分页，默认为空字符串

**返回:**
- 首页时间线列表，包含以下字段：
  - `饭否内容`: 饭否消息内容
  - `发布时间`: 消息发布时间
  - `发布者`: 发布者昵称
  - `发布者 ID`: 发布者的用户ID
  - `图片链接`: 如果有图片，返回图片的大图链接

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。