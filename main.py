#!/usr/bin/env python3
"""
饭否 MCP 服务器

饭否是一款基于 Web 的微博客服务，用户可以发布 140 字以内的消息，并可以关注其他用户。
该 MCP 服务器提供了饭否 API 的核心功能，包括时间线获取和 OAuth 认证管理。
"""

import os
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP
from fanfou_client import FanFou

# 创建 MCP 服务器实例
mcp = FastMCP("饭否 MCP 服务器", instructions="饭否是一款基于 Web 的微博客服务，用户可以发布 140 字以内的消息，并可以关注其他用户。该 MCP 服务器提供了诸多饭否 API 的工具。")

# 全局 FanFou 实例
_fanfou_client: Optional[FanFou] = None

def get_fanfou_client() -> FanFou:
    """
    获取饭否客户端实例
    
    优先使用 OAuth Token 认证，如果没有则使用用户名密码登录。
    支持自动生成和缓存 OAuth Token 以提高安全性和性能。
    """
    global _fanfou_client
    if _fanfou_client is None:
        # 从环境变量获取配置
        api_key = os.getenv('FANFOU_API_KEY')
        api_secret = os.getenv('FANFOU_API_SECRET')
        oauth_token = os.getenv('FANFOU_OAUTH_TOKEN')
        oauth_token_secret = os.getenv('FANFOU_OAUTH_TOKEN_SECRET')
        username = os.getenv('FANFOU_USERNAME')
        password = os.getenv('FANFOU_PASSWORD')
        
        if not all([api_key, api_secret]):
            raise Exception("缺少必要的环境变量：FANFOU_API_KEY, FANFOU_API_SECRET")
        
        # 检查是否缺少 OAuth Token
        if not oauth_token or not oauth_token_secret:
            if not username or not password:
                # 既没有 OAuth Token 也没有用户名密码
                error_msg = """
⚠️  缺少认证信息！

请设置以下环境变量之一：

方式1：使用用户名密码（需要进一步生成 OAuth Token）
- FANFOU_USERNAME  
- FANFOU_PASSWORD

方式2：直接使用 OAuth Token
- FANFOU_OAUTH_TOKEN
- FANFOU_OAUTH_TOKEN_SECRET

🔧 如果您是首次使用，请先设置用户名密码，然后我会帮助您生成 OAuth Token。
                """
                raise Exception(error_msg.strip())
            else:
                # 有用户名密码，但没有 OAuth Token，拦截并要求先生成
                error_msg = """
🔑 检测到缺少 OAuth Token！

为了安全和性能考虑，我将帮助您生成 OAuth Token：

1. 调用 generate_oauth_token 工具
2. 将生成的 Token 保存到 MCP env 中：
   - FANFOU_OAUTH_TOKEN
   - FANFOU_OAUTH_TOKEN_SECRET
3. 然后即可正常使用所有功能

💡 OAuth Token 方式更安全且避免重复登录。
                """
                raise Exception(error_msg.strip())
        else:
            # 有 OAuth Token，直接使用
            print("✅ 使用缓存的 OAuth Token")
            _fanfou_client = FanFou(api_key, api_secret, oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
    
    return _fanfou_client

@mcp.tool()
def generate_oauth_token() -> Dict[str, str]:
    """
    生成 OAuth Token
    
    使用用户名密码通过 x_auth 方式生成 OAuth Token，用于后续免密登录。
    生成的 Token 会在控制台输出，用户需要手动保存到环境变量中。
    
    环境变量要求：
    - FANFOU_API_KEY: 饭否应用的 API Key
    - FANFOU_API_SECRET: 饭否应用的 API Secret
    - FANFOU_USERNAME: 饭否用户名
    - FANFOU_PASSWORD: 饭否密码
    
    Returns:
        包含 OAuth Token 信息的字典，包括 oauth_token 和 oauth_token_secret
    """
    try:
        # 从环境变量获取配置
        api_key = os.getenv('FANFOU_API_KEY')
        api_secret = os.getenv('FANFOU_API_SECRET')
        username = os.getenv('FANFOU_USERNAME')
        password = os.getenv('FANFOU_PASSWORD')
        
        if not all([api_key, api_secret]):
            return {"error": "缺少必要的环境变量：FANFOU_API_KEY, FANFOU_API_SECRET"}
        
        if not all([username, password]):
            return {"error": "缺少用户名密码：FANFOU_USERNAME, FANFOU_PASSWORD"}
        
        # 创建临时客户端来生成 Token
        print("🔑 正在生成 OAuth Token...")
        temp_client = FanFou(api_key, api_secret, username=username, password=password)
        
        return {
            "success": "OAuth Token 生成成功！请查看 MCP 输出并保存环境变量（以 JSON 格式输出给用户）。",
            "oauth_token": temp_client.token,
            "oauth_token_secret": temp_client.token_secret,
            "instructions": "请将生成的 OAuth Token 保存到 MCP env 中，然后移除用户名密码配置。"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_user_timeline(user_id: str = '', max_id: str = '', count: int = 5) -> List[Dict[str, Any]]:
    """
    根据用户 ID 获取某个用户发表内容的时间线
    
    调用饭否 API 的 /statuses/user_timeline.json 接口获取指定用户的时间线。
    如果 user_id 为空，则获取当前登录用户的时间线。
    
    Args:
        user_id: 用户 ID，如果为空则获取当前用户时间线
        max_id: 返回列表中内容最新 ID，用于分页获取更早的内容
        count: 获取数量，默认 5 条
        
    Returns:
        用户时间线列表，每个元素包含：
        - 饭否内容: 消息文本内容（HTML 格式）
        - 饭否 ID: 消息的唯一标识符
        - 发布时间: 消息发布时间
        - 发布者: 发布者的显示名称
        - 发布者 ID: 发布者的用户 ID
        - 图片链接: 如果包含图片，则提供图片链接
    """
    try:
        client = get_fanfou_client()
        raw_data = client.request_user_timeline(user_id, max_id, count)
        
        # 过滤返回数据，只保留关键信息
        filtered_data = []
        for item in raw_data:
            filtered_item = {
                "饭否内容": item.get("text", ""),
                "饭否 ID": item.get("id", ""),
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

@mcp.tool()
def get_home_timeline(count: int = 5, max_id: str = '') -> List[Dict[str, Any]]:
    """
    获取当前用户首页关注用户及自己的饭否时间线
    
    调用饭否 API 的 /statuses/home_timeline.json 接口获取当前用户的首页时间线，
    包含用户关注的所有人的最新消息。

    注：通常用户询问「我的饭否」时，指的是该时间线，除非用户明确指出「某个用户的饭否」。
    
    Args:
        count: 获取数量，默认 5 条
        max_id: 返回列表中内容最新 ID，用于分页获取更早的内容
        
    Returns:
        首页时间线列表，每个元素包含：
        - 饭否内容: 消息文本内容（HTML 格式）
        - 饭否 ID: 消息的唯一标识符
        - 发布时间: 消息发布时间
        - 发布者: 发布者的显示名称
        - 发布者 ID: 发布者的用户 ID
        - 图片链接: 如果包含图片，则提供图片链接
    """
    try:
        client = get_fanfou_client()
        raw_data = client.get_home_timeline(count, max_id)
        
        # 过滤返回数据，只保留关键信息
        filtered_data = []
        for item in raw_data:
            filtered_item = {
                "饭否内容": item.get("text", ""),
                "饭否 ID": item.get("id", ""),
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

@mcp.tool()
def get_public_timeline(count: int = 5, max_id: str = '') -> List[Dict[str, Any]]:
    """
    获取公开时间线
    
    调用饭否 API 的 /statuses/public_timeline.json 接口获取饭否全站最新的公开消息，
    这些是所有用户可见的公开饭否内容。
    
    Args:
        count: 获取数量，默认 5 条
        max_id: 返回列表中内容最新 ID，用于分页获取更早的内容
        
    Returns:
        公开时间线列表，每个元素包含：
        - 饭否内容: 消息文本内容（HTML 格式）
        - 饭否 ID: 消息的唯一标识符
        - 发布时间: 消息发布时间
        - 发布者: 发布者的显示名称
        - 发布者 ID: 发布者的用户 ID
        - 图片链接: 如果包含图片，则提供图片链接
    """
    try:
        client = get_fanfou_client()
        raw_data = client.get_public_timeline(count, max_id)
        
        # 过滤返回数据，只保留关键信息
        filtered_data = []
        for item in raw_data:
            filtered_item = {
                "饭否内容": item.get("text", ""),
                "饭否 ID": item.get("id", ""),
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
