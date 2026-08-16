#!/usr/bin/env python3
"""公式ファームウェアと日本語コメント版が完全に同じ動作をすることを検証する。

やっていること:
  1. Arduino API の最小シム（arduino_shim.h）と一緒に、2 つの .ino を
     それぞれ PC 用にコンパイルする
  2. 同じコマンド列を 1 バイトずつ流し込んで実行する
  3. サーボへの write() 値とシリアル送信をすべて記録し、両者を比較する

実機の AVR ビルドではなく、あくまで「ロジックが同一か」の検証です。

公式ファームウェアはメーカーの著作物のためリポジトリに含めていません。
検証を実行するには、製品に付属する Drawing.ino を次の場所に置いてください
（.gitignore 済みなのでコミットされることはありません）。

    official-manual/2.Code_Drawing/Drawing.ino
    SHA-256: 933670b86acaa96c0d8575f49459844b199f9a434edb11945e75317cb09924b2

ファイルが無い場合は、日本語コメント版が単体でビルド・実行できることだけを確認します。

使い方:
    python3 tools/equivalence_check/run.py
"""

import difflib
import hashlib
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent

OFFICIAL = ROOT / "official-manual" / "2.Code_Drawing" / "Drawing.ino"
COMMENTED = ROOT / "firmware" / "Drawing" / "Drawing.ino"


def build_and_run(sketch: pathlib.Path, workdir: pathlib.Path) -> str:
    exe = workdir / (sketch.parent.name + "_" + sketch.stem)
    cmd = [
        "g++", "-std=c++17", "-O0", "-w",
        "-I", str(HERE),
        f'-DSKETCH_PATH="{sketch}"',
        str(HERE / "harness.cpp"),
        "-o", str(exe),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"[NG] ビルド失敗: {sketch}", file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        sys.exit(1)

    run = subprocess.run([str(exe)], capture_output=True, text=True)
    if run.returncode != 0:
        print(f"[NG] 実行失敗: {sketch}", file=sys.stderr)
        print(run.stderr, file=sys.stderr)
        sys.exit(1)
    return run.stdout


OFFICIAL_SHA256 = "933670b86acaa96c0d8575f49459844b199f9a434edb11945e75317cb09924b2"


def main() -> int:
    if not COMMENTED.exists():
        print(f"[NG] ファイルが見つかりません: {COMMENTED}", file=sys.stderr)
        return 1

    if not OFFICIAL.exists():
        # 公式版が無いので比較はできない。コメント版が動くことだけ確認する。
        with tempfile.TemporaryDirectory() as tmp:
            out = build_and_run(COMMENTED, pathlib.Path(tmp))
        n = len(out.strip().splitlines())
        print("[SKIP] 公式ファームウェアが無いため比較を省略しました。")
        print(f"       比較するには付属の Drawing.ino を次に置いてください: {OFFICIAL}")
        print(f"       (SHA-256: {OFFICIAL_SHA256})")
        print(f"[OK]   日本語コメント版は単体でビルド・実行できました（{n} 件の操作）")
        return 0

    actual = hashlib.sha256(OFFICIAL.read_bytes()).hexdigest()
    if actual != OFFICIAL_SHA256:
        print(f"[警告] 公式版のハッシュが想定と異なります。ロット違いの可能性があります。",
              file=sys.stderr)
        print(f"       期待: {OFFICIAL_SHA256}\n       実際: {actual}", file=sys.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        workdir = pathlib.Path(tmp)
        official_out = build_and_run(OFFICIAL, workdir)
        commented_out = build_and_run(COMMENTED, workdir)

    if official_out == commented_out:
        n = len(official_out.strip().splitlines())
        print(f"[OK] 公式版と日本語コメント版の動作は完全に一致しました（{n} 件の操作を比較）")
        return 0

    print("[NG] 動作が一致しません。差分:", file=sys.stderr)
    diff = difflib.unified_diff(
        official_out.splitlines(keepends=True),
        commented_out.splitlines(keepends=True),
        fromfile="official-manual/2.Code_Drawing/Drawing.ino",
        tofile="firmware/Drawing/Drawing.ino",
    )
    sys.stderr.writelines(diff)
    return 1


if __name__ == "__main__":
    sys.exit(main())
