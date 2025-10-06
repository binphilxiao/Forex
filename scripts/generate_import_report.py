#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HTML导入报告生成器
用于快速导入模式生成详细的HTML报告
"""

from datetime import datetime
from pathlib import Path
from collections import defaultdict


def generate_html_report(d1_result, m1_result):
    """生成HTML导入报告
    
    参数:
        d1_result: D1导入结果字典
        m1_result: M1导入结果字典
    
    返回:
        报告文件路径
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 统计信息
    total_files = d1_result['total_files'] + m1_result['total_files']
    total_inserted = d1_result['total_inserted'] + m1_result['total_inserted']
    total_skipped = d1_result['total_skipped'] + m1_result['total_skipped']
    total_errors = d1_result['error_count'] + m1_result['error_count']
    total_time = d1_result['elapsed_time'] + m1_result['elapsed_time']
    
    # 按货币对统计
    symbol_stats = defaultdict(lambda: {'inserted': 0, 'skipped': 0, 'files': 0, 'errors': 0})
    
    for file_detail in d1_result.get('file_details', []) + m1_result.get('file_details', []):
        symbol = file_detail['symbol']
        symbol_stats[symbol]['files'] += 1
        symbol_stats[symbol]['inserted'] += file_detail['inserted']
        symbol_stats[symbol]['skipped'] += file_detail['skipped']
        if file_detail['status'] == 'error':
            symbol_stats[symbol]['errors'] += 1
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FXCM 数据导入报告 - 快速模式</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        .header .mode-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        .header p {{
            margin-top: 15px;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 25px;
            padding: 40px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            text-align: center;
            border-left: 5px solid;
            transition: transform 0.2s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        .stat-card.success {{ border-left-color: #28a745; }}
        .stat-card.warning {{ border-left-color: #ffc107; }}
        .stat-card.info {{ border-left-color: #17a2b8; }}
        .stat-card.danger {{ border-left-color: #dc3545; }}
        .stat-card.primary {{ border-left-color: #007bff; }}
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .stat-label {{
            color: #6c757d;
            font-size: 0.95em;
            margin-top: 8px;
        }}
        .section {{
            padding: 40px;
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 1.8em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            background: white;
            box-shadow: 0 2px 15px rgba(0,0,0,0.08);
            border-radius: 8px;
            overflow: hidden;
        }}
        thead {{
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
            color: white;
        }}
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 500;
            font-size: 0.95em;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        tbody tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tbody tr:hover {{
            background-color: #e3f2fd;
            transition: background-color 0.2s;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .status-inserted {{ background: #d4edda; color: #155724; }}
        .status-skipped {{ background: #fff3cd; color: #856404; }}
        .status-error {{ background: #f8d7da; color: #721c24; }}
        .status-empty {{ background: #d1ecf1; color: #0c5460; }}
        .progress-bar {{
            width: 100%;
            height: 25px;
            background-color: #e9ecef;
            border-radius: 12px;
            overflow: hidden;
            margin: 8px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 25px;
            font-size: 0.9em;
        }}
        .mode-info {{
            background: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .mode-info h4 {{
            color: #1976D2;
            margin-bottom: 10px;
        }}
        .mode-info p {{
            color: #333;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 FXCM 数据导入报告</h1>
            <div class="mode-badge">⚡ 快速模式 (Fast Mode)</div>
            <p>生成时间: {timestamp}</p>
        </div>
        
        <div class="mode-info" style="margin: 30px 40px;">
            <h4>📋 导入模式说明</h4>
            <p>本次使用<strong>快速模式</strong>进行导入检查：只验证每个CSV文件的首尾记录是否存在于数据库中。</p>
            <p>• 如果首尾记录都存在，则跳过整个文件（认为数据已完整导入）</p>
            <p>• 如果任一记录缺失，则进行完整导入</p>
            <p>• 此模式可将检查速度提升 <strong>10-20倍</strong>，适合日常批量导入</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card success">
                <div class="stat-number">{total_files}</div>
                <div class="stat-label">📁 处理文件总数</div>
            </div>
            <div class="stat-card info">
                <div class="stat-number">{total_inserted:,}</div>
                <div class="stat-label">✅ 新增记录数</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-number">{total_skipped:,}</div>
                <div class="stat-label">⏭️ 跳过记录数</div>
            </div>
            <div class="stat-card danger">
                <div class="stat-number">{total_errors}</div>
                <div class="stat-label">❌ 错误数量</div>
            </div>
            <div class="stat-card primary">
                <div class="stat-number">{total_time:.1f}s</div>
                <div class="stat-label">⏱️ 总耗时</div>
            </div>
            <div class="stat-card info">
                <div class="stat-number">{(total_inserted/total_time if total_time > 0 else 0):.0f}</div>
                <div class="stat-label">🚄 导入速度 (条/秒)</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 按货币对统计</h2>
            <table>
                <thead>
                    <tr>
                        <th>货币对</th>
                        <th>文件数</th>
                        <th>新增记录</th>
                        <th>跳过记录</th>
                        <th>错误数</th>
                        <th>完成度</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for symbol in sorted(symbol_stats.keys()):
        stats = symbol_stats[symbol]
        success_rate = ((stats['files'] - stats['errors']) / stats['files'] * 100) if stats['files'] > 0 else 0
        
        html_content += f"""
                    <tr>
                        <td><strong>{symbol}</strong></td>
                        <td>{stats['files']}</td>
                        <td>{stats['inserted']:,}</td>
                        <td>{stats['skipped']:,}</td>
                        <td>{stats['errors']}</td>
                        <td>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {success_rate}%">{success_rate:.1f}%</div>
                            </div>
                        </td>
                    </tr>
"""
    
    html_content += f"""
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>📈 D1日线数据详情</h2>
            <div class="stats-grid" style="padding: 0;">
                <div class="stat-card success">
                    <div class="stat-number">{d1_result['total_files']}</div>
                    <div class="stat-label">文件总数</div>
                </div>
                <div class="stat-card info">
                    <div class="stat-number">{d1_result['total_inserted']:,}</div>
                    <div class="stat-label">新增记录</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-number">{d1_result['total_skipped']:,}</div>
                    <div class="stat-label">跳过记录</div>
                </div>
                <div class="stat-card primary">
                    <div class="stat-number">{d1_result['elapsed_time']:.1f}s</div>
                    <div class="stat-label">耗时</div>
                </div>
            </div>
"""
    
    # D1文件详情表格
    if 'file_details' in d1_result and d1_result['file_details']:
        html_content += """
            <table>
                <thead>
                    <tr>
                        <th>货币对</th>
                        <th>文件名</th>
                        <th>状态</th>
                        <th>新增</th>
                        <th>跳过</th>
                    </tr>
                </thead>
                <tbody>
"""
        for detail in d1_result['file_details']:
            status_class = f"status-{detail['status']}"
            status_text = {
                'inserted': '✅ 已导入',
                'skipped': '⏭️ 已跳过',
                'error': '❌ 错误',
                'empty': 'ℹ️ 空文件'
            }.get(detail['status'], detail['status'])
            
            html_content += f"""
                    <tr>
                        <td><strong>{detail['symbol']}</strong></td>
                        <td><code>{detail['file_name']}</code></td>
                        <td><span class="status-badge {status_class}">{status_text}</span></td>
                        <td>{detail['inserted']:,}</td>
                        <td>{detail['skipped']:,}</td>
                    </tr>
"""
        html_content += """
                </tbody>
            </table>
"""
    
    html_content += f"""
        </div>
        
        <div class="section">
            <h2>📊 M1分钟线数据详情</h2>
            <div class="stats-grid" style="padding: 0;">
                <div class="stat-card success">
                    <div class="stat-number">{m1_result['total_files']}</div>
                    <div class="stat-label">文件总数</div>
                </div>
                <div class="stat-card info">
                    <div class="stat-number">{m1_result['total_inserted']:,}</div>
                    <div class="stat-label">新增记录</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-number">{m1_result['total_skipped']:,}</div>
                    <div class="stat-label">跳过记录</div>
                </div>
                <div class="stat-card primary">
                    <div class="stat-number">{m1_result['elapsed_time']:.1f}s</div>
                    <div class="stat-label">耗时</div>
                </div>
            </div>
"""
    
    # M1文件详情表格 (只显示前50条，避免过长)
    if 'file_details' in m1_result and m1_result['file_details']:
        display_limit = 50
        html_content += f"""
            <p style="margin: 20px 0; color: #6c757d;">显示前 {min(display_limit, len(m1_result['file_details']))} 个文件（共 {len(m1_result['file_details'])} 个）</p>
            <table>
                <thead>
                    <tr>
                        <th>货币对</th>
                        <th>文件名</th>
                        <th>状态</th>
                        <th>新增</th>
                        <th>跳过</th>
                    </tr>
                </thead>
                <tbody>
"""
        for detail in m1_result['file_details'][:display_limit]:
            status_class = f"status-{detail['status']}"
            status_text = {
                'inserted': '✅ 已导入',
                'skipped': '⏭️ 已跳过',
                'error': '❌ 错误',
                'empty': 'ℹ️ 空文件'
            }.get(detail['status'], detail['status'])
            
            html_content += f"""
                    <tr>
                        <td><strong>{detail['symbol']}</strong></td>
                        <td><code>{detail['file_name']}</code></td>
                        <td><span class="status-badge {status_class}">{status_text}</span></td>
                        <td>{detail['inserted']:,}</td>
                        <td>{detail['skipped']:,}</td>
                    </tr>
"""
        
        if len(m1_result['file_details']) > display_limit:
            html_content += f"""
                    <tr>
                        <td colspan="5" style="text-align: center; color: #6c757d; padding: 20px;">
                            ... 还有 {len(m1_result['file_details']) - display_limit} 个文件未显示
                        </td>
                    </tr>
"""
        
        html_content += """
                </tbody>
            </table>
"""
    
    html_content += f"""
        </div>
        
        <div class="footer">
            <p>FXCM 数据快速导入工具 v4.1.0 | 生成时间: {timestamp}</p>
            <p>模式: 快速检查（仅验证首尾记录）| 速度提升: 10-20倍</p>
            <p>💡 如需详细验证，请运行: <code>verify_consistency.bat</code></p>
        </div>
    </div>
</body>
</html>
"""
    
    # 保存HTML文件
    timestamp_file = datetime.now().strftime('%Y%m%d_%H%M%S')
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    report_file = logs_dir / f'import_report_{timestamp_file}.html'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file


if __name__ == "__main__":
    # 测试用例
    test_d1 = {
        'total_files': 42,
        'success_count': 40,
        'skip_count': 2,
        'error_count': 0,
        'total_inserted': 12971,
        'total_skipped': 0,
        'elapsed_time': 3.23,
        'file_details': []
    }
    
    test_m1 = {
        'total_files': 3290,
        'success_count': 3200,
        'skip_count': 90,
        'error_count': 0,
        'total_inserted': 26500000,
        'total_skipped': 0,
        'elapsed_time': 178.5,
        'file_details': []
    }
    
    report = generate_html_report(test_d1, test_m1)
    print(f"测试报告已生成: {report}")
