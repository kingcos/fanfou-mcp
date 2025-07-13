#!/usr/bin/env python3
"""
工具函数模块

包含各种通用的工具函数
"""

import base64
import requests
from typing import Optional


def image_url_to_base64(large_url: str, normal_url: str = "") -> Optional[str]:
    """
    将图片URL转换为base64编码
    
    如果大图(largeurl)超过300KB，则使用普通图片(imageurl)进行转换
    
    Args:
        large_url: 大图的URL地址
        normal_url: 普通图片的URL地址，如果大图过大则使用此URL
        
    Returns:
        base64编码的图片数据（data URL格式），如果失败则返回None
    """
    try:
        # 首先尝试获取大图的大小
        head_response = requests.head(large_url, timeout=10)
        head_response.raise_for_status()
        
        # 获取内容长度
        content_length = head_response.headers.get('content-length')
        if content_length:
            file_size = int(content_length)
            # 如果大图超过300KB且有普通图片URL，则使用普通图片
            if file_size > 300 * 1024 and normal_url:
                print(f"大图尺寸 {file_size} 字节超过300KB，使用普通图片")
                image_url = normal_url
            else:
                image_url = large_url
        else:
            # 如果无法获取大小信息，默认使用大图
            image_url = large_url
        
        # 下载图片
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # 获取图片内容类型
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        # 转换为base64
        image_base64 = base64.b64encode(response.content).decode('utf-8')
        
        # 返回data URL格式
        return f"data:{content_type};base64,{image_base64}"
    except Exception as e:
        print(f"转换图片为base64失败: {e}")
        return None 