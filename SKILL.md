---
name: ai-non-recorder-text-summary
description: AI 非录音笔 · 结构化视觉生成器：借鉴微信的「AI 录音笔」模式，将录音转写、课程讲稿、口播文案等非结构化口述，梳理、分析、重构为符合大脑习惯记忆的结构化表达 HTML 网页——零外网依赖、自包含、可嵌入分享，主题色随需定制。当用户要求把转写文本"生成网页/总结页/分享页/可视化页面"，或提到"AI 录音笔式网页生成"、讲稿转网页、文本总结可视化时使用本 skill。支持自定义主题色（颜色名或十六进制），用户不指定时默认使用原始微信绿色系。触发词：录音转写网页、语音总结页、讲稿可视化、分享页生成、文本总结网页、AI 非录音笔。
agent_created: true
---

# AI 非录音笔 · 结构化视觉生成器

## Overview

把口语化录音转写文本（课程、口播、会议）直接重构为一个自包含的单文件 HTML 总结页面：移动端安全网 + 明暗双主题 + 结构化图表，读者"一读即懂"。零外部依赖，可 iframe 嵌入分享。

## 工作流（按序执行）

### 1. 确定主题色

- 扫描用户请求中是否指定主题色：颜色名（"用蓝色主题"）、十六进制（"主题色 #2563eb"）、或风格描述（"科技感"→蓝、"暖色"→橙红、"金融"→金/深蓝）。
- **未指定 → 直接用默认预设（原始微信绿色系），不要询问。**
- 指定 → 运行脚本生成令牌，禁止手推色值：

```bash
python3 scripts/theme_tokens.py                        # 默认预设（绿色系）
python3 scripts/theme_tokens.py --accent "#2563eb"     # 指定主题色
python3 scripts/theme_tokens.py --accent "#e63946" --dark-accent "#ff6b6b"
python3 scripts/theme_tokens.py --accent "#7c3aed" --tint-neutrals  # 中性色也按色相重生成
```

脚本输出一段完整 CSS（`:root` + 暗色 media query）。

### 2. 搭建页面骨架

复制 `assets/base-template.html` 到目标输出路径（如用户当前工作区，文件名用内容主题），将脚本输出的主题令牌**原样替换**其中的 `/*__THEME_TOKENS__*/` 占位符。

模板已内置：移动端安全网（与原始管线逐字节一致，禁止改动）、标准组件库 + 交互组件库（关键词导航/落差对照/勾选清单/二选一）、入场动效（IntersectionObserver + 滚动/轮询兜底，确保 `.rv` 元素任何引擎与滚动方式下必然可见，4 秒终极全显）、**健壮的 iframe 自适应测高 + 锚点滚动脚本**（ResizeObserver + MutationObserver + 图片/字体/主题监听，rAF+定时器双保险，兼容 `app:*` 与 `voice-recorder:*` 双协议）。只需在 `<div class="page">` 内按注释标记填充内容。

### 3. 生成内容

严格遵循 `references/pipeline.md` 的契约（先读该文件再写内容）：

- **结构**：hero（kicker+h1+lede）→ part 分区 → mod 模块卡 → figure 图表 → steps 行动清单 → creed 收束 → teaser 预告（可选）→ signoff 落款
- **口语转书面**：剔除语气词与重复，修正同音错别字，不改变原意、不新增原文没有的信息
- **结构化重组**：按内容比重与逻辑重组，不按说话顺序平铺
- **图表**：全文 2-5 张 figure，类型不重复，每张必须带全 5 个 `data-visual-*` 属性（id/title/type/relation/source），详见 pipeline.md 第六节
- **讲者原话**进 `keyline` 金句框；**自己的提炼**进 `insight` 洞察框并标"洞察"，两者不混用
- 数字、价格、时间、结论用 `.hl`/`<strong>`/`.price` 突出
- 行动清单 2-4 步，每步动词开头
- 结尾通用化：落款与预告面向大众

**交互组件（借鉴原版真实分享页，按内容按需选用，不滥用）：**

- `.kw-nav` 关键词主线导航：3 个递进关键词卡片 + 锚点，跳到正文 `.part[id]`；有明确 3 段主线时用，写到 hero 之后
- `.gap-row` 落差对照：`信号 ≠ 真相` 三行对照，适合破题/澄清误区
- `.crit` 勾选清单：读者逐项点圆圈确认，全过给正反馈。用于"自检/准入条件/核对项"，结构：`.crit-check`（`aria-pressed`）→ `.crit` → `.chk-foot`（含 `.chk-count` + `.alltxt`）
- `.dl-btns` 二选一两难：点选项展开对应反馈。用于"要不要答应/选 A 还是 B"的决策演示，反馈写在 `<template data-fb="yes|no">`（可含任意 HTML），配 `.dl-fb` 容器
- `.key` 核心诀窍框 / `.note` 注释条：加重关键结论
- 交互组件 DOM 变化会自动触发重测高（脚本已内置），无需额外处理

长文本（数千字以上）先分段提炼要点，再汇总成页，避免丢细节。

### 4. 校验并交付

生成后逐项检查：

1. 无外部资源：全文无 `http://`/`https://` 引用、无 `<script src>`、无外链字体/图片（SVG 的 xmlns 命名空间声明除外）
2. 无 `position:fixed`、无 `alert/confirm/prompt`、无框架依赖
3. `<title>` 与 h1 一致；`lang="zh-CN"`
4. 明色/暗色/≤600px 窄屏/prefers-reduced-motion 四类适配均在模板内覆盖
5. 5 个 `data-visual-*` 属性齐全；figure 数量 2-5 且类型不重复
6. 若用了交互组件：勾选清单每个 `.crit-check` 有 `aria-label`，二选一反馈写在 `<template data-fb>` 而非属性里（避免 HTML 引号截断）
7. 用 `present_files` 交付 HTML

## 主题色速查

| 用户说法 | 处理 |
|---|---|
| 未提颜色 | 默认预设（绿色系 #0e7c56），交付时说明用的是默认主题 |
| "蓝色/科技感" | `--accent "#2563eb"` |
| "红色/暖色/喜庆" | `--accent "#e63946"` |
| "紫色/高端" | `--accent "#7c3aed"` |
| "金色/金融" | `--accent "#b8860b"`（暗色脚本会自动提亮） |
| 十六进制 | 直接传入 `--accent` |
| 指定明暗两色 | `--accent` + `--dark-accent` |

换主题只需重跑脚本、替换令牌块，内容不动。

## Resources

- `scripts/theme_tokens.py` — 主题色令牌生成器（默认预设 / 派生 / JSON 输出；含 warn/ok/risk 语义色）
- `assets/base-template.html` — 页面骨架（含安全网 + 标准组件库 + 交互组件库 + 动效/测高脚本，唯一占位符是 `/*__THEME_TOKENS__*/`）
- `references/pipeline.md` — 完整管线契约：主题色派生规则表、硬性输出约束、页面结构契约、组件规范、图表元数据契约、内容质量规则、交互组件契约、分享封面 SVG 模板
