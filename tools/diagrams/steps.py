#!/usr/bin/env python3
"""組み立て 16 ステップの「使う部品」カードを SVG で生成する。

これは写真の代わりではなく、写真と併読するための部品早見表です。
部品の種類と数量は公式組立説明書の各ページから読み取ったもので、
配置や向きの詳細までは表現していません（そこは付属 PDF を参照）。
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from common import (ACCENT, BG, INK, INK_SUB, METAL, PLASTIC, Svg, icon_bearing,
                    icon_board, icon_bolt, icon_bracket, icon_hc06, icon_link,
                    icon_nut, icon_plate, icon_servo, icon_spacer, icon_spring,
                    icon_tapping, icon_washer, icon_wire)

CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯"

# (見出し, [部品...], 補足)
#   部品 = (種類, ラベル, 数量, 追加引数)
STEPS = [
    ("ベースプレートに Nano + 拡張シールドを載せる", [
        ("plate", "ベースプレート", 1, {}),
        ("board", "Nano + 拡張シールド", 1, {}),
        ("rail", "金属レール", 2, {}),
        ("bolt", "M3×8 ボルト", 8, {"mm": 8}),
        ("nut", "M3 ナット", 8, {}),
        ("pwasher", "M3×2 樹脂ワッシャ", 4, {}),
    ], "Nano の Mini-USB がシールドの DC ジャック側に来る向きで差し込む"),

    ("HC-06（Bluetooth）を取り付ける", [
        ("hc06", "HC-06", 1, {}),
        ("holder", "樹脂ホルダー", 1, {}),
        ("bolt", "M3×12 ボルト", 4, {"mm": 12}),
        ("nut", "M3 ナット", 4, {}),
    ], "4 ピンヘッダ（VCC/GND/TXD/RXD）が外側を向くように置く"),

    ("サーボ台座ブラケットを取り付ける", [
        ("bracket", "板金ブラケット（大）", 1, {}),
        ("bolt", "M3×8 ボルト", 2, {"mm": 8}),
        ("nut", "M3 ナット", 2, {}),
    ], "ナットはプレートの裏側で締める"),

    ("ペン昇降レバーを組む（バネ + 支点）", [
        ("bracket", "板金レバー（小）", 1, {}),
        ("spring", "引張バネ 5×0.4×6", 1, {}),
        ("washer", "M3×8 ワッシャ", 1, {}),
        ("bolt", "M3×6 ボルト", 1, {"mm": 6}),
        ("nut", "M3 ナット", 1, {}),
    ], "ボルトに「バネの輪 → ワッシャ」の順に通してから板金へ"),

    ("ペン昇降レバーをベースに取り付ける", [
        ("bolt", "M3×16 ボルト", 2, {"mm": 16}),
        ("spacer", "M3×9 樹脂スペーサ", 2, {}),
        ("nut", "M3 ナット", 2, {}),
    ], "レバーが軽く回る程度に締める。締めすぎると動かない"),

    ("肩サーボ 2 個をブラケットに固定する", [
        ("bracket", "サーボ用ブラケット", 1, {}),
        ("servo", "MG90S", 2, {}),
        ("bolt", "M2×8 ボルト", 4, {"mm": 8}),
        ("nut", "M2 ナット", 4, {}),
    ], "サーボホーンはまだ付けない（手順 ⑫ まで待つ）"),

    ("肘のベアリングを取り付ける", [
        ("bolt", "M3×12 ボルト", 1, {"mm": 12}),
        ("bearing", "M3×8 ベアリング", 2, {}),
        ("bolt", "M3×8 ボルト", 1, {"mm": 8}),
        ("nut", "M3 ナット", 2, {}),
    ], "内輪だけを締める。外輪が指でスルスル回ることを確認"),

    ("サーボブラケットをベースに固定する", [
        ("bolt", "M3×6 ボルト", 1, {"mm": 6}),
        ("washer", "M3×8 ワッシャ", 1, {}),
        ("nut", "M3 ナット", 1, {}),
    ], ""),

    ("反対側のブラケットを固定する", [
        ("bracket", "小型 L 字ブラケット", 1, {}),
        ("bolt", "M3×8 ボルト", 2, {"mm": 8}),
        ("nut", "M3 ナット", 2, {}),
    ], "これで肩サーボの土台が両側から支えられ剛性が出る"),

    ("ペン昇降用サーボ（3 個目）を取り付ける", [
        ("servo", "MG90S", 1, {}),
        ("bolt", "M2×8 ボルト", 2, {"mm": 8}),
        ("nut", "M2 ナット", 2, {}),
    ], "これが後の「サーボ A（D9 / ペン上下）」になる"),

    ("配線する", [
        ("wire", "サーボ延長ケーブル", 3, {}),
        ("wire", "ジャンパワイヤ", 4, {}),
    ], "A=D9 / B=D10 / C=D11、HC-06 は TXD→D0・RXD→D1（クロス）"),

    ("通電して原点を出し、サーボホーンを取り付ける", [
        ("horn", "サーボホーン", 3, {}),
        ("tapping", "ホーン固定ビス", 3, {"mm": 6}),
    ], "★先にファームウェアを書き込むこと。サーボ静止後にホーンを水平で差す"),

    ("上腕リンクをホーンに取り付ける", [
        ("link", "短いリンク板", 2, {"w": 58}),
        ("tapping", "M2.5×6 タッピングビス", 2, {"mm": 6}),
    ], "左右のリンクが同じ向き（水平）に揃っていることを確認"),

    ("前腕リンクを 2 本つなぐ", [
        ("link", "長いリンク板", 2, {"w": 84}),
        ("bolt", "M3×8 ボルト", 1, {"mm": 8}),
        ("nut", "M3 ナット", 1, {}),
    ], "V 字に自由に開閉できる程度に締める。固いとペンが動かない"),

    ("ペンホルダーを取り付ける", [
        ("holder", "ペンホルダーブロック", 1, {}),
        ("bolt", "M3×10 ボルト", 2, {"mm": 10}),
        ("nut", "M3 ナット", 2, {}),
    ], ""),

    ("アームを本体に接続して完成", [
        ("bolt", "M3×12 ボルト", 1, {"mm": 12}),
        ("bolt", "M3×10 ボルト", 1, {"mm": 10}),
        ("nut", "M3 ナット", 2, {}),
        ("pwasher", "M3×2 樹脂ワッシャ", 1, {}),
    ], "全関節が抵抗なく回ることを手で確認する"),
]


def draw_part(s, kind, cx, cy, args):
    """セル中心 (cx, cy) に部品アイコンを描く。"""
    if kind == "bolt":
        w = 3.1 * args["mm"] ** 0.72 + 21
        icon_bolt(s, cx - w / 2, cy - 7, args["mm"])
    elif kind == "tapping":
        w = 3.1 * args["mm"] ** 0.72 + 26
        icon_tapping(s, cx - w / 2, cy - 8, args["mm"])
    elif kind == "nut":
        icon_nut(s, cx, cy, 11)
    elif kind == "washer":
        icon_washer(s, cx, cy, 10)
    elif kind == "pwasher":
        icon_washer(s, cx, cy, 9, fill=PLASTIC)
    elif kind == "spacer":
        icon_spacer(s, cx - 7, cy - 12, h=24, w=14)
    elif kind == "bearing":
        icon_bearing(s, cx, cy, 13)
    elif kind == "spring":
        icon_spring(s, cx - 26, cy - 9, w=52)
    elif kind == "servo":
        icon_servo(s, cx - 30, cy - 20, w=48, h=28)
    elif kind == "bracket":
        icon_bracket(s, cx - 26, cy - 15, w=52, h=30)
    elif kind == "link":
        icon_link(s, cx - args.get("w", 64) / 2, cy - 6, w=args.get("w", 64))
    elif kind == "board":
        icon_board(s, cx - 40, cy - 16, 80, 32, "Nano")
    elif kind == "plate":
        icon_plate(s, cx - 42, cy - 16, 84, 32,
                   holes=((10, 10), (74, 10), (10, 22), (74, 22)))
    elif kind == "rail":
        s.rect(cx - 38, cy - 5, 76, 10, fill=METAL, sw=1.4, rx=2)
        s.circle(cx - 26, cy, 2.6, fill=BG, sw=1.0)
        s.circle(cx + 26, cy, 2.6, fill=BG, sw=1.0)
    elif kind == "hc06":
        icon_hc06(s, cx - 27, cy - 16)
    elif kind == "holder":
        s.rect(cx - 30, cy - 12, 60, 24, fill=PLASTIC, sw=1.5, rx=3)
        s.rect(cx - 22, cy - 5, 44, 10, fill=BG, sw=1.2, rx=2)
    elif kind == "horn":
        s.path(f"M{cx-30},{cy} a30,6 0 0 1 60,0 a30,6 0 0 1 -60,0",
               fill=METAL, sw=1.4)
        s.circle(cx, cy, 5.5, fill=BG, sw=1.3)
        for i in (-1, 1):
            for j in (1, 2, 3):
                s.circle(cx + i * j * 7.5, cy, 1.8, fill=BG, sw=0.8)
    elif kind == "wire":
        icon_wire(s, cx - 27, cy - 12)


def build(n, title, parts, note, out):
    cols = min(len(parts), 6)
    cell = 118
    width = max(560, 48 + cols * cell)
    height = 236 if not note else 262

    s = Svg(width, height, f"手順 {CIRCLED[n-1]} {title}")
    # ヘッダ
    s.rect(0, 0, width, 52, fill="#f0f3f6", stroke="none", sw=0)
    s.line(0, 52, width, 52, stroke="#d5dbe2", sw=1.2)
    s.circle(30, 26, 15, fill=ACCENT, stroke="none", sw=0)
    s.text(30, 32, str(n), size=15, fill="#ffffff", anchor="middle", weight="700")
    s.text(54, 26, title, size=14.5, weight="700")
    s.text(54, 44, f"公式組立説明書 {CIRCLED[n-1]}ページ（{n} ページ目）を併せて参照",
           size=10.5, fill=INK_SUB)

    s.text(24, 78, "使う部品", size=12, weight="700", fill=INK_SUB)

    # 部品セル
    y = 132
    for i, (kind, label, qty, args) in enumerate(parts):
        cx = 24 + cell / 2 + i * cell
        draw_part(s, kind, cx, y, args)
        # 数量バッジ
        if qty > 1:
            s.circle(cx + cell / 2 - 22, y - 26, 11, fill=ACCENT, stroke=BG, sw=1.6)
            s.text(cx + cell / 2 - 22, y - 22, f"×{qty}", size=10.5, fill="#ffffff",
                   anchor="middle", weight="700")
        # ラベル（長いものは 2 行に折る）
        if len(label) > 11:
            cut = label.rfind(" ", 0, 11)
            cut = cut if cut > 0 else 11
            s.text(cx, y + 44, label[:cut], size=10.5, anchor="middle")
            s.text(cx, y + 58, label[cut:].strip(), size=10.5, anchor="middle")
        else:
            s.text(cx, y + 44, label, size=10.5, anchor="middle")

    if note:
        s.rect(24, height - 52, width - 48, 36, fill="#fff8f0",
               stroke="#e0c9a6", sw=1.0, rx=5)
        s.text(38, height - 29, "▶ " + note, size=11)

    s.save(out / f"step-{n:02d}.svg")


def main():
    out = (pathlib.Path(__file__).resolve().parent.parent.parent
           / "docs-dev" / "manual" / "images")
    out.mkdir(parents=True, exist_ok=True)
    for i, (title, parts, note) in enumerate(STEPS, start=1):
        build(i, title, parts, note, out)
    print(f"  step-01.svg 〜 step-{len(STEPS):02d}.svg を生成しました")


if __name__ == "__main__":
    main()
