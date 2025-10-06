#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FXCM 数据处理系统 - 快速开始演示
==============================

这个脚本演示了如何快速设置和启动FXCM数据处理系统的Web界面

使用方法:
1. python demo_setup.py
2. 按照提示完成设置
3. 自动启动Web界面

作者: AI Assistant
创建时间: 2025-10-04
版本: 1.0.2
"""

import subprocess
import sys
import os
from pathlib import Path

def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    FXCM 数据处理系统                          ║
║                      快速开始演示                             ║
║                                                              ║
║  🚀 一键式设置和启动Web可视化界面                              ║
║  📊 集成数据下载、转换、分析功能                               ║
║  🌐 现代化Web界面，支持实时监控                               ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    
    version_info = sys.version_info
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        print(f"   当前版本: Python {version_info.major}.{version_info.minor}.{version_info.micro}")
        return False
    
    print(f"✅ Python版本检查通过: {version_info.major}.{version_info.minor}.{version_info.micro}")
    return True

def setup_virtual_environment():
    """设置虚拟环境"""
    venv_path = Path('.venv')
    
    if venv_path.exists():
        print("✅ 虚拟环境已存在")
        return True
    
    print("📦 创建虚拟环境...")
    try:
        subprocess.check_call([sys.executable, '-m', 'venv', '.venv'])
        print("✅ 虚拟环境创建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 虚拟环境创建失败: {e}")
        return False

def install_requirements():
    """安装依赖库"""
    requirements_file = Path('requirements.txt')
    
    if not requirements_file.exists():
        print("⚠️  requirements.txt文件不存在，手动安装核心依赖...")
        core_packages = ['streamlit', 'plotly', 'pandas', 'requests']
    else:
        print("📚 从requirements.txt安装依赖库...")
        core_packages = None
    
    try:
        if core_packages:
            for package in core_packages:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        else:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        
        print("✅ 依赖库安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖库安装失败: {e}")
        return False

def check_required_files():
    """检查必要的文件"""
    required_files = [
        'fxcm_web_interface.py',
        'fxcm_data_downloader.py',
        'm1_timeframe_converter.py',
        'verify_data_consistency.py'
    ]
    
    print("📁 检查必要文件...")
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少以下必要文件:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ 所有必要文件检查完成")
    return True

def create_directories():
    """创建必要的目录"""
    directories = ['fxcm_data', 'logs']
    
    print("📂 创建必要目录...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ 目录结构创建完成")

def show_usage_guide():
    """显示使用指南"""
    guide = """
🎯 使用指南:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📥 数据下载:
   1. 在Web界面选择"数据下载"标签页
   2. 配置货币对和时间范围
   3. 点击"开始下载"按钮
   
🔄 数据转换:
   1. 确保已有M1数据
   2. 选择"数据转换"标签页
   3. 配置要生成的时间周期
   4. 点击"开始转换"按钮
   
📊 数据分析:
   1. 选择"数据分析"标签页
   2. 点击"分析数据"按钮
   3. 查看完整性热力图和统计信息
   
📋 实时监控:
   1. 在"实时日志"标签页查看任务进度
   2. 可以按日志级别过滤信息
   3. 支持自动滚动和手动清空

🌐 Web界面地址: http://localhost:8501
⏹️  停止服务: 按 Ctrl+C

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    print(guide)

def main():
    """主函数"""
    print_banner()
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 检查必要文件
    if not check_required_files():
        print("\n💡 请确保所有脚本文件都在当前目录中")
        return
    
    # 创建目录结构
    create_directories()
    
    # 安装依赖
    print("\n" + "="*60)
    user_input = input("🤔 是否需要安装Python依赖库? (y/n): ").lower().strip()
    
    if user_input in ['y', 'yes']:
        if not install_requirements():
            print("\n💡 请手动安装依赖库后再试:")
            print("   pip install streamlit plotly pandas requests")
            return
    
    # 显示使用指南
    show_usage_guide()
    
    # 询问是否立即启动
    print("="*60)
    user_input = input("🚀 是否立即启动Web界面? (y/n): ").lower().strip()
    
    if user_input in ['y', 'yes']:
        print("\n🌐 正在启动Web界面...")
        print("📱 界面将在浏览器中自动打开: http://localhost:8501")
        print("⏹️  按 Ctrl+C 停止服务器")
        print("="*60)
        
        try:
            # 启动Web界面
            web_interface = Path('fxcm_web_interface.py')
            subprocess.run([
                sys.executable, '-m', 'streamlit', 'run', 
                str(web_interface),
                '--server.address', 'localhost',
                '--server.port', '8501'
            ])
        except KeyboardInterrupt:
            print("\n\n👋 Web界面已停止，感谢使用!")
        except Exception as e:
            print(f"\n❌ 启动失败: {e}")
    else:
        print("\n💡 手动启动Web界面:")
        print("   python run_web_interface.py")
        print("   或者: streamlit run fxcm_web_interface.py")
        
    print("\n🎉 设置完成! 享受使用FXCM数据处理系统!")

if __name__ == "__main__":
    main()