#!/usr/bin/env bash
# 由 ../探究/*.md 生成《哲学×AI探究集》。依赖：pandoc、xelatex、霞鹜文楷。
set -e
cd "$(dirname "$0")"
mkdir -p book
python3 - <<'PY'
import re, glob, os

def fix_quotes(t):
    # ASCII 直引号 -> 中文全角弯引号（仅在代码块外，按出现顺序开/合交替）
    parts = t.split('```')
    for i in range(0, len(parts), 2):
        out, op = [], True
        for ch in parts[i]:
            if ch == '"':
                out.append('“' if op else '”'); op = not op
            else:
                out.append(ch)
        parts[i] = ''.join(out)
    return '```'.join(parts)

for p in sorted(glob.glob('../探究/0*.md')):
    num=os.path.basename(p)[:2]
    t=open(p,encoding='utf-8').read()
    def repl(m):
        if num=='00':
            return '\n```{=latex}\n\\begin{center}\\includegraphics[width=0.82\\linewidth]{img/tension-map.pdf}\\end{center}\n```\n'
        return '\n*（论辩骨架图见在线 Obsidian 版；本书以文字论证为主。）*\n'
    t=re.sub(r'```mermaid.*?```', repl, t, flags=re.S)   # 去 mermaid（00 换成 TikZ 图）
    t=re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)          # 链接降级为纯文字
    t=t.replace('∴','=>')                                  # 代码块推论符换 ASCII
    t=fix_quotes(t)                                        # 直引号 -> 中文全角
    open(f'book/ch{num}.md','w',encoding='utf-8').write(t)
PY
for f in book/ch*.md; do pandoc "$f" -f markdown-smart --top-level-division=chapter -o "${f%.md}.tex"; done
# pandoc 的 latex 写出器会把弯引号写成 ``/'' 西文连字；换回全角中文引号，交给 xeCJK charclass 用文楷渲染
python3 - <<'PY'
import glob
for f in glob.glob('book/ch*.tex'):
    t=open(f,encoding='utf-8').read()
    t=t.replace('``','“').replace("''",'”')
    open(f,'w',encoding='utf-8').write(t)
PY
latexmk -xelatex -interaction=nonstopmode book.tex
cp book.pdf "哲学×AI探究集.pdf"
echo "OK -> 哲学×AI探究集.pdf"
