> **声明**：此 skill 是基于对微信 AI 录音笔进行反编译分析后编写的，仅供学习参考之用。

<div align="center">

# AI 非录音笔 · 结构化视觉生成器

**借鉴微信的「AI 录音笔」模式，将录音转写、课程讲稿、口播文案等非结构化口述，梳理、分析、重构为符合大脑习惯记忆的结构化表达 HTML 网页——零外网依赖、自包含、可嵌入分享，主题色随需定制。**

![type](https://img.shields.io/badge/type-Agent%20Skill-0e7c56)
![platforms](https://img.shields.io/badge/platforms-WorkBuddy%20%7C%20Claude%20%7C%20Cursor%20%7C%20Codex%20%7C%20DeepSeek-0e7c56)
![deps](https://img.shields.io/badge/dependencies-0-0e7c56)
![theme](https://img.shields.io/badge/default%20theme-wechat--green%20%230e7c56-0e7c56)
![version](https://img.shields.io/badge/version-1.0.0-0e7c56)

</div>

**目录**：[它做什么](#它做什么) · [主题色](#主题色核心扩展) · [快速开始](#快速开始) · [文件结构](#文件结构) · [可视化说明](#可视化说明) · [质量校验清单](#质量校验清单)

## 它做什么

传统 AI 总结输出 Markdown 或纯文本，阅读成本高、分享体验差。本 skill 让模型**直接输出完整 HTML 页面**：结构契约固定、色板令牌化、移动端安全网兜底，任何产出版式统一，可直接 iframe 嵌入分享。

三个硬保证：

- **零外部依赖** — 无 CDN、无外链字体与图片，图形全部内联 SVG/CSS 绘制
- **640px 窄栏居中** — 桌面两侧留白，任何窄屏不出现横向滚动
- **四类适配全覆盖** — 明色 / 暗色（`prefers-color-scheme`）、≤600px 窄屏、减少动效（`prefers-reduced-motion`）

## 主题色（核心扩展）

用户不指定主题色时，**一律使用默认预设（原始微信绿色系），不询问、不发明新配色**。指定方式：

| 说法 | 处理 |
|---|---|
| "用蓝色主题" / "科技感一点" | `--accent "#2563eb"` |
| "主题色 #e63946" | 十六进制直接传入 |
| "分别指定明暗" | `--accent` + `--dark-accent` |
| "中性色也按色相来" | 加 `--tint-neutrals` |

一个 accent 色由脚本派生整套令牌（禁止手推色值）：

```bash
python3 scripts/theme_tokens.py                      # 默认预设（绿色系）
python3 scripts/theme_tokens.py --accent "#2563eb"   # 指定主题色
python3 scripts/theme_tokens.py --json               # JSON 输出
```

| 令牌 | 明色规则 | 暗色规则 |
|---|---|---|
| accent | 用户指定色 | 同色相提亮（L+0.22，封顶 0.62），饱和 ×0.7 |
| accent-ink | 加深 21% | 混白 28% |
| accent-soft | 混白 88% | 混页面底色 72% |
| accent-line | 混白 70% | 混页面底色 60% |
| on-accent | 亮度 >0.45 取深墨，否则白 | 亮度 >0.35 取深墨，否则白 |

## 快速开始

本 skill 遵循 Agent Skills 开放标准（`SKILL.md` + `name`/`description` frontmatter），**一份目录，多平台通用**——拷到对应平台的 skills 目录即被自动发现，零改动。

### 方式一：原生支持 Skills 的平台（推荐）

| 平台 | 用户级（全局生效） | 项目级（随仓库共享） | 触发方式 |
|---|---|---|---|
| WorkBuddy | `~/.workbuddy/skills/` | `.workbuddy/skills/` | `@ai-non-recorder-text-summary …` 或自然语言 |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` | 自动匹配，`/` 菜单点名 |
| claude.ai | 设置 → 功能 → Skills 上传 zip（需付费计划） | — | 自动匹配 |
| Cursor | `~/.cursor/skills/`（或 `~/.agents/skills/`） | `.cursor/skills/`（或 `.agents/skills/`） | `/name` 或 `@name` |
| OpenAI Codex | `~/.agents/skills/` | `<仓库根>/.agents/skills/`（向上扫描） | `/skills` 或 `$name` |
| DeepSeek Deep Code | `~/.agents/skills/` | `.deepcode/skills/` | `/` 技能选择器 |
| DeepSeek Harness | `~/.dsh/skills/`（或 `~/.agents/skills/`） | `.dsh/skills/`（或 `.agents/skills/`） | `/name` 或 `@name` |

```bash
# 按平台拷一次即可，目录名保持不变
cp -r ai-non-recorder-text-summary ~/.workbuddy/skills/
cp -r ai-non-recorder-text-summary ~/.claude/skills/
cp -r ai-non-recorder-text-summary ~/.agents/skills/
```

### 方式二：没有 Skills 机制的平台

把 `SKILL.md` 正文作为系统提示词或项目规则注入（`scripts/`、`references/` 需与 SKILL.md 保持同仓，相对路径可达）：

| 平台 | 接入文件 |
|---|---|
| Windsurf | `.windsurf/rules/*.md` |
| Cline | `.clinerules` |
| Gemini CLI | `GEMINI.md` |
| 通用标准 | 根目录 `AGENTS.md` |
| 纯 API 调用 | system prompt 直接粘贴 SKILL.md 正文 |

生成流程四步：**定主题色 → 套骨架（替换 `/*__THEME_TOKENS__*/` 占位符）→ 按 `references/pipeline.md` 契约填内容 → 过六项校验交付**。

两条红线：安全网 CSS 禁止改动一个字符；主题色必须走 `theme_tokens.py`。

## 文件结构

```
ai-non-recorder-text-summary/
├── SKILL.md                   # 入口：触发词、四步工作流、主题色速查表
├── README.md                  # 本文件
├── README.html                # 可视化说明页（科技蓝 #2563eb 演示）
├── scripts/
│   └── theme_tokens.py        # 主题色令牌生成器
├── references/
│   └── pipeline.md            # 完整管线契约：结构/组件/图表元数据/内容规则
└── assets/
    ├── base-template.html     # 页面骨架：安全网 + 组件库 + 动效脚本
    └── cover.svg              # 512×512 分享封面（科技蓝）
```

## 可视化说明

**[README.html](README.html)** 由本 skill 自己生成：主题色科技蓝 `#2563eb`，包含管线输入输出示意图、明暗令牌对照矩阵、仓库结构图、多平台安装流程图——既是文档，也是效果预览。已通过 GitHub Pages 部署，点击即看：

**[在线预览 → https://myouzh.github.io/ai-non-recorder-text-summary/README.html](https://myouzh.github.io/ai-non-recorder-text-summary/README.html)**

（仓库中的 `.html` 文件在 GitHub 上默认只显示源码，在线版由 Pages 直接渲染；也可以下载到本地用浏览器打开。）

## 质量校验清单

生成后逐项过：无外部请求 → 无 `position:fixed` → `<title>` 与 h1 一致 → 四类适配 → 每张图带全 5 个 `data-visual-*` 属性 → figure 数量 2-5 且类型不重复。
