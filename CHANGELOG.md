# 更新日志

本文档记录了 fanfou-mcp 项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2024-07-13

### 新增
- 初始版本发布
- 基于 FastMCP 框架构建的饭否 MCP 服务器
- 支持饭否 API 的主要功能：
  - 认证管理（OAuth Token 生成）
  - 时间线获取（首页、用户、公开时间线）
  - 用户信息查询
  - 内容管理（发布、删除、收藏）
  - 社交功能（关注、取消关注）
- 完整的 API 文档
- MIT 许可证

### 技术特性
- Python 3.11+ 支持
- 使用 uv 包管理器
- 支持 MCP (Model Context Protocol) 协议
- OAuth2 认证支持
- 完整的错误处理和用户确认机制 