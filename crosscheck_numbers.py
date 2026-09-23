#!/usr/bin/env python3
"""摘要数字交叉核查：摘要里的每个数字是否在正文出现过、是否精度虚高。

用法:
    python crosscheck_numbers.py paper.txt
    python crosscheck_numbers.py paper.txt --min-len 4 --decimals 3

输入是 extract_text.py 生成的 txt。摘要取"摘要"到"关键词"之间的文字。
只做机械比对：正文没出现不一定是错（可能写法不同，如 1234.5万 vs 12345000），
但每一条都值得人工看一眼。
"""
import argparse
import re
import sys
from pathlib import Path

NUM = re.compile(r"(?<![0-9A-Za-z.])[-−]?\d[\d,，]*(?:\.\d+)?%?")


def norm(s: str) -> str:
    return s.replace(",", "").replace("，", "").replace("−", "-").rstrip("%")


def split_abstract(text: str) -> tuple[str, str]:
    m = re.search(r"摘\s*要", text)
    if not m:
        sys.exit("没找到“摘要”二字，请确认输入文本")
    k = re.search(r"关\s*键\s*词|Keywords", text[m.end():])
    end = m.end() + (k.start() if k else 3000)
    return text[m.end():end], text[end:]


def main() -> None:
    ap = argparse.ArgumentParser(description="摘要数字 ↔ 正文 交叉核查")
    ap.add_argument("txt")
    ap.add_argument("--min-len", type=int, default=3, help="忽略位数少于此值的数字（默认 3）")
    ap.add_argument("--decimals", type=int, default=4, help="小数位 ≥ 此值视为精度虚高（默认 4）")
    args = ap.parse_args()

    text = Path(args.txt).read_text(encoding="utf-8")
    text = re.sub(r"===== P\d+ =====", "", text)
    abstract, body = split_abstract(text)
    body_norm = norm(re.sub(r"\s+", "", body))

    seen, missing, precise = set(), [], []
    for raw in NUM.findall(abstract):
        n = norm(raw)
        digits = re.sub(r"\D", "", n)
        if len(digits) < args.min_len or n in seen:
            continue
        seen.add(n)
        if n not in body_norm:
            missing.append(raw)
        dec = re.search(r"\.(\d+)", n)
        if dec and len(dec.group(1)) >= args.decimals:
            precise.append(raw)

    print(f"摘要中检查了 {len(seen)} 个数字（位数 ≥ {args.min_len}）")
    print(f"\n[正文未出现] {len(missing)} 个 —— 逐个人工核对来源：")
    for x in missing:
        print("  ", x)
    print(f"\n[精度虚高] {len(precise)} 个（≥ {args.decimals} 位小数）—— 摘要里一般保留到有意义的位数：")
    for x in precise:
        print("  ", x)


if __name__ == "__main__":
    main()
