#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple Markdown link checker for the project documentation."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set, Tuple

LINK_PATTERN = r"\[([^\]]+)\]\(([^)]+)\)"
IGNORE_PREFIXES = ("http://", "https://", "mailto:", "#")
EXCLUDE_DIRS = {".git", ".venv", "__pycache__", "node_modules"}


@dataclass
class LinkIssue:
    file: Path
    line: int
    link: str
    resolved_path: Path


def find_markdown_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for path in root.rglob("*.md"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def extract_links(content: str) -> Iterable[Tuple[int, str]]:
    import re

    pattern = re.compile(LINK_PATTERN)
    for line_number, line in enumerate(content.splitlines(), start=1):
        for match in pattern.finditer(line):
            link = match.group(2).strip()
            if not link or link.startswith(IGNORE_PREFIXES):
                continue
            # drop inline anchors for resolution
            link = link.split("#", 1)[0]
            if link:
                yield line_number, link


def resolve_link(source_file: Path, link: str, project_root: Path) -> Path:
    if link.startswith("/"):
        return (project_root / link.lstrip("/")).resolve()
    return (source_file.parent / link).resolve()


def verify_file(path: Path, project_root: Path) -> List[LinkIssue]:
    issues: List[LinkIssue] = []
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - surfaced in CLI output
        print(f"[READ-ERROR] {path.relative_to(project_root)} -> {exc}")
        return issues

    links = list(extract_links(content))
    if not links:
        return issues

    for line_no, link in links:
        resolved = resolve_link(path, link, project_root)
        if not resolved.exists():
            issues.append(LinkIssue(path, line_no, link, resolved))
    return issues


def run(root: Path) -> int:
    project_root = root.resolve()
    markdown_files = find_markdown_files(project_root)
    all_issues: List[LinkIssue] = []

    print(f"Scanning {len(markdown_files)} Markdown files under {project_root}...\n")

    for md_file in markdown_files:
        issues = verify_file(md_file, project_root)
        all_issues.extend(issues)
        if issues:
            print(f"[FAIL] {md_file.relative_to(project_root)} -> {len(issues)} broken link(s)")
        else:
            print(f"[OK]   {md_file.relative_to(project_root)}")

    if not all_issues:
        print("\nAll links resolved successfully.")
        return 0

    print("\nBroken links found:\n-------------------")
    for issue in all_issues:
        rel_file = issue.file.relative_to(project_root)
        rel_target = issue.resolved_path.relative_to(project_root)
        print(f"- {rel_file}:{issue.line} -> {issue.link} (expected {rel_target})")

    return 1


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Markdown links.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root to scan (default: current working directory)",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)
    os.chdir(args.root)
    return run(Path.cwd())


if __name__ == "__main__":
    raise SystemExit(main())
