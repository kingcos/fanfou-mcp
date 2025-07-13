# 饭否 MCP 服务器

基于 FastMCP 构建的饭否（Fanfou）MCP 服务器，提供饭否相关的工具和服务。

[![Publish to PyPI](https://github.com/kingcos/fanfou-mcp/actions/workflows/publish.yml/badge.svg)](https://github.com/kingcos/fanfou-mcp/actions/workflows/publish.yml)

## 功能特性

- 🛠️ 基于 FastMCP 框架构建
- 🔧 提供饭否相关的工具函数
- 📡 支持 MCP (Model Context Protocol) 协议
- 🐍 使用 Python 3.11+ 开发

## 快速开始

### 前提条件

- Python 3.11+
- uv 包管理器（用于 `uvx` 命令）
- 饭否账号和 API 密钥

### 使用方式

#### 推荐：直接使用 uvx（无需本地安装）

```bash
# uvx 会自动从 PyPI 下载并运行最新版本
uvx fanfou-mcp

# 如果遇到缓存问题，可以强制重新安装最新版本
uvx --force-reinstall fanfou-mcp
```

#### 本地开发模式

如果你需要修改代码或进行开发：

```bash
# 克隆仓库
git clone https://github.com/kingcos/fanfou-mcp.git
cd fanfou-mcp

# 安装依赖
uv sync

# 运行服务器
python main.py
# 或者使用 uv
uv run main.py
```

## 客户端配置

### MCP 配置

#### 方式1：使用 uvx（推荐，无需本地安装）

```json
{
  "mcpServers": {
    "fanfou-mcp": {
      "command": "uvx",
      "args": ["fanfou-mcp"],
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

**如果遇到导入错误，请使用强制更新版本**：

```json
{
  "mcpServers": {
    "fanfou-mcp": {
      "command": "uvx",
      "args": ["--force-reinstall", "fanfou-mcp"],
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

#### 方式2：使用 uvx + 用户名密码（首次登录）

```json
{
  "mcpServers": {
    "fanfou-mcp": {
      "command": "uvx",
      "args": ["fanfou-mcp"],
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

#### 方式3：本地开发模式

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

**注意**: 
- **推荐使用方式1**：`uvx` 会自动从 PyPI 下载和运行最新版本，无需本地安装
- **缓存问题**：如果遇到导入错误，可能是 `uvx` 缓存了旧版本，请在配置中将 `"args": ["fanfou-mcp"]` 改为 `"args": ["--force-reinstall", "fanfou-mcp"]` 来强制更新
- **OAuth Token 方式**：避免每次都需要登录，更安全便捷
- **首次使用**：如果没有 OAuth Token，请先使用方式2，系统会自动生成并显示 OAuth Token，然后切换到方式1
- **本地开发**：如果你需要修改代码或调试，可以使用方式3
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

## 开发和发布

### 本地测试构建

```bash
# 测试包构建
python scripts/test_build.py

# 手动构建
uv build
```

### 发布到 PyPI

本项目使用 GitHub Actions 自动发布到 PyPI。详细信息请参考：[发布指南](docs/PUBLISHING.md)

## 文档

- [API 文档](docs/API.md) - 详细的工具函数说明
- [发布指南](docs/PUBLISHING.md) - 如何发布到 PyPI

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。