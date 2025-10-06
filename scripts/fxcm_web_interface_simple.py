#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FXCM 数据处理 Web 界面 - 简化版
=================================

独立的Web界面，不依赖现有模块
提供基础的界面操作和任务启动功能

作者: AI Assistant
创建时间: 2025-10-04
版本: 1.0.2
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import subprocess
import sys
import os
from datetime import datetime
import json

class SimpleFXCMWebInterface:
    """简化版FXCM数据处理Web界面"""
    
    def __init__(self):
        self.base_path = Path('fxcm_data')
        self.logs_path = Path('logs')
        self.instruments = ['EURUSD', 'USDCAD', 'GBPUSD', 'USDCHF', 'AUDUSD', 'USDJPY']
        self.timeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'D1']
        self.start_year = 2015
        self.end_year = 2025
        
        # 初始化会话状态
        self.init_session_state()
        
    def init_session_state(self):
        """初始化Streamlit会话状态"""
        if 'task_running' not in st.session_state:
            st.session_state.task_running = False
            
        if 'task_status' not in st.session_state:
            st.session_state.task_status = "就绪"
            
        if 'last_log_update' not in st.session_state:
            st.session_state.last_log_update = datetime.now()
    
    def render_header(self):
        """渲染页面头部"""
        st.set_page_config(
            page_title="FXCM 数据处理系统", 
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("📈 FXCM 历史数据处理系统")
        st.markdown("---")
        
        # 状态指示器
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_color = "🟢" if not st.session_state.task_running else "🟡"
            st.metric("系统状态", f"{status_color} {st.session_state.task_status}")
            
        with col2:
            if self.base_path.exists():
                total_files = len(list(self.base_path.rglob("*.csv")))
                st.metric("数据文件数", f"{total_files:,}")
            else:
                st.metric("数据文件数", "0")
                
        with col3:
            if self.base_path.exists():
                total_size = sum(f.stat().st_size for f in self.base_path.rglob("*.csv") if f.exists())
                size_mb = total_size / (1024 * 1024)
                st.metric("数据大小", f"{size_mb:.1f} MB")
            else:
                st.metric("数据大小", "0 MB")
                
        with col4:
            if self.logs_path.exists():
                log_files = len(list(self.logs_path.glob("*.log")))
                st.metric("日志文件数", f"{log_files}")
            else:
                st.metric("日志文件数", "0")
    
    def render_sidebar(self):
        """渲染侧边栏配置"""
        st.sidebar.header("⚙️ 配置选项")
        
        # 货币对选择
        st.sidebar.subheader("货币对选择")
        selected_instruments = st.sidebar.multiselect(
            "选择要处理的货币对:",
            options=self.instruments,
            default=self.instruments[:3],  # 默认选择前3个
            key="selected_instruments"
        )
        
        # 时间范围选择
        st.sidebar.subheader("时间范围")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_year = st.number_input("开始年份", 
                                       min_value=2010, 
                                       max_value=2025, 
                                       value=2020,  # 默认较小范围
                                       key="start_year")
        with col2:
            end_year = st.number_input("结束年份", 
                                     min_value=2010, 
                                     max_value=2025, 
                                     value=2022,  # 默认较小范围
                                     key="end_year")
        
        # 时间周期选择（转换用）
        st.sidebar.subheader("转换时间周期")
        conversion_timeframes = st.sidebar.multiselect(
            "选择要生成的时间周期:",
            options=['M5', 'M15', 'M30', 'H1'],
            default=['M5', 'M15'],  # 默认选择较少周期
            key="conversion_timeframes"
        )
        
        # 高级选项
        st.sidebar.subheader("高级选项")
        max_retries = st.sidebar.slider("重试次数", 1, 10, 5, key="max_retries")
        skip_existing = st.sidebar.checkbox("跳过已存在文件", value=True, key="skip_existing")
        
        return {
            'instruments': selected_instruments,
            'start_year': start_year,
            'end_year': end_year,
            'conversion_timeframes': conversion_timeframes,
            'max_retries': max_retries,
            'skip_existing': skip_existing
        }
    
    def check_script_files(self):
        """检查必要的脚本文件是否存在"""
        required_scripts = {
            'fxcm_data_downloader.py': 'FXCM数据下载器v2.0',
            'm1_timeframe_converter.py': 'M1时间框架转换器v2.0',
            'verify_data_consistency.py': '数据一致性验证工具'
        }
        
        missing_scripts = []
        existing_scripts = []
        
        for script, desc in required_scripts.items():
            if Path(script).exists():
                existing_scripts.append((script, desc))
            else:
                missing_scripts.append((script, desc))
        
        return existing_scripts, missing_scripts
    
    def check_m1_data_exists(self):
        """检查M1数据是否存在"""
        if not self.base_path.exists():
            return False
        
        m1_files = list(self.base_path.rglob("*/M1/*/*.csv"))
        return len(m1_files) > 0
    
    def run_script_command(self, script_name, description):
        """运行脚本命令"""
        try:
            st.session_state.task_running = True
            st.session_state.task_status = f"{description}中..."
            
            # 显示启动信息
            with st.spinner(f'正在启动{description}...'):
                # 构建命令
                python_exe = sys.executable
                script_path = Path(script_name)
                
                if not script_path.exists():
                    st.error(f"❌ 脚本文件不存在: {script_name}")
                    return False
                
                # 在后台启动脚本
                process = subprocess.Popen(
                    [python_exe, str(script_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=Path.cwd()
                )
                
                st.success(f"✅ {description}已启动！")
                st.info("💡 任务在后台运行，请查看日志文件了解详细进度")
                
                return True
                
        except Exception as e:
            st.error(f"❌ 启动失败: {str(e)}")
            return False
        finally:
            st.session_state.task_running = False
            st.session_state.task_status = "就绪"
    
    def render_data_download_tab(self, config):
        """渲染数据下载标签页"""
        st.header("📥 数据下载")
        
        # 检查脚本文件
        existing_scripts, missing_scripts = self.check_script_files()
        download_script_exists = any(script[0] == 'fxcm_data_downloader.py' for script in existing_scripts)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(f"""
            **下载配置:**
            - 货币对: {', '.join(config['instruments']) if config['instruments'] else '未选择'}
            - 时间范围: {config['start_year']} - {config['end_year']}
            - 重试次数: {config['max_retries']}
            - 跳过已存在: {'是' if config['skip_existing'] else '否'}
            """)
            
        with col2:
            # 检查下载条件
            can_download = (download_script_exists and 
                          len(config['instruments']) > 0 and
                          not st.session_state.task_running)
            
            download_btn = st.button(
                "🚀 开始下载", 
                disabled=not can_download,
                key="download_button",
                use_container_width=True,
                help="开始下载选中的货币对数据"
            )
            
        # 显示状态信息
        if not download_script_exists:
            st.error("❌ 下载脚本不存在: fxcm_data_downloader.py")
        elif len(config['instruments']) == 0:
            st.warning("⚠️ 请先选择要下载的货币对")
        elif st.session_state.task_running:
            st.info("🔄 有任务正在运行，请等待完成")
            
        if download_btn and can_download:
            self.run_script_command('fxcm_data_downloader.py', 'FXCM数据下载')
            st.rerun()
            
        # 显示下载统计
        self.render_download_stats()
    
    def render_data_conversion_tab(self, config):
        """渲染数据转换标签页"""
        st.header("🔄 数据转换")
        
        # 检查脚本文件
        existing_scripts, missing_scripts = self.check_script_files()
        convert_script_exists = any(script[0] == 'convert_m1_to_multi_timeframes.py' for script in existing_scripts)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(f"""
            **转换配置:**
            - 货币对: {', '.join(config['instruments']) if config['instruments'] else '未选择'}
            - 目标时间周期: {', '.join(config['conversion_timeframes']) if config['conversion_timeframes'] else '未选择'}
            - 跳过已存在: {'是' if config['skip_existing'] else '否'}
            """)
            
        with col2:
            # 检查转换条件
            has_m1_data = self.check_m1_data_exists()
            can_convert = (convert_script_exists and
                          has_m1_data and
                          len(config['instruments']) > 0 and
                          len(config['conversion_timeframes']) > 0 and
                          not st.session_state.task_running)
            
            convert_btn = st.button(
                "⚡ 开始转换", 
                disabled=not can_convert,
                key="convert_button",
                use_container_width=True,
                help="开始转换M1数据到多时间周期"
            )
            
        # 显示状态信息
        if not convert_script_exists:
            st.error("❌ 转换脚本不存在: convert_m1_to_multi_timeframes.py")
        elif not has_m1_data:
            st.warning("⚠️ 未发现M1数据，请先下载数据")
        elif len(config['instruments']) == 0:
            st.warning("⚠️ 请选择要转换的货币对")
        elif len(config['conversion_timeframes']) == 0:
            st.warning("⚠️ 请选择要生成的时间周期")
        elif st.session_state.task_running:
            st.info("🔄 有任务正在运行，请等待完成")
            
        if convert_btn and can_convert:
            self.run_script_command('convert_m1_to_multi_timeframes.py', '数据转换')
            st.rerun()
            
        # 显示转换统计
        self.render_conversion_stats()
    
    def render_data_analysis_tab(self):
        """渲染数据分析标签页"""
        st.header("📊 数据分析")
        
        # 检查脚本文件
        existing_scripts, missing_scripts = self.check_script_files()
        analysis_script_exists = any(script[0] == 'verify_data_consistency.py' for script in existing_scripts)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info("""
            **分析功能:**
            - 检查数据完整性
            - 生成可视化报告
            - 统计缺失数据
            - 计算完整率
            """)
            
        with col2:
            # 检查分析条件
            has_any_data = self.base_path.exists() and len(list(self.base_path.rglob("*.csv"))) > 0
            can_analyze = (analysis_script_exists and
                          has_any_data and
                          not st.session_state.task_running)
            
            analyze_btn = st.button(
                "🔍 分析数据", 
                disabled=not can_analyze,
                key="analyze_button",
                use_container_width=True,
                help="分析数据完整性并生成报告"
            )
            
        # 显示状态信息
        if not analysis_script_exists:
            st.error("❌ 分析脚本不存在: verify_data_consistency.py")
        elif not has_any_data:
            st.warning("⚠️ 未发现数据文件，请先下载数据")
        elif st.session_state.task_running:
            st.info("🔄 有任务正在运行，请等待完成")
            
        if analyze_btn and can_analyze:
            self.run_script_command('verify_data_consistency.py', '数据一致性验证')
            st.rerun()
            
        # 显示数据概览
        self.render_data_overview()
    
    def render_system_status_tab(self):
        """渲染系统状态标签页"""
        st.header("🔧 系统状态")
        
        # 脚本文件检查
        st.subheader("📄 脚本文件检查")
        existing_scripts, missing_scripts = self.check_script_files()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**✅ 可用脚本:**")
            if existing_scripts:
                for script, desc in existing_scripts:
                    st.success(f"✅ {script} - {desc}")
            else:
                st.info("暂无可用脚本")
                
        with col2:
            st.write("**❌ 缺失脚本:**")
            if missing_scripts:
                for script, desc in missing_scripts:
                    st.error(f"❌ {script} - {desc}")
            else:
                st.success("所有脚本文件完整")
        
        # 目录结构检查
        st.subheader("📂 目录结构")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**数据目录:**")
            if self.base_path.exists():
                st.success(f"✅ {self.base_path} 存在")
                
                # 显示货币对目录
                for instrument in self.instruments:
                    instrument_path = self.base_path / instrument
                    if instrument_path.exists():
                        timeframes = [tf for tf in self.timeframes if (instrument_path / tf).exists()]
                        st.info(f"📁 {instrument}: {', '.join(timeframes) if timeframes else '无数据'}")
            else:
                st.warning(f"⚠️ {self.base_path} 不存在")
                
        with col2:
            st.write("**日志目录:**")
            if self.logs_path.exists():
                st.success(f"✅ {self.logs_path} 存在")
                log_files = list(self.logs_path.glob("*.log"))
                st.info(f"📋 日志文件数量: {len(log_files)}")
            else:
                st.warning(f"⚠️ {self.logs_path} 不存在")
        
        # 最新日志文件
        st.subheader("📋 最新日志")
        if self.logs_path.exists():
            log_files = sorted(self.logs_path.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
            
            if log_files:
                latest_log = log_files[0]
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.info(f"最新日志: {latest_log.name}")
                
                with col2:
                    if st.button("📖 查看日志", key="view_log"):
                        try:
                            with open(latest_log, 'r', encoding='utf-8') as f:
                                log_content = f.read()
                            
                            st.text_area(
                                f"日志内容 - {latest_log.name}",
                                value=log_content,
                                height=300,
                                key="log_content"
                            )
                        except Exception as e:
                            st.error(f"读取日志文件失败: {e}")
            else:
                st.info("暂无日志文件")
        else:
            st.warning("日志目录不存在")
    
    def render_download_stats(self):
        """渲染下载统计"""
        st.subheader("📈 下载统计")
        
        if not self.base_path.exists():
            st.warning("数据目录不存在")
            return
            
        # 统计各类型文件
        m1_files = list(self.base_path.rglob("*/M1/*/*.csv"))
        d1_files = list(self.base_path.rglob("*/D1/*.csv"))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("M1文件数", len(m1_files))
        with col2:
            st.metric("D1文件数", len(d1_files))
        with col3:
            total_size = sum(f.stat().st_size for f in m1_files + d1_files if f.exists())
            st.metric("总大小", f"{total_size / (1024*1024):.1f} MB")
        with col4:
            # 估算完整率
            expected_files = len(self.instruments) * 10 * 50  # 估算
            completeness = min(100, len(m1_files) / max(1, expected_files) * 100)
            st.metric("估算完整率", f"{completeness:.1f}%")
    
    def render_conversion_stats(self):
        """渲染转换统计"""
        st.subheader("⚡ 转换统计")
        
        if not self.base_path.exists():
            st.warning("数据目录不存在")
            return
            
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            m5_files = len(list(self.base_path.rglob("*/M5/*/*.csv")))
            st.metric("M5文件数", m5_files)
        with col2:
            m15_files = len(list(self.base_path.rglob("*/M15/*/*.csv")))
            st.metric("M15文件数", m15_files)
        with col3:
            m30_files = len(list(self.base_path.rglob("*/M30/*/*.csv")))
            st.metric("M30文件数", m30_files)
        with col4:
            h1_files = len(list(self.base_path.rglob("*/H1/*/*.csv")))
            st.metric("H1文件数", h1_files)
    
    def render_data_overview(self):
        """渲染数据概览"""
        st.subheader("📊 数据概览")
        
        if not self.base_path.exists():
            st.warning("数据目录不存在")
            return
        
        # 创建数据概览图表
        data_summary = []
        
        for instrument in self.instruments:
            instrument_path = self.base_path / instrument
            if instrument_path.exists():
                for tf in self.timeframes:
                    tf_path = instrument_path / tf
                    if tf_path.exists():
                        files = list(tf_path.rglob("*.csv"))
                        data_summary.append({
                            'Instrument': instrument,
                            'Timeframe': tf,
                            'Files': len(files)
                        })
        
        if data_summary:
            df = pd.DataFrame(data_summary)
            
            # 创建热力图
            pivot_df = df.pivot(index='Instrument', columns='Timeframe', values='Files').fillna(0)
            
            fig = go.Figure(data=go.Heatmap(
                z=pivot_df.values,
                x=pivot_df.columns,
                y=pivot_df.index,
                colorscale='Blues',
                text=pivot_df.values,
                texttemplate="%{text}",
                textfont={"size": 10},
                colorbar=dict(title="文件数量")
            ))
            
            fig.update_layout(
                title="数据文件分布热力图",
                xaxis_title="时间周期",
                yaxis_title="货币对",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无数据可显示")
    
    def run(self):
        """运行Web界面"""
        # 渲染头部
        self.render_header()
        
        # 渲染侧边栏
        config = self.render_sidebar()
        
        # 创建主要标签页
        tab1, tab2, tab3, tab4 = st.tabs(["📥 数据下载", "🔄 数据转换", "📊 数据分析", "🔧 系统状态"])
        
        with tab1:
            self.render_data_download_tab(config)
            
        with tab2:
            self.render_data_conversion_tab(config)
            
        with tab3:
            self.render_data_analysis_tab()
            
        with tab4:
            self.render_system_status_tab()

def main():
    """主函数"""
    try:
        # 创建并运行Web界面
        app = SimpleFXCMWebInterface()
        app.run()
        
    except Exception as e:
        st.error(f"应用启动失败: {str(e)}")
        st.write("请检查以下事项:")
        st.write("1. 确保已安装所需依赖: `pip install streamlit plotly pandas`")
        st.write("2. 确保在正确的项目目录中运行")
        st.write("3. 检查文件权限和路径设置")

if __name__ == "__main__":
    main()