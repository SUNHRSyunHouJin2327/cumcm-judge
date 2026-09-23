#!/usr/bin/env python3
"""把 PDF 指定页渲染成 PNG，用来真正看图（评可视化时不要只看图题）。

用法:
    python render_pages.py paper.pdf -p 1,5-8          # 输出到 paper_pages/
    python render_pages.py paper.pdf -p all -s 1.5 -d out/
依赖: pip install pypdfium2
"""
import argparse
import sys
from pathlib import Path

try:
    import pypdfium2 as pdfium
except ImportError:
    sys.exit("缺少依赖：pip install pypdfium2")


def parse_pages(spec: str, n: int) -> list[int]:
    if spec == "all":
        return list(range(n))
    pages = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            pages.update(range(int(a), int(b) + 1))
        else:
            pages.add(int(part))
    bad = [p for p in pages if p < 1 or p > n]
    if bad:
        sys.exit(f"页码超出范围（共 {n} 页）：{sorted(bad)}")
    return sorted(p - 1 for p in pages)


def main() -> None:
    ap = argparse.ArgumentParser(description="PDF 页面 → PNG")
    ap.add_argument("pdf")
    ap.add_argument("-p", "--pages", default="1", help="如 1,3-5 或 all（从 1 开始）")
    ap.add_argument("-s", "--scale", type=float, default=1.3, help="缩放倍数，1.0≈72dpi")
    ap.add_argument("-d", "--outdir", help="输出目录（默认 <pdf名>_pages/）")
    args = ap.parse_args()

    src = Path(args.pdf)
    outdir = Path(args.outdir) if args.outdir else src.with_name(src.stem + "_pages")
    outdir.mkdir(parents=True, exist_ok=True)

    doc = pdfium.PdfDocument(str(src))
    for idx in parse_pages(args.pages, len(doc)):
        img = doc[idx].render(scale=args.scale).to_pil()
        path = outdir / f"p{idx + 1:02d}.png"
        img.save(path)
        print(path)


if __name__ == "__main__":
    main()
