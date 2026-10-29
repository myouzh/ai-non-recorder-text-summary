<div align="center">

# AI 非录音笔文本总结

**把录音转写、课程讲稿、口播文案，变成单文件 HTML 总结网页的 WorkBuddy Skill**

![type](https://img.shields.io/badge/type-WorkBuddy%20Skill-2563eb)
![deps](https://img.shields.io/badge/dependencies-0-2563eb)
![theme](https://img.shields.io/badge/default%20theme-tech--blue%20%232563eb-2563eb)
![version](https://img.shields.io/badge/version-1.0.0-2563eb)

</div>

## 它做什么

传统 AI 总结输出 Markdown 或纯文本，阅读成本高、分享体验差。本 skill 让模型**直接输出完整 HTML 页面**：结构契约固定、色板令牌化、移动端安全网兜底，任何产出版式统一，可直接 iframe 嵌入分享。

三个硬保证：

- **零外部依赖** — 无 CDN、无外链字体与图片，图形全部内联 SVG/CSS 绘制
- **760px 居中** — 任何窄屏不出现横向滚动
- **四类适配全覆盖** — 明色 / 暗色（`prefers-color-scheme`）、≤600px 窄屏、减少动效（`prefers-reduced-motion`）

## 主题色（核心扩展）

用户不指定主题色时，**一律使用默认预设（原始绿色系），不询问、不发明新配色**。指定方式：

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

```bash
# 1. 安装：拷入用户级 skills 目录
cp -r ai-non-recorder-text-summary ~/.workbuddy/skills/

# 2. 对话中触发（直接提需求，或显式点名）
@ai-non-recorder-text-summary 把这段录音转写生成总结网页，用科技蓝
```

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

**[README.html](README.html)** 由本 skill 自己生成：主题色科技蓝 `#2563eb`，包含管线输入输出示意图、明暗令牌对照矩阵、仓库结构图——既是文档，也是效果预览。直接用浏览器打开即可。

## 质量校验清单

生成后逐项过：无外部请求 → 无 `position:fixed` → `<title>` 与 h1 一致 → 四类适配 → 每张图带全 5 个 `data-visual-*` 属性 → figure 数量 2-5 且类型不重复。
