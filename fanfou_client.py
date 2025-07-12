#!/usr/bin/env python3
"""
饭否 API 客户端
"""

import json
import urllib.parse
import oauth2
from typing import List, Dict, Any, Optional, Tuple


class FanFou:
    """饭否 API 客户端"""
    host = "fanfou.com"

    def __init__(self, api_key: str, api_secret: str, username: str = '', password: str = '', 
                 oauth_token: str = '', oauth_token_secret: str = ''):
        self.api_key = api_key
        self.api_secret = api_secret
        self.username = username
        self.password = password
        
        # 优先使用传入的 oauth token
        if oauth_token and oauth_token_secret:
            print('------ 使用已有的 OAuth Token ------')
            self.token = oauth_token
            self.token_secret = oauth_token_secret
        elif username and password:
            print('------ 使用用户名密码登录 ------')
            self.token, self.token_secret = self.login(username, password)
        else:
            raise Exception("必须提供 oauth_token + oauth_token_secret 或者 username + password")
        
        self.user_id = self.get_current_user_id()

    def login(self, username: str, password: str) -> Tuple[str, str]:
        """登录获取 OAuth token"""
        print('------ login ------')
        params = {'x_auth_username': username, 'x_auth_password': password, 'x_auth_mode': 'client_auth'}
        url = "http://fanfou.com/oauth/access_token?{}".format(urllib.parse.urlencode(params))

        consumer = oauth2.Consumer(self.api_key, self.api_secret)
        client = oauth2.Client(consumer)
        client.add_credentials(username, password)
        client.set_signature_method(oauth2.SignatureMethod_HMAC_SHA1())
        resp, token_bytes = client.request(url)
        tokens = dict(urllib.parse.parse_qsl(token_bytes.decode("utf-8")))

        if len(tokens) == 2:
            oauth_token = tokens['oauth_token']
            oauth_token_secret = tokens['oauth_token_secret']
            print('=' * 60)
            print('🎉 登录成功！已生成 OAuth Token')
            print('=' * 60)
            print(f'📋 请将以下环境变量保存到你的配置中：')
            print()
            print(f'FANFOU_OAUTH_TOKEN={oauth_token}')
            print(f'FANFOU_OAUTH_TOKEN_SECRET={oauth_token_secret}')
            print()
            print('💡 提示：')
            print('1. 将上述环境变量添加到你的 .env 文件中')
            print('2. 添加后即可移除 FANFOU_USERNAME 和 FANFOU_PASSWORD')
            print('3. OAuth Token 方式更安全且避免重复登录')
            print('=' * 60)
            return oauth_token, oauth_token_secret
        else:
            print('登录失败！')
            raise Exception('登录失败，请检查用户名和密码')

    def get_current_user_id(self) -> str:
        """获取当前用户 ID"""
        print('------ get_current_user_id ------')
        url = 'http://api.fanfou.com/account/verify_credentials.json'
        params = {'mode': 'lite'}

        consumer = oauth2.Consumer(self.api_key, self.api_secret)
        token = oauth2.Token(self.token, self.token_secret)
        client = oauth2.Client(consumer, token)

        response, content = client.request(url, method='POST', body=urllib.parse.urlencode(params))
        result = json.loads(content)
        return result['id']

    def request_user_timeline(self, user_id: str = '', max_id: str = '', count: int = 5, q: str = '') -> List[Dict[str, Any]]:
        """
        根据用户 ID 获取某个用户发表内容的时间线
        
        user_id 为用户 ID，如果为空，则获取当前用户时间线
        max_id 为返回列表中内容最新 ID，如果为空，则获取最新时间线
        count 为获取数量，默认 5 条
        q 为搜索关键词，如果为空，则获取普通用户时间线；如果不为空，则搜索该用户包含该关键词的消息
        """
        print('------ request_user_timeline ------')
        if user_id == '':
            user_id = self.user_id

        # 根据是否有搜索关键词选择不同的API接口
        if q:
            # 使用搜索接口
            url = f"http://api.fanfou.com/search/user_timeline.json?id={user_id}&count={count}&format=html&q={urllib.parse.quote(q)}"
            if max_id:
                url += f"&max_id={max_id}"
        else:
            # 使用普通用户时间线接口
            url = f"http://api.fanfou.com/statuses/user_timeline.json?id={user_id}&count={count}&format=html"
            if max_id:
                url = f"http://api.fanfou.com/statuses/user_timeline.json?max_id={max_id}&id={user_id}&count={count}&format=html"

        consumer = oauth2.Consumer(self.api_key, self.api_secret)
        token = oauth2.Token(self.token, self.token_secret)
        client = oauth2.Client(consumer, token)

        response, content = client.request(url)
        return json.loads(content)

    def get_home_timeline(self, count: int = 5, max_id: str = '') -> List[Dict[str, Any]]:
        """
        获取当前用户首页关注用户及自己的饭否时间线

        max_id 为返回列表中内容最新 ID，如果为空，则获取最新时间线
        count 为获取数量，默认 5 条
        """
        print('------ get_home_timeline ------')
        url = f"http://api.fanfou.com/statuses/home_timeline.json?count={count}&format=html"
        if max_id:
            url += f"&max_id={max_id}"

        consumer = oauth2.Consumer(self.api_key, self.api_secret)
        token = oauth2.Token(self.token, self.token_secret)
        client = oauth2.Client(consumer, token)

        response, content = client.request(url)
        return json.loads(content)

    def get_public_timeline(self, count: int = 5, max_id: str = '', q: str = '') -> List[Dict[str, Any]]:
        """
        获取公开时间线，获取饭否全站最新的公开消息
        
        max_id 为返回列表中内容最新 ID，如果为空，则获取最新时间线
        count 为获取数量，默认 5 条
        q 为搜索关键词，如果为空，则获取普通公开时间线；如果不为空，则搜索包含该关键词的公开消息
        """
        print('------ get_public_timeline ------')
        
        # 根据是否有搜索关键词选择不同的API接口
        if q:
            # 使用搜索接口
            url = f"http://api.fanfou.com/search/public_timeline.json?count={count}&format=html&mode=lite&q={urllib.parse.quote(q)}"
            if max_id:
                url += f"&max_id={max_id}"
        else:
            # 使用普通公开时间线接口
            url = f"http://api.fanfou.com/statuses/public_timeline.json?count={count}&format=html"
            if max_id:
                url += f"&max_id={max_id}"

        consumer = oauth2.Consumer(self.api_key, self.api_secret)
        token = oauth2.Token(self.token, self.token_secret)
        client = oauth2.Client(consumer, token)

        response, content = client.request(url)
        return json.loads(content)

    def get_user_info(self, user_id: str = '') -> Dict[str, Any]:
        """
        获取用户信息
        
        user_id 为用户 ID，如果为空，则获取当前用户信息
        """
        print('------ get_user_info ------')
        
        if user_id == '':
            user_id = self.user_id
        
        url = f"http://api.fanfou.com/users/show.json?id={user_id}"

        consumer = oauth2.Consumer(self.api_key, self.api_secret)
        token = oauth2.Token(self.token, self.token_secret)
        client = oauth2.Client(consumer, token)

        response, content = client.request(url)
        return json.loads(content)

    def get_status_info(self, status_id: str) -> Dict[str, Any]:
        """
        获取某条饭否内容的具体信息
        
        status_id 为饭否内容的 ID
        """
        print('------ get_status_info ------')
        
        url = f"http://api.fanfou.com/statuses/show/{status_id}.json?format=html"

        consumer = oauth2.Consumer(self.api_key, self.api_secret)
        token = oauth2.Token(self.token, self.token_secret)
        client = oauth2.Client(consumer, token)

        response, content = client.request(url)
        return json.loads(content)

    def manage_favorite(self, status_id: str, action: str) -> Dict[str, Any]:
        """
        管理饭否内容的收藏状态
        
        status_id 为饭否内容的 ID
        action 为操作类型：'create' 表示收藏，'destroy' 表示取消收藏
        """
        print(f'------ manage_favorite ({action}) ------')
        
        if action not in ['create', 'destroy']:
            raise ValueError("action 参数必须是 'create' 或 'destroy'")
        
        url = f"http://api.fanfou.com/favorites/{action}/{status_id}.json"

        consumer = oauth2.Consumer(self.api_key, self.api_secret)
        token = oauth2.Token(self.token, self.token_secret)
        client = oauth2.Client(consumer, token)

        response, content = client.request(url, method='POST')
        return json.loads(content) 

    def manage_friendship(self, user_id: str, action: str) -> Dict[str, Any]:
        """
        管理用户关注状态
        
        user_id 为目标用户 ID
        action 为操作类型：'create' 表示关注，'destroy' 表示取消关注
        """
        print(f'------ manage_friendship ({action}) ------')
        
        if action not in ['create', 'destroy']:
            raise ValueError("action 参数必须是 'create' 或 'destroy'")
        
        url = f"http://api.fanfou.com/friendships/{action}.json"
        params = {'id': user_id}

        consumer = oauth2.Consumer(self.api_key, self.api_secret)
        token = oauth2.Token(self.token, self.token_secret)
        client = oauth2.Client(consumer, token)

        response, content = client.request(url, method='POST', body=urllib.parse.urlencode(params))
        return json.loads(content) 

    def publish_status(self, status: str) -> Dict[str, Any]:
        """
        发布饭否内容（仅文字）
        
        status 为要发布的文字内容（最多140字）
        """
        print('------ publish_status ------')
        
        if len(status) > 140:
            raise ValueError("饭否内容不能超过140字")
        
        url = "http://api.fanfou.com/statuses/update.json"
        params = {'status': status}

        consumer = oauth2.Consumer(self.api_key, self.api_secret)
        token = oauth2.Token(self.token, self.token_secret)
        client = oauth2.Client(consumer, token)

        response, content = client.request(url, method='POST', body=urllib.parse.urlencode(params))
        return json.loads(content)

    def publish_photo(self, status: str, photo_url: str) -> Dict[str, Any]:
        """
        发布饭否内容（文字+图片）
        
        status 为要发布的文字内容（最多140字）
        photo_url 为图片的网络 URL 地址
        """
        print('------ publish_photo ------')
        
        if len(status) > 140:
            raise ValueError("饭否内容不能超过140字")
        
        # 下载图片
        import requests
        try:
            print(f"正在下载图片: {photo_url}")
            response = requests.get(photo_url, timeout=30)
            response.raise_for_status()
            photo_data = response.content
            
            # 获取图片的 MIME 类型
            content_type = response.headers.get('content-type', '')
            if content_type.startswith('image/'):
                mime_type = content_type
            else:
                # 根据 URL 扩展名猜测 MIME 类型
                import mimetypes
                mime_type, _ = mimetypes.guess_type(photo_url)
                if mime_type is None or not mime_type.startswith('image/'):
                    mime_type = 'image/jpeg'  # 默认为 JPEG
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"无法下载图片: {str(e)}")
        except Exception as e:
            raise ValueError(f"下载图片时发生错误: {str(e)}")
        
        # 检查图片大小（饭否图片限制通常为5MB）
        if len(photo_data) > 5 * 1024 * 1024:  # 5MB
            raise ValueError("图片文件过大，请选择小于5MB的图片")
        
        # 检查是否为有效的图片数据
        if len(photo_data) < 100:  # 太小的文件可能不是有效图片
            raise ValueError("下载的文件可能不是有效的图片")
        
        url = "http://api.fanfou.com/photos/upload.json"
        
        # 构建multipart/form-data格式的数据
        import uuid
        
        # 生成边界标识符
        boundary = f"----formdata-{uuid.uuid4().hex}"
        
        # 构建multipart数据
        body_parts = []
        
        # 添加status字段
        body_parts.append(f'--{boundary}')
        body_parts.append('Content-Disposition: form-data; name="status"')
        body_parts.append('Content-Type: text/plain')
        body_parts.append('')
        body_parts.append(status)
        
        # 添加photo字段
        # 根据 MIME 类型确定文件扩展名
        if 'png' in mime_type:
            filename = 'image.png'
        elif 'gif' in mime_type:
            filename = 'image.gif'
        elif 'bmp' in mime_type:
            filename = 'image.bmp'
        elif 'webp' in mime_type:
            filename = 'image.webp'
        else:
            filename = 'image.jpg'
            
        body_parts.append(f'--{boundary}')
        body_parts.append(f'Content-Disposition: form-data; name="photo"; filename="{filename}"')
        body_parts.append(f'Content-Type: {mime_type}')
        body_parts.append('')
        
        # 将文本部分合并
        body_text = '\r\n'.join(body_parts) + '\r\n'
        
        # 构建完整的body（文本 + 图片数据 + 结束边界）
        body = body_text.encode('utf-8') + photo_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')
        
        # 设置请求头
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(body))
        }

        consumer = oauth2.Consumer(self.api_key, self.api_secret)
        token = oauth2.Token(self.token, self.token_secret)
        client = oauth2.Client(consumer, token)

        response, content = client.request(url, method='POST', body=body, headers=headers)
        return json.loads(content) 

    def delete_status(self, status_id: str) -> Dict[str, Any]:
        """
        删除饭否内容
        
        status_id 为要删除的饭否内容的 ID
        """
        print('------ delete_status ------')
        
        url = "http://api.fanfou.com/statuses/destroy.json"
        params = {'id': status_id}

        consumer = oauth2.Consumer(self.api_key, self.api_secret)
        token = oauth2.Token(self.token, self.token_secret)
        client = oauth2.Client(consumer, token)

        response, content = client.request(url, method='POST', body=urllib.parse.urlencode(params))
        return json.loads(content) 