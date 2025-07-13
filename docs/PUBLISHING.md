# 发布到 PyPI 指南

本文档详细说明如何将 `fanfou-mcp` 包发布到 PyPI。

## 🚀 自动发布（推荐）

我们已经配置了 GitHub Actions 来自动发布到 PyPI。有两种方式触发发布：

### 方式 1：通过 GitHub Release（推荐）

1. **创建新的 Git 标签**：
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. **在 GitHub 上创建 Release**：
   - 访问：https://github.com/kingcos/fanfou-mcp/releases
   - 点击 "Create a new release"
   - 选择刚创建的标签 `v0.1.0`
   - 填写 Release 标题和描述
   - 点击 "Publish release"

3. **自动发布**：
   - GitHub Action 会自动触发
   - 包会自动构建并发布到 PyPI
   - 可以在 Actions 页面查看进度

### 方式 2：手动触发 GitHub Action

1. **访问 Actions 页面**：
   - 前往：https://github.com/kingcos/fanfou-mcp/actions
   - 选择 "Publish to PyPI" workflow

2. **手动运行**：
   - 点击 "Run workflow"
   - 选择是否发布到 Test PyPI（用于测试）
   - 点击 "Run workflow" 按钮

## 🧪 测试发布

在正式发布前，建议先发布到 Test PyPI 进行测试：

1. **手动触发 GitHub Action**
2. **勾选 "Publish to Test PyPI"**
3. **验证包**：
   ```bash
   pip install -i https://test.pypi.org/simple/ fanfou-mcp
   ```

## 🔧 本地测试构建

在发布前，可以本地测试构建过程：

```bash
# 运行测试构建脚本
python scripts/test_build.py

# 或者手动测试
uv sync
uv build
uv run twine check dist/*
```

## ⚙️ PyPI 配置要求

我们提供了两种认证方式，你可以选择其中一种：

### 方式 A：可信发布设置（推荐）

使用 `.github/workflows/publish.yml` 工作流。

**优点**：
- 更安全，不需要管理 API Token
- PyPI 官方推荐的方式
- 自动轮换凭据

**配置步骤**：
1. **登录 PyPI**：访问 https://pypi.org/
2. **创建项目**（如果是首次发布）
3. **配置可信发布**：
   - 前往项目设置页面
   - 添加可信发布者
   - 配置信息：
     - Owner: `kingcos`
     - Repository: `fanfou-mcp`
     - Workflow: `publish.yml`
     - Environment: `pypi`

### 方式 B：API Token 认证

使用 `.github/workflows/publish-with-token.yml` 工作流。

**优点**：
- 设置简单
- 适合个人项目
- 立即可用

**配置步骤**：
1. **获取 PyPI API Token**：
   - 登录 https://pypi.org/
   - 前往 Account settings → API tokens
   - 创建新的 API token
   - 复制 token（格式：`pypi-xxx...`）

2. **设置 GitHub Secrets**：
   - 前往仓库 Settings → Secrets and variables → Actions
   - 添加以下 secrets：
     - `PYPI_API_TOKEN`：你的 PyPI API token
     - `TEST_PYPI_API_TOKEN`：Test PyPI 的 API token（可选）

3. **禁用默认工作流**：
   - 重命名或删除 `.github/workflows/publish.yml`
   - 启用 `.github/workflows/publish-with-token.yml`

### GitHub 环境设置

**仅适用于可信发布方式**，在 GitHub 仓库中配置环境：

1. **前往仓库设置**：Settings → Environments
2. **创建环境**：
   - 名称：`pypi`
   - 名称：`test-pypi`
3. **配置保护规则**（可选）：
   - 需要审查者
   - 等待计时器
   - 部署分支限制

**注意**：如果使用 API Token 方式，不需要创建环境，但仍需要设置 Secrets。

## 📝 版本管理

### 版本号规范

使用语义化版本（SemVer）：
- `MAJOR.MINOR.PATCH`
- 例如：`0.1.0`, `0.1.1`, `0.2.0`, `1.0.0`

### 更新版本

1. **更新 `pyproject.toml`**：
   ```toml
   [project]
   version = "0.1.1"  # 更新版本号
   ```

2. **提交更改**：
   ```bash
   git add pyproject.toml
   git commit -m "bump version to 0.1.1"
   git push
   ```

3. **创建标签和 Release**（参考上面的步骤）

## 🔍 发布检查清单

发布前请确认：

- [ ] 版本号已更新
- [ ] CHANGELOG 已更新（如果有）
- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] 构建测试成功
- [ ] PyPI 可信发布已配置
- [ ] GitHub 环境已设置

## 🚨 故障排除

### 常见问题

1. **构建失败**：
   - 检查 `pyproject.toml` 配置
   - 确保所有依赖都正确安装
   - 运行本地测试构建

2. **发布权限错误**：
   - 确认 PyPI 可信发布配置正确
   - 检查 GitHub 环境设置
   - 验证仓库权限

3. **包名冲突**：
   - 检查 PyPI 上是否已存在同名包
   - 考虑更改包名

### 获取帮助

如果遇到问题：
1. 查看 GitHub Actions 日志
2. 检查 PyPI 项目页面
3. 参考 PyPI 官方文档
4. 提交 Issue 到项目仓库

## 📚 相关资源

- [PyPI 官方文档](https://packaging.python.org/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [可信发布指南](https://docs.pypi.org/trusted-publishers/)
- [语义化版本](https://semver.org/) 