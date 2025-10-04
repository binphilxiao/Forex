#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FXCM 数据处理 Web 界面 (Flask版本)
==================================

轻量级、友好的Web界面，使用Flask框架

功能特点:
- 现代化的响应式设计
- 实时任务进度显示
- 简洁友好的用户界面
- 无多线程上下文问题

作者: Claude 4.5
创建时间: 2025-10-04
版本: 3.0.0
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, make_response
import subprocess
import sys
import threading
import queue
import json
from pathlib import Path
from datetime import datetime
import os

app = Flask(__name__)

# 全局变量
current_task_runner = None
task_status = {
    'running': False,
    'status': '就绪',
    'progress': 0,
    'task_name': ''
}

class TaskRunner:
    """任务运行器"""
    
    def __init__(self):
        self.process = None
        self.should_stop = False
        
    def run_script(self, script_name, task_name):
        """运行脚本"""
        global task_status
        
        task_status['running'] = True
        task_status['status'] = f'正在{task_name}...'
        task_status['progress'] = 0
        task_status['task_name'] = task_name
        
        print(f"\n{'='*60}")
        print(f"🚀 开始{task_name}")
        print(f"{'='*60}\n")
        
        try:
            self.process = subprocess.Popen(
                [sys.executable, script_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True
            )
            
            # 实时读取并打印输出到终端
            line_count = 0
            for line in self.process.stdout:
                if self.should_stop:
                    self.process.terminate()
                    print(f"\n⏹ {task_name}已被用户终止")
                    task_status['status'] = '已停止'
                    task_status['progress'] = 0
                    break
                    
                line = line.strip()
                if line:
                    print(line)  # 直接打印到终端
                    line_count += 1
                    # 简单的进度估算
                    if line_count % 10 == 0:
                        task_status['progress'] = min(95, task_status['progress'] + 5)
            
            # 等待完成
            if not self.should_stop:
                return_code = self.process.wait()
                
                if return_code == 0:
                    task_status['status'] = f'{task_name}完成'
                    task_status['progress'] = 100
                    print(f"\n✅ {task_name}成功完成！")
                else:
                    stderr = self.process.stderr.read()
                    task_status['status'] = f'{task_name}失败'
                    task_status['progress'] = 0
                    print(f"\n❌ {task_name}失败:")
                    print(stderr)
                    
        except Exception as e:
            task_status['status'] = f'{task_name}出错'
            task_status['progress'] = 0
            print(f"\n❌ 错误: {str(e)}")
            
        finally:
            if not self.should_stop:
                task_status['running'] = False
            self.process = None
            print(f"\n{'='*60}\n")
            
    def stop(self):
        """停止任务"""
        self.should_stop = True
        if self.process:
            try:
                self.process.terminate()
                print("\n⏹ 正在终止任务...")
            except:
                pass

# 路由
@app.route('/')
@app.route('/v3')
def index():
    """主页"""
    import time
    # 添加时间戳避免缓存
    version = int(time.time())
    response = make_response(render_template('index.html', v=version))
    # 强制禁用缓存
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/start_download', methods=['POST'])
def start_download():
    """开始下载"""
    global current_task_runner
    
    if task_status['running']:
        return jsonify({'success': False, 'message': '已有任务在运行'})
    
    current_task_runner = TaskRunner()
    thread = threading.Thread(target=current_task_runner.run_script, args=('download_fxcm_candles.py', '数据下载'))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': '下载任务已启动，请查看终端输出'})

@app.route('/api/start_conversion', methods=['POST'])
def start_conversion():
    """开始转换"""
    global current_task_runner
    
    if task_status['running']:
        return jsonify({'success': False, 'message': '已有任务在运行'})
    
    current_task_runner = TaskRunner()
    thread = threading.Thread(target=current_task_runner.run_script, args=('multi_timeframe_converter.py', '数据转换'))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': '转换任务已启动，请查看终端输出'})

@app.route('/api/start_analysis', methods=['POST'])
def start_analysis():
    """开始分析"""
    global current_task_runner
    
    if task_status['running']:
        return jsonify({'success': False, 'message': '已有任务在运行'})
    
    current_task_runner = TaskRunner()
    thread = threading.Thread(target=current_task_runner.run_script, args=('check_data_completeness.py', '数据分析'))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': '分析任务已启动，请查看终端输出'})

@app.route('/api/status')
def get_status():
    """获取状态"""
    return jsonify(task_status)

@app.route('/api/stop_task', methods=['POST'])
def stop_task():
    """停止任务"""
    global current_task_runner, task_status
    
    if not task_status['running']:
        return jsonify({'success': False, 'message': '没有正在运行的任务'})
    
    if current_task_runner:
        current_task_runner.stop()
        task_status['running'] = False
        task_status['status'] = '已停止'
        task_status['progress'] = 0
        return jsonify({'success': True, 'message': '任务已停止'})
    
    return jsonify({'success': False, 'message': '无法停止任务'})

@app.route('/static/<path:filename>')
def static_files(filename):
    """静态文件"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 FXCM 数据处理系统 - Web界面")
    print("版本: 3.0.1 (Flask)")
    print("=" * 60)
    print()
    print("🌐 访问地址: http://localhost:5000")
    print("📱 或手机访问: http://你的电脑IP:5000")
    print()
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()
    
    # 自动打开浏览器
    import webbrowser
    import threading
    import time
    
    def open_browser():
        time.sleep(1.5)  # 等待服务器完全启动
        try:
            webbrowser.open('http://127.0.0.1:5000')
            print("🔗 浏览器已自动打开\n")
        except:
            print("⚠️ 无法自动打开浏览器，请手动访问: http://127.0.0.1:5000\n")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
