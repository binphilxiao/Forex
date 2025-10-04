#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本输出
用于验证终端输出是否正常工作
"""

import time

print("=" * 60)
print("🧪 测试脚本开始")
print("=" * 60)
print()

for i in range(1, 11):
    print(f"📊 进度: {i * 10}% - 这是第 {i} 行输出")
    time.sleep(0.5)

print()
print("=" * 60)
print("✅ 测试脚本完成")
print("=" * 60)
