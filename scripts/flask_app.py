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
版本: 4.1.1
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
    'task_name': '',
    'report_file': None  # 存储生成的报告文件路径
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
        task_status['report_file'] = None  # 清除之前的报告文件
        
        print(f"\n{'='*60}")
        print(f"🚀 开始{task_name}")
        print(f"🔧 调用脚本: {script_name}")
        print(f"{'='*60}\n")
        
        try:
            # 使用PYTHONUNBUFFERED环境变量确保输出不缓冲
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            
            self.process = subprocess.Popen(
                [sys.executable, '-u', script_name],  # -u 参数强制unbuffered输出
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 合并stderr到stdout
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=0,  # 无缓冲
                env=env
            )
            
            # 实时读取并打印输出到终端
            line_count = 0
            for line in iter(self.process.stdout.readline, ''):
                if self.should_stop:
                    self.process.terminate()
                    print(f"\n⏹ {task_name}已被用户终止")
                    task_status['status'] = '已停止'
                    task_status['progress'] = 0
                    break
                    
                line = line.rstrip()  # 只去掉右侧空白，保留左侧缩进
                if line:
                    print(line, flush=True)  # 直接打印到终端并刷新
                    sys.stdout.flush()  # 强制刷新标准输出
                    line_count += 1
                    # 简单的进度估算
                    if line_count % 10 == 0:
                        task_status['progress'] = min(95, task_status['progress'] + 5)
                    
                    # 捕获HTML报告文件路径
                    if task_name == '数据分析' and '🌐 HTML报告:' in line:
                        # 从日志中提取报告文件路径
                        try:
                            report_path = line.split('🌐 HTML报告:')[1].strip()
                            report_file = Path(report_path)
                            if report_file.exists():
                                task_status['report_file'] = report_file.name  # 只存储文件名
                                print(f"📋 已捕获报告文件: {report_file.name}", flush=True)
                        except:
                            pass
            
            # 等待完成
            if not self.should_stop:
                return_code = self.process.wait()
                
                if return_code == 0:
                    task_status['status'] = f'{task_name}完成'
                    task_status['progress'] = 100
                    print(f"\n✅ {task_name}成功完成！", flush=True)
                else:
                    task_status['status'] = f'{task_name}失败'
                    task_status['progress'] = 0
                    print(f"\n❌ {task_name}失败 (退出码: {return_code})", flush=True)
                    
        except FileNotFoundError:
            task_status['status'] = f'{task_name}出错'
            task_status['progress'] = 0
            print(f"\n❌ 错误: 找不到脚本文件 '{script_name}'", flush=True)
            print(f"请确认文件存在于当前目录: {os.getcwd()}", flush=True)
        except Exception as e:
            task_status['status'] = f'{task_name}出错'
            task_status['progress'] = 0
            print(f"\n❌ 错误: {str(e)}", flush=True)
            import traceback
            traceback.print_exc()
            
        finally:
            if not self.should_stop:
                task_status['running'] = False
            self.process = None
            print(f"\n{'='*60}\n", flush=True)
            
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
    
    # 获取配置
    config = request.get_json() or {}
    pairs = config.get('pairs', ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF'])
    start_year = config.get('start_year', 2015)
    end_year = config.get('end_year', 2021)
    retry_enabled = config.get('retry_enabled', True)
    retry_times = config.get('retry_times', 3)
    
    # 保存配置到JSON文件
    import json
    config_data = {
        'pairs': pairs,
        'start_year': start_year,
        'end_year': end_year,
        'retry_enabled': retry_enabled,
        'retry_times': retry_times
    }
    
    with open('download_config.json', 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 下载配置:")
    print(f"   外汇对: {', '.join(pairs)}")
    print(f"   年份范围: {start_year} - {end_year}")
    print(f"   失败重试: {'是' if retry_enabled else '否'}")
    if retry_enabled:
        print(f"   重试次数: {retry_times}")
    print()
    
    current_task_runner = TaskRunner()
    script_path = Path(__file__).parent / 'download_fxcm_candles.py'
    thread = threading.Thread(target=current_task_runner.run_script, args=(str(script_path), '数据下载'))
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
    script_path = Path(__file__).parent / 'convert_m1_to_multi_timeframes.py'
    thread = threading.Thread(target=current_task_runner.run_script, args=(str(script_path), '数据转换'))
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
    script_path = Path(__file__).parent / 'check_data_completeness.py'
    thread = threading.Thread(target=current_task_runner.run_script, args=(str(script_path), '数据分析'))
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

@app.route('/report/<path:filename>')
def serve_report(filename):
    """提供报告文件"""
    logs_dir = Path('logs')
    response = make_response(send_from_directory(logs_dir, filename))
    # 禁用缓存
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 FXCM 数据处理系统 - Web界面")
    print("版本: 4.1.1 (Flask)")
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
