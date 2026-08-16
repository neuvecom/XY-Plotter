# XY-Plotter (Drawing Bot / お絵かきロボットアーム)

AliExpress などで販売されている **サーボ 3 個 + Arduino Nano + Bluetooth(HC-06)** 構成の
小型お絵かきロボット（平行リンク型 XY プロッター）の、**日本語の実用ドキュメント**です。

付属してきた公式資料は説明が不足しており、
- 部品の名前と数量が一覧化されていない
- 配線図の解説がない（ピン番号が図からしか読めない）
- ファームウェアの書き込み手順が一切書かれていない
- 付属の「アプリ操作動画」が **別製品のアプリ** を映している

といった問題があります。本リポジトリは、
**付属の PDF・ファームウェア・APK・動画を実際に解析して裏を取った** 手順書です。

> ⚠️ **付属資料そのものは本リポジトリに含めていません。**
> 組立説明書 PDF・アプリ APK・操作動画はいずれもメーカーの著作物のため、再配布を避けています。
> 本ドキュメントは、製品に付属する資料を手元に持っている方が併せて読むことを前提にしています。
> 詳細は [08. 付属資料についての注意](docs-dev/manual/08-official-materials-notes.md) を参照してください。

---

## これは何をする機械か

- 2 つのサーボ（左右の肩）が 5 節リンク（平行リンク）を駆動し、先端のペンを XY 平面上で動かします。
- 3 つ目のサーボがペンを上下させます。
- Android スマホの `Drawing Bot` アプリで画面に指を走らせると、その軌跡が Bluetooth 経由で送られ、実際に紙へ描かれます。

| 項目 | 値 |
|---|---|
| 制御基板 | Arduino Nano (ATmega328P) + Nano 用 IO 拡張シールド |
| サーボ | Tower Pro MG90S × 3 |
| 無線 | HC-06 (Bluetooth Classic SPP), 9600 bps, ペアリング PIN `1234` |
| リンク寸法 | 肩間 45 mm / 上腕 30 mm / 前腕 60 mm |
| 描画範囲 | およそ 104 mm × 56 mm（長方形ではなくドーム状。→ [06](docs-dev/manual/06-serial-protocol.md)） |
| 分解能 | 1 コマンド単位 = 0.2 mm |

---

## ドキュメント一覧

| # | 内容 |
|---|---|
| [01](docs-dev/manual/01-overview-and-bom.md) | 概要・部品リスト（BOM）・必要工具 |
| [02](docs-dev/manual/02-assembly.md) | 組み立て手順（全 16 ステップ、公式写真つき） |
| [03](docs-dev/manual/03-wiring.md) | 配線図・ピンアサイン |
| [04](docs-dev/manual/04-firmware.md) | ファームウェアの書き込み手順とソース解説 |
| [05](docs-dev/manual/05-android-app.md) | Android アプリの導入・Bluetooth 接続・使い方 |
| [06](docs-dev/manual/06-serial-protocol.md) | シリアル通信プロトコル仕様・座標系・描画範囲 |
| [07](docs-dev/manual/07-calibration-and-troubleshooting.md) | 原点調整とトラブルシューティング |
| [08](docs-dev/manual/08-official-materials-notes.md) | 付属資料の内容と、そのまま信じてはいけない点 |

---

## 最短セットアップ

1. **組み立てる** → [02-assembly.md](docs-dev/manual/02-assembly.md)
2. **配線する** → [03-wiring.md](docs-dev/manual/03-wiring.md)
   - サーボ A(ペン)=**D9** / B=**D10** / C=**D11**、HC-06 は **D0/D1**
3. **ファームウェアを書き込む** → [04-firmware.md](docs-dev/manual/04-firmware.md)
   - ⚠️ **書き込み前に HC-06 の RXD/TXD を必ず抜く**（D0/D1 が USB と競合します）
4. **サーボホーンを取り付ける** → 通電して 3 個のサーボが止まってから、水平になるよう差し込む（[02](docs-dev/manual/02-assembly.md) 手順 ⑫）
5. **アプリを入れて接続する** → [05-android-app.md](docs-dev/manual/05-android-app.md)
   - `APP_Drawing Bot.apk` をインストール → OS 設定で `HC-06` とペアリング（PIN `1234`）→ アプリ内 `Bluetooth` ボタンで接続

---

## リポジトリ構成

```
XY-Plotter/
├── README.md                     このファイル
├── firmware/
│   └── Drawing/Drawing.ino       公式と同一動作の日本語コメント付きリファレンス
├── tools/
│   ├── workspace_map.py          描画可能範囲を逆運動学から計算するスクリプト
│   └── equivalence_check/        公式版と解説版の等価性を検証するテスト
└── docs-dev/
    ├── manual/                   日本語ドキュメント（上表）
    └── work_log/                 作業ログ
```

### 付属資料を手元に置く場合

メーカー付属のファームウェアと比較検証したい場合は、付属の `Drawing.ino` を
次の場所に置いてください（`.gitignore` 済みで、コミットされることはありません）。

```
official-manual/2.Code_Drawing/Drawing.ino
```

---

## ライセンス・出典について

- `docs-dev/` および `firmware/`、`tools/` は本リポジトリで新規に作成した解説・検証コードです。
- 製品に付属する PDF・APK・動画・ファームウェアはメーカーの著作物であり、
  本リポジトリには **含めていません**。
- 本ドキュメントの数値（ピン番号・描画範囲・プロトコル）は、
  付属の `Drawing.ino` と `APP_Drawing Bot.apk` を実際に解析して確認したものです。
  確認方法は各ページの「根拠」節に記載しています。
