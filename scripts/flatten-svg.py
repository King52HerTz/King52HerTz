#!/usr/bin/env python3
"""把生成的统计卡 SVG 里依赖动画的部分压实成静态值。

github-readme-stats 生成的卡片把文字初始 opacity 设成 0，靠 CSS 动画
fade-in 显示。SVG 被放进 <img> 里时，部分渲染环境（无头浏览器、部分
客户端预览）不会播动画，结果就是一张只剩边框和评级圆环的空卡。

这里把 opacity 直接改成 1，并把评级圆环的动画终值写成静态
stroke-dashoffset，这样任何环境都能看到完整卡片。

用法: python3 scripts/flatten-svg.py profile/*.svg
"""

import re
import sys

RANK_TO = re.compile(r"to\s*\{\s*stroke-dashoffset:\s*([\d.]+)\s*;", re.S)


def flatten(path: str) -> None:
    with open(path, encoding="utf-8") as fh:
        svg = fh.read()

    original = svg

    # 文字与统计行：不再从透明淡入
    svg = svg.replace("opacity: 0;", "opacity: 1;")

    # 评级圆环：动画终值落成静态值，去掉 animation 声明
    m = RANK_TO.search(svg)
    if m:
        svg = re.sub(
            r"(\.rank-circle\s*\{[^}]*?)animation:\s*rankAnimation[^;]*;",
            r"\1stroke-dashoffset: %s;" % m.group(1),
            svg,
            count=1,
        )

    # 其余动画全部去掉（keyframes 留着无害，但引用会被删干净）
    svg = re.sub(r"animation:\s*(?!none)[^;]+;", "", svg)

    # 评级字母居中：原实现把文字放在 x=-5 y=3，相对圆心 (-10, 8) 偏了半个字，
    # 视觉上像没对齐。直接用圆心的 cx/cy 定位文字。
    rim = re.search(r'class="rank-circle-rim"\s+cx="(-?[\d.]+)"\s+cy="(-?[\d.]+)"', svg)
    if rim:
        cx, cy = rim.group(1), rim.group(2)
        svg = re.sub(
            r'(<text\s+)x="-?[\d.]+"\s+y="-?[\d.]+"([^>]*data-testid="level-rank-icon")',
            r'\1x="%s" y="%s"\2' % (cx, cy),
            svg,
            count=1,
        )

    if svg != original:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        print(f"flattened {path}")
    else:
        print(f"unchanged {path}")


if __name__ == "__main__":
    targets = sys.argv[1:]
    if not targets:
        sys.exit("usage: flatten-svg.py <file.svg> [more.svg ...]")
    for target in targets:
        flatten(target)
