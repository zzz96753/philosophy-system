#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把具身智能面试题库的 Markdown 合并转换为一本 LaTeX 书并编译成 PDF（美化版）。"""
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

SYM = {
    '→': r'$\rightarrow$', '←': r'$\leftarrow$', '↑': r'$\uparrow$', '↓': r'$\downarrow$',
    '⇒': r'$\Rightarrow$', '×': r'$\times$', '≤': r'$\le$', '≥': r'$\ge$',
    '≈': r'$\approx$', '≠': r'$\ne$', '∼': r'$\sim$', '∇': r'$\nabla$',
    '∑': r'$\sum$', '∏': r'$\prod$', '∈': r'$\in$', '∞': r'$\infty$',
    '⊙': r'$\odot$', '‖': r'$\Vert$', '²': r'$^2$', '³': r'$^3$',
    'ε': r'$\varepsilon$', 'α': r'$\alpha$', 'β': r'$\beta$', 'γ': r'$\gamma$',
    'δ': r'$\delta$', 'θ': r'$\theta$', 'λ': r'$\lambda$', 'μ': r'$\mu$',
    'σ': r'$\sigma$', 'τ': r'$\tau$', 'ω': r'$\omega$', 'π': r'$\pi$',
    'φ': r'$\phi$', 'Δ': r'$\Delta$',
    '★': r'{\starf}', '☆': r'{\staro}', '◆': r'{\diaf}',
}
EMOJI = ['🔥','🎯','📌','📐','📊','💻','💡','⚙️','🤖','🧩','🚀','🎓','🌍','🧊','🏗️',
         '📑','📱','🛒','🧮','💰','✅','⚠️','🎉','💼','🦾','🤔','📈','🌟','💪','👀',
         '🦖','🧘','🔍','🧠','🦉','✨','📝','➕','🔬','👇','🌐','⭐','️','　','📕','📚','🎤','🏆']

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
    s = s.replace('\\', r'\textbackslash{}')
    for a, b in [('&', r'\&'), ('%', r'\%'), ('#', r'\#'), ('_', r'\_'),
                 ('{', r'\{'), ('}', r'\}'), ('~', r'\textasciitilde{}'),
                 ('^', r'\textasciicircum{}'), ('$', r'\$')]:
        s = s.replace(a, b)
    return s

def inline(text):
    text = strip_emoji(text)
    maths, codes = [], []
    def keep_math(m):
        maths.append(m.group(1)); return f'\x00M{len(maths)-1}\x00'
    text = re.sub(r'\$([^$]+)\$', keep_math, text)
    def keep_code(m):
        codes.append(m.group(1)); return f'\x00C{len(codes)-1}\x00'
    text = re.sub(r'`([^`]+)`', keep_code, text)
    text = re.sub(r'\*\*(.+?)\*\*', '\x01\\1\x02', text)
    text = esc(text)
    for k, v in SYM.items():
        text = text.replace(k, v)
    text = text.replace('\x01', r'\textbf{').replace('\x02', '}')
    for i, m in enumerate(maths):
        text = text.replace(f'\x00M{i}\x00', f'${m}$')
    for i, c in enumerate(codes):
        e = esc(c)
        if '/' in c:   # 路径等长 token：用可断行等宽体，避免溢出
            repl = r'\texttt{' + e.replace('/', r'/\allowbreak ') + '}'
        else:
            repl = r'\hlcode{' + e + '}'
        text = text.replace(f'\x00C{i}\x00', repl)
    return final_strip(text)

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
    n = max(len(r) for r in rows)
    out = [r'\begin{center}\footnotesize',
           r'\arrayrulecolor{gray!30}',
           r'\rowcolors{2}{white}{brandlt}',
           r'\renewcommand{\arraystretch}{1.35}',
           r'\begin{tabularx}{\linewidth}{' + '|' + 'X|'*n + '}', r'\hline']
    hdr = rows[0]
    hcells = [r'\textcolor{white}{\textbf{' + inline(c.strip()) + '}}' for c in hdr] + ['']*(n-len(hdr))
    out.append(r'\rowcolor{brand}' + ' & '.join(hcells) + r' \\ \hline')
    for r in rows[1:]:
        cells = [inline(c.strip()) for c in r] + ['']*(n-len(r))
        out.append(' & '.join(cells) + r' \\ \hline')
    out += [r'\end{tabularx}', r'\arrayrulecolor{black}', r'\end{center}', '']
    return out

def convert(md):
    lines = md.split('\n')
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if ln.lstrip().startswith('```'):
            lang = ln.lstrip()[3:].strip().lower()
            i += 1; buf = []
            while i < len(lines) and not lines[i].lstrip().startswith('```'):
                buf.append(clean_code(lines[i])); i += 1
            i += 1
            style = 'pystyle' if lang in ('python', 'py') else 'plainstyle'
            out.append(r'\begin{lstlisting}[style=' + style + ']'); out += buf
            out.append(r'\end{lstlisting}'); continue
        st = ln.strip()
        if st.startswith('$$'):
            body = st[2:]
            if body.endswith('$$') and len(body) >= 2:
                out.append(r'\[' + body[:-2] + r'\]'); i += 1; continue
            buf = [body]; i += 1
            while i < len(lines) and not lines[i].strip().endswith('$$'):
                buf.append(lines[i]); i += 1
            if i < len(lines):
                buf.append(lines[i].strip()[:-2]); i += 1
            out.append(r'\[' + ' '.join(buf) + r'\]'); continue
        if '|' in ln and i+1 < len(lines) and re.match(r'^\s*\|?[\s:|-]+\|[\s:|-]+$', lines[i+1]):
            block = []
            while i < len(lines) and '|' in lines[i]:
                block.append(lines[i]); i += 1
            rows = []
            for bi, b in enumerate(block):
                if bi == 1: continue
                rows.append(b.strip().strip('|').split('|'))
            out += table(rows); continue
        m = re.match(r'^(#{1,4})\s+(.*)$', ln)
        if m:
            level = len(m.group(1)); title = inline(m.group(2).strip())
            cmd = {1: r'\section', 2: r'\subsection', 3: r'\subsubsection'}.get(level, r'\paragraph')
            out.append(cmd + '{' + title + '}'); i += 1; continue
        if re.match(r'^\s*---+\s*$', ln) or re.match(r'^\s*===+\s*$', ln):
            out.append(r'\smallskip{\color{gray!30}\hrule}\smallskip'); i += 1; continue
        if ln.lstrip().startswith('> '):
            quote = []
            while i < len(lines) and lines[i].lstrip().startswith('>'):
                quote.append(lines[i].lstrip()[1:].lstrip()); i += 1
            out.append(r'\begin{quotebox}'); out.append(inline(' '.join(quote)))
            out.append(r'\end{quotebox}'); continue
        if re.match(r'^\s*([-*]|\d+\.)\s+', ln):
            items = []; ordered = bool(re.match(r'^\s*\d+\.', ln)); allcheck = True
            while i < len(lines) and re.match(r'^\s*([-*]|\d+\.)\s+', lines[i]):
                content = re.sub(r'^\s*([-*]|\d+\.)\s+', '', lines[i])
                cb = re.match(r'^\[([ xX])\]\s*(.*)$', content)
                if cb:
                    mark = r'$\boxtimes$' if cb.group(1).lower() == 'x' else r'\sq'
                    items.append(r'\item[' + mark + '] ' + inline(cb.group(2)))
                else:
                    allcheck = False; items.append(r'\item ' + inline(content))
                i += 1
            if allcheck and not ordered:
                out.append(r'\begin{selfcheck}')
                out.append(r'\begin{itemize}[leftmargin=1.6em,itemsep=2pt,topsep=1pt,label={}]')
                out += items; out.append(r'\end{itemize}'); out.append(r'\end{selfcheck}')
            else:
                env = 'enumerate' if ordered else 'itemize'
                out.append(r'\begin{' + env + r'}[leftmargin=1.5em,itemsep=1pt,topsep=2pt]')
                out += items; out.append(r'\end{' + env + '}')
            continue
        if ln.strip() == '':
            out.append(''); i += 1; continue
        out.append(inline(ln) + r'\par'); i += 1
    return '\n'.join(out)

PRE = r"""\PassOptionsToPackage{table,dvipsnames}{xcolor}
\documentclass[UTF8,a4paper,11pt,fontset=none]{ctexart}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage{amsmath,amssymb}
\usepackage[a4paper,margin=2.3cm,headsep=10pt]{geometry}
\usepackage{tabularx}
\usepackage{colortbl}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{listings}
\usepackage[most]{tcolorbox}
\usepackage{tikz}
\usepackage{needspace}
\usepackage[unicode,colorlinks,linkcolor=brand,urlcolor=accent]{hyperref}

% ---------- 字体 ----------
\setCJKmainfont{Noto Serif CJK SC}
\newCJKfontfamily\cjksans{Noto Sans CJK SC}
\setCJKmonofont{Noto Sans Mono CJK SC}
\newfontfamily\codefont{Noto Sans Mono CJK SC}

% ---------- 配色 ----------
\definecolor{brand}{RGB}{34,71,123}
\definecolor{brandlt}{RGB}{237,242,249}
\definecolor{accent}{RGB}{0,150,136}
\definecolor{accentlt}{RGB}{231,247,245}
\definecolor{codebg}{RGB}{248,249,251}
\definecolor{kw}{RGB}{170,30,120}
\definecolor{cm}{RGB}{120,135,120}
\definecolor{st}{RGB}{30,120,60}
\definecolor{inlbg}{RGB}{240,240,244}

% ---------- 标记 ----------
\newcommand{\starf}{\textcolor{brand}{$\bigstar$}}
\newcommand{\staro}{\textcolor{brand}{$\star$}}
\newcommand{\diaf}{\textcolor{accent}{$\blacklozenge$}}
\newcommand{\sq}{\textcolor{brand}{$\square$}}
\newcommand{\hlcode}[1]{\colorbox{inlbg}{\codefont\small #1}}

% ---------- 代码 ----------
\lstdefinestyle{pystyle}{language=Python,basicstyle=\codefont\scriptsize,
  keywordstyle=\color{kw}\bfseries,commentstyle=\color{cm}\itshape,
  stringstyle=\color{st},showstringspaces=false,breaklines=true,
  columns=fullflexible,keepspaces=true,frame=leftline,framerule=2pt,
  rulecolor=\color{accent},backgroundcolor=\color{codebg},
  xleftmargin=10pt,aboveskip=8pt,belowskip=8pt,extendedchars=true}
\lstdefinestyle{plainstyle}{basicstyle=\codefont\scriptsize,breaklines=true,
  columns=fullflexible,keepspaces=true,frame=leftline,framerule=2pt,
  rulecolor=\color{brand!50},backgroundcolor=\color{codebg},
  xleftmargin=10pt,aboveskip=8pt,belowskip=8pt,extendedchars=true}

% ---------- 标题样式 ----------
\titleformat{\section}
  {\cjksans\LARGE\bfseries\color{brand}}
  {\colorbox{brand}{\color{white}\cjksans\,\thesection\,}}{0.6em}{}
  [\vspace{1.5pt}{\color{accent}\titlerule[2pt]}]
\titleformat{\subsection}
  {\cjksans\large\bfseries\color{brand}}{}{0em}
  {\textcolor{accent}{\rule[-0.12em]{3.5pt}{1.15em}}\,}
\titleformat{\subsubsection}
  {\cjksans\normalsize\bfseries\color{brand!75!black}}{}{0em}{}
\titlespacing{\section}{0pt}{2.4ex}{1.4ex}
\titlespacing{\subsection}{0pt}{1.8ex}{0.8ex}

% ---------- 引用框 / 自测框 ----------
\newtcolorbox{quotebox}{enhanced,breakable,colback=accentlt,colframe=accent,
  boxrule=0pt,leftrule=3.5pt,arc=2pt,boxsep=3pt,left=8pt,right=7pt,top=5pt,bottom=5pt,
  fontupper=\itshape}
\newtcolorbox{selfcheck}{enhanced,breakable,colback=brandlt,colframe=brand!55,
  boxrule=0.6pt,arc=3pt,title={\cjksans\bfseries 自测清单},coltitle=white,
  colbacktitle=brand,attach boxed title to top left={xshift=8pt,yshift=-2pt},
  boxed title style={arc=2pt,boxrule=0pt},left=8pt,right=7pt,top=8pt,bottom=6pt}

% ---------- 页眉页脚 ----------
\setlength{\headheight}{15pt}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small\cjksans\color{brand}具身智能大模型 · 面试题库与精讲}
\fancyhead[R]{\small\cjksans\color{brand}\thepage}
\renewcommand{\headrulewidth}{0.6pt}
\renewcommand{\footrulewidth}{0pt}
\setlength{\parindent}{0pt}\setlength{\parskip}{4pt}
\emergencystretch=3em\hyphenpenalty=1000\sloppy
\renewcommand{\arraystretch}{1.2}

\begin{document}
% ================= 封面 =================
\begin{titlepage}\thispagestyle{empty}
\begin{tikzpicture}[remember picture,overlay]
  \fill[brand] ([yshift=-5cm]current page.north west) rectangle (current page.north east);
  \fill[accent] ([yshift=-5cm]current page.north west) rectangle ([yshift=-5.18cm]current page.north east);
  \fill[brand] (current page.south west) rectangle ([yshift=1.4cm]current page.south east);
  % 主标题（band 内）
  \node[anchor=north,text=white,align=center,inner sep=0pt]
     at ([yshift=-1.35cm]current page.north)
     {\cjksans\bfseries\fontsize{38}{44}\selectfont 具身智能大模型\\[8pt]
      \fontsize{26}{30}\selectfont 面试题库与精讲};
  % 英文副标题（band 下方）
  \node[anchor=north,text=brand,align=center]
     at ([yshift=-6.3cm]current page.north)
     {\itshape\Large Embodied AI \& VLA Interview Handbook};
  % 卖点框（页面中部）
  \node[anchor=center,align=center,text width=0.76\paperwidth,
        fill=brandlt,draw=brand,line width=1pt,rounded corners=5pt,inner sep=14pt]
     at ([yshift=0.6cm]current page.center)
     {\cjksans\large 12 大模块 \quad\textbullet\quad 78 道高频题 \quad\textbullet\quad
      数理推导 $+$ PyTorch 代码\\[8pt]
      从基础概念到 SOTA（RT / OpenVLA / $\pi_0$ / RDT）};
  % 署名与版本
  \node[anchor=south,align=center]
     at ([yshift=3.0cm]current page.south)
     {\large\cjksans 整理：\underline{\hspace{4.5cm}}\\[12pt]
      \large\cjksans\bfseries\color{brand} 版本 v1.1};
  % 底部 band 文字
  \node[anchor=south,text=white,align=center]
     at ([yshift=0.45cm]current page.south)
     {\cjksans\small 学习整理 · 仅供个人备考使用};
\end{tikzpicture}
\end{titlepage}

% ================= 目录 =================
\thispagestyle{fancy}
{\cjksans\bfseries\Large\color{brand} 目\quad 录}\par\vspace{0.4em}
{\color{accent}\hrule height 1.5pt}\vspace{1em}
\makeatletter
\renewcommand{\l@section}[2]{\vskip4pt{\cjksans\bfseries\color{brand}#1\hfill#2}\par}
\renewcommand{\l@subsection}[2]{\small\hspace{1.4em}#1\dotfill#2\par}
\makeatother
\@starttoc{toc}
\clearpage
"""
POST = r"\end{document}"

parts = [PRE]
for f in FILES:
    md = open(os.path.join(BASE, f), encoding='utf-8').read()
    parts.append('% ===== ' + f + ' =====')
    parts.append(convert(md))
    parts.append(r'\clearpage')
parts.append(POST)

os.makedirs('build', exist_ok=True)
open('build/handbook.tex', 'w', encoding='utf-8').write('\n'.join(parts))
print("生成 build/handbook.tex，长度", len('\n'.join(parts)), "字符")
