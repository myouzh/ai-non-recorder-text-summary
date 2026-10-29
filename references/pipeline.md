# AI 录音笔式网页生成管线 · 完整契约

> 逆向自微信输入法「AI 录音笔」分享页（2026-10-28 抓取），还原其"LLM 直接生成整页 HTML"管线的提示词设计。
> 本文件是 skill 的完整参考；执行时以 SKILL.md 的流程为准，细节查本文件。

---

## 一、管线原理

传统 AI 总结输出 Markdown/纯文本，本管线让模型**直接输出完整 HTML 页面**。系统随提示词下发三样东西：

1. **设计令牌 CSS**：一套固定色板/字号/圆角变量（明暗双主题），模型只能用令牌取色，保证任何产出版式统一
2. **移动端安全网 CSS**：用类名通配符兜底（任何含 grid/board/split/cols 的类在窄屏自动单列、`:only-child` 自动跨列），**允许模型自由发明组件类名**而不破版
3. **结构契约 + 图表元数据规范**：规定页面骨架（hero→分区→模块→图表→行动→落款）和每张图必须携带的 `data-visual-*` 元数据

产物形态：单文件 HTML，零外部依赖，可 iframe 嵌入分享。

---

## 二、主题色定制（本 skill 的核心扩展）

**默认规则：用户未指定主题色时，一律使用默认预设（原始微信绿色系），不要询问、不要发明新配色。**

指定方式（用户口头描述即可）：
- 颜色名：「用蓝色主题」「换成红色」「品牌色是深蓝」
- 十六进制：「主题色 #2563eb」
- 场景描述：「科技感一点」「暖色调」→ 映射到常见色（科技感=蓝、暖色=橙/红、金融=金/深蓝、自然=绿），并在交付时说明映射结果

**执行方式（必须走脚本，禁止手推色值）：**

```bash
python3 scripts/theme_tokens.py                      # 默认预设（绿色系）
python3 scripts/theme_tokens.py --accent "#2563eb"   # 指定主题色
python3 theme_tokens.py --accent "#e63946" --dark-accent "#ff6b6b"  # 分别指定明暗
python3 theme_tokens.py --accent "#7c3aed" --tint-neutrals           # 中性色也按色相重生成
python3 theme_tokens.py --json                       # JSON 输出（便于程序处理）
```

脚本输出一段完整 CSS（`:root` + 暗色 media query），**原样替换 `assets/base-template.html` 中的 `/*__THEME_TOKENS__*/` 占位符**。

派生规则（脚本内部固定，无需手算）：
| 令牌 | 明色规则 | 暗色规则 |
|---|---|---|
| accent | 用户指定色 | 同色相，亮度提升（L+0.22，封顶 0.62），饱和 ×0.7 |
| accent-ink | accent 加深 21% | dark-accent 混白 28% |
| accent-soft | accent 混白 88% | dark-accent 混页面底色 72% |
| accent-line | accent 混白 70% | dark-accent 混页面底色 60% |
| on-accent | accent 亮度 >0.45 取深墨，否则白 | dark-accent 亮度 >0.35 取深墨，否则白 |
| 中性色 | 默认保持原预设；`--tint-neutrals` 时按色相 8–16% 低饱和重生成 | 同上 |

warn 家族（琥珀警示色）为语义色，不随主题色变化。

---

## 三、硬性输出约束（违反任何一条即失败）

1. 只输出一个完整 HTML 文件：以 `<!doctype html>` 开头，`html lang="zh-CN"`，所有 CSS/JS 全部内联
2. 禁止任何外部资源：不得引用 CDN、外部字体、外链图片、图标库。图形一律用内联 SVG 或 CSS 绘制
3. 语言为简体中文；`<title>` 与页面大标题一致
4. JS 只允许原生 JS，禁止任何框架；禁止 alert/confirm/prompt；禁止 fixed 定位（页面将被 iframe 嵌入）
5. 移动端安全网 CSS 必须原样嵌入（已包含在 `assets/base-template.html` 中，直接复制使用，禁止改动其中任何色值与选择器）
6. 必须同时适配：明色/暗色（prefers-color-scheme）、移动端窄屏（≤600px）、减少动效（prefers-reduced-motion）
7. 页面最大宽度 640px 窄栏居中（`.page{max-width:640px;margin:0 auto;padding:28px 18px 56px;}`，已内置在 base-template.html）：桌面两侧留白、移动端保留 18px 安全边距；代码块 pre 已内置 pre-wrap 换行规则，长命令行不得溢出卡片；任何情况下不得出现横向滚动

---

## 四、页面结构契约（必须遵循）

按以下骨架组织，各部分按内容取舍：

1. `<header class="hero">`：kicker（栏目标签）+ h1（标题）+ lede（一段话摘要，关键词用 `<em class="hl">` 高亮）
2. `<div class="part"><span>第一部分 · xxx</span></div>`：分区标题，可多个
3. `<section class="mod">`：内容模块卡。内部为 eyebrow（小标签）+ h2 + 段落；可内嵌 keyline（金句框）/insight（洞察框）/warnbox（误区框）/figure（图表）
4. `<figure class="fig">`：可视化图表 + figcaption 图注
5. 行动区：`<hr class="hair">` + `.steps-label` + `<ol class="steps"><li><i>1</i>…</li></ol>`
6. `.creed`：一句收束金句（居中、强调色）
7. （可选）`<section class="mod teaser">`：下讲/下期预告
8. `<footer class="signoff">`：落款

---

## 五、组件规范（标准组件库已内置在 base-template.html）

- 金句框：`<div class="keyline">`，左侧强调色竖线，放讲者原话金句
- 洞察框：`<div class="insight"><b>洞察</b><span>…</span></div>`，放自己的提炼观点（区别于原文）
- 误区框：`<div class="warnbox"><div class="wt">常见误区</div><p>…</p><p class="wn">…</p></div>`
- 对比双栏：`.vs > .lane.lane-once|.lane-sub`，栏内 `.fnode` 节点 + `.fconn` 连接线；`.price` 价格标签、`.badge` 徽标、`.fnode.loop` 循环节点
- 对照矩阵：`.payboard > .pb-col.pb-no|.pb-yes`，`.pb-item` 条目（否定侧用 `<s>` 删除线），`.mk` 放 ✕/✓
- 分工图：`.dv > .dv-chain(.dv-box + .dv-join(＋) + .dv-you) + .dv-down(↓) + .dv-out`，`.dv-chips span` 标签
- SVG 图示：用 `.arena`（虚线容器）、`.lk-dash path`（流动虚线，动画 dashMove）、`.mem circle`（成员）、`.host`（主角）、`.t-on/.t-mut/.t-ink`（文字）、`.pill-bg/.pill-t`（药丸标签）、`.arr-ok`（箭头）等类名；文字必须用 `<text>`，不用图片
- 入场动效：模块加 `class="mod rv"`/`class="part rv"`（IntersectionObserver 脚本已内置）
- 流动动画：连接线用 `repeating-linear-gradient` + `animation:marchY`，SVG 虚线用 `animation:dashMove`

可自由发明同类组件类名，但必须满足安全网约束：避免使用含 grid/board/split/cols/columns/layout/panel/row/cluster 的类名承载需要保留多列的布局（除非接受窄屏自动单列）；含 flow/chain/timeline 的 flex 容器会在窄屏改为纵向；含 arrow 的元素会在窄屏旋转 90°（因此向下箭头类名用 `.dv-down` 而非 arrow）。

---

## 六、图表元数据契约（每个 figure 必须带全 5 个属性）

```html
<figure class="fig" data-visual-id="kebab-case 唯一 id"
        data-visual-title="图表标题"
        data-visual-type="流程对比图|关系示意图|对照矩阵|分工流程图|结构图|时间线"
        data-visual-relation="图中各元素的关系一句话描述"
        data-visual-source="该图依据的原文要点">
  …图形…
  <figcaption>图注（12-13px，muted 色）</figcaption>
</figure>
```

---

## 七、内容质量规则

1. 口语转书面：剔除"嗯/啊/那个/对吧"等语气词和重复，修正明显同音错别字（如"艺人公司"→"一人公司"），但不得改变原意、不得新增原文没有的信息
2. 结构化重构：按内容比重与逻辑重组顺序，不按说话顺序平铺
3. 关键信息突出：数字、价格、时间、结论用 `.hl`/`<strong>`/`.price` 突出
4. 洞察必须标注为"洞察"（自己的提炼），与讲者原话（金句框）区分
5. 每个主要分区至少 1 个可视化；全文 2-5 个 figure，类型不重复
6. 行动清单 2-4 步，每步一个动词开头的短句
7. 结尾必须通用化：落款/预告面向大众，不针对特定个人或行业定制

---

## 八、工程化建议（从管线反推）

1. **分段-汇总两段式**：长录音先切分转写段，每段生成结构化要点，再汇总生成最终 HTML，避免超长上下文丢细节
2. **产物存储**：HTML + 封面图（可用文末 SVG 麦克风图标模板渲染 PNG）按 `{hash}/v{版本}/` 路径存对象存储
3. **分享网关**：`/api/getFrame?share_token=...` 代理存储 HTML，响应头加 `CSP: sandbox allow-scripts; frame-ancestors 'self'`，iframe 用 `sandbox="allow-scripts" referrerpolicy="no-referrer"`
4. **高度自适应**：子页 postMessage 上报 `scrollHeight` 与背景色，父页同步 iframe 高度与底色（脚本已内置在 base-template.html）
5. **质量校验**：生成后检查 ① 无外部请求 ② 无横向滚动 ③ 暗色模式 ④ console 无报错
6. **元数据用途**：`data-visual-*` 可用于后续"重新生成单张图"、无障碍描述、分享卡片文案提取

---

## 九、分享封面 SVG 模板（512×512，品牌色）

需要封面图时，将下方 SVG 中的 `#0e7c56` 替换为当前主题 accent、`#f2f4ee` 替换为 page-bg、`#e2a233`/`#c08a28` 可保留为点缀金：

```html
<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="#f2f4ee"/>
  <circle cx="256" cy="256" r="170" fill="none" stroke="#0e7c56" stroke-width="18" stroke-dasharray="480 64 480 44"/>
  <path d="M428 263 L437 233 L413 236 Z" fill="#0e7c56"/>
  <path d="M84 249 L75 276 L99 276 Z" fill="#0e7c56"/>
  <polygon points="256,150 166,232 346,232" fill="#0e7c56"/>
  <rect x="186" y="232" width="140" height="110" fill="#0e7c56"/>
  <path d="M236 342 v-48 a20 20 0 0 1 40 0 v48 Z" fill="#f2f4ee"/>
  <circle cx="256" cy="86" r="22" fill="#e2a233" stroke="#c08a28" stroke-width="4"/>
  <circle cx="256" cy="86" r="11" fill="none" stroke="#c08a28" stroke-width="3"/>
  <circle cx="109" cy="341" r="22" fill="#e2a233" stroke="#c08a28" stroke-width="4"/>
  <circle cx="109" cy="341" r="11" fill="none" stroke="#c08a28" stroke-width="3"/>
  <circle cx="403" cy="171" r="22" fill="#e2a233" stroke="#c08a28" stroke-width="4"/>
  <circle cx="403" cy="171" r="11" fill="none" stroke="#c08a28" stroke-width="3"/>
</svg>
```
