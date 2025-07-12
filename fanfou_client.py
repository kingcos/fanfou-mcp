#!/usr/bin/env python3
"""
饭否 API 客户端
"""

import json
import urllib.parse
import oauth2
from typing import List, Dict, Any


class FanFou:
    """饭否 API 客户端"""
    host = "fanfou.com"

    def __init__(self, api_key: str, api_secret: str, username: str, password: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.token, self.token_secret = self.login(username, password)
        self.user_id = self.get_current_user_id()

    def login(self, username: str, password: str) -> tuple:
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
            return tokens['oauth_token'], tokens['oauth_token_secret']
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

    def request_user_timeline(self, user_id: str = '', max_id: str = '', count: int = 5) -> List[Dict[str, Any]]:
        """
        根据用户 ID 获取某个用户时间线
        如果 user_id 为空，则获取当前用户时间线
        max_id 为空，则获取最新时间线
        count 为获取数量，默认 5 条
        """
        print('------ request_user_timeline ------')
        if user_id == '':
            user_id = self.user_id

        url = f"http://api.fanfou.com/statuses/user_timeline.json?id={user_id}&count={count}&format=html"
        if len(max_id):
            url = f"http://api.fanfou.com/statuses/user_timeline.json?max_id={max_id}&id={user_id}&count={count}&format=html"

        consumer = oauth2.Consumer(self.api_key, self.api_secret)
        token = oauth2.Token(self.token, self.token_secret)
        client = oauth2.Client(consumer, token)

        response, content = client.request(url)
        return json.loads(content)

    def get_home_timeline(self, count: int = 5, max_id: str = '') -> List[Dict[str, Any]]:
        """
        获取当前用户首页时间线
        如果 max_id 为空，则获取最新时间线
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