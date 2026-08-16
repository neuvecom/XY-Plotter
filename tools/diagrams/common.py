#!/usr/bin/env python3
"""SVG 線画を組み立てるための共通パーツ。

docs-dev/manual/images/*.svg はすべてこのモジュールを使って生成しています。
手で SVG を書かずスクリプト化しているのは、16 ステップ分のスタイルを揃えるためと、
寸法をファームウェアの定数から直接引いて図に反映させるためです。
"""

# ---- 配色（明背景前提。GitHub のダークテーマでも白地の図として読める） ----
BG = "#ffffff"
INK = "#1f2328"          # 主線・文字
INK_SUB = "#6a737d"      # 補助線・注記
METAL = "#d7dde5"        # 板金・ネジ
METAL_DK = "#9aa5b1"
PCB = "#1f5fa9"          # 基板
PCB_DK = "#14406f"
PLASTIC = "#3a3f45"      # 樹脂・アクリル
ACCENT = "#c9372c"       # 注目させたい箇所
ACCENT2 = "#1a7f37"      # 補足（OK 表示など）
BRASS = "#b08d57"        # バネ

FONT = ("system-ui,-apple-system,'Hiragino Sans','Noto Sans JP',"
        "'Noto Sans CJK JP','Yu Gothic','Meiryo',sans-serif")
FONT_MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Svg:
    """必要な図形だけを持つ最小の SVG ビルダ。"""

    def __init__(self, width, height, title=""):
        self.w = width
        self.h = height
        self.title = title
        self.parts = []
        self._defs = []
        self._arrow_done = False

    # ---- 基本図形 ----
    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=1.6, rx=0, opacity=None, dash=None):
        o = f' opacity="{opacity}"' if opacity is not None else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{o}{d}/>')
        return self

    def circle(self, cx, cy, r, fill="none", stroke=INK, sw=1.6, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')
        return self

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1.6, dash=None, cap="round"):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}"{d}/>')
        return self

    def path(self, d, fill="none", stroke=INK, sw=1.6, dash=None, cap="round", join="round"):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linecap="{cap}" stroke-linejoin="{join}"{da}/>')
        return self

    def poly(self, pts, fill="none", stroke=INK, sw=1.6):
        s = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.parts.append(
            f'<polygon points="{s}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linejoin="round"/>')
        return self

    def text(self, x, y, s, size=13, fill=INK, anchor="start", weight="400",
             mono=False, italic=False):
        f = FONT_MONO if mono else FONT
        st = ' font-style="italic"' if italic else ""
        self.parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="{f}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}"{st}>{esc(s)}</text>')
        return self

    # ---- 引き出し線つきの注記 ----
    def _arrow_def(self):
        if self._arrow_done:
            return
        self._arrow_done = True
        self._defs.append(
            f'<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{ACCENT}"/></marker>')

    def callout(self, x1, y1, x2, y2, label, size=12, anchor="start", color=ACCENT, dy=-5):
        """(x1,y1) の部位から (x2,y2) へ引き出してラベルを置く。"""
        self._arrow_def()
        self.parts.append(
            f'<path d="M{x2:.1f},{y2:.1f} L{x1:.1f},{y1:.1f}" fill="none" stroke="{color}" '
            f'stroke-width="1.3" marker-end="url(#ah)"/>')
        self.text(x2, y2 + dy, label, size=size, fill=color, anchor=anchor, weight="600")
        return self

    def dim(self, x1, y1, x2, y2, label, size=11, offset=0):
        """寸法線（両端に短い直交線）。水平・垂直のみ想定。"""
        self.line(x1, y1, x2, y2, stroke=INK_SUB, sw=1.0)
        if abs(y2 - y1) < 0.5:      # 水平
            for x in (x1, x2):
                self.line(x, y1 - 4, x, y1 + 4, stroke=INK_SUB, sw=1.0)
            self.text((x1 + x2) / 2, y1 - 6 + offset, label, size=size,
                      fill=INK_SUB, anchor="middle")
        else:                        # 垂直
            for y in (y1, y2):
                self.line(x1 - 4, y, x1 + 4, y, stroke=INK_SUB, sw=1.0)
            self.text(x1 + 7 + offset, (y1 + y2) / 2 + 4, label, size=size, fill=INK_SUB)
        return self

    # ---- 出力 ----
    def render(self):
        defs = f"<defs>{''.join(self._defs)}</defs>" if self._defs else ""
        t = f"<title>{esc(self.title)}</title>" if self.title else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w}" height="{self.h}" role="img">{t}{defs}'
            f'<rect width="{self.w}" height="{self.h}" fill="{BG}"/>'
            + "".join(self.parts) + "</svg>\n")

    def save(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(), encoding="utf-8")


# ============================================================
#  部品アイコン（部品カードで使う）
# ============================================================

def icon_bolt(svg, x, y, length_mm, head="cap"):
    """六角穴付きボルトを横から見た図。x,y は頭の左上。"""
    px = 3.1 * length_mm ** 0.72 + 10      # 長さを緩やかに反映
    hw, hh = 11, 13                         # 頭の寸法
    svg.rect(x, y, hw, hh, fill=METAL, sw=1.4, rx=1.5)
    svg.circle(x + hw / 2, y + hh / 2, 3.2, fill=METAL_DK, sw=1.0)  # 六角穴
    sy = y + hh / 2 - 3.5
    svg.rect(x + hw, sy, px, 7, fill=METAL, sw=1.4)
    n = max(3, int(px / 5))
    for i in range(n):                      # ねじ山
        xx = x + hw + 3 + i * (px - 4) / n
        svg.line(xx, sy + 0.6, xx - 2.0, sy + 6.4, stroke=METAL_DK, sw=0.9)
    return px + hw


def icon_tapping(svg, x, y, length_mm):
    """なべ頭タッピングビス。"""
    px = 3.1 * length_mm ** 0.72 + 8
    svg.path(f"M{x},{y+11} a9,9 0 0 1 18,0 z", fill=METAL, sw=1.4)
    svg.line(x + 4, y + 5, x + 14, y + 5, stroke=METAL_DK, sw=1.3)   # ドライバ溝
    svg.path(f"M{x+18},{y+7} L{x+18+px},{y+9.5} L{x+18+px},{y+12.5} L{x+18},{y+15} z",
             fill=METAL, sw=1.4)
    return px + 18


def icon_nut(svg, cx, cy, r=10):
    """六角ナット（上から見た図）。"""
    import math
    pts = [(cx + r * math.cos(math.radians(60 * i - 90)),
            cy + r * math.sin(math.radians(60 * i - 90))) for i in range(6)]
    svg.poly(pts, fill=METAL, sw=1.4)
    svg.circle(cx, cy, r * 0.46, fill=BG, sw=1.2)
    return r * 2


def icon_washer(svg, cx, cy, r=9, fill=METAL):
    svg.circle(cx, cy, r, fill=fill, sw=1.4)
    svg.circle(cx, cy, r * 0.42, fill=BG, sw=1.2)
    return r * 2


def icon_spacer(svg, x, y, h=22, w=13):
    """円筒スペーサ（横から見た図）。"""
    svg.rect(x, y, w, h, fill=METAL_DK, sw=1.4, rx=2)
    svg.line(x + w / 2, y + 2, x + w / 2, y + h - 2, stroke=BG, sw=3.5)
    return w


def icon_bearing(svg, cx, cy, r=12):
    svg.circle(cx, cy, r, fill=METAL, sw=1.5)
    svg.circle(cx, cy, r * 0.72, fill=BG, sw=1.1)
    svg.circle(cx, cy, r * 0.52, fill=METAL_DK, sw=1.1)
    svg.circle(cx, cy, r * 0.28, fill=BG, sw=1.1)
    for i in range(8):                      # ボール
        import math
        a = math.radians(45 * i)
        svg.circle(cx + r * 0.62 * math.cos(a), cy + r * 0.62 * math.sin(a),
                   1.6, fill=METAL_DK, sw=0.6)
    return r * 2


def icon_spring(svg, x, y, w=46, h=18, coils=7):
    """引張バネ（両端に掛け輪）。"""
    svg.circle(x + 4, y + h / 2, 4.2, sw=1.5, stroke=BRASS)
    d = [f"M{x+8},{y+h/2}"]
    step = (w - 16) / coils
    for i in range(coils):
        xx = x + 8 + i * step
        d.append(f"L{xx+step*0.5:.1f},{y+1:.1f} L{xx+step:.1f},{y+h-1:.1f}")
    d.append(f"L{x+w-8:.1f},{y+h/2:.1f}")
    svg.path(" ".join(d), stroke=BRASS, sw=2.0)
    svg.circle(x + w - 4, y + h / 2, 4.2, sw=1.5, stroke=BRASS)
    return w


def icon_servo(svg, x, y, w=46, h=30, label="MG90S"):
    """マイクロサーボ（横から見た図）。出力軸は左上。"""
    svg.rect(x, y + 6, w, h, fill=PLASTIC, sw=1.5, rx=2)
    svg.rect(x + 2, y + 11, w - 4, 9, fill="#7a2f52", stroke="none", sw=0)   # ラベル帯
    svg.text(x + w / 2, y + 18.5, label, size=7.5, fill="#ffffff", anchor="middle",
             weight="700")
    svg.circle(x + 10, y + 6, 7.5, fill=METAL_DK, sw=1.4)                     # 出力軸
    svg.circle(x + 10, y + 6, 3.0, fill=METAL, sw=1.0)
    svg.rect(x - 6, y + 9, 6, 8, fill=PLASTIC, sw=1.2)                        # 取付耳
    svg.rect(x + w, y + 9, 6, 8, fill=PLASTIC, sw=1.2)
    for i, c in enumerate(("#d9760f", "#c0392b", "#8b4a10")):                 # 3 極ケーブル
        svg.path(f"M{x+w+6},{y+20+i*3.2} q14,2 22,{-6+i*3}", stroke=c, sw=2.0)
    return w + 12


def icon_board(svg, x, y, w, h, label="", pins_top=True):
    svg.rect(x, y, w, h, fill=PCB, sw=1.4, rx=2)
    if pins_top:
        n = max(4, int(w / 9))
        for i in range(n):
            svg.rect(x + 4 + i * (w - 8) / n, y + 2.5, 4, 4, fill="#e8c33a", sw=0.7)
    if label:
        svg.text(x + w / 2, y + h / 2 + 4, label, size=9, fill="#ffffff",
                 anchor="middle", weight="700")
    return w


def icon_plate(svg, x, y, w, h, fill=PLASTIC, holes=()):
    svg.rect(x, y, w, h, fill=fill, sw=1.5, rx=3)
    for hx, hy in holes:
        svg.circle(x + hx, y + hy, 3, fill=BG, sw=1.1)
    return w


def icon_bracket(svg, x, y, w=52, h=30):
    """コの字／L 字の板金ブラケット（簡略図）。"""
    svg.path(f"M{x},{y+h} L{x},{y+6} L{x+8},{y+6} L{x+8},{y+h-8} "
             f"L{x+w-8},{y+h-8} L{x+w-8},{y+6} L{x+w},{y+6} L{x+w},{y+h} z",
             fill=METAL, sw=1.5)
    return w


def icon_link(svg, x, y, w=64, kind="short"):
    """リンク板（両端に穴）。"""
    h = 12
    svg.path(f"M{x+h/2},{y} L{x+w-h/2},{y} a{h/2},{h/2} 0 0 1 0,{h} "
             f"L{x+h/2},{y+h} a{h/2},{h/2} 0 0 1 0,{-h} z", fill=METAL, sw=1.5)
    svg.circle(x + h / 2 + 1, y + h / 2, 3, fill=BG, sw=1.1)
    svg.circle(x + w - h / 2 - 1, y + h / 2, 3, fill=BG, sw=1.1)
    return w


def icon_hc06(svg, x, y, w=54, h=26):
    svg.rect(x, y, w, h, fill="#1f7a4d", sw=1.4, rx=2)
    svg.rect(x + 4, y + 4, 16, 10, fill="#c9a227", stroke="none", sw=0)   # アンテナ部
    svg.text(x + w / 2 + 6, y + h / 2 + 8, "HC-06", size=8, fill="#ffffff",
             anchor="middle", weight="700")
    for i in range(4):
        svg.rect(x + w - 22 + i * 5, y + h, 3, 6, fill=METAL_DK, sw=0.7)
    return w


def icon_wire(svg, x, y, w=54, color=ACCENT):
    svg.path(f"M{x},{y+12} q{w*0.3},-14 {w*0.5},0 q{w*0.2},14 {w*0.5},0",
             stroke=color, sw=2.2)
    svg.rect(x - 5, y + 8, 6, 9, fill=PLASTIC, sw=1.0)
    svg.rect(x + w - 1, y + 8, 6, 9, fill=PLASTIC, sw=1.0)
    return w + 10
