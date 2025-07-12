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

### Claude Desktop 配置

在 Claude Desktop 中配置此 MCP 服务器：

1. 打开 Claude Desktop 配置文件：
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. 添加服务器配置：

```json
{
  "mcpServers": {
    "fanfou-mcp": {
      "command": "uv",
      "args": ["run", "python", "/path/to/your/fanfou-mcp/main.py"],
      "env": {}
    }
  }
}
```

**注意**: 请将 `/path/to/your/fanfou-mcp/main.py` 替换为你项目的实际路径。

### 其他 MCP 客户端配置

对于其他支持 MCP 的客户端（如 Cline、Continue 等），通常需要：

1. 配置服务器命令：
   ```bash
   uv run python /path/to/your/fanfou-mcp/main.py
   ```

2. 设置传输方式为 `stdio`

3. 确保客户端可以访问到 `uv` 和 Python 环境

### 快速配置

使用项目提供的配置脚本快速生成正确的配置：

```bash
python get_config.py
```

这个脚本会：
1. 自动生成包含正确路径的配置文件内容
2. 显示你系统上的 Claude Desktop 配置文件位置
3. 提供详细的配置步骤说明

### 验证配置

配置完成后，重启客户端，你应该能看到以下工具可用：
- `hello_fanfou`: 向饭否世界问好
- `get_fanfou_info`: 获取饭否平台信息

## 可用工具

### hello_fanfou

向饭否世界问好

**参数:**
- `name` (str, 可选): 要问候的名字，默认为 "世界"

**返回:**
- 问候语字符串

### get_fanfou_info

获取饭否平台的基本信息

**返回:**
- 包含饭否平台信息的字典

## 开发

### 项目结构

```
fanfou-mcp/
├── main.py                      # 主服务器文件
├── get_config.py               # 配置生成脚本
├── claude_desktop_config.json  # 示例配置文件
├── pyproject.toml              # 项目配置
├── uv.lock                     # 依赖锁定文件
└── README.md                   # 项目说明
```

### 添加新工具

在 `main.py` 中使用 `@mcp.tool()` 装饰器添加新的工具函数：

```python
@mcp.tool()
def your_tool_name(param: str) -> str:
    """
    工具描述
    
    Args:
        param: 参数描述
        
    Returns:
        返回值描述
    """
    return "your implementation"
```

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。