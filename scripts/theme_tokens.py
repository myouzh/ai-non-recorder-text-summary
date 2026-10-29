#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""主题色令牌生成器 —— 「AI 录音笔式网页生成」skill 配套脚本。

用法：
    python3 theme_tokens.py                      # 输出默认预设（原始微信绿色系，与模板一致）
    python3 theme_tokens.py --accent "#2563eb"   # 由主题色派生整套设计令牌
    python3 theme_tokens.py --accent "#e63946" --dark-accent "#ff6b6b"

规则：
    - 不传 --accent 时，原样输出默认预设色值（禁止改动默认预设）。
    - 传入 --accent 时，accent 家族（accent / accent-ink / accent-soft /
      accent-line / on-accent，明暗两套）由该色按固定规则派生；
      中性色（page-bg / surface / ink / muted / line 等）默认保持默认预设，
      除非显式用 --tint-neutrals 按主题色相重新生成。
    - warn 家族为语义警示色，不随主题色变化。

输出为一段可直接粘贴进 <style> 的 CSS（含 :root 与暗色 media query）。
"""

import argparse
import colorsys
import sys

# ---------------------------------------------------------------- 默认预设
# 与提示词模板的设计令牌完全一致；禁止修改此处默认值。
DEFAULT_LIGHT = {
    "page-bg": "#f2f4ee", "surface": "#ffffff", "surface-2": "#e9efe6",
    "ink": "#1d2721", "muted": "#63726a", "line": "#dde3d6",
    "accent": "#0e7c56", "accent-ink": "#0b6244", "accent-soft": "#e2f0e8",
    "accent-line": "#b9d8c6", "on-accent": "#ffffff",
    "warn-ink": "#8a4f10", "warn-bg": "#f8eedb", "warn-line": "#ead8b4",
}
DEFAULT_DARK = {
    "page-bg": "#0e1411", "surface": "#182119", "surface-2": "#202b22",
    "ink": "#e6ede7", "muted": "#93a398", "line": "#2a382d",
    "accent": "#43c48d", "accent-ink": "#7cd9af", "accent-soft": "#17352a",
    "accent-line": "#2e5c45", "on-accent": "#082015",
    "warn-ink": "#e5b273", "warn-bg": "#2c2314", "warn-line": "#514020",
}

ORDER = ["page-bg", "surface", "surface-2", "ink", "muted", "line",
         "accent", "accent-ink", "accent-soft", "accent-line", "on-accent",
         "warn-ink", "warn-bg", "warn-line"]

# ---------------------------------------------------------------- 颜色工具


def hx(c):
    """'#rgb' / '#rrggbb' -> (r, g, b)"""
    c = c.strip().lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    if len(c) != 6:
        raise ValueError("颜色需为 #rgb 或 #rrggbb 十六进制: %r" % c)
    try:
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        raise ValueError("颜色需为 #rgb 或 #rrggbb 十六进制: %r" % c)


def rgb(t):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in t)


def mix(a, b, t):
    """a 向 b 混合，t 为 b 的权重 (0~1)"""
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def lum(c):
    """相对亮度 (WCAG)"""
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = hx(c) if isinstance(c, str) else c
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def rgb_to_hsl(t):
    r, g, b = [v / 255.0 for v in t]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360.0, s, l


def hsl_rgb(h, s, l):
    r, g, b = colorsys.hls_to_rgb((h % 360.0) / 360.0, max(0.0, min(1.0, l)),
                                  max(0.0, min(1.0, s)))
    return (r * 255, g * 255, b * 255)

# ---------------------------------------------------------------- 派生逻辑


def derive_accent_family(accent_hex):
    """由主题色派生明色 accent 家族"""
    a = hx(accent_hex)
    light = {
        "accent": rgb(a),
        "accent-ink": rgb(mix(a, (0, 0, 0), 0.21)),        # 加深 ~21%
        "accent-soft": rgb(mix(a, (255, 255, 255), 0.88)),  # 88% 白淡化
        "accent-line": rgb(mix(a, (255, 255, 255), 0.70)),  # 70% 白淡化
        # 亮色主题：accent 偏亮时改用深色文字保证对比度
        "on-accent": "#1d2721" if lum(a) > 0.45 else "#ffffff",
    }
    return light


def derive_dark_accent(accent_hex, dark_accent_hex=None):
    """派生暗色模式 accent：同色相，提亮度、降饱和"""
    if dark_accent_hex:
        return hx(dark_accent_hex)
    h, s, l = rgb_to_hsl(hx(accent_hex))
    l2 = min(0.62, l + 0.22) if l < 0.5 else min(0.66, l + 0.12)
    s2 = max(0.35, min(0.65, s * 0.70))
    return hsl_rgb(h, s2, l2)


def derive_dark_family(accent_hex, dark_accent_hex, page_bg_dark):
    da = derive_dark_accent(accent_hex, dark_accent_hex)
    bg = hx(page_bg_dark)
    dark = {
        "accent": rgb(da),
        "accent-ink": rgb(mix(da, (255, 255, 255), 0.28)),
        "accent-soft": rgb(mix(da, bg, 0.72)),
        "accent-line": rgb(mix(da, bg, 0.60)),
        "on-accent": "#082015" if lum(da) > 0.35 else "#ffffff",
    }
    return dark


def tint_neutrals(accent_hex):
    """按主题色相以极低饱和度重生成中性色（可选，--tint-neutrals 开启）"""
    h, _, _ = rgb_to_hsl(hx(accent_hex))
    light = {
        "page-bg": rgb(hsl_rgb(h, 0.14, 0.955)),
        "surface": "#ffffff",
        "surface-2": rgb(hsl_rgb(h, 0.16, 0.92)),
        "ink": rgb(hsl_rgb(h, 0.12, 0.13)),
        "muted": rgb(hsl_rgb(h, 0.08, 0.42)),
        "line": rgb(hsl_rgb(h, 0.12, 0.86)),
    }
    dark = {
        "page-bg": rgb(hsl_rgb(h, 0.12, 0.07)),
        "surface": rgb(hsl_rgb(h, 0.10, 0.10)),
        "surface-2": rgb(hsl_rgb(h, 0.10, 0.13)),
        "ink": rgb(hsl_rgb(h, 0.10, 0.90)),
        "muted": rgb(hsl_rgb(h, 0.06, 0.60)),
        "line": rgb(hsl_rgb(h, 0.10, 0.19)),
    }
    return light, dark

# ---------------------------------------------------------------- 输出


def emit(light, dark):
    def block(sel, d):
        rows = []
        for i in range(0, len(ORDER), 3):
            chunk = ORDER[i:i + 3]
            rows.append("  " + " ".join("--%s:%s;" % (k, d[k]) for k in chunk))
        return "%s{\n%s\n}" % (sel, "\n".join(rows))

    out = [":root{\n  color-scheme: light dark;"]
    for i in range(0, len(ORDER), 3):
        chunk = ORDER[i:i + 3]
        out.append("  " + " ".join("--%s:%s;" % (k, light[k]) for k in chunk))
    out.append("  --radius:16px;")
    out.append("  --shadow:0 1px 2px rgba(23,34,27,.05),0 10px 30px rgba(23,34,27,.06);")
    out.append("}")
    out.append("@media (prefers-color-scheme: dark){")
    out.append("  :root{")
    for i in range(0, len(ORDER), 3):
        chunk = ORDER[i:i + 3]
        out.append("    " + " ".join("--%s:%s;" % (k, dark[k]) for k in chunk))
    out.append("    --shadow:0 1px 2px rgba(0,0,0,.35),0 12px 32px rgba(0,0,0,.4);")
    out.append("  }")
    out.append("}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="生成 AI 录音笔式网页的设计令牌 CSS")
    ap.add_argument("--accent", help="主题色（强调色）#rrggbb；不传则输出默认预设")
    ap.add_argument("--dark-accent", help="暗色模式强调色；缺省由主题色派生")
    ap.add_argument("--tint-neutrals", action="store_true",
                    help="按主题色相重生成中性色（默认保持原中性色）")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出色值而非 CSS")
    args = ap.parse_args()

    light = dict(DEFAULT_LIGHT)
    dark = dict(DEFAULT_DARK)

    if args.accent:
        light.update(derive_accent_family(args.accent))
        dark.update(derive_dark_family(args.accent, args.dark_accent,
                                       DEFAULT_DARK["page-bg"]))
        if args.tint_neutrals:
            tl, td = tint_neutrals(args.accent)
            light.update(tl)
            dark.update(td)

    if args.json:
        import json
        print(json.dumps({"light": light, "dark": dark}, ensure_ascii=False,
                         indent=2))
        return

    print(emit(light, dark))
    if args.accent:
        sys.stderr.write(
            "[theme_tokens] 主题色 %s 已派生：accent=%s / dark accent=%s / "
            "on-accent=%s；中性色=%s\n" % (
                args.accent, light["accent"], dark["accent"],
                light["on-accent"],
                "已按色相重生成" if args.tint_neutrals else "保持默认预设"))
    else:
        sys.stderr.write("[theme_tokens] 未指定主题色，输出默认预设（原始微信绿色系）\n")


if __name__ == "__main__":
    main()
