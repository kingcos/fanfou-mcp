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

根据用户 ID 获取某个用户发表内容的时间线

**功能:**
- 调用饭否 API 的 /statuses/user_timeline.json 接口获取指定用户的时间线
- 当提供搜索关键词时，会调用 /search/user_timeline.json 接口进行搜索

**参数:**
- `user_id` (str, 可选): 用户 ID，如果为空则获取当前用户时间线
- `max_id` (str, 可选): 返回列表中内容最新 ID，用于分页获取更早的内容
- `count` (int, 可选): 获取数量，默认 5 条
- `q` (str, 可选): 搜索关键词，如果为空则获取普通用户时间线；如果不为空则搜索该用户包含该关键词的消息

**返回:**
- 用户时间线列表，包含以下字段：
  - `饭否内容`: 饭否消息内容（HTML 格式）
  - `发布 ID`: 消息的唯一标识符
  - `发布时间`: 消息发布时间
  - `发布者`: 发布者的用户名
  - `发布者 ID`: 发布者的用户 ID
  - `图片链接`: 如果包含图片，则提供图片链接

### get_home_timeline

获取当前用户首页关注用户及自己的饭否时间线

**功能:**
- 调用饭否 API 的 /statuses/home_timeline.json 接口获取当前用户的首页时间线
- 包含用户关注的所有人的最新消息
- 注：通常用户询问「我的饭否」时，指的是该时间线，除非用户明确指出「某个用户的饭否」

**参数:**
- `count` (int, 可选): 获取数量，默认 5 条
- `max_id` (str, 可选): 返回列表中内容最新 ID，用于分页获取更早的内容

**返回:**
- 首页时间线列表，包含以下字段：
  - `饭否内容`: 饭否消息内容（HTML 格式）
  - `发布 ID`: 消息的唯一标识符
  - `发布时间`: 消息发布时间
  - `发布者`: 发布者的用户名
  - `发布者 ID`: 发布者的用户 ID
  - `图片链接`: 如果包含图片，则提供图片链接

### get_public_timeline

获取公开时间线

**功能:**
- 调用饭否 API 的 /statuses/public_timeline.json 接口获取饭否全站最新的公开消息
- 这些是所有用户可见的公开饭否内容
- 当提供搜索关键词时，会调用 /search/public_timeline.json 接口进行搜索

**参数:**
- `count` (int, 可选): 获取数量，默认 5 条
- `max_id` (str, 可选): 返回列表中内容最新 ID，用于分页获取更早的内容
- `q` (str, 可选): 搜索关键词，如果为空则获取普通公开时间线；如果不为空则搜索包含该关键词的公开消息

**返回:**
- 公开时间线列表，包含以下字段：
  - `饭否内容`: 饭否消息内容（HTML 格式）
  - `发布 ID`: 消息的唯一标识符
  - `发布时间`: 消息发布时间
  - `发布者`: 发布者的用户名
  - `发布者 ID`: 发布者的用户 ID
  - `图片链接`: 如果包含图片，则提供图片链接

### get_user_info

获取用户信息

**功能:**
- 调用饭否 API 的 /users/show.json 接口获取指定用户的详细信息
- 如果 user_id 为空，则获取当前登录用户的信息

**参数:**
- `user_id` (str, 可选): 用户 ID，如果为空则获取当前用户信息

**返回:**
- 用户信息字典，包含以下字段：
  - `用户 ID`: 用户的唯一标识符
  - `用户名`: 用户名
  - `位置`: 用户所在位置
  - `性别`: 用户性别
  - `生日`: 用户生日
  - `描述`: 用户个人描述
  - `头像`: 用户头像链接
  - `链接`: 用户个人网站链接
  - `是否加锁`: 账号是否受保护
  - `粉丝数`: 被关注数量
  - `朋友数`: 互相关注数量
  - `收藏数`: 收藏的消息数量
  - `发布数`: 发布的消息数量
  - `照片数`: 发布的照片数量
  - `是否关注`: 当前用户是否关注该用户
  - `注册时间`: 账号注册时间
  - `最新状态`: 用户最新发布的消息信息（包含发布时间、发布 ID、发布内容）

### get_status_info

获取某条饭否内容的具体信息

**功能:**
- 调用饭否 API 的 /statuses/show/id.json 接口获取指定饭否内容的详细信息

**参数:**
- `status_id` (str, 必需): 饭否内容的 ID

**返回:**
- 饭否内容的详细信息字典，包含以下字段：
  - `饭否内容`: 消息文本内容（HTML 格式）
  - `发布 ID`: 消息的唯一标识符
  - `发布时间`: 消息发布时间
  - `发布者`: 发布者的显示名称
  - `发布者 ID`: 发布者的用户 ID
  - `是否收藏`: 当前用户是否收藏了该消息
  - `是否是自己`: 是否是当前用户发布的消息
  - `发布位置`: 消息发布的地理位置
  - `回复信息`: 如果是回复消息，包含被回复的状态 ID、用户 ID 和用户名
  - `图片链接`: 如果包含图片，则提供图片链接

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。