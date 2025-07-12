# 饭否 MCP 服务器

基于 FastMCP 构建的饭否（Fanfou）MCP 服务器，提供饭否相关的工具和服务。

## 功能特性

- 🛠️ 基于 FastMCP 框架构建
- 🔧 提供饭否相关的工具函数
- 📡 支持 MCP (Model Context Protocol) 协议
- 🐍 使用 Python 3.11+ 开发

## 快速开始

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
      "args": ["--directory", "/path/to/your/fanfou-mcp", "run", "python", "main.py"],
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
      "args": ["--directory", "/path/to/your/fanfou-mcp", "run", "python", "main.py"],
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
- 请将 `/path/to/your/fanfou-mcp` 替换为你项目的实际路径
- **推荐使用方式1**：OAuth Token 方式避免每次都需要登录
- **首次使用**：如果没有 OAuth Token，请先使用方式2，系统会自动生成并显示 OAuth Token，然后切换到方式1
- 请将环境变量中的占位符替换为你的实际饭否 API 凭据

## 可用工具

本服务器提供以下工具：

### 认证相关
- `generate_oauth_token` - 生成 OAuth Token

### 时间线相关
- `get_home_timeline` - 获取首页时间线
- `get_user_timeline` - 获取用户时间线
- `get_public_timeline` - 获取公开时间线

### 用户和内容相关
- `get_user_info` - 获取用户信息
- `get_status_info` - 获取饭否内容详情

### 互动相关
- `manage_favorite` - 管理收藏状态
- `manage_friendship` - 管理关注状态

### 发布相关
- `publish_status` - 发布文字内容
- `publish_photo` - 发布图片内容
- `delete_status` - 删除内容

详细的 API 文档请参考：[API 文档](docs/API.md)

## 文档

- [API 文档](docs/API.md) - 详细的工具函数说明

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。