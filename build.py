#!/usr/bin/env python3
"""把 src/ 下的模板 + 数据 + 片段构建成根目录的 index.html。

用法：
    python build.py                 # 生成 ./index.html
    python build.py --out dist/index.html
    python build.py --check         # 只校验不写文件（CI 用）

零第三方依赖，只需 Python 3.8+。
模板语法（够用就好）：
    {{site.title}}                      取变量（支持 a.b.c 路径）
    {{#if btn.external}} ... {{/if}}    条件（空串/空列表/false 视为假）
    {{#for nav as link}} ... {{/for}}   循环（循环体内用 {{link.href}}）
    {{> nav}}                           引入 src/partials/nav.html（自动缩进）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
PARTIALS = SRC / "partials"
DATA_FILE = SRC / "data" / "site.json"
TEMPLATE_FILE = SRC / "templates" / "base.html"
DEFAULT_OUTPUT = ROOT / "index.html"

VAR_RE = re.compile(r"\{\{\s*([\w.]+)\s*\}\}")
INCLUDE_RE = re.compile(r"^([ \t]*)\{\{>\s*([\w./-]+)\s*\}\}[ \t]*$", re.M)
# 开标记：{{#for list as item}} / {{#if x}}；闭标记：{{/for}} / {{/if}}
TAG_RE = re.compile(
    r"\{\{#(for|if)\s+([\w.]+)(?:\s+as\s+(\w+))?\s*\}\}|\{\{/(for|if)\}\}"
)


class TemplateError(Exception):
    pass


def lookup(ctx: dict, path: str):
    """按 a.b.c 路径取值，取不到就报错，避免静默渲染出空洞页面。"""
    cur = ctx
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            raise TemplateError(f"未定义的变量：{path}")
    return cur


def truthy(value) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, (list, dict, str)):
        return len(value) > 0
    return bool(value)


def render(template: str, ctx: dict) -> str:
    """先展开 {{> partial}}，再递归解析 #for / #if，最后替换 {{var}}。"""

    def include_sub(m: re.Match) -> str:
        indent, name = m.group(1), m.group(2)
        path = PARTIALS / f"{name}.html"
        if not path.is_file():
            raise TemplateError(f"找不到片段文件：{path}")
        chunk = render(path.read_text(encoding="utf-8"), ctx).rstrip("\n")
        lines = chunk.split("\n")
        return "\n".join([lines[0]] + [indent + ln if ln else ln for ln in lines[1:]])

    return parse_blocks(INCLUDE_RE.sub(include_sub, template), ctx)


def parse_blocks(text: str, ctx: dict) -> str:
    """递归解析 #for / #if 块（支持嵌套），叶子文本只做变量替换。"""
    opening = TAG_RE.search(text)
    if not opening:
        return VAR_RE.sub(lambda m: str(lookup(ctx, m.group(1))), text)

    if opening.group(4):  # 孤立的 {{/for}} {{/if}}
        raise TemplateError(f"多余的结束标记：{opening.group(0)}")

    kind, path, alias = opening.group(1), opening.group(2), opening.group(3)
    if kind == "for" and not alias:
        raise TemplateError(f"#for 缺少 as 别名：{opening.group(0)}")

    body_start, close_end, body_end = match_close(text, opening, kind)
    body = text[body_start:body_end]
    before = parse_blocks(text[: opening.start()], ctx)
    after = parse_blocks(text[close_end:], ctx)

    if kind == "for":
        try:
            items = lookup(ctx, path)
        except TemplateError:
            items = []  # 列表字段省略时当作空列表
        if not isinstance(items, list):
            raise TemplateError(f"#for 只能遍历列表，{path} 不是列表")
        chunks = []
        for item in items:
            local = dict(ctx)
            local[alias] = item
            chunks.append(parse_blocks(body, local))
        return before + "".join(chunks) + after

    # kind == "if"
    try:
        value = lookup(ctx, path)
    except TemplateError:
        value = None  # 可选字段在数据中省略时视为假
    return before + (parse_blocks(body, ctx) if truthy(value) else "") + after


def match_close(text: str, opening: re.Match, kind: str):
    """找到与 opening 配对的结束标记，返回 (body_start, close_end, body_end)。"""
    depth = 1  # 开标记自身算一层
    pos = opening.end()
    while True:
        tag = TAG_RE.search(text, pos)
        if not tag:
            raise TemplateError(f"标记 {opening.group(0)} 没有对应的 {{{{/{kind}}}}}")
        if tag.group(4) == kind:  # 同类型的结束标记
            depth -= 1
            if depth == 0:
                return opening.end(), tag.end(), tag.start()
        elif tag.group(1) == kind:  # 同类型的嵌套开标记
            depth += 1
        pos = tag.end()


def build() -> str:
    if not TEMPLATE_FILE.is_file():
        raise TemplateError(f"找不到模板：{TEMPLATE_FILE}")
    if not DATA_FILE.is_file():
        raise TemplateError(f"找不到数据文件：{DATA_FILE}")

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    html = render(TEMPLATE_FILE.read_text(encoding="utf-8"), data)
    # 循环/条件块展开后会留下只有缩进的空白行和连续空行，整理一下保持产物可读
    html = re.sub(r"\n[ \t]+\n", "\n\n", html)
    return re.sub(r"\n(?:[ \t]*\n){2,}", "\n\n", html)


def main() -> int:
    parser = argparse.ArgumentParser(description="构建静态主页 index.html")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT), help="输出文件路径")
    parser.add_argument("--check", action="store_true", help="只校验模板与数据，不写文件")
    args = parser.parse_args()

    try:
        html = build()
    except (TemplateError, json.JSONDecodeError) as exc:
        print(f"[构建失败] {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(f"[校验通过] 模板与数据正常，预计输出 {len(html)} 字符")
        return 0

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"[构建完成] {out_path.relative_to(ROOT)} ({len(html)} 字符)")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    raise SystemExit(main())
