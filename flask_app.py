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

from flask import Flask, render_template, request, jsonify, send_from_directory
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
task_queue = queue.Queue()
current_task = None
task_status = {
    'running': False,
    'status': '就绪',
    'progress': 0,
    'logs': []
}

class TaskRunner:
    """任务运行器"""
    
    def __init__(self):
        self.process = None
        self.log_queue = queue.Queue()
        
    def run_script(self, script_name, task_name):
        """运行脚本"""
        global task_status
        
        task_status['running'] = True
        task_status['status'] = f'正在{task_name}...'
        task_status['progress'] = 10
        task_status['logs'] = []
        
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
            
            # 读取输出
            for line in self.process.stdout:
                line = line.strip()
                if line:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    log_entry = {'time': timestamp, 'message': line, 'level': self._get_log_level(line)}
                    task_status['logs'].append(log_entry)
                    task_status['progress'] = min(90, task_status['progress'] + 1)
            
            # 等待完成
            return_code = self.process.wait()
            
            if return_code == 0:
                task_status['status'] = f'{task_name}完成'
                task_status['progress'] = 100
                self._add_log(f'✅ {task_name}成功完成！', 'success')
            else:
                stderr = self.process.stderr.read()
                task_status['status'] = f'{task_name}失败'
                self._add_log(f'❌ {task_name}失败: {stderr[:200]}', 'error')
                
        except Exception as e:
            task_status['status'] = f'{task_name}出错'
            self._add_log(f'❌ 错误: {str(e)}', 'error')
            
        finally:
            task_status['running'] = False
            self.process = None
            
    def _get_log_level(self, message):
        """判断日志级别"""
        if '✅' in message or '成功' in message:
            return 'success'
        elif '❌' in message or '错误' in message or '失败' in message:
            return 'error'
        elif '⚠️' in message or '警告' in message:
            return 'warning'
        else:
            return 'info'
            
    def _add_log(self, message, level='info'):
        """添加日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = {'time': timestamp, 'message': message, 'level': level}
        task_status['logs'].append(log_entry)
        
    def stop(self):
        """停止任务"""
        if self.process:
            self.process.terminate()
            self._add_log('⏹ 任务已被用户终止', 'warning')
            task_status['running'] = False
            task_status['status'] = '已停止'

# 路由
@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/start_download', methods=['POST'])
def start_download():
    """开始下载"""
    if task_status['running']:
        return jsonify({'success': False, 'message': '已有任务在运行'})
    
    runner = TaskRunner()
    thread = threading.Thread(target=runner.run_script, args=('download_fxcm_candles.py', '数据下载'))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': '下载任务已启动'})

@app.route('/api/start_conversion', methods=['POST'])
def start_conversion():
    """开始转换"""
    if task_status['running']:
        return jsonify({'success': False, 'message': '已有任务在运行'})
    
    runner = TaskRunner()
    thread = threading.Thread(target=runner.run_script, args=('convert_m1_to_multi_timeframes.py', '数据转换'))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': '转换任务已启动'})

@app.route('/api/start_analysis', methods=['POST'])
def start_analysis():
    """开始分析"""
    if task_status['running']:
        return jsonify({'success': False, 'message': '已有任务在运行'})
    
    runner = TaskRunner()
    thread = threading.Thread(target=runner.run_script, args=('check_data_completeness.py', '数据分析'))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': '分析任务已启动'})

@app.route('/api/status')
def get_status():
    """获取状态"""
    return jsonify(task_status)

@app.route('/api/clear_logs', methods=['POST'])
def clear_logs():
    """清空日志"""
    task_status['logs'] = []
    return jsonify({'success': True})

@app.route('/static/<path:filename>')
def static_files(filename):
    """静态文件"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 FXCM 数据处理系统 - Web界面")
    print("版本: 3.0.0 (Flask)")
    print("=" * 60)
    print()
    print("🌐 访问地址: http://localhost:5000")
    print("📱 或手机访问: http://你的电脑IP:5000")
    print()
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
