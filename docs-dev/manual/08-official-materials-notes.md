# 08. 付属資料の内容と、そのまま信じてはいけない点

[← 目次に戻る](../../README.md) ／ 前へ [07. 調整とトラブルシュート](07-calibration-and-troubleshooting.md)

製品にはメーカー付属の資料一式が入っています。
それぞれが何なのか、どこに落とし穴があるのかをまとめます。

> ⚠️ **これらの資料は本リポジトリに含めていません。**
> 組立説明書 PDF・APK・操作動画はいずれもメーカー（および動画については第三者）の著作物であり、
> 再配布を避けるためリポジトリから除外しています。
> 以下は「製品に付属してくる資料」を手元に持っている前提の説明です。

---

## 1. 付属資料の一覧

| 付属資料のパス | 内容 | 評価 |
|---|---|---|
| `1.Installation instruction.pdf` | 組立説明書。16 ページ、全ページが写真 1 枚 | 写真は有用。文字は中国語＋簡単な英語のみ |
| `Backup/1.Installation instruction/01〜16.jpg` | 上記 PDF と **同じ内容の JPEG** | PDF より扱いやすい |
| `2.Code_Drawing/Drawing.ino` | Arduino ファームウェア（244 行） | 動作する。ただし説明・コメントは皆無 |
| `APP_Drawing Bot.apk` | Android アプリ | 動作する。説明書なし |
| `Backup/APP_Drawing Bot.zip` | 上記 APK を zip で包んだだけ | **中身は同一** |
| `3.APP bluetooth Video/APP bluetooth connection tutorial.txt` | Bluetooth 接続の 3 ステップ（英語） | 内容は正しい |
| `3.APP bluetooth Video/App use video/*.mov` | 「アプリ操作動画」2 本 | ⚠️ **別製品の動画**（下記 3 章） |

### PDF と JPEG の関係

`1.Installation instruction.pdf` は 16 ページ・画像 16 枚で構成されており、
`Backup/1.Installation instruction/` の 01〜16.jpg と 1 対 1 で対応しています。
**どちらか片方を見れば十分** です。

---

## 2. 説明書に書かれていない重要事項

公式資料を最後まで読んでも分からない、しかし組み立てに必須の情報です。

| 項目 | 公式資料 | 本ドキュメント |
|---|---|---|
| **ファームウェアの書き込み方** | 記載なし（.ino が置いてあるだけ） | [04](04-firmware.md) |
| **書き込み時に HC-06 を抜く必要がある** | 記載なし | [03](03-wiring.md) の §5 |
| ピン番号（D9/D10/D11, D0/D1） | 図から読み取るしかない | [03](03-wiring.md) |
| 通信プロトコル | 記載なし | [06](06-serial-protocol.md) |
| 描画できる範囲 | 記載なし | [06 §5](06-serial-protocol.md#5-描画可能範囲) |
| 原点がずれたときの直し方 | 記載なし | [07](07-calibration-and-troubleshooting.md) |
| DC ジャックの推奨電圧 | 記載なし | **不明**（[03 §6](03-wiring.md#6-電源について)） |
| 部品の数量一覧 | 各ページの写真のみ | [01](01-overview-and-bom.md) |

> 手順 ⑫（通電してからホーンを取り付ける）は公式資料にも書かれていますが、
> **その前にファームウェアを書き込む必要がある** ことが書かれていません。
> ファームが無いとサーボは動かないので、この手順は実行不能です。
> ここが、この製品でつまずく人がいちばん多いポイントだと思われます。

---

## 3. ⚠️ 付属の「アプリ操作動画」は別製品のものです

`3.APP bluetooth Video/App use video/` の 2 本の動画（`5 APP control 1 and slove error.mov`,
`5 APP control 2.mov`）を確認したところ、映っているのは **このプロッターのアプリではありません**。

### 実際に映っているもの

- アプリ名: **「RA示教器」/「Robot Arm 四軸機械臂示教器 V1.01」**（Red Sun Global）
- 画面: X / Y / Z / E の数値入力欄と多数のボタンを持つ **4 軸ロボットアームのティーチングペンダント**
- 実機: リニアレール＋ステッピングモータの **多軸ロボットアーム**（本製品とは全く別物）

一方、本製品のアプリ `Drawing Bot` は
**黒い描画エリアを指でなぞるだけ** の、`Bluetooth` / `Redraw` / `Clear` / `ESC` しかない画面です。
動画のような数値入力 UI はありません。

### それでも役に立つ部分

動画の前半に映っている以下の操作は、**アプリが違っても手順は同じ**なので参考になります。

1. Android の設定 → アプリ → 権限 →「近くのデバイス」などをすべて許可する
2. Android の設定 → Bluetooth → `HC-06` を選ぶ → PIN `1234` を入力してペアリング
3. アプリ内の Bluetooth ボタンで、ペアリング済み一覧から `HC-06` を選ぶ

### 結論

**動画のアプリ画面は無視してください。** 本製品のアプリの使い方は
[05. Android アプリ](05-android-app.md) にまとめてあります。

---

## 4. `APP bluetooth connection tutorial.txt` の内容

原文（英語）は次の 3 ステップです。内容自体は正しいものです。

1. `APP_Drawing Bot.apk` をインストールする（**Android 専用**）
   - アプリの権限はすべて許可すること
2. ロボットに通電し、スマホの Bluetooth で **`HC-06`** を探して **PIN `1234`** を入力する
3. `App use video` の動画に従ってアプリで接続する（← この 3 番だけが上記のとおり別製品）

---

## 5. 解析対象ファイルの同一性

本ドキュメントの記載は、次のファイルを解析して得たものです。
お手元の付属資料が同一かどうかは、SHA-256 で照合できます。

| ファイル | SHA-256 |
|---|---|
| `APP_Drawing Bot.apk` | `70143a2c333d0d2c9bb01b8a3600c4ab54a20ee60b3f7557169d26f34084e896` |
| `2.Code_Drawing/Drawing.ino` | `933670b86acaa96c0d8575f49459844b199f9a434edb11945e75317cb09924b2` |
| `1.Installation instruction.pdf` | `fd982c7c7782421718ecbb68cf44bb955053abbbffa0816f20c1ddb33010cdbb` |

`Backup/APP_Drawing Bot.zip` は APK を zip で包んだだけのもので、中身は同一です。

```bash
sha256sum "APP_Drawing Bot.apk"
```

ハッシュが異なる場合はロット違い等の可能性があり、
本ドキュメントの記載（特にピンアサインやプロトコル）が当てはまらないことがあります。

---

## 6. 本ドキュメントの数値をどう検証したか

| 記載内容 | 検証方法 |
|---|---|
| ピンアサイン | `Drawing.ino` の `attach()` と公式配線図の突き合わせ |
| プロトコル書式 | `Drawing.ino` の `loop()` パーサと、APK 内の文字列連結処理（`",".."。,R"` の join）の一致確認 |
| ハンドシェイク `N` | `Drawing.ino` の `Serial.print("N")` と、APK 側 `Clock1$Timer` の `"N"` 比較処理 |
| 描画可能範囲 | `tools/workspace_map.py`（ファームの計算式を移植して総当たり） |
| コメント版ファームの同一性 | `tools/equivalence_check/`（両版を同一入力で実行し全出力を比較） |
| アプリの UI 構成・権限 | APK の `AndroidManifest.xml` と `classes.dex` の解析 |

---

[← 目次に戻る](../../README.md)
