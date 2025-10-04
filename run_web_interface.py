#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FXCM 数据处理系统启动脚本
========================

快速启动 Streamlit Web 界面的便捷脚本

使用方法:
1. 直接运行: python run_web_interface.py
2. 或使用 streamlit run fxcm_web_interface.py

作者: AI Assistant  
创建时间: 2025-10-04
版本: 1.0.2
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """检查必要的依赖库"""
    required_packages = [
        'streamlit',
        'plotly',
        'pandas',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(packages):
    """安装缺失的依赖库"""
    print(f"正在安装缺失的依赖库: {', '.join(packages)}")
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ 成功安装 {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 安装 {package} 失败: {e}")
            return False
    
    return True

def main():
    """主函数"""
    print("🚀 启动 FXCM 数据处理系统 Web 界面")
    print("=" * 50)
    
    # 检查当前目录
    current_dir = Path.cwd()
    web_interface_file = current_dir / 'fxcm_web_interface.py'
    
    if not web_interface_file.exists():
        print("❌ 错误: 找不到 fxcm_web_interface.py 文件")
        print(f"请确保在正确的目录中运行此脚本: {current_dir}")
        return
    
    # 检查依赖
    print("🔍 检查依赖库...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"⚠️  发现缺失的依赖库: {', '.join(missing_packages)}")
        
        user_input = input("是否自动安装缺失的依赖库? (y/n): ").lower().strip()
        
        if user_input in ['y', 'yes']:
            if not install_dependencies(missing_packages):
                print("❌ 依赖库安装失败，请手动安装后再试")
                return
        else:
            print("💡 请手动安装依赖库:")
            print(f"   pip install {' '.join(missing_packages)}")
            return
    
    print("✅ 所有依赖库检查完成")
    
    # 启动 Streamlit 应用
    print("\n🌐 启动 Web 界面...")
    print("📱 界面将在浏览器中自动打开")
    print("🔗 如果没有自动打开，请访问: http://localhost:8501")
    print("\n⏹️  按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    try:
        # 启动 Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            str(web_interface_file),
            '--server.address', 'localhost',
            '--server.port', '8501',
            '--browser.gatherUsageStats', 'false'
        ])
    except KeyboardInterrupt:
        print("\n👋 Web 界面已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n💡 手动启动方法:")
        print(f"   streamlit run {web_interface_file}")

if __name__ == "__main__":
    main()