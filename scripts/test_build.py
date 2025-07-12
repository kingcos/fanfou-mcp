#!/usr/bin/env python3
"""
测试构建脚本 - 验证包的构建过程
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """运行命令并检查结果"""
    print(f"\n🔄 {description}")
    print(f"运行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} 成功")
        if result.stdout:
            print(f"输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"错误: {e.stderr}")
        return False

def main():
    """主函数"""
    print("🚀 开始测试包构建过程")
    
    # 检查是否在项目根目录
    if not Path("pyproject.toml").exists():
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 清理之前的构建
    if Path("dist").exists():
        print("🧹 清理之前的构建文件")
        subprocess.run(["rm", "-rf", "dist"], check=True)
    
    # 测试步骤
    steps = [
        (["uv", "sync"], "安装依赖"),
        (["uv", "build"], "构建包"),
        (["uv", "run", "twine", "check", "dist/*"], "检查包"),
    ]
    
    success_count = 0
    for cmd, desc in steps:
        if run_command(cmd, desc):
            success_count += 1
        else:
            break
    
    # 显示构建结果
    if success_count == len(steps):
        print("\n🎉 所有测试步骤都成功完成！")
        print("\n📦 构建的文件:")
        if Path("dist").exists():
            for file in Path("dist").iterdir():
                print(f"  - {file.name}")
        
        print("\n✨ 你的包已准备好发布到 PyPI！")
        print("\n📝 下一步:")
        print("1. 创建 GitHub Release 来自动发布到 PyPI")
        print("2. 或者手动运行 GitHub Action")
        print("3. 确保已在 PyPI 上配置了可信发布")
    else:
        print(f"\n❌ 测试失败 ({success_count}/{len(steps)} 步骤成功)")
        sys.exit(1)

if __name__ == "__main__":
    main() 