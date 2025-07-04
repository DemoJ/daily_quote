#!/usr/bin/env python3
"""
每日一言系统启动脚本
"""
import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"   当前版本: {sys.version}")
        sys.exit(1)
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")


def check_env_file():
    """检查环境变量文件"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  未找到 .env 文件，正在从 .env.example 创建...")
            env_file.write_text(env_example.read_text(encoding='utf-8'), encoding='utf-8')
            print("✅ 已创建 .env 文件")
        else:
            print("❌ 错误: 未找到 .env 和 .env.example 文件")
            sys.exit(1)
    
    # 检查关键配置
    env_content = env_file.read_text(encoding='utf-8')
    if "your_openai_api_key_here" in env_content:
        print("⚠️  警告: 请在 .env 文件中配置您的 OpenAI API Key")
        print("   编辑 .env 文件，将 OPENAI_API_KEY 设置为您的实际API密钥")
        
        # 询问是否继续
        response = input("是否继续启动？(y/N): ").strip().lower()
        if response != 'y':
            print("启动已取消")
            sys.exit(0)
    
    print("✅ 环境配置文件检查完成")


def install_dependencies():
    """安装依赖包"""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ 错误: 未找到 requirements.txt 文件")
        sys.exit(1)
    
    print("📦 检查并安装依赖包...")
    try:
        # 检查是否在虚拟环境中
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ 检测到虚拟环境")
        else:
            print("⚠️  建议在虚拟环境中运行")
        
        # 安装依赖
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True)
        
        print("✅ 依赖包安装完成")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装依赖包失败: {e}")
        print("请手动运行: pip install -r requirements.txt")
        sys.exit(1)


def create_directories():
    """创建必要的目录"""
    directories = ["static", "templates", "app"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ 目录结构检查完成")


def main():
    """主函数"""
    print("🚀 正在启动每日一言系统...")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 检查环境配置
    check_env_file()
    
    # 创建目录
    create_directories()
    
    # 安装依赖
    install_dependencies()
    
    print("=" * 50)
    print("🎉 准备工作完成，正在启动应用...")
    print()
    
    # 启动应用
    try:
        import uvicorn

        # 从环境变量获取配置
        host = os.getenv("APP_HOST", "0.0.0.0")
        port = int(os.getenv("APP_PORT", "8000"))
        debug = os.getenv("DEBUG", "True").lower() == "true"

        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if debug else "warning"
        )
        
    except KeyboardInterrupt:
        print("\n👋 感谢使用每日一言系统！")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
