# cumcm-judge

一个让 Claude 以**评委视角**评审数学建模竞赛论文（国赛 CUMCM 为主，也适用于美赛 MCM/ICM）的技能包：按评阅要点和评分细则逐项打分、交叉核查数字一致性、单独评摘要 / 图表 / AI 使用，最后给出带概率的获奖档位预测。

它的出发点是：模型给论文打分**容易偏松**——会给写了但没执行的方法、结论对但支撑链断了的论文打高分。所以这套标准默认从严，并在最后强制做一次"如果我偏松 10 分，结论还成立吗"的检查。

## 包含什么

```
cumcm-judge/
├── SKILL.md                    # 评审标准本体（Claude 技能）
├── scripts/
│   ├── extract_text.py         # PDF → 带页码的纯文本（中文友好）
│   ├── render_pages.py         # PDF 页 → PNG，评图时真正看图
│   ├── crosscheck_numbers.py   # 摘要数字 ↔ 正文 交叉核查、精度虚高
│   └── style_markers.py        # 文风信号统计（开发日志词、过度限定等），非 AI 检测
├── templates/
│   └── score-sheet.md          # 评分表模板
└── references/
    └── ai-rules.md             # 国赛 AI 使用规定摘要与出处
```

## 安装

**Claude Code**：克隆到技能目录即可。

```bash
git clone https://github.com/<你的用户名>/cumcm-judge.git ~/.claude/skills/cumcm-judge
pip install -r ~/.claude/skills/cumcm-judge/requirements.txt
```

**Claude 应用**：把本仓库打包成 zip，作为自定义技能上传。

之后直接说"帮我给这篇论文打分 / 评奖"，并附上论文 PDF（有当年评阅要点或评分细则的话一起给），就会按这套标准执行。

## 脚本单独使用

```bash
pip install -r requirements.txt

python scripts/extract_text.py paper.pdf                  # 生成 paper.txt
python scripts/render_pages.py paper.pdf -p 1,5-8         # 生成 paper_pages/p01.png …
python scripts/crosscheck_numbers.py paper.txt            # 摘要里哪些数字在正文找不到
python scripts/style_markers.py a.txt b.txt --stop-at 参考文献   # 多篇论文文风对比
```

## 评审标准要点

1. **分清评阅要点和评分细则**：前者用来打勾，后者用来算分；先查封顶条款
2. **逐问从严**：没执行不给分；支撑断了最多 60%；一问无结果拖累全篇；题目问"是否"必须有明确回答
3. **一致性交叉核查**：摘要 ↔ 正文 ↔ 表格 ↔ 结果文件，这是收益最高的一步
4. **摘要按"两分钟可读性"评**：每问 = 标准方法 → 核心数字 → 和什么比 → 回答题目问的话
5. **真的看图**：每问要有一张核心结果图，图题短、能自解释
6. **AI**：不按检测"AI 率"扣分；查声明是否如实；文风问题要给计数证据
7. **映射奖项**：给每个档位的概率，并做偏松 10 分检查

详见 [SKILL.md](SKILL.md)。

## 局限与声明

- 本项目与全国大学生数学建模竞赛组委会及任何赛区**无关**，不是官方评分标准
- 分数与档位是估计，校准样本很少，**不构成任何获奖预期的承诺**；省一线附近的判断尤其不确定
- 请只评审你有权使用的论文。官方优秀论文受组委会版权保护，请勿把原文提交到本仓库
- `style_markers.py` 统计的是文风信号，**不能**据此认定某篇论文使用了 AI

## License

[MIT](LICENSE)
