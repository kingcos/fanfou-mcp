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
- 请将环境变量中的占位符替换为你的实际饭否 API 凭据

## 可用工具

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