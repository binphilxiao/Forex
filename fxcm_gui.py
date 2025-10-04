#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FXCM 数据处理图形界面 (Tkinter版本)
====================================

简单、稳定、易用的图形界面，集成所有FXCM数据处理功能

功能特点:
- 基于Tkinter的原生图形界面
- 数据下载管理
- 多时间周期转换
- 数据完整性分析
- 实时进度显示
- 详细日志输出

作者: Claude 4.5
创建时间: 2025-10-04
版本: 2.0.0
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import sys
import threading
from pathlib import Path
from datetime import datetime
import queue
import os

class FXCMDataGUI:
    """FXCM数据处理图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("FXCM 历史数据处理系统 v2.0")
        self.root.geometry("1000x700")
        
        # 配置样式
        self.setup_styles()
        
        # 任务队列和状态
        self.task_running = False
        self.current_process = None
        self.log_queue = queue.Queue()
        
        # 创建界面
        self.create_widgets()
        
        # 启动日志更新
        self.update_log_display()
        
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置颜色
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        style.configure('TButton', font=('Arial', 10), padding=10)
        style.configure('Success.TButton', background='#27ae60', foreground='white')
        style.configure('Danger.TButton', background='#e74c3c', foreground='white')
        style.configure('Primary.TButton', background='#3498db', foreground='white')
        
    def create_widgets(self):
        """创建所有界面组件"""
        
        # 顶部标题
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(title_frame, text="📈 FXCM 历史数据处理系统", 
                               style='Title.TLabel')
        title_label.pack()
        
        # 主要内容区域
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        left_panel = ttk.Frame(main_frame, padding="5")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        # 右侧日志显示
        right_panel = ttk.Frame(main_frame, padding="5")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建控制面板内容
        self.create_control_panel(left_panel)
        
        # 创建日志显示区域
        self.create_log_panel(right_panel)
        
        # 底部状态栏
        self.create_status_bar()
        
    def create_control_panel(self, parent):
        """创建控制面板"""
        
        # 货币对选择
        currency_frame = ttk.LabelFrame(parent, text="货币对选择", padding="10")
        currency_frame.pack(fill=tk.X, pady=5)
        
        self.currency_vars = {}
        currencies = ['EURUSD', 'USDCAD', 'GBPUSD', 'USDCHF', 'AUDUSD', 'USDJPY']
        
        for i, currency in enumerate(currencies):
            var = tk.BooleanVar(value=True)
            self.currency_vars[currency] = var
            cb = ttk.Checkbutton(currency_frame, text=currency, variable=var)
            cb.grid(row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2)
        
        # 年份范围选择
        year_frame = ttk.LabelFrame(parent, text="年份范围", padding="10")
        year_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(year_frame, text="起始年份:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.start_year = ttk.Spinbox(year_frame, from_=2015, to=2025, width=10)
        self.start_year.set(2015)
        self.start_year.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(year_frame, text="结束年份:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.end_year = ttk.Spinbox(year_frame, from_=2015, to=2025, width=10)
        self.end_year.set(2025)
        self.end_year.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # 时间周期选择（用于转换）
        timeframe_frame = ttk.LabelFrame(parent, text="转换时间周期", padding="10")
        timeframe_frame.pack(fill=tk.X, pady=5)
        
        self.timeframe_vars = {}
        timeframes = ['M5', 'M15', 'M30', 'H1']
        
        for i, tf in enumerate(timeframes):
            var = tk.BooleanVar(value=True)
            self.timeframe_vars[tf] = var
            cb = ttk.Checkbutton(timeframe_frame, text=tf, variable=var)
            cb.grid(row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2)
        
        # 操作按钮
        button_frame = ttk.LabelFrame(parent, text="操作", padding="10")
        button_frame.pack(fill=tk.X, pady=5)
        
        self.btn_download = ttk.Button(button_frame, text="📥 下载数据", 
                                      command=self.start_download,
                                      style='Primary.TButton')
        self.btn_download.pack(fill=tk.X, pady=3)
        
        self.btn_convert = ttk.Button(button_frame, text="🔄 转换数据", 
                                     command=self.start_conversion,
                                     style='Primary.TButton')
        self.btn_convert.pack(fill=tk.X, pady=3)
        
        self.btn_analyze = ttk.Button(button_frame, text="📊 分析数据", 
                                     command=self.start_analysis,
                                     style='Primary.TButton')
        self.btn_analyze.pack(fill=tk.X, pady=3)
        
        ttk.Separator(button_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        self.btn_stop = ttk.Button(button_frame, text="⏹ 停止任务", 
                                   command=self.stop_task,
                                   style='Danger.TButton',
                                   state=tk.DISABLED)
        self.btn_stop.pack(fill=tk.X, pady=3)
        
        self.btn_clear = ttk.Button(button_frame, text="🗑 清空日志", 
                                    command=self.clear_log)
        self.btn_clear.pack(fill=tk.X, pady=3)
        
        # 快捷操作
        quick_frame = ttk.LabelFrame(parent, text="快捷操作", padding="10")
        quick_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(quick_frame, text="📂 打开数据目录", 
                  command=self.open_data_folder).pack(fill=tk.X, pady=2)
        ttk.Button(quick_frame, text="📄 打开日志目录", 
                  command=self.open_log_folder).pack(fill=tk.X, pady=2)
        
    def create_log_panel(self, parent):
        """创建日志显示面板"""
        
        log_label = ttk.Label(parent, text="📋 实时日志", style='Header.TLabel')
        log_label.pack(anchor=tk.W, pady=5)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, 
                                                  font=('Consolas', 9),
                                                  bg='#2c3e50', fg='#ecf0f1')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置日志颜色标签
        self.log_text.tag_config('INFO', foreground='#3498db')
        self.log_text.tag_config('SUCCESS', foreground='#27ae60')
        self.log_text.tag_config('WARNING', foreground='#f39c12')
        self.log_text.tag_config('ERROR', foreground='#e74c3c')
        self.log_text.tag_config('TIMESTAMP', foreground='#95a5a6')
        
        self.add_log("系统已启动，准备就绪", "INFO")
        
    def create_status_bar(self):
        """创建状态栏"""
        
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN, padding="2")
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="就绪", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate', length=200)
        self.progress.pack(side=tk.RIGHT, padx=5)
        
    def add_log(self, message, level='INFO'):
        """添加日志消息"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_queue.put((timestamp, message, level))
        
    def update_log_display(self):
        """更新日志显示"""
        try:
            while True:
                timestamp, message, level = self.log_queue.get_nowait()
                
                self.log_text.insert(tk.END, f"[{timestamp}] ", 'TIMESTAMP')
                self.log_text.insert(tk.END, f"{message}\n", level)
                self.log_text.see(tk.END)
                
        except queue.Empty:
            pass
        
        # 继续更新
        self.root.after(100, self.update_log_display)
        
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.add_log("日志已清空", "INFO")
        
    def get_selected_currencies(self):
        """获取选中的货币对"""
        return [curr for curr, var in self.currency_vars.items() if var.get()]
        
    def set_task_running(self, running):
        """设置任务运行状态"""
        self.task_running = running
        
        if running:
            self.btn_download.config(state=tk.DISABLED)
            self.btn_convert.config(state=tk.DISABLED)
            self.btn_analyze.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.progress.start(10)
        else:
            self.btn_download.config(state=tk.NORMAL)
            self.btn_convert.config(state=tk.NORMAL)
            self.btn_analyze.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            self.progress.stop()
            
    def run_script_in_thread(self, script_name, task_name):
        """在后台线程中运行脚本"""
        
        def worker():
            self.add_log(f"开始{task_name}...", "INFO")
            self.status_label.config(text=f"正在{task_name}...")
            
            try:
                # 运行脚本
                self.current_process = subprocess.Popen(
                    [sys.executable, script_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # 实时读取输出
                for line in self.current_process.stdout:
                    line = line.strip()
                    if line:
                        # 根据内容确定日志级别
                        if '✅' in line or '成功' in line:
                            self.add_log(line, "SUCCESS")
                        elif '❌' in line or '错误' in line or '失败' in line:
                            self.add_log(line, "ERROR")
                        elif '⚠️' in line or '警告' in line:
                            self.add_log(line, "WARNING")
                        else:
                            self.add_log(line, "INFO")
                
                # 等待完成
                return_code = self.current_process.wait()
                
                if return_code == 0:
                    self.add_log(f"{task_name}完成！", "SUCCESS")
                    self.status_label.config(text=f"{task_name}完成")
                    messagebox.showinfo("完成", f"{task_name}已成功完成！")
                else:
                    stderr = self.current_process.stderr.read()
                    self.add_log(f"{task_name}失败: {stderr}", "ERROR")
                    self.status_label.config(text=f"{task_name}失败")
                    messagebox.showerror("错误", f"{task_name}失败！\n{stderr[:200]}")
                    
            except Exception as e:
                self.add_log(f"{task_name}出错: {str(e)}", "ERROR")
                self.status_label.config(text=f"{task_name}出错")
                messagebox.showerror("错误", f"{task_name}出错！\n{str(e)}")
                
            finally:
                self.current_process = None
                self.set_task_running(False)
        
        # 启动线程
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        
    def start_download(self):
        """开始下载数据"""
        if self.task_running:
            messagebox.showwarning("警告", "已有任务正在运行！")
            return
            
        selected = self.get_selected_currencies()
        if not selected:
            messagebox.showwarning("警告", "请至少选择一个货币对！")
            return
            
        self.add_log(f"准备下载货币对: {', '.join(selected)}", "INFO")
        self.add_log(f"年份范围: {self.start_year.get()} - {self.end_year.get()}", "INFO")
        
        self.set_task_running(True)
        self.run_script_in_thread('download_fxcm_candles.py', '数据下载')
        
    def start_conversion(self):
        """开始数据转换"""
        if self.task_running:
            messagebox.showwarning("警告", "已有任务正在运行！")
            return
            
        # 检查是否有M1数据
        data_path = Path('fxcm_data')
        has_m1_data = False
        
        if data_path.exists():
            for currency_dir in data_path.iterdir():
                if currency_dir.is_dir():
                    m1_dir = currency_dir / 'M1'
                    if m1_dir.exists() and any(m1_dir.rglob('*.csv')):
                        has_m1_data = True
                        break
        
        if not has_m1_data:
            messagebox.showwarning("警告", "未发现M1数据！\n请先下载数据。")
            return
            
        selected_tf = [tf for tf, var in self.timeframe_vars.items() if var.get()]
        if not selected_tf:
            messagebox.showwarning("警告", "请至少选择一个时间周期！")
            return
            
        self.add_log(f"准备转换时间周期: {', '.join(selected_tf)}", "INFO")
        
        self.set_task_running(True)
        self.run_script_in_thread('convert_m1_to_multi_timeframes.py', '数据转换')
        
    def start_analysis(self):
        """开始数据分析"""
        if self.task_running:
            messagebox.showwarning("警告", "已有任务正在运行！")
            return
            
        # 检查是否有数据
        data_path = Path('fxcm_data')
        if not data_path.exists() or not any(data_path.rglob('*.csv')):
            messagebox.showwarning("警告", "未发现数据文件！\n请先下载数据。")
            return
            
        self.add_log("开始数据完整性分析...", "INFO")
        
        self.set_task_running(True)
        self.run_script_in_thread('check_data_completeness.py', '数据分析')
        
    def stop_task(self):
        """停止当前任务"""
        if self.current_process:
            if messagebox.askyesno("确认", "确定要停止当前任务吗？"):
                self.current_process.terminate()
                self.add_log("任务已被用户终止", "WARNING")
                self.status_label.config(text="任务已终止")
                self.set_task_running(False)
                
    def open_data_folder(self):
        """打开数据文件夹"""
        data_path = Path('fxcm_data')
        if data_path.exists():
            os.startfile(data_path)
        else:
            messagebox.showinfo("提示", "数据目录尚不存在")
            
    def open_log_folder(self):
        """打开日志文件夹"""
        log_path = Path('logs')
        if log_path.exists():
            os.startfile(log_path)
        else:
            messagebox.showinfo("提示", "日志目录尚不存在")

def main():
    """主函数"""
    root = tk.Tk()
    app = FXCMDataGUI(root)
    
    # 设置窗口图标（可选）
    try:
        root.iconbitmap(default='icon.ico')  # 如果有图标文件
    except:
        pass
    
    # 运行主循环
    root.mainloop()

if __name__ == '__main__':
    main()
