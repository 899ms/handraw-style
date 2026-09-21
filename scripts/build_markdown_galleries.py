#!/usr/bin/env python3
"""Generate bilingual STYLES.md and LAYOUTS.md for GitHub-native visual browsing."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "handdraw-style-prompter"
SOURCE_MD = ROOT / "styles_200_reorganized.md"
LAYOUTS_JSON = SKILL / "references" / "layouts.json"

SHEET_GROUPS = [
    ("A", "国际社论漫画与幽默手绘（001–035）", "Editorial & Humorous (001–035)", ["A_001-016.webp", "A_017-032.webp", "A_033-035.webp"]),
    ("B", "国际绘本与叙事型手绘（036–054）", "Picture Book & Narrative (036–054)", ["B_036-048.webp", "B_049-054.webp"]),
    ("C", "现代平面与艺术化人物体系（055–082）", "Graphic & Stylized Figure (055–082)", ["C_055-070.webp", "C_071-082.webp"]),
    ("D", "日本作者与当代插画体系（083–123）", "Japanese Contemporary Illustration (083–123)", ["D_083-098.webp", "D_099-114.webp", "D_115-123.webp"]),
    ("E", "中国作者与当代插画体系（124–154）", "Chinese Contemporary Illustration (124–154)", ["E_124-139.webp", "E_140-154.webp"]),
    ("F", "通用网感、媒介与地域手绘（155–200）", "Internet Culture, Medium & Regional (155–200)", ["F_155-170.webp", "F_171-186.webp", "F_187-200.webp"]),
    ("G", "中国当代插画补充（201–216）", "Contemporary Chinese Illustration Supplement (201–216)", ["G_201-216.webp"]),
    ("H", "其他精选风格（217–274）", "Other Curated Styles (217–274)", ["H_217-232.webp", "H_233-248.webp", "H_249-264.webp", "H_265-274.webp"]),
]

LAYOUT_CATEGORIES = [
    ("social-card", "1. 社媒卡（19 种）", "1. Social Cards (19 Layouts)",
     "适合小红书、朋友圈、公众号配图及观点金句卡片。结构包含上下图文、文案主导、双格对照等。",
     "Ideal for Xiaohongshu, Instagram, newsletter hero images, and quote cards. Includes top-bottom split, text-driven cards, two-column contrasts, and sticky notes."),
    ("infographic", "2. 信息图（31 种）", "2. Infographics (31 Layouts)",
     "适合知识科普、对比清单、流程步骤及数据架构展示。结构包含金字塔层级、中心主图标注、多行多列对比等。",
     "Ideal for knowledge sharing, comparison charts, process workflows, and structured data visuals. Includes hierarchy pyramids, central icons, matrices, and multi-column comparison tables."),
    ("comic-storyboard", "3. 漫画分镜（68 种）", "3. Comic Storyboards (68 Layouts)",
     "适合多格叙事、剧情转折、条漫分镜及动态视觉表现。结构包含规则四格、起承转合、大格冲击、对角切割等专业分镜。",
     "Ideal for multi-panel narratives, webtoons, emotional storylines, and cinematic pacing. Includes standard 4-panel grids, dramatic wide-angle focus, diagonal cuts, and manga storyboards."),
]


def build_styles_md() -> None:
    # 1. Chinese STYLES.md
    zh_lines = [
        '<p align="right">',
        '  <strong>中文</strong> | <a href="STYLES_en.md">English</a>',
        '</p>',
        '',
        "# 手绘风格完整图鉴（001–274）",
        "",
        "> 这里汇总了本库收录的 **001–274 种手绘风格**的全部拼图大表。每张拼图包含对应风格编号与画面参考，供在 GitHub 上直接图文浏览选款。详细的英文生图名称与提示词特征对照表见 [styles_200_reorganized.md](styles_200_reorganized.md)。",
        "",
        "## 目录导航",
        "",
    ]
    for letter, title_zh, _, _ in SHEET_GROUPS:
        zh_lines.append(f"- [{letter} · {title_zh}](#group-{letter.lower()})")
    zh_lines.extend(["", "---", ""])

    for letter, title_zh, _, sheets in SHEET_GROUPS:
        zh_lines.append(f'<a id="group-{letter.lower()}"></a>')
        zh_lines.append(f"## {letter} · {title_zh}")
        zh_lines.append("")
        for sheet in sheets:
            label = sheet.replace(".webp", "").replace("_", " ")
            zh_lines.append(f"![{label}](images/{sheet})")
            zh_lines.append("")
        zh_lines.append("---")
        zh_lines.append("")

    (ROOT / "STYLES.md").write_text("\n".join(zh_lines).strip() + "\n", encoding="utf-8")
    print("Built STYLES.md")

    # 2. English STYLES_en.md
    en_lines = [
        '<p align="right">',
        '  <a href="STYLES.md">中文</a> | <strong>English</strong>',
        '</p>',
        '',
        "# Hand-drawn Style Visual Sheet (001–274)",
        "",
        "> Visual contact sheets for all **274 hand-drawn illustration styles** (001–274). Each sheet displays style numbers and visual references for easy browsing and selection directly on GitHub. For detailed generation names and prompt traits, see [styles_200_reorganized.md](styles_200_reorganized.md).",
        "",
        "## Table of Contents",
        "",
    ]
    for letter, _, title_en, _ in SHEET_GROUPS:
        en_lines.append(f"- [{letter} · {title_en}](#group-{letter.lower()})")
    en_lines.extend(["", "---", ""])

    for letter, _, title_en, sheets in SHEET_GROUPS:
        en_lines.append(f'<a id="group-{letter.lower()}"></a>')
        en_lines.append(f"## {letter} · {title_en}")
        en_lines.append("")
        for sheet in sheets:
            label = sheet.replace(".webp", "").replace("_", " ")
            en_lines.append(f"![{label}](images/{sheet})")
            en_lines.append("")
        en_lines.append("---")
        en_lines.append("")

    (ROOT / "STYLES_en.md").write_text("\n".join(en_lines).strip() + "\n", encoding="utf-8")
    print("Built STYLES_en.md")


def build_layouts_md() -> None:
    layouts = json.loads(LAYOUTS_JSON.read_text(encoding="utf-8"))
    anchor_map = {
        "social-card": "social-cards",
        "infographic": "infographics",
        "comic-storyboard": "comic-storyboards",
    }
    cols = 3

    # 1. Chinese LAYOUTS.md
    zh_lines = [
        '<p align="right">',
        '  <strong>中文</strong> | <a href="LAYOUTS_en.md">English</a>',
        '</p>',
        '',
        f"# 排版图型完整图鉴（{len(layouts)} 种）",
        "",
        f"> 这里收录了本库全部 **{len(layouts)} 种排版图型**（社媒卡、信息图、漫画分镜）的图片预览与排版提示词。在 AI 生图时直接指定图型编号（如 `SC-001`、`IG-003`、`SB-002`），即可精确控制画面的构图版式与排版层次。",
        "",
        "## 目录导航",
        "",
        "- [1. 社媒卡（19 种）](#social-cards)",
        "- [2. 信息图（31 种）](#infographics)",
        "- [3. 漫画分镜（68 种）](#comic-storyboards)",
        "",
        "---",
        "",
    ]

    for cat_id, cat_title_zh, _, cat_desc_zh, _ in LAYOUT_CATEGORIES:
        cat_layouts = [l for l in layouts if l["category"] == cat_id]
        anchor = anchor_map.get(cat_id, cat_id)
        zh_lines.append(f'<a id="{anchor}"></a>')
        zh_lines.append(f"## {cat_title_zh}")
        zh_lines.append("")
        zh_lines.append(cat_desc_zh)
        zh_lines.append("")
        zh_lines.append("| 效果预览 | 效果预览 | 效果预览 |")
        zh_lines.append("| :---: | :---: | :---: |")
        for i in range(0, len(cat_layouts), cols):
            chunk = cat_layouts[i:i + cols]
            row_cells = []
            for l in chunk:
                rel_img = str(l["image"]).replace("../../../", "")
                prompt_file = SKILL / "references" / l["prompt_file"]
                prompt_zh = ""
                if prompt_file.exists():
                    content = prompt_file.read_text(encoding="utf-8")
                    if "<!-- zh -->" in content:
                        zh_part = content.split("<!-- en -->")[0].replace("<!-- zh -->", "").strip()
                    else:
                        zh_part = content.strip()
                    prompt_zh = zh_part.replace("|", "&#124;").replace("\n", "<br>")
                name = l["name"]
                cell = f"<img src='{rel_img}' width='260' alt='{l['id']} {name}'><br>**{l['id']}** · {name}"
                if prompt_zh:
                    cell += f"<br><details><summary>查看排版提示词</summary><br>{prompt_zh}</details>"
                row_cells.append(cell)
            while len(row_cells) < cols:
                row_cells.append("")
            zh_lines.append(f"| {' | '.join(row_cells)} |")
        zh_lines.append("")
        zh_lines.append("---")
        zh_lines.append("")

    (ROOT / "LAYOUTS.md").write_text("\n".join(zh_lines).strip() + "\n", encoding="utf-8")
    print("Built LAYOUTS.md")

    # 2. English LAYOUTS_en.md
    en_lines = [
        '<p align="right">',
        '  <a href="LAYOUTS.md">中文</a> | <strong>English</strong>',
        '</p>',
        '',
        f"# Layout Composition Visual Sheet ({len(layouts)} Layouts)",
        "",
        f"> Visual previews and layout prompts for all **{len(layouts)} layout compositions** (Social Cards, Infographics, Comic Storyboards). Specify layout IDs (e.g. `SC-001`, `IG-003`, `SB-002`) during AI image generation to control compositions, text placements, and visual hierarchy.",
        "",
        "## Table of Contents",
        "",
        "- [1. Social Cards (19 Layouts)](#social-cards)",
        "- [2. Infographics (31 Layouts)](#infographics)",
        "- [3. Comic Storyboards (68 Layouts)](#comic-storyboards)",
        "",
        "---",
        "",
    ]

    for cat_id, _, cat_title_en, _, cat_desc_en in LAYOUT_CATEGORIES:
        cat_layouts = [l for l in layouts if l["category"] == cat_id]
        anchor = anchor_map.get(cat_id, cat_id)
        en_lines.append(f'<a id="{anchor}"></a>')
        en_lines.append(f"## {cat_title_en}")
        en_lines.append("")
        en_lines.append(cat_desc_en)
        en_lines.append("")
        en_lines.append("| Preview | Preview | Preview |")
        en_lines.append("| :---: | :---: | :---: |")
        for i in range(0, len(cat_layouts), cols):
            chunk = cat_layouts[i:i + cols]
            row_cells = []
            for l in chunk:
                rel_img = str(l["image"]).replace("../../../", "")
                prompt_file = SKILL / "references" / l["prompt_file"]
                prompt_en = ""
                if prompt_file.exists():
                    content = prompt_file.read_text(encoding="utf-8")
                    if "<!-- en -->" in content:
                        en_part = content.split("<!-- en -->")[1].strip()
                    else:
                        en_part = ""
                    prompt_en = en_part.replace("|", "&#124;").replace("\n", "<br>")
                cell = f"<img src='{rel_img}' width='260' alt='{l['id']}'><br>**{l['id']}**"
                if prompt_en:
                    cell += f"<br><details><summary>View Layout Prompt</summary><br>{prompt_en}</details>"
                row_cells.append(cell)
            while len(row_cells) < cols:
                row_cells.append("")
            en_lines.append(f"| {' | '.join(row_cells)} |")
        en_lines.append("")
        en_lines.append("---")
        en_lines.append("")

    (ROOT / "LAYOUTS_en.md").write_text("\n".join(en_lines).strip() + "\n", encoding="utf-8")
    print("Built LAYOUTS_en.md")


def main() -> None:
    build_styles_md()
    build_layouts_md()


if __name__ == "__main__":
    main()
