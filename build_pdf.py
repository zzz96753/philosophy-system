#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把具身智能面试题库的 Markdown 合并转换为一本 LaTeX 书并编译成 PDF。"""
import re, os

BASE = "面试准备/具身智能大模型"
FILES = [
    "00-题库总览.md",
    "逐题精讲/01-基础概念.md",
    "逐题精讲/02-多模态基础.md",
    "逐题精讲/03-VLA模型.md",
    "逐题精讲/04-模仿学习与策略.md",
    "逐题精讲/05-强化学习.md",
    "逐题精讲/06-世界模型.md",
    "逐题精讲/07-数据与仿真.md",
    "逐题精讲/08-感知与3D.md",
    "逐题精讲/09-规划控制系统.md",
    "逐题精讲/10-经典论文SOTA.md",
    "逐题精讲/11-工程部署.md",
    "逐题精讲/12-开放题与项目面.md",
    "深度补充/A-数学基础速查.md",
    "深度补充/B-核心算法代码.md",
]

# ---- 文本段中的符号 -> LaTeX（math 与 code 段不走这里）----
SYM = {
    '→': r'$\rightarrow$', '←': r'$\leftarrow$', '↑': r'$\uparrow$', '↓': r'$\downarrow$',
    '⇒': r'$\Rightarrow$', '×': r'$\times$', '≤': r'$\le$', '≥': r'$\ge$',
    '≈': r'$\approx$', '≠': r'$\ne$', '∼': r'$\sim$', '∇': r'$\nabla$',
    '∑': r'$\sum$', '∏': r'$\prod$', '∈': r'$\in$', '∞': r'$\infty$',
    '⊙': r'$\odot$', '‖': r'$\Vert$', '²': r'$^2$', '³': r'$^3$',
    'ε': r'$\varepsilon$', 'α': r'$\alpha$', 'β': r'$\beta$', 'γ': r'$\gamma$',
    'δ': r'$\delta$', 'θ': r'$\theta$', 'λ': r'$\lambda$', 'μ': r'$\mu$',
    'σ': r'$\sigma$', 'τ': r'$\tau$', 'ω': r'$\omega$', 'π': r'$\pi$',
    'φ': r'$\phi$', 'Δ': r'$\Delta$', 'γ': r'$\gamma$',
    '★': r' \starf ', '☆': r' \staro ', '◆': r' \diaf ',
}
# 装饰性 emoji / 符号 -> 去除
EMOJI = ['🔥','🎯','📌','📐','📊','💻','💡','⚙️','🤖','🧩','🚀','🎓','🌍','🧊','🏗️',
         '📑','📱','🛒','🧮','💰','✅','⚠️','🎉','💼','🦾','🤔','📈','🌟','💪','👀',
         '🦖','🧘','🔍','🧠','🦉','✨','📝','➕','🔬','👇','🌐','⭐','️','　']

def strip_emoji(s):
    for e in EMOJI:
        s = s.replace(e, '')
    return s

def allowed(ch):
    o = ord(ch)
    if ch in '\n\t': return True
    if 0x20 <= o <= 0x7E: return True
    if 0x4E00 <= o <= 0x9FFF: return True
    if 0x3400 <= o <= 0x4DBF: return True
    if 0x3000 <= o <= 0x303F: return True
    if 0xFF00 <= o <= 0xFFEF: return True
    if 0x2018 <= o <= 0x201F: return True
    if o in (0x2014, 0x2026, 0x00B7, 0x00B0, 0x00D7): return True
    return False

def final_strip(s):
    return ''.join(c for c in s if allowed(c))

def esc(s):
    """转义普通文本中的 LaTeX 特殊字符。"""
    s = s.replace('\\', r'\textbackslash{}')
    for a, b in [('&', r'\&'), ('%', r'\%'), ('#', r'\#'), ('_', r'\_'),
                 ('{', r'\{'), ('}', r'\}'), ('~', r'\textasciitilde{}'),
                 ('^', r'\textasciicircum{}'), ('$', r'\$')]:
        s = s.replace(a, b)
    return s

def inline(text):
    """处理一段行内文本：保护 math/code，处理 bold，转义，符号替换。"""
    text = strip_emoji(text)
    maths, codes = [], []
    # 保护行内 math $...$
    def keep_math(m):
        maths.append(m.group(1)); return f'\x00M{len(maths)-1}\x00'
    text = re.sub(r'\$([^$]+)\$', keep_math, text)
    # 保护行内 code `...`
    def keep_code(m):
        codes.append(m.group(1)); return f'\x00C{len(codes)-1}\x00'
    text = re.sub(r'`([^`]+)`', keep_code, text)
    # 加粗 **...**
    text = re.sub(r'\*\*(.+?)\*\*', '\x01\\1\x02', text)
    # 转义特殊字符
    text = esc(text)
    # 符号替换
    for k, v in SYM.items():
        text = text.replace(k, v)
    # 还原加粗标记
    text = text.replace('\x01', r'\textbf{').replace('\x02', '}')
    # 还原 math（原样）
    for i, m in enumerate(maths):
        text = text.replace(f'\x00M{i}\x00', f'${m}$')
    # 还原 code（转义后 \texttt）
    for i, c in enumerate(codes):
        text = text.replace(f'\x00C{i}\x00', r'\texttt{' + esc(c) + '}')
    return final_strip(text)

# ---- 代码块符号清洗 ----
BOX = {'─':'-','━':'-','│':'|','┃':'|','┌':'+','┐':'+','└':'+','┘':'+','├':'+',
       '┤':'+','┬':'+','┴':'+','┼':'+','╔':'+','╗':'+','╚':'+','╝':'+','║':'|',
       '═':'=','▶':'>','◀':'<','•':'*','◦':'-','·':'.'}
CODE_SYM = {'→':'->','←':'<-','↑':'^','↓':'v','⇒':'=>','×':'x','≤':'<=','≥':'>=',
            'π':'pi','ε':'eps','α':'alpha','β':'beta','θ':'theta','μ':'mu','σ':'sigma',
            'τ':'tau','λ':'lambda','γ':'gamma','δ':'delta','ω':'omega','φ':'phi',
            'Δ':'D','√':'sqrt','⊙':'*'}
def clean_code(s):
    s = strip_emoji(s)
    for k, v in {**BOX, **CODE_SYM}.items():
        s = s.replace(k, v)
    return final_strip(s)

def table(rows):
    """rows: list of cell-lists（已去掉分隔行）。"""
    n = max(len(r) for r in rows)
    out = [r'\begin{center}\small', r'\begin{tabularx}{\linewidth}{|' + 'X|'*n + '}', r'\hline']
    for ri, r in enumerate(rows):
        cells = [inline(c.strip()) for c in r] + ['']*(n-len(r))
        out.append(' & '.join(cells) + r' \\ \hline')
        if ri == 0:
            pass
    out += [r'\end{tabularx}', r'\end{center}', '']
    return out

def convert(md, first_title=False):
    lines = md.split('\n')
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        # 代码围栏
        if ln.lstrip().startswith('```'):
            lang = ln.lstrip()[3:].strip().lower()
            i += 1
            buf = []
            while i < len(lines) and not lines[i].lstrip().startswith('```'):
                buf.append(clean_code(lines[i])); i += 1
            i += 1  # 跳过结束 ```
            style = 'pystyle' if lang in ('python','py') else 'plainstyle'
            out.append(r'\begin{lstlisting}[style=' + style + ']')
            out += buf
            out.append(r'\end{lstlisting}')
            continue
        # 块级 display math $$...$$
        st = ln.strip()
        if st.startswith('$$'):
            body = st[2:]
            if body.endswith('$$') and len(body) >= 2:   # 单行 $$...$$
                out.append(r'\[' + body[:-2] + r'\]'); i += 1; continue
            buf = [body]; i += 1                          # 多行
            while i < len(lines) and not lines[i].strip().endswith('$$'):
                buf.append(lines[i]); i += 1
            if i < len(lines):
                buf.append(lines[i].strip()[:-2]); i += 1
            out.append(r'\[' + ' '.join(buf) + r'\]'); continue
        # 表格
        if '|' in ln and i+1 < len(lines) and re.match(r'^\s*\|?[\s:|-]+\|[\s:|-]+$', lines[i+1]):
            block = []
            while i < len(lines) and '|' in lines[i]:
                block.append(lines[i]); i += 1
            rows = []
            for bi, b in enumerate(block):
                if bi == 1:  # 分隔行
                    continue
                cells = b.strip().strip('|').split('|')
                rows.append(cells)
            out += table(rows)
            continue
        # 标题
        m = re.match(r'^(#{1,4})\s+(.*)$', ln)
        if m:
            level = len(m.group(1)); title = inline(m.group(2).strip())
            if level == 1:
                cmd = r'\section'
            elif level == 2:
                cmd = r'\subsection'
            elif level == 3:
                cmd = r'\subsubsection'
            else:
                cmd = r'\paragraph'
            out.append(cmd + '{' + title + '}'); i += 1; continue
        # 分隔线
        if re.match(r'^\s*---+\s*$', ln) or re.match(r'^\s*===+\s*$', ln):
            out.append(r'\vspace{0.4em}\hrule\vspace{0.6em}'); i += 1; continue
        # 引用
        if ln.lstrip().startswith('> '):
            quote = []
            while i < len(lines) and lines[i].lstrip().startswith('>'):
                quote.append(lines[i].lstrip()[1:].lstrip()); i += 1
            out.append(r'\begin{quoting}')
            out.append(inline(' '.join(quote)))
            out.append(r'\end{quoting}'); continue
        # 列表
        if re.match(r'^\s*([-*]|\d+\.)\s+', ln):
            items = []
            ordered = bool(re.match(r'^\s*\d+\.', ln))
            while i < len(lines) and re.match(r'^\s*([-*]|\d+\.)\s+', lines[i]):
                raw = lines[i]
                indent = len(raw) - len(raw.lstrip())
                content = re.sub(r'^\s*([-*]|\d+\.)\s+', '', raw)
                cb = re.match(r'^\[([ xX])\]\s*(.*)$', content)
                if cb:
                    mark = r'$\boxtimes$' if cb.group(1).lower() == 'x' else r'$\square$'
                    items.append((indent, r'\item[' + mark + '] ' + inline(cb.group(2))))
                else:
                    items.append((indent, r'\item ' + inline(content)))
                i += 1
            env = 'enumerate' if ordered else 'itemize'
            out.append(r'\begin{' + env + r'}[leftmargin=1.4em,itemsep=1pt,topsep=2pt]')
            out += [it[1] for it in items]
            out.append(r'\end{' + env + '}')
            continue
        # 空行
        if ln.strip() == '':
            out.append(''); i += 1; continue
        # 普通段落
        out.append(inline(ln) + r'\par'); i += 1
    return '\n'.join(out)

# ---------- 组装 ----------
PRE = r"""\documentclass[UTF8,a4paper,11pt,fontset=none]{ctexart}
\usepackage{fontspec}
\setCJKmainfont[AutoFakeBold=3,AutoFakeSlant=0.2]{WenQuanYi Zen Hei}
\setCJKsansfont[AutoFakeBold=3]{WenQuanYi Zen Hei}
\setCJKmonofont{WenQuanYi Zen Hei}
\usepackage{amsmath,amssymb}
\usepackage[a4paper,margin=2.2cm]{geometry}
\usepackage{xcolor}
\definecolor{brand}{RGB}{30,90,180}
\definecolor{brandlt}{RGB}{235,242,252}
\definecolor{codebg}{RGB}{248,248,248}
\definecolor{kw}{RGB}{170,30,120}
\definecolor{cm}{RGB}{110,130,110}
\definecolor{st}{RGB}{30,120,60}
\usepackage{listings}
\usepackage{tabularx}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{fancyhdr}
\setlength{\headheight}{14pt}
\usepackage{quoting}
\usepackage[unicode,colorlinks,linkcolor=brand,urlcolor=brand]{hyperref}
\newcommand{\starf}{\textcolor{brand}{$\bigstar$}}
\newcommand{\staro}{\textcolor{brand}{$\star$}}
\newcommand{\diaf}{\textcolor{brand}{$\blacklozenge$}}
\lstdefinestyle{pystyle}{language=Python,basicstyle=\ttfamily\footnotesize,
  keywordstyle=\color{kw}\bfseries,commentstyle=\color{cm}\itshape,
  stringstyle=\color{st},showstringspaces=false,breaklines=true,
  columns=fullflexible,keepspaces=true,frame=single,rulecolor=\color{gray!40},
  backgroundcolor=\color{codebg},numbers=none,extendedchars=true}
\lstdefinestyle{plainstyle}{basicstyle=\ttfamily\footnotesize,breaklines=true,
  columns=fullflexible,keepspaces=true,frame=single,rulecolor=\color{gray!40},
  backgroundcolor=\color{codebg},extendedchars=true}
\titleformat{\section}{\Large\bfseries\color{brand}}{}{0em}{}[\vspace{2pt}\hrule]
\titleformat{\subsection}{\large\bfseries\color{brand!85!black}}{}{0em}{}
\titleformat{\subsubsection}{\normalsize\bfseries}{}{0em}{}
\setlength{\parindent}{0pt}\setlength{\parskip}{4pt}
\emergencystretch=3em
\hyphenpenalty=1000\sloppy
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small\color{brand}具身智能大模型 · 面试题库}
\fancyhead[R]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\begin{document}
\begin{titlepage}\centering
\vspace*{2.5cm}
{\Huge\bfseries\color{brand} 具身智能大模型\\[6pt] 面试题库与精讲}\\[1.2cm]
{\Large Embodied AI \& VLA Interview Handbook}\\[2cm]
{\large 12 大模块 \quad 78 道高频题 \quad 数理推导 + PyTorch 代码}\\[0.6cm]
{\large 从基础概念到 SOTA（RT / OpenVLA / $\pi_0$ / RDT）}\\[3cm]
{\large 整理：\underline{\hspace{4cm}}}\\[0.4cm]
{\large 版本 v1.0}\\
\vfill
{\small 本资料为学习整理，仅供个人备考使用。}
\end{titlepage}
\tableofcontents
\newpage
"""
POST = r"\end{document}"

parts = [PRE]
for f in FILES:
    p = os.path.join(BASE, f)
    md = open(p, encoding='utf-8').read()
    parts.append('% ===== ' + f + ' =====')
    parts.append(convert(md))
    parts.append(r'\clearpage')
parts.append(POST)

os.makedirs('build', exist_ok=True)
open('build/handbook.tex', 'w', encoding='utf-8').write('\n'.join(parts))
print("生成 build/handbook.tex，长度", len('\n'.join(parts)), "字符")
