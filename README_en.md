<p align="right">
  <a href="README.md">中文</a> | <strong>English</strong>
</p>

# Hand-drawn Style & Layout Prompter for AI Image Generation

> **Struggling to describe art styles? Trouble structuring visual layouts? Simply pick an index number to generate highly recognizable AI image prompts.**

This repository curates **274 distinct hand-drawn illustration styles** (`001`–`274`) and **118 composition layout patterns** (`SC-*` Social Cards, `IG-*` Infographics, `SB-*` Comic Storyboards).

Whether you are crafting social media post covers, educational infographics, architectural comparisons, or multi-panel narrative comics, you no longer need to memorize obscure art history terminology or struggle with complex compositions. **Simply choose a style number and layout ID, supply your topic, and instantly get verified, high-fidelity bilingual prompts ready to paste into Midjourney, DALL-E 3, Flux, Stable Diffusion, or any other image generator.**

---

## 🌟 Core Pain Points & Solutions

| Creator Pain Point | How This Library Solves It |
| :--- | :--- |
| **Vague style descriptions lead to style drift** | **Numbered Indexing**: 274 systematically categorized illustration styles, eliminating guess-and-pray prompting. |
| **Monotonous composition; hard to format complex graphics** | **118 Layout Compositions**: 19 Social Cards, 31 Infographics, 68 Comic Storyboards ready out-of-the-box. |
| **Text disconnects from art; awkward typography placement** | **Dual-Mode Workflow**: Seamlessly toggle between "Pure-Image Mode" (pure illustration) and "Graphic-Text Mode" (unified visual-textual composition). |
| **Models ignore style keywords or lack style fidelity** | **Tiered Model Adaptation & Fallback**: Calibrated keyword activation for native models; automatic Reference Image Fallback (4-grid sheets) for all third-party models. |

---

## 🎯 Target Audiences & Use Cases

- **Content Creators & Influencers**: Social media covers (Xiaohongshu, Instagram, X/Twitter), newsletter hero images, viral quote cards.
- **Knowledge & Tech Bloggers**: Comparison lists, architecture pyramids, step-by-step processes, and high-engagement infographics.
- **Comic & Story Creators**: 4-panel strips, emotional webtoons, storyboard drafts, children's storybook illustrations.
- **Brand & Visual Designers**: Rapid concept sketching, creative campaign posters, character design prototypes.

---

## Installation

You can install this skill directly into your AI coding assistant (Codex, Claude Code, Cursor, WorkBuddy, OpenCode):

> **"Install this Skill for me: https://github.com/yang0/handraw-style"**

The assistant will automatically clone the repository and configure all styles, layout templates, and reference assets.

---

## How to Use

1. Browse the [Style Visual Sheet (STYLES.md)](STYLES.md) or [Layout Visual Sheet (LAYOUTS.md)](LAYOUTS.md) to pick your desired numbers.
2. Note your chosen ID, such as style `041`, or layout `SC-001`.
3. Provide your command to the assistant:
   - **Style only**: `Style: 041, Theme: First milk tea of autumn`
   - **Layout + Style**: `Layout: SC-001, Style: 041, Theme: First milk tea of autumn`
4. Receive clean, copyable bilingual prompts (English and Chinese).
5. Copy and paste into Midjourney, DALL-E 3, Flux, Stable Diffusion, or your favorite AI generation tool.

---

## Two Prompt Modes, Instant Switching

Any number and theme can seamlessly toggle between two modes without changing your style:

- **Pure-Image Mode (纯图模式)**: Let the theme dictate pure pictorial content without in-image text. Ideal for pure illustrations, wallpapers, book covers, and concept art.  
  *Example*: `Pure-image mode, Style: 041, Theme: First milk tea of autumn`
- **Graphic-Text Mode (图文模式)**: Preserves your copy text and guides the AI to design metaphors and integrate typography harmoniously into the visual composition. Ideal for quote posters, meme graphics, and social cards.  
  *Example*: `Graphic-text mode, Style: 267, Theme: There are many things you couldn't figure out back then. Don't worry, give it some time and you might just forget about them.`

Switch modes anytime by typing *"switch to pure-image mode"* or *"switch to graphic-text mode"*. Defaults to pure-image mode.

### Graphic-Text Mode Demonstration

The illustration below shows text integrated harmoniously with the visual composition (this is a conceptual demonstration and not tied to any single number):

![Graphic-Text Mode Demo: Duck with hand-drawn lettering](images/graphic-text-mode-demo.webp)

---

## Model Adaptation & Reference Image Fallback

By default, the Skill crafts copyable prompts. When you explicitly request image generation, it optimizes the output based on verified model capabilities:

- **Explicitly Calibrated Models (e.g., `gpt-image-2`)**: Full activation hierarchy for all 274 styles: Style/Author Name → Positive Core Traits → Reference Image only when traits alone cannot reliably trigger the style.
- **Third-Party & General Models (Midjourney, Flux, Stable Diffusion, Imagen, Gemini, etc.)**: Employs the rock-solid **Reference Image Fallback** strategy. Automatically attaches or points to the 1024x1024 4-grid style reference sheet, ensuring 100% faithful reproduction of linework, texture, and color palette without prompt hallucination.
- **Open for Contributions**: The capability matrix is transparently defined in [`skills/handdraw-style-prompter/references/model_capabilities.json`](skills/handdraw-style-prompter/references/model_capabilities.json). Pull requests for other model benchmarks are welcome!

---

## Examples

### Example 1: Style Only (Pure-Image Mode)
> **User Input**: `Style: 018, Theme: Late-night coder talking to a rubber duck`
>
> **English Prompt**:
> ```text
> Style name: #018 · Minimal Deadpan Dialogue Cartoon. Theme: Late-night coder talking to a rubber duck. Reference author/style name: Poorly Drawn Lines / Reza Farazmand.
> ```
> **Chinese Prompt**:
> ```text
> 风格名称：#018 · Minimal Deadpan Dialogue Cartoon。主题：深夜程序员与一只小黄鸭对话。参考作者/风格名称：Poorly Drawn Lines / Reza Farazmand。
> ```

### Example 2: Layout + Style (Graphic-Text Mode)
> **User Input**: `Layout: SC-001, Style: 248, Theme: Remote work vs Office work`
>
> **English Prompt**:
> ```text
> Xiaohongshu social-media card. Use a text-above-image layout: place the theme copy and concise supporting text in the upper section, with a complete primary or scene illustration below. Keep a clear top-to-bottom reading order, let the text and image relate naturally, and keep the overall composition simple. Theme: Remote work vs Office work. Style name: #248 · Tactile Soft 3D Claymation & Storybook Character. Reference author/style name: OscarAI. 【如果主题直白包含画面元素那就按主题出图，文案由你来升华，但是不要直接描述画面。 如果主题比较概念化，那么文案和主题尽量保持一致，如果文案较长由你提炼，由你先设计画面隐喻（人类和非人类都行）再出图   。    文字参与构图，图文一体】
> ```

### Example 3: Infographic Knowledge Card
> **User Input**: `Layout: IG-007, Theme: 3 stages of building a habit`
>
> **English Prompt**:
> ```text
> Layout: IG-007 · Bold Headline Tag Cards. Theme: 3 stages of building a habit. 【如果主题直白包含画面元素那就按主题出图，文案由你来升华，但是不要直接描述画面。 如果主题比较概念化，那么文案和主题尽量保持一致，如果文案较长由你提炼，由你先设计画面隐喻（人类和非人类都行）再出图   。    文字参与构图，图文一体】
> ```

---

## Offline Visual Galleries

You can browse the interactive local galleries directly in your browser:
- **Style Gallery**: [`skills/handdraw-style-prompter/gallery/index.html`](skills/handdraw-style-prompter/gallery/index.html) — 20 contact sheets and 274 style cards with live language switching.
- **Layout Gallery**: [`skills/handdraw-style-prompter/gallery/layouts.html`](skills/handdraw-style-prompter/gallery/layouts.html) — 118 visual compositions with category filtering and one-click bilingual prompt copying.

---

## Community & Author

- GitHub: [yang0/handraw-style](https://github.com/yang0/handraw-style)
- X (Twitter): [@yang02010](https://x.com/yang02010)
- WeChat Community: Available via the top-right button in the local visual galleries.
