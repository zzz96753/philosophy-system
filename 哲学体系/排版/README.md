# 排版（LaTeX → PDF）

把知识库中的文章排成专业 PDF。引擎 **XeLaTeX**，文档类 `ctexart`。

## 字体依赖

正文统一使用 **霞鹜文楷 LXGW WenKai**（温润书卷气）；英文走 Latin Modern。
仓库不内置字体文件，需先安装：

```bash
# 系统中文支持（思源黑/宋体，作为对比与回退）
apt-get install -y texlive-xetex texlive-lang-chinese latexmk fonts-noto-cjk

# 霞鹜文楷（正文字体，从 GitHub Releases 下载）
mkdir -p /usr/share/fonts/truetype/lxgw && cd /usr/share/fonts/truetype/lxgw
for w in Light Regular Medium; do
  curl -sL -o LXGWWenKai-$w.ttf \
    "https://github.com/lxgw/LxgwWenKai/releases/latest/download/LXGWWenKai-$w.ttf"
done
fc-cache -f
```

## 编译

```bash
latexmk -xelatex story.tex       # 《哲学的故事》
latexmk -xelatex flagship.tex    # 《什么是思维》（依赖 img/tension-map.png）
latexmk -xelatex compare.tex          # 字体对比样张
xelatex tikz-tension-map.tex && cp tikz-tension-map.pdf img/tension-map.pdf  # 重绘张力图
```

## 文件

| 文件 | 说明 |
|------|------|
| `story.tex` | 《哲学的故事·一场跨越2500年的对话》源码 |
| `flagship.tex` | 旗舰范本《什么是思维（机器在思考吗）》源码 |
| `tikz-tension-map.tex` | 论辩张力地图源码（手绘 TikZ：一问题→四视角→一立场） |
| `img/tension-map.pdf` | 张力地图成品（由上面的 TikZ 编译，被 flagship 引用） |
| `compare.tex` | 三体（文楷/宋体/黑体）对比样张 |
| `*.pdf`（中文名） | 已编译成品 |

> 切换字体：改各 `.tex` 顶部"字体"区块的 `\setCJKmainfont` 即可（如换回 `Noto Sans CJK SC` 思源黑体 / `Noto Serif CJK SC` 思源宋体）。
