#!/usr/bin/env python3
"""機構図・座標系図・描画範囲図・配線図を生成する。

寸法はすべてファームウェアの定数（baselen=4.5 / arm1len=3.0 / arm2len=6.0 cm）
および tools/workspace_map.py の計算結果から引いているので、
図とドキュメント本文の数値がずれることはありません。
"""

import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from common import (ACCENT, ACCENT2, BG, BRASS, INK, INK_SUB, METAL, METAL_DK,
                    PCB, PLASTIC, Svg, icon_servo)
import workspace_map as wm


# ============================================================
#  1. 5 節リンクの機構図
# ============================================================
def linkage_geometry(out):
    s = Svg(760, 500, "5 節平行リンクの寸法")
    s.text(24, 34, "5 節平行リンク機構と寸法", size=18, weight="700")
    s.text(24, 56, "ファームウェアの baselen / arm1len / arm2len に対応する実寸",
           size=12, fill=INK_SUB)

    K = 42.0                      # 1 cm = 42 px
    ox, oy = 285.0, 360.0         # 肩 B の画面座標
    def P(xc, yc):
        return (ox + xc * K, oy - yc * K)

    base, a1, a2 = 4.5, 3.0, 6.0
    px, py = 2.25, 6.6            # 図示するペン先位置

    def elbow(sx, sy, tx, ty, sign):
        dx, dy = tx - sx, ty - sy
        d = math.hypot(dx, dy)
        a = (a1 * a1 - a2 * a2 + d * d) / (2 * d)
        h = math.sqrt(max(a1 * a1 - a * a, 0))
        mx, my = sx + a * dx / d, sy + a * dy / d
        return (mx + sign * h * dy / d, my - sign * h * dx / d)

    e1 = elbow(0, 0, px, py, +1)
    e2 = elbow(base, 0, px, py, -1)

    # 台座
    s.rect(ox - 70, oy + 12, base * K + 140, 12, fill=PLASTIC, sw=1.4, rx=3)

    # リンク（縁取り＋本体の 2 度描きで板厚を表現）
    segs = [((0, 0), e1), ((base, 0), e2), (e1, (px, py)), (e2, (px, py))]
    for (sx, sy), (ex, ey) in segs:
        x1, y1 = P(sx, sy); x2, y2 = P(ex, ey)
        s.line(x1, y1, x2, y2, stroke=METAL_DK, sw=11)
        s.line(x1, y1, x2, y2, stroke=METAL, sw=7)

    # 関節
    for pt in (P(*e1), P(*e2)):
        s.circle(pt[0], pt[1], 6.5, fill=BG, stroke=INK, sw=2.2)
        s.circle(pt[0], pt[1], 2.2, fill=INK, stroke="none", sw=0)
    for pt in (P(0, 0), P(base, 0)):
        s.circle(pt[0], pt[1], 7.5, fill=BG, stroke=ACCENT, sw=2.6)
        s.circle(pt[0], pt[1], 2.6, fill=ACCENT, stroke="none", sw=0)

    # ペン先
    tip = P(px, py)
    s.circle(tip[0], tip[1], 8, fill=BG, stroke=ACCENT2, sw=2.6)
    s.line(tip[0], tip[1], tip[0], tip[1] - 48, stroke=ACCENT2, sw=3)
    s.text(tip[0] + 13, tip[1] - 34, "ペン先", size=13, fill=ACCENT2, weight="700")

    # 肩のラベル（台座の下に置いて図と重ねない）
    for pt, name, pin in ((P(0, 0), "肩 B", "D10"), (P(base, 0), "肩 C", "D11")):
        s.line(pt[0], pt[1] + 10, pt[0], oy + 40, stroke=ACCENT, sw=1.0, dash="3 3")
        s.text(pt[0], oy + 56, name, size=13, anchor="middle", weight="700", fill=ACCENT)
        s.text(pt[0], oy + 72, pin, size=11, anchor="middle", fill=INK_SUB, mono=True)

    # 寸法
    s.dim(P(0, 0)[0], oy + 98, P(base, 0)[0], oy + 98, "肩間 baselen = 45 mm")

    m1 = ((P(0, 0)[0] + P(*e1)[0]) / 2, (P(0, 0)[1] + P(*e1)[1]) / 2)
    s.callout(m1[0], m1[1] + 6, 150, 300, "上腕 arm1len = 30 mm",
              color=INK_SUB, anchor="middle", size=12)
    m2 = ((P(*e1)[0] + tip[0]) / 2, (P(*e1)[1] + tip[1]) / 2)
    s.callout(m2[0] + 6, m2[1], 600, 210, "前腕 arm2len = 60 mm",
              color=INK_SUB, anchor="middle", size=12)

    s.text(24, 76, "※ 左右の上腕は内側を向いて交差する形になる", size=11, fill=INK_SUB)

    s.text(24, 480, "寸法は穴の中心間距離。実測とずれる場合は Drawing.ino の"
                    "同名の定数を書き換えて校正する。", size=11, fill=INK_SUB)
    s.save(out / "linkage-geometry.svg")


# ============================================================
#  2. 座標系
# ============================================================
def coordinate_system(out):
    s = Svg(760, 430, "座標系と原点")
    s.text(24, 34, "座標系と原点", size=18, weight="700")
    s.text(24, 56, "アプリが送る X / Y の意味（1 単位 = 0.2 mm）", size=12, fill=INK_SUB)

    K = 42.0
    ox, oy = 300.0, 350.0
    base = 4.5
    origin = (ox + 2.25 * K, oy - 3.0 * K)

    s.rect(ox - 70, oy + 8, base * K + 140, 14, fill=PLASTIC, sw=1.4, rx=3)
    for cx in (0, base):
        s.circle(ox + cx * K, oy, 7, fill=BG, stroke=INK, sw=2.2)
        s.circle(ox + cx * K, oy, 2.4, fill=INK, stroke="none", sw=0)
    s.text(ox, oy + 42, "肩 B", size=11, fill=INK_SUB, anchor="middle")
    s.text(ox + base * K, oy + 42, "肩 C", size=11, fill=INK_SUB, anchor="middle")
    s.line(ox, oy, ox + base * K, oy, stroke=INK_SUB, sw=1.2, dash="4 3")
    s.dim(ox, oy + 66, ox + base * K, oy + 66, "45 mm")

    s.line(ox + 2.25 * K, oy, ox + 2.25 * K, origin[1], stroke=INK_SUB, sw=1.2, dash="4 3")
    s.dim(ox + 2.25 * K, oy, ox + 2.25 * K, origin[1], "30 mm", offset=4)

    s._arrow_def()
    s.parts.append(f'<path d="M{origin[0]},{origin[1]} L{origin[0]+205},{origin[1]}" '
                   f'fill="none" stroke="{ACCENT}" stroke-width="2" marker-end="url(#ah)"/>')
    s.parts.append(f'<path d="M{origin[0]},{origin[1]} L{origin[0]},{origin[1]-190}" '
                   f'fill="none" stroke="{ACCENT}" stroke-width="2" marker-end="url(#ah)"/>')
    s.text(origin[0] + 214, origin[1] + 5, "+X", size=14, fill=ACCENT, weight="700")
    s.text(origin[0], origin[1] - 200, "+Y", size=14, fill=ACCENT, weight="700",
           anchor="middle")
    s.circle(origin[0], origin[1], 5.5, fill=ACCENT, stroke=BG, sw=1.6)
    s.text(origin[0] - 12, origin[1] - 8, "原点 (X=0, Y=0)", size=12, fill=ACCENT,
           weight="700", anchor="end")
    s.text(origin[0] - 12, origin[1] + 8, "起動時のサーボ姿勢", size=10.5, fill=INK_SUB,
           anchor="end")

    for u in (100, 200):
        s.line(origin[0] + u / 50 * K, origin[1] - 4, origin[0] + u / 50 * K,
               origin[1] + 4, stroke=ACCENT, sw=1.4)
        s.text(origin[0] + u / 50 * K, origin[1] + 20, f"{u}", size=10, fill=ACCENT,
               anchor="middle", mono=True)
        s.line(origin[0] - 4, origin[1] - u / 50 * K, origin[0] + 4,
               origin[1] - u / 50 * K, stroke=ACCENT, sw=1.4)
        s.text(origin[0] + 10, origin[1] - u / 50 * K + 4, f"{u}", size=10, fill=ACCENT,
               mono=True)

    bx, by = 500, 100
    s.rect(bx, by, 236, 112, fill="#f6f8fa", stroke=INK_SUB, sw=1.0, rx=6)
    s.text(bx + 14, by + 26, "ファームウェア内の換算", size=12, weight="700")
    s.text(bx + 14, by + 52, "selx = X / 50 + 2.25", size=11.5, mono=True)
    s.text(bx + 14, by + 72, "sely = Y / 50 + 3.0", size=11.5, mono=True)
    s.text(bx + 14, by + 96, "1 単位 = 1/50 cm = 0.2 mm", size=10.5, fill=INK_SUB)

    s.save(out / "coordinate-system.svg")


# ============================================================
#  3. 描画可能範囲（逆運動学から実際に計算）
# ============================================================
def workspace(out):
    s = Svg(760, 510, "描画可能範囲")
    s.text(24, 34, "描画可能範囲", size=18, weight="700")
    s.text(24, 56, "Drawing.ino の逆運動学とサーボ可動域 0〜180° から総当たりで算出",
           size=12, fill=INK_SUB)

    L, R, T, B = 96.0, 690.0, 100.0, 392.0
    xmin, xmax, ymin, ymax = -300, 300, -20, 300
    def SX(x): return L + (x - xmin) * (R - L) / (xmax - xmin)
    def SY(y): return B - (y - ymin) * (B - T) / (ymax - ymin)

    left, right = [], []
    for y in range(ymin, ymax + 1, 2):
        row = [x for x in range(xmin, xmax + 1, 2) if wm.reachable(x, y)]
        if row:
            left.append((SX(row[0]), SY(y)))
            right.append((SX(row[-1]), SY(y)))
    poly = left + right[::-1]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in poly) + " Z"
    s.path(d, fill="#d3ecd8", stroke=ACCENT2, sw=2.0)

    s.rect(SX(-240), SY(200), SX(240) - SX(-240), SY(20) - SY(200),
           fill="none", stroke=ACCENT, sw=2.0, dash="7 4")
    s.text(SX(0), SY(120), "実用域", size=13, fill=ACCENT, anchor="middle", weight="700")
    s.text(SX(0), SY(120) + 18, "X ±240 / Y 20〜200", size=11, fill=ACCENT, anchor="middle")
    s.text(SX(0), SY(120) + 34, "≒ 96 × 36 mm", size=11, fill=ACCENT, anchor="middle")

    s.line(SX(xmin), SY(0), SX(xmax), SY(0), stroke=INK_SUB, sw=1.0, dash="4 3")
    s.line(SX(0), SY(ymin), SX(0), SY(ymax), stroke=INK_SUB, sw=1.0, dash="4 3")
    for x in (-240, -120, 0, 120, 240):
        s.line(SX(x), B, SX(x), B + 5, stroke=INK, sw=1.2)
        s.text(SX(x), B + 20, str(x), size=10, anchor="middle", mono=True, fill=INK_SUB)
    for y in (0, 100, 200, 280):
        s.line(L - 5, SY(y), L, SY(y), stroke=INK, sw=1.2)
        s.text(L - 9, SY(y) + 4, str(y), size=10, anchor="end", mono=True, fill=INK_SUB)
    s.text((L + R) / 2, B + 42, "X（1 単位 = 0.2 mm）", size=12, anchor="middle", fill=INK_SUB)
    s.text(34, (T + B) / 2, "Y", size=12, fill=INK_SUB)

    s.rect(496, 104, 190, 62, fill="#ffffff", stroke=INK_SUB, sw=1.0, rx=5)
    s.rect(508, 116, 18, 12, fill="#d3ecd8", stroke=ACCENT2, sw=1.5)
    s.text(534, 126, "到達可能", size=11)
    s.rect(508, 138, 18, 12, fill="none", stroke=ACCENT, sw=1.5, dash="4 3")
    s.text(534, 148, "推奨の実用矩形", size=11)

    s.text(24, 466, "肩の並びはこの図の下側（Y = −150 相当）にあり、"
                    "上へ行くほど届く幅が狭くなる。", size=11, fill=INK_SUB)
    s.text(24, 486, "範囲外の座標を送るとファームウェアはペンを上げて何もしない"
                    "（エラーは返らず 'N' だけ返る）。", size=11, fill=INK_SUB)
    s.save(out / "workspace.svg")


# ============================================================
#  4. 配線図
# ============================================================
def wiring(out):
    s = Svg(800, 580, "配線図とピンアサイン")
    s.text(24, 34, "配線図・ピンアサイン", size=18, weight="700")
    s.text(24, 56, "サーボ A=D9 / B=D10 / C=D11、HC-06 は D0・D1（クロス接続）",
           size=12, fill=INK_SUB)

    # ---- 拡張シールド ----
    bx, by, bw, bh = 300, 96, 300, 224
    s.rect(bx, by, bw, bh, fill=PCB, sw=1.6, rx=4)
    s.text(bx + bw / 2, by + 24, "Arduino Nano + IO 拡張シールド", size=11,
           fill="#ffffff", anchor="middle", weight="700")
    s.rect(bx + 80, by + 40, 140, 68, fill="#173f6b", stroke="#0d2a48", sw=1.2, rx=3)
    s.text(bx + 150, by + 80, "Nano", size=13, fill="#ffffff", anchor="middle", weight="700")

    # 左辺の端子（5V / GND / D0 / D1）
    lpads = [("5V", 130, "#a06fd6"), ("GND", 156, "#c9a227"),
             ("D0 (RX)", 182, ACCENT), ("D1 (TX)", 208, "#5b3fa8")]
    for name, y, col in lpads:
        s.rect(bx + 4, y, 22, 16, fill="#c9b45f", stroke="#8a7420", sw=1.1, rx=2)
        s.text(bx + 32, y + 12, name, size=10, fill="#ffffff", mono=True)

    # サーボ端子（D9 / D10 / D11）
    sblocks = [("9", 372, ACCENT), ("10", 432, "#c07a1f"), ("11", 492, "#5b3fa8")]
    sb_y = 240
    for pin, x, col in sblocks:
        s.rect(x, sb_y, 30, 56, fill="#e8c33a", stroke="#8a7420", sw=1.2, rx=2)
        s.rect(x - 2, sb_y - 2, 34, 60, fill="none", stroke=col, sw=2.0, rx=3)
        s.text(x + 15, sb_y - 8, pin, size=12, fill="#ffffff", anchor="middle",
               weight="700", mono=True)
        for i, lb in enumerate(("S", "V", "G")):
            s.text(x + 15, sb_y + 15 + i * 17, lb, size=9.5, anchor="middle",
                   mono=True, fill="#6b5a1a", weight="700")

    # ---- HC-06 ----
    hx, hy, hw2, hh2 = 56, 130, 150, 96
    s.rect(hx, hy, hw2, hh2, fill="#1f7a4d", sw=1.5, rx=4)
    s.text(hx + hw2 / 2, hy + 34, "HC-06", size=14, fill="#ffffff", anchor="middle",
           weight="700")
    s.text(hx + hw2 / 2, hy + 54, "Bluetooth SPP", size=9.5, fill="#cfe9dc", anchor="middle")
    s.text(hx + hw2 / 2, hy + 70, "9600 bps / PIN 1234", size=9.5, fill="#cfe9dc",
           anchor="middle")

    hpins = [("VCC", 138, "#a06fd6", 240, 0),
             ("GND", 160, "#c9a227", 252, 0),
             ("TXD", 182, ACCENT, 264, 0),
             ("RXD", 204, "#5b3fa8", 276, 0)]
    for name, y, col, jog, _ in hpins:
        s.rect(hx + hw2, y, 14, 10, fill=METAL_DK, sw=0.9)
        s.text(hx + hw2 - 6, y + 9, name, size=9.5, anchor="end", mono=True,
               fill="#ffffff")

    # HC-06 → シールド左辺
    for (name, y, col, jog, _), (pname, py2, _c) in zip(hpins, lpads):
        s.path(f"M{hx+hw2+14},{y+5} L{jog},{y+5} L{jog},{py2+8} L{bx+4},{py2+8}",
               stroke=col, sw=2.2, fill="none")

    # ---- サーボ 3 個 ----
    servos = [("A", "ペン昇降", 9, 664, 108, ACCENT, 344, 630),
              ("B", "肩（servo1）", 10, 664, 216, "#c07a1f", 360, 642),
              ("C", "肩（servo2）", 11, 664, 324, "#5b3fa8", 376, 654)]
    for name, role, pin, sx, sy, col, lane, riser in servos:
        icon_servo(s, sx, sy, w=52, h=30, label="MG90S")
        s.text(sx + 26, sy - 8, f"サーボ {name}", size=12, anchor="middle",
               weight="700", fill=col)
        s.text(sx + 26, sy + 56, role, size=10, anchor="middle", fill=INK_SUB)
        bxx = [b for b in sblocks if b[0] == str(pin)][0][1] + 15
        s.path(f"M{bxx},{sb_y+56} L{bxx},{lane} L{riser},{lane} L{riser},{sy+21} "
               f"L{sx-8},{sy+21}", stroke=col, sw=2.2, fill="none")
        s.text(bxx + 6, lane - 6, f"D{pin}", size=10.5, mono=True, weight="700", fill=col)

    # ---- 注記 ----
    s.rect(24, 424, 752, 78, fill="#fff5f5", stroke=ACCENT, sw=1.2, rx=6)
    s.text(40, 450, "⚠ ファームウェア書き込み時は HC-06 の TXD / RXD を必ず抜く",
           size=13.5, weight="700", fill=ACCENT)
    s.text(40, 472, "D0 / D1 は USB 書き込みと同じハードウェアシリアル。"
                    "挿したままだと書き込みに失敗する。", size=11, fill=INK)
    s.text(40, 490, "TXD→D0 / RXD→D1 のクロス接続。同じ名前どうしを繋ぐと通信できない。",
           size=11, fill=INK)
    s.text(40, 528, "サーボの 3 極は S（信号・橙）/ V（+・赤）/ G（GND・茶）。"
                    "逆挿しするとサーボが発熱する。", size=11, fill=INK_SUB)

    s.save(out / "wiring.svg")


# ============================================================
#  5. ペン昇降機構
# ============================================================
def pen_lift(out):
    s = Svg(720, 470, "ペン昇降機構")
    s.text(24, 34, "ペン昇降機構（手順 ④⑤⑩）", size=18, weight="700")
    s.text(24, 56, "サーボは「持ち上げる」だけ。紙への押し付けはバネが担当する",
           size=12, fill=INK_SUB)
    s.text(24, 76, "※ 模式図。バネの掛け位置は個体差があるため実機で確認すること",
           size=10.5, fill=INK_SUB)

    PLATE_Y = 340
    s.rect(56, PLATE_Y, 600, 14, fill=PLASTIC, sw=1.4, rx=3)      # ベースプレート
    s.rect(80, PLATE_Y - 4, 210, 5, fill="#f4f4f2", stroke=INK_SUB, sw=1.0)  # 紙
    s.text(185, PLATE_Y + 34, "紙", size=11, fill=INK_SUB, anchor="middle")
    s.text(600, PLATE_Y + 34, "ベースプレート", size=11, fill=INK_SUB, anchor="middle")

    PX, PY = 372.0, 226.0            # 支点
    TIP_DN, TIP_UP = 258.0, 222.0    # ペン側リンク端の y（下げ / 上げ）
    LX = 165.0                       # ペン側リンク端の x

    # レバー（上げ位置＝破線）
    s.line(PX, PY, LX, TIP_UP, stroke=INK_SUB, sw=4, dash="7 5")
    # レバー（下げ位置＝実線）
    s.line(PX, PY, LX, TIP_DN, stroke=METAL_DK, sw=10)
    s.line(PX, PY, LX, TIP_DN, stroke=METAL, sw=6)
    # サーボ側の腕
    s.line(PX, PY, 436, PY - 12, stroke=METAL_DK, sw=9)
    s.line(PX, PY, 436, PY - 12, stroke=METAL, sw=5)

    # ペン（下げ位置＝実線 / 上げ位置＝破線）
    s.rect(LX - 12, TIP_UP, 24, 66, fill="none", stroke=INK_SUB, sw=1.2, dash="5 4", rx=3)
    s.poly([(LX - 12, TIP_UP + 66), (LX + 12, TIP_UP + 66), (LX, TIP_UP + 84)],
           fill="none", stroke=INK_SUB, sw=1.2)
    s.rect(LX - 12, TIP_DN, 24, 66, fill="#e8b93a", stroke=INK, sw=1.5, rx=3)
    s.poly([(LX - 12, TIP_DN + 66), (LX + 12, TIP_DN + 66), (LX, TIP_DN + 84)],
           fill="#c98a2a", sw=1.4)

    # 支点
    s.circle(PX, PY, 8, fill=BG, stroke=INK, sw=2.4)
    s.circle(PX, PY, 2.6, fill=INK, stroke="none", sw=0)
    s.callout(PX + 4, PY - 8, PX + 30, 140, "支点：M3×16 + M3×9 スペーサ", size=11.5)
    s.text(PX + 30, 156, "軽く回る程度に締める（固いと動かない）", size=10, fill=INK_SUB)

    # バネ（ペン側を下へ引く）
    sx = 262.0
    top, bot = 244.0, PLATE_Y - 4
    s.circle(sx, top, 4.4, stroke=BRASS, sw=1.6)
    d = [f"M{sx},{top+4}"]
    n = 8
    for i in range(n):
        yy = top + 10 + i * (bot - top - 20) / n
        d.append(f"L{sx + (10 if i % 2 == 0 else -10)},{yy:.1f}")
    d.append(f"L{sx},{bot-6}")
    s.path(" ".join(d), stroke=BRASS, sw=2.2)
    s.circle(sx, bot - 2, 4.4, stroke=BRASS, sw=1.6)
    s.callout(sx + 12, 300, sx + 50, 300, "引張バネ 5×0.4×6", size=11.5, color=BRASS)
    s.text(sx + 50, 316, "ペンを紙へ押し付ける力", size=10, fill=INK_SUB)

    # サーボ A
    icon_servo(s, 470, 172, w=54, h=32, label="MG90S")
    s.text(497, 164, "サーボ A（D9）", size=12, anchor="middle", weight="700", fill=ACCENT)
    s.line(436, PY - 12, 480, 178, stroke=METAL_DK, sw=3)          # ホーンとのリンク
    s.text(497, 246, "回すとペン側が持ち上がる", size=10, fill=INK_SUB, anchor="middle")

    # 凡例
    s.rect(56, 118, 210, 62, fill="#ffffff", stroke=INK_SUB, sw=1.0, rx=5)
    s.line(70, 138, 100, 138, stroke=METAL_DK, sw=6)
    s.text(110, 142, "ペン下げ（描画中）", size=11)
    s.line(70, 162, 100, 162, stroke=INK_SUB, sw=3, dash="7 5")
    s.text(110, 166, "ペン上げ（移動中）", size=11)

    # 角度表
    s.rect(430, 384, 262, 72, fill="#f6f8fa", stroke=INK_SUB, sw=1.0, rx=6)
    s.text(444, 406, "penupdown() の角度", size=12, weight="700")
    s.text(444, 426, "10° = ペン上げ（起動時）　110° = ペン下げ", size=10.5, mono=True)
    s.text(444, 444, "1° ずつ 3 ms 間隔 → 昇降に約 300 ms", size=10.5, fill=INK_SUB)

    s.save(out / "pen-lift.svg")


def main():
    out = pathlib.Path(__file__).resolve().parent.parent.parent / "docs-dev" / "manual" / "images"
    out.mkdir(parents=True, exist_ok=True)
    linkage_geometry(out)
    coordinate_system(out)
    workspace(out)
    wiring(out)
    pen_lift(out)
    for f in sorted(out.glob("*.svg")):
        print(f"  {f.relative_to(out.parent.parent.parent)}  ({f.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
