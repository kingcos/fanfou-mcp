#!/usr/bin/env python3
"""
饭否 MCP 服务器
"""

from fastmcp import FastMCP

# 创建 MCP 服务器实例
mcp = FastMCP("饭否 MCP 服务器")

@mcp.tool()
def hello_fanfou(name: str = "世界") -> str:
    """
    向饭否世界问好
    
    Args:
        name: 要问候的名字
        
    Returns:
        问候语
    """
    return f"你好，{name}！欢迎来到饭否 MCP 服务器！"

@mcp.tool()
def get_fanfou_info() -> dict:
    """
    获取饭否平台信息
    
    Returns:
        饭否平台的基本信息
    """
    return {
        "name": "饭否",
        "description": "中国的微博客服务",
        "website": "https://fanfou.com",
        "founded": "2007年",
        "features": ["微博客", "社交网络", "实时更新"]
    }

if __name__ == "__main__":
    # 启动服务器
    mcp.run()
