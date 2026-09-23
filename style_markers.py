#!/usr/bin/env python3
"""文风信号统计：开发日志词、过度限定、高频术语，按每万字归一，便于多篇对比。

用法:
    python style_markers.py a.txt b.txt --stop-at 参考文献
    python style_markers.py a.txt --json

注意：这不是 AI 检测器，结果只是"读起来像不像"的证据，不能据此认定使用了 AI。
竞赛规则看的是 AI 使用声明是否如实，而不是某个"AI 率"数字。
可以用 --extra 追加自己的词表（每行一个正则）。
"""
import argparse
import json
import re
import sys
from pathlib import Path

GROUPS = {
    "开发日志词": [r"终版", r"第?[A-Z]轮", r"晋升", r"修订阶段", r"v\d+_?final", r"最终版本", r"旧版"],
    "限定/免责": [r"不能", r"不保证", r"不等同", r"不据此", r"不代表", r"并非", r"不宣称", r"仅用于", r"不应解读"],
    "高频术语": [r"口径", r"账本", r"因果", r"闭环", r"赋能", r"抓手"],
}


def load(path: str, stop_at: str | None) -> str:
    text = Path(path).read_text(encoding="utf-8")
    text = re.sub(r"===== P\d+ =====", "", text)
    if stop_at:
        idx = [m.start() for m in re.finditer(stop_at, text)]
        # 取最后一次出现之前的部分（避免目录里的同名标题截断正文）
        if idx:
            text = text[: idx[-1]]
    return text


def count(text: str, extra: list[str]) -> dict:
    chars = len(re.sub(r"\s", "", text))
    groups = dict(GROUPS)
    if extra:
        groups = {**groups, "自定义": extra}
    res = {"字符数": chars, "分组": {}}
    for g, pats in groups.items():
        items = {p: len(re.findall(p, text)) for p in pats}
        total = sum(items.values())
        res["分组"][g] = {
            "合计": total,
            "每万字": round(total / chars * 1e4, 2) if chars else 0.0,
            "明细": {k: v for k, v in items.items() if v},
        }
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description="文风信号统计（非 AI 检测）")
    ap.add_argument("txt", nargs="+")
    ap.add_argument("--stop-at", help="只统计该正则最后一次出现之前的正文，如 参考文献 或 附录")
    ap.add_argument("--extra", help="自定义词表文件，每行一个正则")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    extra = []
    if args.extra:
        extra = [l.strip() for l in Path(args.extra).read_text(encoding="utf-8").splitlines() if l.strip()]

    results = {p: count(load(p, args.stop_at), extra) for p in args.txt}
    if args.json:
        json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return

    names = list(results)
    groups = list(next(iter(results.values()))["分组"])
    print("每万字出现次数（括号内为总次数）")
    print("分组".ljust(10) + "".join(Path(n).name[:18].ljust(22) for n in names))
    for g in groups:
        row = g.ljust(10)
        for n in names:
            d = results[n]["分组"][g]
            row += f"{d['每万字']} ({d['合计']})".ljust(22)
        print(row)
    print("字符数".ljust(10) + "".join(str(results[n]["字符数"]).ljust(22) for n in names))
    for n in names:
        print(f"\n{n} 明细：")
        for g in groups:
            if results[n]["分组"][g]["明细"]:
                print(f"  {g}: {results[n]['分组'][g]['明细']}")
    print("\n提示：这是文风证据，不是 AI 检测结论。")


if __name__ == "__main__":
    main()
