#!/usr/bin/env python3
"""
饭否 Gradio MCP 服务器

基于 Gradio 构建的饭否 MCP 服务器，提供 Web UI 和 SSE MCP 服务。
同时支持人工交互和 AI 模型通过 MCP 协议访问。

支持 Header 传递认证信息，实现多用户隔离：
X-Fanfou-Api-Key, X-Fanfou-Api-Secret, X-Fanfou-OAuth-Token, X-Fanfou-OAuth-Token-Secret
"""

import json
import gradio as gr
from typing import Dict
from fanfou_client import FanFou

def get_mcp_auth_from_request(request: gr.Request) -> Dict[str, str]:
    """从 MCP 请求中提取认证信息"""
    if request is None:
        return {}
    
    # 从 headers 中获取认证信息
    auth_info = {}
    if hasattr(request, 'headers'):
        headers = request.headers
        auth_info = {
            'api_key': headers.get('X-Fanfou-Api-Key', ''),
            'api_secret': headers.get('X-Fanfou-Api-Secret', ''),
            'oauth_token': headers.get('X-Fanfou-OAuth-Token', ''),
            'oauth_token_secret': headers.get('X-Fanfou-OAuth-Token-Secret', ''),
            'username': headers.get('X-Fanfou-Username', ''),
            'password': headers.get('X-Fanfou-Password', '')
        }
    
    return auth_info

def get_fanfou_client_for_request(request: gr.Request = None) -> FanFou:
    """为特定请求创建 FanFou 客户端"""
    # 从 MCP 请求中获取认证信息
    mcp_auth = get_mcp_auth_from_request(request)
    
    # 检查是否有必要的认证信息
    if not mcp_auth.get('api_key') or not mcp_auth.get('api_secret'):
        raise Exception("缺少必要的认证信息：api_key 和 api_secret")
    
    api_key = mcp_auth['api_key']
    api_secret = mcp_auth['api_secret']
    oauth_token = mcp_auth.get('oauth_token', '')
    oauth_token_secret = mcp_auth.get('oauth_token_secret', '')
    username = mcp_auth.get('username', '')
    password = mcp_auth.get('password', '')
    
    # 创建 FanFou 客户端
    if oauth_token and oauth_token_secret:
        return FanFou(api_key, api_secret, oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
    elif username and password:
        return FanFou(api_key, api_secret, username=username, password=password)
    else:
        raise Exception("需要提供 OAuth Token 或用户名密码")

def format_result(result):
    """格式化返回结果为 JSON 字符串"""
    if isinstance(result, (dict, list)):
        return json.dumps(result, ensure_ascii=False, indent=2)
    return str(result)

# ==================== 支持 MCP 用户认证的工具函数 ====================

def generate_oauth_token(request: gr.Request = None) -> str:
    """
    生成 OAuth Token
    
    使用用户名密码通过 x_auth 方式生成 OAuth Token，用于后续免密登录。
    生成的 Token 会在控制台输出，用户需要手动保存到环境变量中。
    
    支持 Header 传递认证信息：
    X-Fanfou-Api-Key, X-Fanfou-Api-Secret, X-Fanfou-Username, X-Fanfou-Password
    
    Returns:
        包含 OAuth Token 信息的字典，包括 oauth_token 和 oauth_token_secret
    """
    try:
        # 从 MCP 请求中获取认证信息
        mcp_auth = get_mcp_auth_from_request(request)
        
        if not mcp_auth.get('api_key') or not mcp_auth.get('api_secret'):
            return format_result({
                "error": "缺少必要的认证信息：api_key 和 api_secret"
            })
        
        if not mcp_auth.get('username') or not mcp_auth.get('password'):
            return format_result({
                "error": "生成 OAuth Token 需要用户名和密码"
            })
        
        # 使用 MCP 请求中的认证信息生成 Token
        temp_client = FanFou(
            mcp_auth['api_key'], 
            mcp_auth['api_secret'], 
            username=mcp_auth['username'], 
            password=mcp_auth['password']
        )
        
        return format_result({
            "success": "OAuth Token 生成成功！",
            "oauth_token": temp_client.token,
            "oauth_token_secret": temp_client.token_secret,
            "instructions": "请将生成的 OAuth Token 保存到 Header 中使用。"
        })
    except Exception as e:
        return format_result({"error": str(e)})

def get_home_timeline(count: int = 5, max_id: str = "", request: gr.Request = None) -> str:
    """
    获取当前用户首页关注用户及自己的饭否时间线
    
    调用饭否 API 的 /statuses/home_timeline.json 接口获取当前用户的首页时间线，
    包含用户关注的所有人的最新消息。

    注：通常用户询问「我的饭否」时，指的是该时间线，除非用户明确指出「某个用户的饭否」。
    
    Args:
        count: 获取数量，默认 5 条
        max_id: 返回列表中内容最新 ID，用于分页获取更早的内容，默认传递空字符串
        
    Returns:
        首页时间线列表，每个元素包含：
        - 饭否内容: 消息文本内容（HTML 格式）
          * 转发：以「转@」开头，后跟用户链接，如 转@<a href="https://fanfou.com/~FgPOFSnmkW8" class="former">kingcos</a>，其中 href 中的是用户 ID，inner Text 是被转发用户的显示名称，一条饭否可能有多个转发
          * 话题：以「#」包围，如 #<a href="/q/%E6%AD%A3%E5%9C%A8%E6%92%AD%E6%94%BE">正在播放</a>#，其中 q/ 后面的是话题名，一条饭否可能有多个话题
          * 审核状态：如果内容末尾显示「【审核中】」，表示该内容正在审核中
        - 发布 ID: 消息的唯一标识符
        - 发布时间: 消息发布时间
        - 发布者: 发布者的用户名
        - 发布者 ID: 发布者的用户 ID
        - 图片链接: 如果包含图片，则提供图片链接
    """
    try:
        client = get_fanfou_client_for_request(request)
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
        
        return format_result(filtered_data)
    except Exception as e:
        return format_result({"error": str(e)})

def get_user_timeline(user_id: str = "", max_id: str = "", count: int = 5, q: str = "", request: gr.Request = None) -> str:
    """
    根据用户 ID 获取某个用户发表内容的时间线
    
    调用饭否 API 的 /statuses/user_timeline.json 接口获取指定用户的时间线。
    如果 user_id 为空，则获取当前登录用户的时间线。
    
    当提供搜索关键词时，会调用 /search/user_timeline.json 接口进行搜索。
    
    Args:
        user_id: 用户 ID，如果为空则获取当前用户时间线
        max_id: 返回列表中内容最新 ID，用于分页获取更早的内容，默认传递空字符串
        count: 获取数量，默认 5 条
        q: 搜索关键词，如果为空则获取普通用户时间线；如果不为空则搜索该用户包含该关键词的消息
        
    Returns:
        用户时间线列表，每个元素包含：
        - 饭否内容: 消息文本内容（HTML 格式）
          * 转发：以「转@」开头，后跟用户链接，如 转@<a href="https://fanfou.com/~FgPOFSnmkW8" class="former">kingcos</a>，其中 href 中的是用户 ID，inner Text 是被转发用户的显示名称，一条饭否可能有多个转发
          * 话题：以「#」包围，如 #<a href="/q/%E6%AD%A3%E5%9C%A8%E6%92%AD%E6%94%BE">正在播放</a>#，其中 q/ 后面的是话题名，一条饭否可能有多个话题
          * 审核状态：如果内容末尾显示「【审核中】」，表示该内容正在审核中
        - 发布 ID: 消息的唯一标识符
        - 发布时间: 消息发布时间
        - 发布者: 发布者的用户名
        - 发布者 ID: 发布者的用户 ID
        - 图片链接: 如果包含图片，则提供图片链接
    """
    try:
        client = get_fanfou_client_for_request(request)
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
        
        return format_result(filtered_data)
    except Exception as e:
        return format_result({"error": str(e)})

def get_public_timeline(count: int = 5, max_id: str = "", q: str = "", request: gr.Request = None) -> str:
    """
    获取公开时间线
    
    调用饭否 API 的 /statuses/public_timeline.json 接口获取饭否全站最新的公开消息，
    这些是所有用户可见的公开饭否内容。
    
    当提供搜索关键词时，会调用 /search/public_timeline.json 接口进行搜索。
    
    Args:
        count: 获取数量，默认 5 条
        max_id: 返回列表中内容最新 ID，用于分页获取更早的内容，默认传递空字符串
        q: 搜索关键词，如果为空则获取普通公开时间线；如果不为空则搜索包含该关键词的公开消息
        
    Returns:
        公开时间线列表，每个元素包含：
        - 饭否内容: 消息文本内容（HTML 格式）
          * 转发：以「转@」开头，后跟用户链接，如 转@<a href="https://fanfou.com/~FgPOFSnmkW8" class="former">kingcos</a>，其中 href 中的是用户 ID，inner Text 是被转发用户的显示名称，一条饭否可能有多个转发
          * 话题：以「#」包围，如 #<a href="/q/%E6%AD%A3%E5%9C%A8%E6%92%AD%E6%94%BE">正在播放</a>#，其中 q/ 后面的是话题名，一条饭否可能有多个话题
          * 审核状态：如果内容末尾显示「【审核中】」，表示该内容正在审核中
        - 发布 ID: 消息的唯一标识符
        - 发布时间: 消息发布时间
        - 发布者: 发布者的用户名
        - 发布者 ID: 发布者的用户 ID
        - 图片链接: 如果包含图片，则提供图片链接
    """
    try:
        client = get_fanfou_client_for_request(request)
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
        
        return format_result(filtered_data)
    except Exception as e:
        return format_result({"error": str(e)})

def get_user_info(user_id: str = "", request: gr.Request = None) -> str:
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
        client = get_fanfou_client_for_request(request)
        raw_data = client.get_user_info(user_id)
        
        # 过滤返回数据，只保留关键信息
        user_info = {
            "用户名": raw_data.get("name", ""),
            "用户 ID": raw_data.get("id", ""),
            "显示名": raw_data.get("screen_name", ""),
            "个人描述": raw_data.get("description", ""),
            "关注数": raw_data.get("friends_count", 0),
            "粉丝数": raw_data.get("followers_count", 0),
            "发布数": raw_data.get("statuses_count", 0),
            "收藏数": raw_data.get("favourites_count", 0),
            "注册时间": raw_data.get("created_at", ""),
            "头像链接": raw_data.get("profile_image_url_large", ""),
            "个人主页": raw_data.get("url", ""),
            "地理位置": raw_data.get("location", "")
        }
        
        return format_result(user_info)
    except Exception as e:
        return format_result({"error": str(e)})

def get_status_info(status_id: str, request: gr.Request = None) -> str:
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
        - 发布时间: 消息发布时间
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
        client = get_fanfou_client_for_request(request)
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
        
        # 处理图片链接
        if "photo" in raw_data and raw_data["photo"]:
            status_info["图片链接"] = raw_data["photo"].get("largeurl", "")
        else:
            status_info["图片链接"] = None
        
        return format_result(status_info)
    except Exception as e:
        return format_result({"error": str(e)})

def manage_favorite(status_id: str, action: str, confirm: bool = False, request: gr.Request = None) -> str:
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
        if not confirm:
            return format_result({
                "error": "请确认操作：此操作需要确认才能执行"
            })
        
        client = get_fanfou_client_for_request(request)
        raw_data = client.manage_favorite(status_id, action)
        
        result = {
            "操作": "收藏" if action == "create" else "取消收藏",
            "状态 ID": status_id,
            "结果": "成功" if raw_data.get("id") else "失败",
            "饭否内容": raw_data.get("text", ""),
            "发布者": raw_data.get("user", {}).get("name", "")
        }
        
        return format_result(result)
    except Exception as e:
        return format_result({"error": str(e)})

def manage_friendship(user_id: str, action: str, confirm: bool = False, request: gr.Request = None) -> str:
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
        if not confirm:
            return format_result({
                "error": "请确认操作：此操作需要确认才能执行"
            })
        
        client = get_fanfou_client_for_request(request)
        raw_data = client.manage_friendship(user_id, action)
        
        result = {
            "操作": "关注" if action == "create" else "取消关注",
            "用户 ID": user_id,
            "结果": "成功" if raw_data.get("id") else "失败",
            "用户名": raw_data.get("name", ""),
            "显示名": raw_data.get("screen_name", "")
        }
        
        return format_result(result)
    except Exception as e:
        return format_result({"error": str(e)})

def publish_status(status: str, confirm: bool = False, request: gr.Request = None) -> str:
    """
    发布饭否内容（仅文字）
    
    调用饭否 API 的 /statuses/update.json 接口发布纯文字内容。
    
    Args:
        status: 要发布的文字内容（最多140字）
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
        if not confirm:
            return format_result({
                "error": "请确认操作：此操作需要确认才能执行"
            })
        
        client = get_fanfou_client_for_request(request)
        raw_data = client.publish_status(status)
        
        result = {
            "操作": "发布文字内容",
            "结果": "成功" if raw_data.get("id") else "失败",
            "发布 ID": raw_data.get("id", ""),
            "发布时间": raw_data.get("created_at", ""),
            "内容": raw_data.get("text", "")
        }
        
        return format_result(result)
    except Exception as e:
        return format_result({"error": str(e)})

def publish_photo(status: str, photo_url: str, confirm: bool = False, request: gr.Request = None) -> str:
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
        if not confirm:
            return format_result({
                "error": "请确认操作：此操作需要确认才能执行"
            })
        
        client = get_fanfou_client_for_request(request)
        raw_data = client.publish_photo(status, photo_url)
        
        result = {
            "操作": "发布图片内容",
            "结果": "成功" if raw_data.get("id") else "失败",
            "发布 ID": raw_data.get("id", ""),
            "发布时间": raw_data.get("created_at", ""),
            "内容": raw_data.get("text", ""),
            "图片链接": raw_data.get("photo", {}).get("largeurl", "")
        }
        
        return format_result(result)
    except Exception as e:
        return format_result({"error": str(e)})

def delete_status(status_id: str, confirm: bool = False, request: gr.Request = None) -> str:
    try:
        if not confirm:
            return format_result({
                "error": "请确认操作：此操作需要确认才能执行"
            })
        
        client = get_fanfou_client_for_request(request)
        raw_data = client.delete_status(status_id)
        
        result = {
            "操作": "删除内容",
            "状态 ID": status_id,
            "结果": "成功" if raw_data.get("id") else "失败",
            "删除时间": raw_data.get("created_at", ""),
            "原内容": raw_data.get("text", "")
        }
        
        return format_result(result)
    except Exception as e:
        return format_result({"error": str(e)})

# ==================== 创建 Gradio 接口 ====================

def create_interfaces():
    """创建所有 Gradio 接口"""
    
    # 认证相关接口
    auth_interface = gr.Interface(
        fn=generate_oauth_token,
        inputs=[],
        outputs=gr.Textbox(label="使用说明", lines=10),
        title="生成 OAuth Token",
        description="""
使用用户名密码通过 x_auth 方式生成 OAuth Token，用于后续免密登录。
生成的 Token 会在控制台输出，用户需要手动保存到环境变量中。

支持 Header 传递认证信息：
X-Fanfou-Api-Key, X-Fanfou-Api-Secret, X-Fanfou-Username, X-Fanfou-Password

Returns:
    包含 OAuth Token 信息的字典，包括 oauth_token 和 oauth_token_secret
"""
    )
    
    # 时间线相关接口
    home_timeline = gr.Interface(
        fn=get_home_timeline,
        inputs=[
            gr.Number(label="获取数量", value=5, minimum=1, maximum=20),
            gr.Textbox(label="最大 ID（可选）", placeholder="用于分页获取更早内容")
        ],
        outputs=gr.Textbox(label="使用说明", lines=10),
        title="获取当前用户首页关注用户及自己的饭否时间线",
        description="""
调用饭否 API 的 /statuses/home_timeline.json 接口获取当前用户的首页时间线，
包含用户关注的所有人的最新消息。

注：通常用户询问「我的饭否」时，指的是该时间线，除非用户明确指出「某个用户的饭否」。

Args:
    count: 获取数量，默认 5 条
    max_id: 返回列表中内容最新 ID，用于分页获取更早的内容，默认传递空字符串
    
Returns:
    首页时间线列表，每个元素包含：
    - 饭否内容: 消息文本内容（HTML 格式）
      * 转发：以「转@」开头，后跟用户链接，如 转@<a href="https://fanfou.com/~FgPOFSnmkW8" class="former">kingcos</a>，其中 href 中的是用户 ID，inner Text 是被转发用户的显示名称，一条饭否可能有多个转发
      * 话题：以「#」包围，如 #<a href="/q/%E6%AD%A3%E5%9C%A8%E6%92%AD%E6%94%BE">正在播放</a>#，其中 q/ 后面的是话题名，一条饭否可能有多个话题
      * 审核状态：如果内容末尾显示「【审核中】」，表示该内容正在审核中
    - 发布 ID: 消息的唯一标识符
    - 发布时间: 消息发布时间
    - 发布者: 发布者的用户名
    - 发布者 ID: 发布者的用户 ID
    - 图片链接: 如果包含图片，则提供图片链接
"""
    )
    
    user_timeline = gr.Interface(
        fn=get_user_timeline,
        inputs=[
            gr.Textbox(label="用户 ID（可选）", placeholder="留空获取当前用户时间线"),
            gr.Textbox(label="最大 ID（可选）", placeholder="用于分页获取更早内容"),
            gr.Number(label="获取数量", value=5, minimum=1, maximum=20),
            gr.Textbox(label="搜索关键词（可选）", placeholder="搜索该用户包含关键词的消息")
        ],
        outputs=gr.Textbox(label="使用说明", lines=10),
        title="根据用户 ID 获取某个用户发表内容的时间线",
        description="""
调用饭否 API 的 /statuses/user_timeline.json 接口获取指定用户的时间线。
如果 user_id 为空，则获取当前登录用户的时间线。

当提供搜索关键词时，会调用 /search/user_timeline.json 接口进行搜索。

Args:
    user_id: 用户 ID，如果为空则获取当前用户时间线
    max_id: 返回列表中内容最新 ID，用于分页获取更早的内容，默认传递空字符串
    count: 获取数量，默认 5 条
    q: 搜索关键词，如果为空则获取普通用户时间线；如果不为空则搜索该用户包含该关键词的消息
    
Returns:
    用户时间线列表，每个元素包含：
    - 饭否内容: 消息文本内容（HTML 格式）
      * 转发：以「转@」开头，后跟用户链接，如 转@<a href="https://fanfou.com/~FgPOFSnmkW8" class="former">kingcos</a>，其中 href 中的是用户 ID，inner Text 是被转发用户的显示名称，一条饭否可能有多个转发
      * 话题：以「#」包围，如 #<a href="/q/%E6%AD%A3%E5%9C%A8%E6%92%AD%E6%94%BE">正在播放</a>#，其中 q/ 后面的是话题名，一条饭否可能有多个话题
      * 审核状态：如果内容末尾显示「【审核中】」，表示该内容正在审核中
    - 发布 ID: 消息的唯一标识符
    - 发布时间: 消息发布时间
    - 发布者: 发布者的用户名
    - 发布者 ID: 发布者的用户 ID
    - 图片链接: 如果包含图片，则提供图片链接
"""
    )
    
    public_timeline = gr.Interface(
        fn=get_public_timeline,
        inputs=[
            gr.Number(label="获取数量", value=5, minimum=1, maximum=20),
            gr.Textbox(label="最大 ID（可选）", placeholder="用于分页获取更早内容"),
            gr.Textbox(label="搜索关键词（可选）", placeholder="搜索包含关键词的公开消息")
        ],
        outputs=gr.Textbox(label="使用说明", lines=10),
        title="获取公开时间线",
        description="""
调用饭否 API 的 /statuses/public_timeline.json 接口获取饭否全站最新的公开消息，
这些是所有用户可见的公开饭否内容。

当提供搜索关键词时，会调用 /search/public_timeline.json 接口进行搜索。

Args:
    count: 获取数量，默认 5 条
    max_id: 返回列表中内容最新 ID，用于分页获取更早的内容，默认传递空字符串
    q: 搜索关键词，如果为空则获取普通公开时间线；如果不为空则搜索包含该关键词的公开消息
    
Returns:
    公开时间线列表，每个元素包含：
    - 饭否内容: 消息文本内容（HTML 格式）
      * 转发：以「转@」开头，后跟用户链接，如 转@<a href="https://fanfou.com/~FgPOFSnmkW8" class="former">kingcos</a>，其中 href 中的是用户 ID，inner Text 是被转发用户的显示名称，一条饭否可能有多个转发
      * 话题：以「#」包围，如 #<a href="/q/%E6%AD%A3%E5%9C%A8%E6%92%AD%E6%94%BE">正在播放</a>#，其中 q/ 后面的是话题名，一条饭否可能有多个话题
      * 审核状态：如果内容末尾显示「【审核中】」，表示该内容正在审核中
    - 发布 ID: 消息的唯一标识符
    - 发布时间: 消息发布时间
    - 发布者: 发布者的用户名
    - 发布者 ID: 发布者的用户 ID
    - 图片链接: 如果包含图片，则提供图片链接
"""
    )
    
    # 用户和内容相关接口
    user_info = gr.Interface(
        fn=get_user_info,
        inputs=[
            gr.Textbox(label="用户 ID（可选）", placeholder="留空获取当前用户信息")
        ],
        outputs=gr.Textbox(label="使用说明", lines=10),
        title="获取用户信息",
        description="""
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
    )
    
    status_info = gr.Interface(
        fn=get_status_info,
        inputs=[
            gr.Textbox(label="饭否内容 ID", placeholder="要查询的饭否内容 ID")
        ],
        outputs=gr.Textbox(label="使用说明", lines=10),
        title="获取某条饭否内容的具体信息",
        description="""
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
    - 发布时间: 消息发布时间
    - 发布者: 发布者的显示名称
    - 发布者 ID: 发布者的用户 ID
    - 是否收藏: 当前用户是否收藏了该消息
    - 是否是自己: 是否是当前用户发布的消息
    - 发布位置: 消息发布的地理位置
    - 回复信息: 如果是回复消息，包含被回复的状态 ID、用户 ID 和用户名
    - 图片base64: 如果包含图片，则提供图片的 base64 编码（data URL 格式）
    - 图片链接: 如果包含图片，则提供原始图片链接作为备用
"""
    )
    
    # 互动相关接口
    favorite_manage = gr.Interface(
        fn=manage_favorite,
        inputs=[
            gr.Textbox(label="饭否内容 ID", placeholder="要操作的饭否内容 ID"),
            gr.Dropdown(label="操作类型", choices=["create", "destroy"], value="create"),
            gr.Checkbox(label="确认操作", value=False)
        ],
        outputs=gr.Textbox(label="使用说明", lines=10),
        title="管理饭否内容的收藏状态",
        description="""
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
    )
    
    friendship_manage = gr.Interface(
        fn=manage_friendship,
        inputs=[
            gr.Textbox(label="用户 ID", placeholder="要操作的用户 ID"),
            gr.Dropdown(label="操作类型", choices=["create", "destroy"], value="create"),
            gr.Checkbox(label="确认操作", value=False)
        ],
        outputs=gr.Textbox(label="使用说明", lines=10),
        title="管理用户关注状态",
        description="""
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
    )
    
    # 发布相关接口
    publish_text = gr.Interface(
        fn=publish_status,
        inputs=[
            gr.Textbox(label="饭否内容", placeholder="要发布的文字内容（最多140字）", lines=3),
            gr.Checkbox(label="确认发布", value=False)
        ],
        outputs=gr.Textbox(label="使用说明", lines=10),
        title="发布饭否内容（仅文字）",
        description="""
调用饭否 API 的 /statuses/update.json 接口发布纯文字内容。

Args:
    status: 要发布的文字内容（最多140字）
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
    )
    
    publish_image = gr.Interface(
        fn=publish_photo,
        inputs=[
            gr.Textbox(label="饭否内容", placeholder="要发布的文字内容（最多140字）", lines=3),
            gr.Textbox(label="图片 URL", placeholder="图片的网络地址"),
            gr.Checkbox(label="确认发布", value=False)
        ],
        outputs=gr.Textbox(label="使用说明", lines=10),
        title="发布饭否内容（文字+图片）",
        description="""
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
    )
    
    delete_content = gr.Interface(
        fn=delete_status,
        inputs=[
            gr.Textbox(label="饭否内容 ID", placeholder="要删除的饭否内容 ID"),
            gr.Checkbox(label="确认删除", value=False)
        ],
        outputs=gr.Textbox(label="使用说明", lines=10),
        title="删除饭否内容",
        description="""
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
    )

    
    # 组合所有接口
    return gr.TabbedInterface(
        [auth_interface, home_timeline, user_timeline, public_timeline, 
         user_info, status_info, favorite_manage, friendship_manage, 
         publish_text, publish_image, delete_content],
        ["生成 OAuth Token", "获取当前用户首页关注用户及自己的饭否时间线", "根据用户 ID 获取某个用户发表内容的时间线", "获取公开时间线", 
         "获取用户信息", "获取某条饭否内容的具体信息", "管理饭否内容的收藏状态", "管理用户关注状态", 
         "发布饭否内容（仅文字）", "发布饭否内容（文字+图片）", "删除饭否内容"],
        title="饭否 MCP 服务器"
    )

# ==================== 主程序 ====================

def main():
    """主程序入口"""
    # 创建 Gradio 应用
    app = create_interfaces()
    
    # 启动应用，同时启用 MCP 服务器
    app.launch(
        mcp_server=True,
        share=True
    )

if __name__ == "__main__":
    main() 