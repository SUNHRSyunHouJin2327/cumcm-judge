#!/usr/bin/env python3
"""把论文 PDF 抽成带页码标记的纯文本（对中文友好）。

用法:
    python extract_text.py paper.pdf            # 输出 paper.txt
    python extract_text.py paper.pdf -o out.txt
依赖: pip install pdfplumber
"""
import argparse
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    sys.exit("缺少依赖：pip install pdfplumber")


def main() -> None:
    ap = argparse.ArgumentParser(description="PDF → 带页码标记的纯文本")
    ap.add_argument("pdf", help="论文 PDF 路径")
    ap.add_argument("-o", "--out", help="输出 txt 路径（默认与 PDF 同名）")
    args = ap.parse_args()

    src = Path(args.pdf)
    dst = Path(args.out) if args.out else src.with_suffix(".txt")

    parts = []
    with pdfplumber.open(src) as pdf:
        n = len(pdf.pages)
        for i, page in enumerate(pdf.pages, 1):
            parts.append(f"===== P{i} =====")
            parts.append(page.extract_text() or "")
    text = "\n".join(parts)
    dst.write_text(text, encoding="utf-8")

    empty = sum(1 for i in range(1, len(parts), 2) if not parts[i].strip())
    print(f"{dst}: {n} 页, {len(text)} 字符" + (f", {empty} 页无文字（可能是扫描件）" if empty else ""))


if __name__ == "__main__":
    main()
