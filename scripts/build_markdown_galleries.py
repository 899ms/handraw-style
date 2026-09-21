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
    ("A", "Editorial & Humorous / 国际社论漫画与幽默手绘（001–035）", ["A_001-016.webp", "A_017-032.webp", "A_033-035.webp"]),
    ("B", "Picture Book & Narrative / 国际绘本与叙事型手绘（036–054）", ["B_036-048.webp", "B_049-054.webp"]),
    ("C", "Graphic & Stylized Figure / 现代平面与艺术化人物体系（055–082）", ["C_055-070.webp", "C_071-082.webp"]),
    ("D", "Japanese Authors / 日本作者与当代插画体系（083–123）", ["D_083-098.webp", "D_099-114.webp", "D_115-123.webp"]),
    ("E", "Chinese Authors / 中国作者与当代插画体系（124–154）", ["E_124-139.webp", "E_140-154.webp"]),
    ("F", "Internet Culture, Medium & Regional / 通用网感、媒介与地域手绘（155–200）", ["F_155-170.webp", "F_171-186.webp", "F_187-200.webp"]),
    ("G", "Contemporary Chinese Illustration Supplement / 中国当代插画补充（201–216）", ["G_201-216.webp"]),
    ("H", "Other Curated Styles / 其他精选风格（217–274）", ["H_217-232.webp", "H_233-248.webp", "H_249-264.webp", "H_265-274.webp"]),
]

LAYOUT_CATEGORIES = [
    ("social-card", "1. Social Cards · 社媒卡（19 种）", "Ideal for social media covers, posters, and quote cards. / 适合小红书、朋友圈、公众号配图及观点金句卡片。结构包含上下图文、文案主导、双格对照等。"),
    ("infographic", "2. Infographics · 信息图（31 种）", "Ideal for knowledge sharing, comparison charts, and process workflows. / 适合知识科普、对比清单、流程步骤及数据架构展示。结构包含金字塔层级、中心主图标注、多行多列对比等。"),
    ("comic-storyboard", "3. Comic Storyboards · 漫画分镜（68 种）", "Ideal for multi-panel narratives, story arcs, and dynamic sequences. / 适合多格叙事、剧情转折、条漫分镜及动态视觉表现。结构包含规则四格、起承转合、大格冲击、对角切割等专业分镜。"),
]


def build_styles_md() -> None:
    lines = [
        "# Hand-drawn Style Complete Visual Sheet / 手绘风格完整图鉴（001–274）",
        "",
        "> **English**: Visual contact sheets for all **274 hand-drawn illustration styles** (001–274). Each sheet displays style numbers and visual references for easy browsing and selection directly on GitHub. For detailed English generation names and prompt traits, see [styles_200_reorganized.md](styles_200_reorganized.md).",
        ">",
        "> **中文**：这里汇总了本库收录的 **001–274 种手绘风格**的全部拼图大表。每张拼图包含对应风格编号与画面参考，供在 GitHub 上直接图文浏览选款。详细的英文生图名称与提示词特征对照表见 [styles_200_reorganized.md](styles_200_reorganized.md)。",
        "",
        "## Table of Contents / 目录导航",
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
        f"# Layout Composition Complete Sheet / 排版图型完整图鉴（{len(layouts)} 种）",
        "",
        f"> **English**: Visual previews and bilingual prompt templates for all **{len(layouts)} layout compositions**. Specify layout IDs (e.g. `SC-001`, `IG-003`, `SB-002`) during AI image generation to control compositions, text placements, and visual hierarchy.",
        ">",
        f"> **中文**：这里收录了本库全部 **{len(layouts)} 种排版图型**的图片预览与中英排版提示词。在 AI 生图时直接指定图型编号（如 `SC-001`、`IG-003`、`SB-002`），即可精确控制画面的构图版式与排版层次。",
        "",
        "## Table of Contents / 目录导航",
        "",
        "- [1. Social Cards · 社媒卡（19 种）](#social-cards)",
        "- [2. Infographics · 信息图（31 种）](#infographics)",
        "- [3. Comic Storyboards · 漫画分镜（68 种）](#comic-storyboards)",
        "",
        "---",
        "",
    ]

    anchor_map = {
        "social-card": "social-cards",
        "infographic": "infographics",
        "comic-storyboard": "comic-storyboards",
    }

    cols = 3
    for cat_id, cat_title, cat_desc in LAYOUT_CATEGORIES:
        cat_layouts = [l for l in layouts if l["category"] == cat_id]
        anchor = anchor_map.get(cat_id, cat_id)
        lines.append(f'<a id="{anchor}"></a>')
        lines.append(f"## {cat_title}")
        lines.append("")
        lines.append(cat_desc)
        lines.append("")
        lines.append("| Preview / 效果预览 | Preview / 效果预览 | Preview / 效果预览 |")
        lines.append("| :---: | :---: | :---: |")
        for i in range(0, len(cat_layouts), cols):
            chunk = cat_layouts[i:i + cols]
            row_cells = []
            for l in chunk:
                rel_img = str(l["image"]).replace("../../../", "")
                prompt_file = SKILL / "references" / l["prompt_file"]
                prompt_zh = ""
                prompt_en = ""
                if prompt_file.exists():
                    content = prompt_file.read_text(encoding="utf-8")
                    if "<!-- en -->" in content:
                        parts = content.split("<!-- en -->")
                        zh_part = parts[0].replace("<!-- zh -->", "").strip()
                        en_part = parts[1].strip()
                    else:
                        zh_part = content.replace("<!-- zh -->", "").strip()
                        en_part = ""
                    prompt_zh = zh_part.replace("|", "&#124;").replace("\n", "<br>")
                    prompt_en = en_part.replace("|", "&#124;").replace("\n", "<br>")
                name = l["name"]
                cell = f"<img src='{rel_img}' width='260' alt='{l['id']} {name}'><br>**{l['id']}** · {name}"
                if prompt_zh or prompt_en:
                    details = "<br><details><summary>Prompts / 排版提示词</summary>"
                    if prompt_en:
                        details += f"<br><b>English:</b><br>{prompt_en}<br>"
                    if prompt_zh:
                        details += f"<br><b>中文:</b><br>{prompt_zh}"
                    details += "</details>"
                    cell += details
                row_cells.append(cell)
            while len(row_cells) < cols:
                row_cells.append("")
            lines.append(f"| {' | '.join(row_cells)} |")
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
