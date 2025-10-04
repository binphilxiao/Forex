#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FXCM 图形界面启动脚本
====================

自动检查依赖并启动图形界面

版本: 2.0.0
"""

import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查必要的依赖库"""
    print("🔍 检查依赖库...")
    
    required = {
        'pandas': 'pandas',
        'requests': 'requests',
        'tkinter': 'tk'  # tkinter通常内置
    }
    
    missing = []
    
    for package, import_name in required.items():
        try:
            if import_name == 'tk':
                import tkinter
            else:
                __import__(import_name)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - 缺失")
            missing.append(package)
    
    return missing

def install_dependencies(packages):
    """安装缺失的依赖"""
    if not packages:
        return True
        
    print(f"\n📦 需要安装: {', '.join(packages)}")
    response = input("是否自动安装？(y/n): ").strip().lower()
    
    if response == 'y':
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'] + packages
            )
            print("✅ 依赖安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败")
            return False
    else:
        print("⚠️  请手动安装依赖: pip install " + " ".join(packages))
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("   FXCM 数据处理系统 - 图形界面")
    print("   版本: 2.0.0 (Tkinter)")
    print("=" * 50)
    print()
    
    # 检查GUI文件是否存在
    gui_file = Path('fxcm_gui.py')
    if not gui_file.exists():
        print("❌ 错误: fxcm_gui.py 文件不存在！")
        input("按任意键退出...")
        return
    
    # 检查依赖
    missing = check_dependencies()
    
    if missing and 'tkinter' not in missing:
        if not install_dependencies([p for p in missing if p != 'tkinter']):
            input("\n按任意键退出...")
            return
    elif 'tkinter' in missing:
        print("\n❌ tkinter 未安装")
        print("tkinter 通常随Python一起安装")
        print("如果缺失，请重新安装Python并确保勾选tk/tkinter组件")
        input("\n按任意键退出...")
        return
    
    # 启动GUI
    print("\n🚀 启动图形界面...")
    print()
    
    try:
        subprocess.run([sys.executable, 'fxcm_gui.py'])
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        input("\n按任意键退出...")

if __name__ == '__main__':
    main()
