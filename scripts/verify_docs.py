#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文档链接验证工具
检查所有Markdown文档中的链接是否有效
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Set

class DocumentVerifier:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.issues = []
        self.checked_files = set()
        self.all_md_files = set()
        
    def find_all_markdown_files(self) -> Set[Path]:
        """查找所有Markdown文件"""
        md_files = set()
        for pattern in ['*.md', '**/*.md']:
            md_files.update(self.root_dir.glob(pattern))
        return md_files
    
    def extract_links(self, content: str, file_path: Path) -> List[Tuple[str, int]]:
        """提取Markdown文件中的所有本地链接"""
        links = []
        
        # 匹配 [text](link) 格式
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        for line_no, line in enumerate(content.split('\n'), 1):
            matches = re.finditer(pattern, line)
            for match in matches:
                link = match.group(2)
                # 只检查本地文件链接，跳过HTTP/HTTPS链接和锚点
                if not link.startswith(('http://', 'https://', '#', 'mailto:')):
                    # 移除锚点部分
                    link = link.split('#')[0]
                    if link:  # 如果不是纯锚点链接
                        links.append((link, line_no))
        
        return links
    
    def resolve_link(self, link: str, source_file: Path) -> Path:
        """解析相对路径链接到绝对路径"""
        if link.startswith('/'):
            # 绝对路径（相对于项目根目录）
            return self.root_dir / link.lstrip('/')
        else:
            # 相对路径（相对于当前文件）
            return (source_file.parent / link).resolve()
    
    def verify_file(self, file_path: Path):
        """验证单个Markdown文件"""
        print(f"\n📄 检查: {file_path.relative_to(self.root_dir)}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.issues.append({
                'file': file_path,
                'type': 'READ_ERROR',
                'message': f"无法读取文件: {e}"
            })
            print(f"  ❌ 读取错误: {e}")
            return
        
        links = self.extract_links(content, file_path)
        
        if not links:
            print(f"  ℹ️  没有本地文件链接")
            return
        
        print(f"  🔗 找到 {len(links)} 个链接")
        
        for link, line_no in links:
            target_path = self.resolve_link(link, file_path)
            
            if not target_path.exists():
                self.issues.append({
                    'file': file_path,
                    'line': line_no,
                    'link': link,
                    'target': target_path,
                    'type': 'BROKEN_LINK',
                    'message': f"链接指向的文件不存在: {link}"
                })
                print(f"  ❌ 行 {line_no}: {link} → 文件不存在")
            else:
                print(f"  ✅ 行 {line_no}: {link}")
    
    def verify_all(self):
        """验证所有Markdown文件"""
        print("="*80)
        print("📚 FXCM 文档链接验证工具")
        print("="*80)
        
        # 查找所有Markdown文件
        self.all_md_files = self.find_all_markdown_files()
        
        # 排除某些目录
        exclude_dirs = {'.git', '.venv', '__pycache__', 'node_modules'}
        self.all_md_files = {
            f for f in self.all_md_files 
            if not any(excluded in f.parts for excluded in exclude_dirs)
        }
        
        print(f"\n📊 找到 {len(self.all_md_files)} 个Markdown文件")
        
        # 验证每个文件
        for md_file in sorted(self.all_md_files):
            self.verify_file(md_file)
            self.checked_files.add(md_file)
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成验证报告"""
        print("\n" + "="*80)
        print("📊 验证报告")
        print("="*80)
        
        print(f"\n✅ 已检查文件: {len(self.checked_files)}")
        
        if not self.issues:
            print("\n🎉 所有链接都是有效的！")
        else:
            print(f"\n⚠️  发现 {len(self.issues)} 个问题：")
            print("-"*80)
            
            # 按文件分组显示问题
            issues_by_file = {}
            for issue in self.issues:
                file_key = issue['file']
                if file_key not in issues_by_file:
                    issues_by_file[file_key] = []
                issues_by_file[file_key].append(issue)
            
            for file_path, issues in sorted(issues_by_file.items()):
                print(f"\n📄 {file_path.relative_to(self.root_dir)}")
                for issue in issues:
                    if issue['type'] == 'BROKEN_LINK':
                        print(f"  ❌ 行 {issue['line']}: {issue['link']}")
                        print(f"     目标文件不存在: {issue['target'].relative_to(self.root_dir)}")
                    elif issue['type'] == 'READ_ERROR':
                        print(f"  ❌ {issue['message']}")
        
        print("\n" + "="*80)
        print("验证完成！")
        print("="*80 + "\n")
        
        return len(self.issues) == 0

def main():
    """主函数"""
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    verifier = DocumentVerifier()
    success = verifier.verify_all()
    
    # 返回退出码
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
