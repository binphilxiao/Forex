#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FXCM Web界面启动脚本
===================

自动检查依赖并启动Flask Web界面

版本: 4.1.1
"""

import sys
import subprocess
from pathlib import Path

def check_and_install_dependencies():
    """检查并安装依赖"""
    print("🔍 检查依赖库...")
    print()
    
    required = {
        'flask': 'Flask',
        'pandas': 'pandas',
        'requests': 'requests'
    }
    
    missing = []
    
    for package, display_name in required.items():
        try:
            __import__(package)
            print(f"  ✅ {display_name}")
        except ImportError:
            print(f"  ❌ {display_name} - 缺失")
            missing.append(package)
    
    if missing:
        print(f"\n📦 需要安装: {', '.join(missing)}")
        response = input("是否自动安装？(y/n): ").strip().lower()
        
        if response == 'y':
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install'] + missing
                )
                print("\n✅ 依赖安装成功！")
                return True
            except subprocess.CalledProcessError:
                print("\n❌ 依赖安装失败")
                print("请手动安装: pip install " + " ".join(missing))
                return False
        else:
            print("\n⚠️  请手动安装依赖后再运行")
            return False
    
    print()
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("   FXCM 数据处理系统 - Web界面启动器")
    print("   版本: 4.1.1 (Flask)")
    print("=" * 60)
    print()
    
    # 检查Flask应用文件
    app_file = Path('flask_app.py')
    if not app_file.exists():
        print("❌ 错误: flask_app.py 文件不存在！")
        input("\n按任意键退出...")
        return
    
    # 检查依赖
    if not check_and_install_dependencies():
        input("\n按任意键退出...")
        return
    
    # 启动Flask应用并自动打开浏览器
    print("🚀 启动Web服务器...")
    print("🌐 浏览器将在1.5秒后自动打开...")
    print()
    
    # 延迟打开浏览器
    import threading
    import webbrowser
    import time
    
    def open_browser():
        time.sleep(1.5)  # 等待服务器启动
        print("🔗 正在打开浏览器...")
        webbrowser.open('http://127.0.0.1:5000')
    
    # 在后台线程打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        subprocess.run([sys.executable, 'flask_app.py'])
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        input("\n按任意键退出...")

if __name__ == '__main__':
    main()
