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
from utils import image_url_to_base64

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
            "success": "OAuth Token 生成成功！请查看 MCP 输出并保存至环境变量（以 JSON 格式输出给用户）。",
            "oauth_token": temp_client.token,
            "oauth_token_secret": temp_client.token_secret,
            "instructions": "请将生成的 OAuth Token 保存到 MCP env 中，然后移除用户名密码配置。"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_user_timeline(user_id: str = '', max_id: str = '', count: int = 5, q: str = '') -> List[Dict[str, Any]]:
    """
    根据用户 ID 获取某个用户发表内容的时间线
    
    调用饭否 API 的 /statuses/user_timeline.json 接口获取指定用户的时间线。
    如果 user_id 为空，则获取当前登录用户的时间线。
    
    当提供搜索关键词时，会调用 /search/user_timeline.json 接口进行搜索。
    
    Args:
        user_id: 用户 ID，如果为空则获取当前用户时间线
        max_id: 返回列表中内容最新 ID，用于分页获取更早的内容
        count: 获取数量，默认 5 条
        q: 搜索关键词，如果为空则获取普通用户时间线；如果不为空则搜索该用户包含该关键词的消息
        
    Returns:
        用户时间线列表，每个元素包含：
        - 饭否内容: 消息文本内容（HTML 格式）
          * 转发：以「转@」开头，后跟用户链接，如 转@<a href="https://fanfou.com/~FgPOFSnmkW8" class="former">kingcos</a>，其中 href 中的是用户 ID，inner Text 是被转发用户的显示名称，一条饭否可能有多个转发
          * 话题：以「#」包围，如 #<a href="/q/%E6%AD%A3%E5%9C%A8%E6%92%AD%E6%94%BE">正在播放</a>#，其中 q/ 后面的是话题名，一条饭否可能有多个话题
          * 审核状态：如果内容末尾显示「【审核中】」，表示该内容正在审核中
        - 发布 ID: 消息的唯一标识符
        - 发布时间: 消息发布时间，需转为北京时间
        - 发布者: 发布者的用户名
        - 发布者 ID: 发布者的用户 ID
        - 图片链接: 如果包含图片，则提供图片链接
    """
    try:
        client = get_fanfou_client()
        raw_data = client.request_user_timeline(user_id, max_id, count, q)
        
        # 过滤返回数据，只保留关键信息
        filtered_data = []
        for item in raw_data:
            filtered_item = {
                "饭否内容": item.get("text", ""),
                "发布 ID": item.get("id", ""),
                "发布时间": item.get("created_at", ""),
                "发布者": item.get("user", {}).get("name", ""),
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
          * 转发：以「转@」开头，后跟用户链接，如 转@<a href="https://fanfou.com/~FgPOFSnmkW8" class="former">kingcos</a>，其中 href 中的是用户 ID，inner Text 是被转发用户的显示名称，一条饭否可能有多个转发
          * 话题：以「#」包围，如 #<a href="/q/%E6%AD%A3%E5%9C%A8%E6%92%AD%E6%94%BE">正在播放</a>#，其中 q/ 后面的是话题名，一条饭否可能有多个话题
          * 审核状态：如果内容末尾显示「【审核中】」，表示该内容正在审核中
        - 发布 ID: 消息的唯一标识符
        - 发布时间: 消息发布时间，需转为北京时间
        - 发布者: 发布者的用户名
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
                "发布 ID": item.get("id", ""),
                "发布时间": item.get("created_at", ""),
                "发布者": item.get("user", {}).get("name", ""),
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
def get_public_timeline(count: int = 5, max_id: str = '', q: str = '') -> List[Dict[str, Any]]:
    """
    获取公开时间线
    
    调用饭否 API 的 /statuses/public_timeline.json 接口获取饭否全站最新的公开消息，
    这些是所有用户可见的公开饭否内容。
    
    当提供搜索关键词时，会调用 /search/public_timeline.json 接口进行搜索。
    
    Args:
        count: 获取数量，默认 5 条
        max_id: 返回列表中内容最新 ID，用于分页获取更早的内容
        q: 搜索关键词，如果为空则获取普通公开时间线；如果不为空则搜索包含该关键词的公开消息
        
    Returns:
        公开时间线列表，每个元素包含：
        - 饭否内容: 消息文本内容（HTML 格式）
          * 转发：以「转@」开头，后跟用户链接，如 转@<a href="https://fanfou.com/~FgPOFSnmkW8" class="former">kingcos</a>，其中 href 中的是用户 ID，inner Text 是被转发用户的显示名称，一条饭否可能有多个转发
          * 话题：以「#」包围，如 #<a href="/q/%E6%AD%A3%E5%9C%A8%E6%92%AD%E6%94%BE">正在播放</a>#，其中 q/ 后面的是话题名，一条饭否可能有多个话题
          * 审核状态：如果内容末尾显示「【审核中】」，表示该内容正在审核中
        - 发布 ID: 消息的唯一标识符
        - 发布时间: 消息发布时间，需转为北京时间
        - 发布者: 发布者的用户名
        - 发布者 ID: 发布者的用户 ID
        - 图片链接: 如果包含图片，则提供图片链接
    """
    try:
        client = get_fanfou_client()
        raw_data = client.get_public_timeline(count, max_id, q)
        
        # 过滤返回数据，只保留关键信息
        filtered_data = []
        for item in raw_data:
            filtered_item = {
                "饭否内容": item.get("text", ""),
                "发布 ID": item.get("id", ""),
                "发布时间": item.get("created_at", ""),
                "发布者": item.get("user", {}).get("name", ""),
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
def get_user_info(user_id: str = '') -> Dict[str, Any]:
    """
    获取用户信息
    
    调用饭否 API 的 /users/show.json 接口获取指定用户的详细信息。
    如果 user_id 为空，则获取当前登录用户的信息。
    
    Args:
        user_id: 用户 ID，如果为空则获取当前用户信息
        
    Returns:
        用户信息字典，包含：
        - 用户 ID: 用户的唯一标识符
        - 用户名: 用户名
        - 位置: 用户所在位置
        - 性别: 用户性别
        - 生日: 用户生日
        - 描述: 用户个人描述
        - 头像: 用户头像链接
        - 链接: 用户个人网站链接
        - 是否加锁: 账号是否受保护
        - 粉丝数: 被关注数量
        - 朋友数: 互相关注数量
        - 收藏数: 收藏的消息数量
        - 发布数: 发布的消息数量
        - 照片数: 发布的照片数量
        - 是否关注: 当前用户是否关注该用户
        - 注册时间: 账号注册时间
        - 最新状态: 用户最新发布的消息信息
    """
    try:
        client = get_fanfou_client()
        raw_data = client.get_user_info(user_id)
        
        # 解析并格式化用户信息
        user_info = {
            "用户 ID": raw_data.get("id", ""),
            "用户名": raw_data.get("name", ""),
            "位置": raw_data.get("location", ""),
            "性别": raw_data.get("gender", ""),
            "生日": raw_data.get("birthday", ""),
            "描述": raw_data.get("description", ""),
            "头像": raw_data.get("profile_image_url_large", ""),
            "链接": raw_data.get("url", ""),
            "是否加锁": raw_data.get("protected", False),
            "粉丝数": raw_data.get("followers_count", 0),
            "朋友数": raw_data.get("friends_count", 0),
            "收藏数": raw_data.get("favourites_count", 0),
            "发布数": raw_data.get("statuses_count", 0),
            "照片数": raw_data.get("photo_count", 0),
            "是否关注": raw_data.get("following", False),
            "注册时间": raw_data.get("created_at", "")
        }
        
        # 解析最新状态信息
        if "status" in raw_data and raw_data["status"]:
            status = raw_data["status"]
            user_info["最新状态"] = {
                "发布时间": status.get("created_at", ""),
                "发布 ID": status.get("id", ""),
                "发布内容": status.get("text", "")
            }
        else:
            user_info["最新状态"] = None
        
        return user_info
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_status_info(status_id: str) -> Dict[str, Any]:
    """
    获取某条饭否内容的具体信息
    
    调用饭否 API 的 /statuses/show/id.json 接口获取指定饭否内容的详细信息。
    
    Args:
        status_id: 饭否内容的 ID
        
    Returns:
        饭否内容的详细信息字典，包含：
        - 饭否内容: 消息文本内容（HTML 格式）
          * 转发：以「转@」开头，后跟用户链接，如 转@<a href="https://fanfou.com/~FgPOFSnmkW8" class="former">kingcos</a>，其中 href 中的是用户 ID，inner Text 是被转发用户的显示名称，一条饭否可能有多个转发
          * 话题：以「#」包围，如 #<a href="/q/%E6%AD%A3%E5%9C%A8%E6%92%AD%E6%94%BE">正在播放</a>#，其中 q/ 后面的是话题名，一条饭否可能有多个话题
          * 审核状态：如果内容末尾显示「【审核中】」，表示该内容正在审核中
        - 发布 ID: 消息的唯一标识符
        - 发布时间: 消息发布时间，需转为北京时间
        - 发布者: 发布者的显示名称
        - 发布者 ID: 发布者的用户 ID
        - 是否收藏: 当前用户是否收藏了该消息
        - 是否是自己: 是否是当前用户发布的消息
        - 发布位置: 消息发布的地理位置
        - 回复信息: 如果是回复消息，包含被回复的状态 ID、用户 ID 和用户名
        - 图片base64: 如果包含图片，则提供图片的 base64 编码（data URL 格式）
        - 图片链接: 如果包含图片，则提供原始图片链接作为备用
    """
    try:
        client = get_fanfou_client()
        raw_data = client.get_status_info(status_id)
        
        # 解析并格式化状态信息
        status_info = {
            "饭否内容": raw_data.get("text", ""),
            "发布 ID": raw_data.get("id", ""),
            "发布时间": raw_data.get("created_at", ""),
            "发布者": raw_data.get("user", {}).get("name", ""),
            "发布者 ID": raw_data.get("user", {}).get("id", ""),
            "是否收藏": raw_data.get("favorited", False),
            "是否是自己": raw_data.get("is_self", False),
            "发布位置": raw_data.get("location", "")
        }
        
        # 处理回复信息
        if raw_data.get("in_reply_to_status_id"):
            status_info["回复信息"] = {
                "回复的状态 ID": raw_data.get("in_reply_to_status_id", ""),
                "回复的用户 ID": raw_data.get("in_reply_to_user_id", ""),
                "回复的用户名": raw_data.get("in_reply_to_screen_name", "")
            }
        else:
            status_info["回复信息"] = None
        
        # 处理图片链接和base64转换
        if "photo" in raw_data and raw_data["photo"]:
            large_url = raw_data["photo"].get("largeurl", "")
            normal_url = raw_data["photo"].get("imageurl", "")
            status_info["图片链接"] = large_url
            
            # 将图片转换为base64，如果大图超过300KB则使用普通图片
            if large_url:
                image_base64 = image_url_to_base64(large_url, normal_url)
                status_info["图片base64"] = image_base64
            else:
                status_info["图片base64"] = None
        else:
            status_info["图片链接"] = None
            status_info["图片base64"] = None
        
        return status_info
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def manage_favorite(status_id: str, action: str, confirm: bool = False) -> Dict[str, Any]:
    """
    管理饭否内容的收藏状态
    
    调用饭否 API 的 /favorites/create/id.json 或 /favorites/destroy/id.json 接口
    来收藏或取消收藏指定的饭否内容。
    
    Args:
        status_id: 饭否内容的 ID
        action: 操作类型，"create" 表示收藏，"destroy" 表示取消收藏
        confirm: 是否确认操作（二次确认参数）
        
    Returns:
        操作结果字典，包含：
        - 是否收藏: 操作后的收藏状态
        - 操作结果: 操作是否成功的描述信息
        - 操作类型: 执行的具体操作（收藏/取消收藏）
        
        或者确认信息字典，包含：
        - 需要确认: 是否需要用户确认
        - 内容预览: 要操作的内容预览
        - 确认提示: 如何进行确认的说明
    """
    try:
        if action not in ['create', 'destroy']:
            return {"error": "action 参数必须是 'create' 或 'destroy'"}
        
        if not status_id.strip():
            return {"error": "饭否内容 ID 不能为空"}
        
        client = get_fanfou_client()
        
        # 如果未确认，先获取内容信息进行预览，绝对不执行操作
        if not confirm:
            try:
                # 获取要操作的内容信息
                status_info = client.get_status_info(status_id)
                
                # 截取内容预览（最多50字）
                content = status_info.get("text", "")
                # 移除HTML标签用于预览
                import re
                clean_content = re.sub(r'<[^>]+>', '', content)
                content_preview = clean_content[:50] + "..." if len(clean_content) > 50 else clean_content
                
                operation_name = "收藏" if action == "create" else "取消收藏"
                current_favorited = status_info.get("favorited", False)
                
                # 检查操作是否有意义
                if action == "create" and current_favorited:
                    return {"error": "该内容已经收藏过了"}
                elif action == "destroy" and not current_favorited:
                    return {"error": "该内容尚未收藏"}
                
                return {
                    "需要确认": True,
                    "内容预览": content_preview,
                    "发布时间": status_info.get("created_at", ""),
                    "发布 ID": status_info.get("id", ""),
                    "发布者": status_info.get("user", {}).get("name", ""),
                    "当前收藏状态": "已收藏" if current_favorited else "未收藏",
                    "操作类型": operation_name,
                    "⚠️ 重要提示": f"即将{operation_name}此内容，请确认是否继续",
                    "确认提示": f"如果确认{operation_name}这条饭否，请用户明确告诉我要{operation_name}，然后我会调用 manage_favorite('{status_id}', '{action}', confirm=True)",
                    "🚫 绝对禁止": "AI助手不能自动确认操作，必须等待用户明确指示！"
                }
                
            except Exception as e:
                # 如果获取内容信息失败，可能是内容不存在或无权访问
                return {"error": f"无法获取饭否内容信息，可能是内容不存在或无权访问: {str(e)}"}
        
        # 只有当用户明确确认时才执行操作
        # 这里应该只有在用户明确要求操作时才会到达
        raw_data = client.manage_favorite(status_id, action)
        
        # 解析操作结果
        favorited = raw_data.get("favorited", False)
        
        if action == "create":
            success_msg = "收藏成功" if favorited else "收藏失败"
            operation = "收藏"
        else:  # destroy
            success_msg = "取消收藏成功" if not favorited else "取消收藏失败"
            operation = "取消收藏"
        
        result = {
            "是否收藏": favorited,
            "操作结果": success_msg,
            "操作类型": operation
        }
        
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def manage_friendship(user_id: str, action: str, confirm: bool = False) -> Dict[str, Any]:
    """
    管理用户关注状态
    
    调用饭否 API 的 /friendships/create.json 或 /friendships/destroy.json 接口
    来关注或取消关注指定用户。
    
    注意：在执行关注操作前，会先调用 get_user_info 查询目标用户信息，
    如果目标用户账号受保护（protected），关注操作将变为申请关注，
    需要对方确认后才能生效。
    
    Args:
        user_id: 目标用户的 ID
        action: 操作类型，"create" 表示关注，"destroy" 表示取消关注
        confirm: 是否确认操作（二次确认参数）
        
    Returns:
        操作结果字典，包含：
        - 是否关注: 操作后的关注状态
        - 操作结果: 操作是否成功的描述信息
        - 操作类型: 执行的具体操作（关注/取消关注）
        - 用户信息: 目标用户的基本信息
        - 特殊情况: 如果是受保护账号的关注申请，会包含相关提示
        
        或者确认信息字典，包含：
        - 需要确认: 是否需要用户确认
        - 用户预览: 要操作的用户预览
        - 确认提示: 如何进行确认的说明
    """
    try:
        if action not in ['create', 'destroy']:
            return {"error": "action 参数必须是 'create' 或 'destroy'"}
        
        if not user_id.strip():
            return {"error": "用户 ID 不能为空"}
        
        client = get_fanfou_client()
        
        # 先获取目标用户信息
        try:
            user_info = client.get_user_info(user_id)
            target_username = user_info.get("name", "")
            is_protected = user_info.get("protected", False)
            current_following = user_info.get("following", False)
        except Exception as e:
            return {"error": f"无法获取用户信息: {str(e)}"}
        
        # 如果未确认，先显示用户信息进行预览，绝对不执行操作
        if not confirm:
            operation_name = "关注" if action == "create" else "取消关注"
            
            # 检查操作是否有意义
            if action == "create" and current_following:
                return {"error": "您已经关注了该用户"}
            elif action == "destroy" and not current_following:
                return {"error": "您尚未关注该用户"}
            
            # 特殊提示：受保护账号的关注申请
            special_note = ""
            if action == "create" and is_protected:
                special_note = "⚠️ 注意：该用户账号受保护，关注操作将变为申请关注，需要对方确认后才能生效"
            
            return {
                "需要确认": True,
                "用户预览": {
                    "用户名": target_username,
                    "用户 ID": user_id,
                    "是否受保护": is_protected,
                    "粉丝数": user_info.get("followers_count", 0),
                    "发布数": user_info.get("statuses_count", 0),
                    "个人描述": user_info.get("description", "")[:100] + "..." if len(user_info.get("description", "")) > 100 else user_info.get("description", "")
                },
                "当前关注状态": "已关注" if current_following else "未关注",
                "操作类型": operation_name,
                "⚠️ 重要提示": f"即将{operation_name}用户 {target_username}，请确认是否继续",
                "特殊情况": special_note if special_note else None,
                "确认提示": f"如果确认{operation_name}这个用户，请用户明确告诉我要{operation_name}，然后我会调用 manage_friendship('{user_id}', '{action}', confirm=True)",
                "🚫 绝对禁止": "AI助手不能自动确认操作，必须等待用户明确指示！"
            }
        
        # 只有当用户明确确认时才执行操作
        # 这里应该只有在用户明确要求操作时才会到达
        raw_data = client.manage_friendship(user_id, action)
        
        # 检查是否有错误消息（特殊情况：受保护账号的关注申请）
        if "error" in raw_data:
            return {
                "操作类型": "关注申请" if action == "create" else "取消关注",
                "操作结果": raw_data["error"],
                "用户信息": {
                    "用户名": target_username,
                    "用户 ID": user_id,
                    "是否受保护": is_protected
                },
                "特殊情况": "该用户账号受保护，已发送关注申请，请等待对方确认"
            }
        
        # 解析正常的操作结果
        following = raw_data.get("following", False)
        
        if action == "create":
            if is_protected:
                success_msg = f"已向 {target_username} 发出关注请求，请等待确认"
                operation = "关注申请"
            else:
                success_msg = "关注成功" if following else "关注失败"
                operation = "关注"
        else:  # destroy
            success_msg = "取消关注成功" if not following else "取消关注失败"
            operation = "取消关注"
        
        result = {
            "是否关注": following,
            "操作结果": success_msg,
            "操作类型": operation,
            "用户信息": {
                "用户名": target_username,
                "用户 ID": user_id,
                "是否受保护": is_protected
            }
        }
        
        # 如果是受保护账号的关注申请，添加特殊情况说明
        if action == "create" and is_protected:
            result["特殊情况"] = "该用户账号受保护，关注操作已转为申请关注"
        
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def publish_status(status: str, confirm: bool = False) -> Dict[str, Any]:
    """
    发布饭否内容（仅文字）
    
    调用饭否 API 的 /statuses/update.json 接口发布纯文字内容。
    
    Args:
        status: 要发布的文字内容（最多140字）
        confirm: 是否确认发布（二次确认参数）
        
    Returns:
        发布结果字典，包含：
        - 发布 ID: 新发布消息的唯一标识符
        - 发布时间: 消息发布时间，需转为北京时间
        - 发布结果: 发布是否成功的描述信息
        - 重要提示: 关于审核的提醒信息
        
        或者确认信息字典，包含：
        - 需要确认: 是否需要用户确认
        - 内容预览: 要发布的内容预览
        - 确认提示: 如何进行确认的说明
    """
    try:
        if len(status) > 140:
            return {"error": "饭否内容不能超过140字"}
        
        if not status.strip():
            return {"error": "饭否内容不能为空"}
        
        # 如果未确认，先显示内容预览，绝对不执行发布
        if not confirm:
            return {
                "需要确认": True,
                "内容预览": status,
                "字数统计": f"{len(status)}/140",
                "操作类型": "发布饭否",
                "⚠️ 重要提示": "即将发布此内容到饭否，发布后需要等待审核，请确认是否继续",
                "确认提示": f"如果确认发布这条饭否，请用户明确告诉我要发布，然后我会调用 publish_status('{status}', confirm=True)",
                "🚫 绝对禁止": "AI助手不能自动确认发布，必须等待用户明确指示！"
            }
        
        # 只有当用户明确确认时才执行发布
        # 这里应该只有在用户明确要求发布时才会到达
        client = get_fanfou_client()
        raw_data = client.publish_status(status)
        
        # 解析发布结果
        result = {
            "发布 ID": raw_data.get("id", ""),
            "发布时间": raw_data.get("created_at", ""),
            "发布结果": "发布成功",
            "重要提示": "内容已发布成功，正在等待审核，审核通过后将出现在时间线中"
        }
        
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def publish_photo(status: str, photo_url: str, confirm: bool = False) -> Dict[str, Any]:
    """
    发布饭否内容（文字+图片）
    
    调用饭否 API 的 /photos/upload.json 接口发布带图片的内容。
    
    Args:
        status: 要发布的文字内容（最多140字）
        photo_url: 图片的网络 URL 地址
        confirm: 是否确认发布（二次确认参数）
        
    Returns:
        发布结果字典，包含：
        - 发布 ID: 新发布消息的唯一标识符
        - 发布时间: 消息发布时间
        - 发布结果: 发布是否成功的描述信息
        - 重要提示: 关于审核的提醒信息
        
        或者确认信息字典，包含：
        - 需要确认: 是否需要用户确认
        - 内容预览: 要发布的内容预览
        - 确认提示: 如何进行确认的说明
    """
    try:
        if len(status) > 140:
            return {"error": "饭否内容不能超过140字"}
        
        if not status.strip():
            return {"error": "饭否内容不能为空"}
        
        if not photo_url.strip():
            return {"error": "图片 URL 不能为空"}
        
        # 验证 URL 格式
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(photo_url):
            return {"error": "无效的图片 URL 格式"}
        
        # 检查 URL 是否看起来像图片
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        url_lower = photo_url.lower()
        has_image_extension = any(url_lower.endswith(ext) for ext in image_extensions)
        
        # 如果未确认，先显示内容预览，绝对不执行发布
        if not confirm:
            # 如果没有图片扩展名，给出提示
            url_warning = ""
            if not has_image_extension:
                url_warning = "⚠️ 注意：URL 不包含常见的图片扩展名，将尝试下载并检测图片格式"
            
            return {
                "需要确认": True,
                "内容预览": status,
                "字数统计": f"{len(status)}/140",
                "图片链接": photo_url,
                "操作类型": "发布带图片的饭否",
                "⚠️ 重要提示": "即将发布此内容和图片到饭否，发布后需要等待审核，请确认是否继续",
                "URL 提示": url_warning if url_warning else "图片 URL 格式正常",
                "确认提示": f"如果确认发布这条带图片的饭否，请用户明确告诉我要发布，然后我会调用 publish_photo('{status}', '{photo_url}', confirm=True)",
                "🚫 绝对禁止": "AI助手不能自动确认发布，必须等待用户明确指示！"
            }
        
        # 只有当用户明确确认时才执行发布
        # 这里应该只有在用户明确要求发布时才会到达
        
        # 如果没有图片扩展名，给出提示但不阻止（有些图片 URL 不包含扩展名）
        if not has_image_extension:
            print(f"提示：URL 不包含常见的图片扩展名，将尝试下载: {photo_url}")
        
        client = get_fanfou_client()
        raw_data = client.publish_photo(status, photo_url)
        
        # 解析发布结果
        result = {
            "发布 ID": raw_data.get("id", ""),
            "发布时间": raw_data.get("created_at", ""),
            "发布结果": "发布成功",
            "重要提示": "内容已发布成功，正在等待审核，审核通过后将出现在时间线中"
        }
        
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_status(status_id: str, confirm: bool = False) -> Dict[str, Any]:
    """
    删除饭否内容
    
    调用饭否 API 的 /statuses/destroy.json 接口删除指定的饭否内容。
    注意：只能删除自己发布的内容。
    
    Args:
        status_id: 要删除的饭否内容的 ID
        confirm: 是否确认删除（二次确认参数）
        
    Returns:
        删除结果字典，包含：
        - 删除 ID: 被删除消息的 ID
        - 删除结果: 删除是否成功的描述信息
        - 重要提示: 关于删除操作的提醒信息
        
        或者确认信息字典，包含：
        - 需要确认: 是否需要用户确认
        - 内容预览: 要删除的内容预览
        - 确认提示: 如何进行确认的说明
    """
    try:
        if not status_id.strip():
            return {"error": "饭否内容 ID 不能为空"}
        
        client = get_fanfou_client()
        
        # 如果未确认，先获取内容信息进行预览，绝对不执行删除
        if not confirm:
            try:
                # 获取要删除的内容信息
                status_info = client.get_status_info(status_id)
                
                # 检查是否是自己的内容
                if not status_info.get("is_self", False):
                    return {"error": "只能删除自己发布的饭否内容"}
                
                # 截取内容预览（最多50字）
                content = status_info.get("text", "")
                # 移除HTML标签用于预览
                import re
                clean_content = re.sub(r'<[^>]+>', '', content)
                content_preview = clean_content[:50] + "..." if len(clean_content) > 50 else clean_content
                
                return {
                    "需要确认": True,
                    "内容预览": content_preview,
                    "发布时间": status_info.get("created_at", ""),
                    "发布 ID": status_info.get("id", ""),
                    "⚠️ 重要警告": "删除后无法恢复，请谨慎操作！",
                    "确认提示": f"如果确认删除这条饭否，请用户明确告诉我要删除，然后我会调用 delete_status('{status_id}', confirm=True)",
                    "🚫 绝对禁止": "AI助手不能自动确认删除，必须等待用户明确指示！"
                }
                
            except Exception as e:
                # 如果获取内容信息失败，可能是内容不存在或无权访问
                return {"error": f"无法获取饭否内容信息，可能是内容不存在或无权访问: {str(e)}"}
        
        # 只有当用户明确确认时才执行删除
        # 这里应该只有在用户明确要求删除时才会到达
        raw_data = client.delete_status(status_id)
        
        # 解析删除结果
        result = {
            "删除 ID": raw_data.get("id", ""),
            "删除结果": "删除成功",
            "重要提示": "饭否内容已成功删除，将从时间线中消失"
        }
        
        return result
    except Exception as e:
        return {"error": str(e)}

def main():
    """MCP 服务器的主入口点"""
    # 启动服务器
    mcp.run()

if __name__ == "__main__":
    main()
