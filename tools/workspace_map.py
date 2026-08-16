#!/usr/bin/env python3
"""ファームウェアの逆運動学をそのまま Python に写し、実際に描画できる範囲を求める。

製品付属ファームウェア Drawing.ino の anglecalc() と loop() の
角度チェック（0〜180 度）を忠実に再現しています。
docs-dev/manual/06-serial-protocol.md に載せている描画範囲の数値は
このスクリプトの出力です。

使い方:
    python3 tools/workspace_map.py            # 範囲の一覧と ASCII マップ
    python3 tools/workspace_map.py --check 100 200   # 指定座標が到達可能か
"""

import argparse
import math
import sys

# --- Drawing.ino と同じ定数（単位 cm） ---
BASELEN = 4.5      # 肩どうしの距離
ARM1LEN = 3.0      # 上腕
ARM2LEN = 6.0      # 前腕
BASLENMID = BASELEN / 2   # 2.25
TOPSTART = 3.0
DIVBY = 50.0       # 受信値 → cm（1 単位 = 0.2mm）
INITIAL_ANGLE = 60.0


def _law_of_cosines_deg(opp, adj, hyp):
    """Drawing.ino の findangle(opp, adj, hyp) と同じ。範囲外なら None。"""
    v = (opp * opp + adj * adj - hyp * hyp) / (2.0 * opp * adj)
    if v < -1.0 or v > 1.0:
        return None          # 実機では acos が NaN を返し、後段の判定で弾かれる
    return math.degrees(math.acos(v))


def solve(x_units, y_units):
    """受信値 (X, Y) からサーボ指令角を求める。到達不能なら None。"""
    selx = x_units / DIVBY + BASLENMID
    sely = y_units / DIVBY + TOPSTART

    arm3lens1 = math.hypot(selx, sely)
    arm3lens2 = math.hypot(selx - BASELEN, sely)

    s1 = _law_of_cosines_deg(ARM1LEN, arm3lens1, ARM2LEN)
    s2 = _law_of_cosines_deg(ARM1LEN, arm3lens2, ARM2LEN)
    c1 = _law_of_cosines_deg(BASELEN, arm3lens1, arm3lens2)
    c2 = _law_of_cosines_deg(BASELEN, arm3lens2, arm3lens1)
    if None in (s1, s2, c1, c2):
        return None

    tot1 = round((s1 + c1) * 100) / 100.0
    tot2 = round((s2 + c2) * 100) / 100.0

    servo1 = tot1 - INITIAL_ANGLE
    servo2 = 180.0 - (tot2 - INITIAL_ANGLE)
    if 0.0 <= servo1 <= 180.0 and 0.0 <= servo2 <= 180.0:
        return (selx, sely, servo1, servo2)
    return None


def reachable(x_units, y_units):
    return solve(x_units, y_units) is not None


def print_table():
    print("Y (受信値)   y[cm]    到達できる X の範囲      幅")
    print("---------------------------------------------------")
    for y in range(0, 300, 20):
        row = [x for x in range(-400, 401) if reachable(x, y)]
        if row:
            print(f"{y:8d}  {y / DIVBY + TOPSTART:6.2f}   {row[0]:6d} .. {row[-1]:6d}"
                  f"   {(row[-1] - row[0]) / DIVBY * 10:6.1f} mm")
        else:
            print(f"{y:8d}  {y / DIVBY + TOPSTART:6.2f}   到達不可")


def print_map(step_x=20, step_y=10):
    print()
    print("描画可能範囲（# = 到達可能）  横: X -280..280 / 縦: Y 290..0")
    for y in range(290, -1, -step_y):
        line = "".join("#" if reachable(x, y) else "." for x in range(-280, 281, step_x))
        print(f"Y={y:4d} |{line}|")
    ncols = len(range(-280, 281, step_x))
    mid = ncols // 2
    caret = [" "] * ncols
    caret[0] = caret[mid] = caret[-1] = "^"
    print(" " * 8 + "".join(caret))
    print(" " * 6 + "X=-280" + " " * (mid - 6) + "X=0" + " " * (ncols - mid - 3 - 3) + "X=+280")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", nargs=2, type=int, metavar=("X", "Y"),
                    help="指定した座標が到達可能かを判定する")
    args = ap.parse_args()

    if args.check:
        x, y = args.check
        r = solve(x, y)
        if r is None:
            print(f"({x}, {y}) は到達できません")
            return 1
        selx, sely, s1, s2 = r
        print(f"({x}, {y}) は到達可能")
        print(f"  ペン先位置 : x={selx:.2f} cm, y={sely:.2f} cm")
        print(f"  サーボ指令 : servo1(D10)={s1:.2f}deg, servo2(D11)={s2:.2f}deg")
        return 0

    print_table()
    print_map()
    return 0


if __name__ == "__main__":
    sys.exit(main())
