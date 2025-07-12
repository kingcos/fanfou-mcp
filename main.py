#!/usr/bin/env python3
"""
饭否 MCP 服务器
"""

import os
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP
from fanfou_client import FanFou

# 创建 MCP 服务器实例
mcp = FastMCP("饭否 MCP 服务器")

# 全局 FanFou 实例
_fanfou_client: Optional[FanFou] = None

def get_fanfou_client() -> FanFou:
    """获取饭否客户端实例"""
    global _fanfou_client
    if _fanfou_client is None:
        # 从环境变量获取配置
        api_key = os.getenv('FANFOU_API_KEY')
        api_secret = os.getenv('FANFOU_API_SECRET')
        username = os.getenv('FANFOU_USERNAME')
        password = os.getenv('FANFOU_PASSWORD')
        
        if not all([api_key, api_secret, username, password]):
            raise Exception("缺少必要的环境变量：FANFOU_API_KEY, FANFOU_API_SECRET, FANFOU_USERNAME, FANFOU_PASSWORD")
        
        _fanfou_client = FanFou(api_key, api_secret, username, password)
    
    return _fanfou_client

@mcp.tool()
def get_user_timeline(max_id: str = '', count: int = 10) -> List[Dict[str, Any]]:
    """
    获取用户时间线
    
    Args:
        max_id: 最大 ID，用于分页
        count: 获取数量，默认 10 条
        
    Returns:
        用户时间线列表
    """
    try:
        client = get_fanfou_client()
        raw_data = client.request_user_timeline(max_id, count)
        
        # 过滤返回数据，只保留关键信息
        filtered_data = []
        for item in raw_data:
            filtered_item = {
                "饭否内容": item.get("text", "")
            }
            
            # 如果有图片，添加 imageurl
            if "photo" in item and item["photo"]:
                filtered_item["图片链接"] = item["photo"].get("largeurl", "")
            
            filtered_data.append(filtered_item)
        
        return filtered_data
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_home_timeline(count: int = 20, max_id: str = '') -> List[Dict[str, Any]]:
    """
    获取首页时间线
    
    Args:
        count: 获取数量，默认 20 条
        max_id: 最大 ID，用于分页
        
    Returns:
        首页时间线列表
    """
    try:
        client = get_fanfou_client()
        raw_data = client.get_home_timeline(count, max_id)
        
        # 过滤返回数据，只保留关键信息
        filtered_data = []
        for item in raw_data:
            filtered_item = {
                "饭否内容": item.get("text", ""),
                "发布时间": item.get("created_at", ""),
                "发布者": item.get("user", {}).get("screen_name", ""),
                "发布者 ID": item.get("user", {}).get("id", "")
            }
            
            # 如果有图片，添加 imageurl
            if "photo" in item and item["photo"]:
                filtered_item["图片链接"] = item["photo"].get("largeurl", "")
            
            filtered_data.append(filtered_item)
        
        return filtered_data
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    # 启动服务器
    mcp.run()
