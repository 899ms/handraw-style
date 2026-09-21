#!/usr/bin/env python3
"""Generate STYLES.md and LAYOUTS.md for GitHub-native visual browsing."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "handdraw-style-prompter"
SOURCE_MD = ROOT / "styles_200_reorganized.md"
LAYOUTS_JSON = SKILL / "references" / "layouts.json"

SHEET_GROUPS = [
    ("A", "国际社论漫画 / 幽默手绘（001–035）", ["A_001-016.webp", "A_017-032.webp", "A_033-035.webp"]),
    ("B", "国际绘本 / 叙事型手绘（036–054）", ["B_036-048.webp", "B_049-054.webp"]),
    ("C", "现代平面 / 艺术化人物体系（055–082）", ["C_055-070.webp", "C_071-082.webp"]),
    ("D", "日本作者 / 当代插画体系（083–123）", ["D_083-098.webp", "D_099-114.webp", "D_115-123.webp"]),
    ("E", "中国作者 / 当代插画体系（124–154）", ["E_124-139.webp", "E_140-154.webp"]),
    ("F", "通用网感 / 媒介 / 地域手绘（155–200）", ["F_155-170.webp", "F_171-186.webp", "F_187-200.webp"]),
    ("G", "附件新增 / 中国当代插画补充（201–216）", ["G_201-216.webp"]),
    ("H", "其他（217–274）", ["H_217-232.webp", "H_233-248.webp", "H_249-264.webp", "H_265-274.webp"]),
]

LAYOUT_CATEGORIES = [
    ("social-card", "1. 社媒卡（Social Cards · 19 种）", "适合小红书、朋友圈、公众号配图及观点金句卡片。结构包含上下图文、文案主导、双格对照等。"),
    ("infographic", "2. 信息图（Infographics · 30 种）", "适合知识科普、对比清单、流程步骤及数据架构展示。结构包含金字塔层级、中心主图标注、多行多列对比等。"),
    ("comic-storyboard", "3. 漫画分镜（Comic Storyboards · 68 种）", "适合多格叙事、剧情转折、条漫分镜及动态视觉表现。结构包含规则四格、起承转合、大格冲击、对角切割等专业分镜。"),
]


def build_styles_md() -> None:
    lines = [
        "# 手绘风格完整图鉴（001–274）",
        "",
        "> 这里汇总了本库收录的 **001–274 种手绘风格**的全部拼图大表。每张拼图包含对应风格编号与画面参考，供在 GitHub 上直接图文浏览选款。",
        "> 详细的英文生图名称与提示词特征对照表见 [styles_200_reorganized.md](styles_200_reorganized.md)。",
        "",
        "## 目录导航",
        "",
    ]
    for letter, title, _ in SHEET_GROUPS:
        lines.append(f"- [{letter} · {title}](#group-{letter.lower()})")

    lines.extend(["", "---", ""])

    for letter, title, sheets in SHEET_GROUPS:
        lines.append(f'<a id="group-{letter.lower()}"></a>')
        lines.append(f"## {letter} · {title}")
        lines.append("")
        for sheet in sheets:
            label = sheet.replace(".webp", "").replace("_", " ")
            lines.append(f"![{label}](images/{sheet})")
            lines.append("")
        lines.append("---")
        lines.append("")

    (ROOT / "STYLES.md").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print("Built STYLES.md")


def build_layouts_md() -> None:
    layouts = json.loads(LAYOUTS_JSON.read_text(encoding="utf-8"))
    lines = [
        "# 排版图型完整图鉴（117 种）",
        "",
        "> 这里收录了本库全部 **117 种排版图型**的图片预览与排版提示词说明。在 AI 生图时直接指定图型编号（如 `SC-001`、`IG-003`、`SB-002`），即可精确控制画面的构图版式与排版层次。",
        "",
        "## 目录导航",
        "",
        "- [1. 社媒卡（Social Cards · 19 种）](#social-cards)",
        "- [2. 信息图（Infographics · 30 种）](#infographics)",
        "- [3. 漫画分镜（Comic Storyboards · 68 种）](#comic-storyboards)",
        "",
        "---",
        "",
    ]

    anchor_map = {
        "social-card": "social-cards",
        "infographic": "infographics",
        "comic-storyboard": "comic-storyboards",
    }

    for cat_id, cat_title, cat_desc in LAYOUT_CATEGORIES:
        cat_layouts = [l for l in layouts if l["category"] == cat_id]
        anchor = anchor_map.get(cat_id, cat_id)
        lines.append(f'<a id="{anchor}"></a>')
        lines.append(f"## {cat_title}")
        lines.append("")
        lines.append(cat_desc)
        lines.append("")
        lines.append("| 编号与名称 | 图型效果预览 | 排版提示词说明 |")
        lines.append("| :--- | :---: | :--- |")
        for l in cat_layouts:
            rel_img = str(l["image"]).replace("../../../", "")
            prompt_file = SKILL / "references" / l["prompt_file"]
            prompt_zh = ""
            if prompt_file.exists():
                content = prompt_file.read_text(encoding="utf-8")
                zh_part = content.split("<!-- en -->")[0].replace("<!-- zh -->", "").strip()
                prompt_zh = zh_part.replace("\n", "<br>")
            name = l["name"]
            lines.append(f"| **{l['id']}**<br>{name} | <img src='{rel_img}' width='200' alt='{l['id']} {name}'> | {prompt_zh} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    (ROOT / "LAYOUTS.md").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print("Built LAYOUTS.md")


def main() -> None:
    build_styles_md()
    build_layouts_md()


if __name__ == "__main__":
    main()
