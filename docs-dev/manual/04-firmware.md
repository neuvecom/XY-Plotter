# 04. ファームウェアの書き込み手順とソース解説

[← 目次に戻る](../../README.md) ／ 前へ [03. 配線図](03-wiring.md)

公式資料には `2.Code_Drawing/Drawing.ino` というファイルが入っているだけで、
**書き込み方法の説明が 1 行もありません**。ここでは手順と、コードの中身を解説します。

> 📄 **公式ファームウェアは本リポジトリに含めていません**（メーカーの著作物のため）。
> 製品に付属する `2.Code_Drawing/Drawing.ino` を使うか、
> 同等品として `firmware/Drawing/Drawing.ino`（日本語コメント版）を使ってください。

---

## 1. 書き込み手順

### 1-1. 準備

| 必要なもの | 補足 |
|---|---|
| Arduino IDE | [arduino.cc](https://www.arduino.cc/en/software) から入手。1.8 系 / 2.x どちらでも可 |
| Mini-USB ケーブル | **データ通信対応品**。充電専用ケーブルでは書き込めません |
| `Servo` ライブラリ | Arduino IDE に標準で同梱されています。追加インストール不要 |

### 1-2. 手順

1. **HC-06 の TXD / RXD の 2 本を抜く**（[03-wiring.md](03-wiring.md) 参照）。
2. 付属の `2.Code_Drawing/Drawing.ino`、または本リポジトリの
   `firmware/Drawing/Drawing.ino`（日本語コメント版・動作は同一）を Arduino IDE で開きます。
3. **ツール → ボード** → `Arduino Nano`
4. **ツール → プロセッサ** → `ATmega328P`
   - ここで書き込みに失敗したら `ATmega328P (Old Bootloader)` に変えて再試行します。
     中国製の互換 Nano は旧ブートローダを積んでいることが多いです。
5. **ツール → シリアルポート** → Nano が見えているポートを選択
   - Windows でポートが出ない場合は **CH340 ドライバ** が必要です（互換 Nano で頻出）。
6. **→（書き込み）** ボタンを押します。
7. `Done uploading` が出たら、HC-06 の TXD / RXD を元に戻します。

### 1-3. 書き込めたかの確認

書き込み直後（またはリセット後）に、**3 個のサーボが動いて初期位置で止まれば成功**です。

- 肩サーボ B → 120°
- 肩サーボ C → 60°
- ペンサーボ A → 10°（ペン上げ）

この動作は組み立て手順 ⑫（ホーンの取り付け）で使います。

---

## 2. よくある書き込みエラー

| 症状 | 原因と対処 |
|---|---|
| `programmer is not responding` / `not in sync` | ① HC-06 が D0/D1 に挿さったまま → 抜く<br/>② プロセッサ設定を `Old Bootloader` に変更<br/>③ USB ケーブルが充電専用 |
| シリアルポートが一覧に出ない | CH340 / CH341 の USB シリアルドライバを入れる |
| 書き込めるがサーボが動かない | 電源不足（USB のみで 3 個駆動）／ サーボの `S`/`V`/`G` 逆挿し |
| 書き込み後に文字化けが延々出る | HC-06 が挿さったまま Arduino IDE のシリアルモニタを開いている |

---

## 3. ソース解説

対象: 付属ファームウェア `Drawing.ino`（244 行 / SHA-256 `933670b8...9924b2`）

### 3-1. 全体構造

```
serialEvent()   受信バッファに文字を溜め、'R' が来たら 1 コマンド完了とみなす
     ↓
loop()          コマンド文字列 "X,Y,P" を分解 → 逆運動学 → サーボを補間しながら動かす → "N" を返信
     ↓
penupdown()     ペンサーボを 10°⇔110° でゆっくり動かす
anglecalc()     余弦定理で 2 つの肩サーボ角度を求める
```

### 3-2. 機体寸法の定義

```cpp
float baselen = 4.5;   // 肩どうしの距離     45 mm
float arm1len = 3.0;   // 上腕（肩→肘）      30 mm
float arm2len = 6.0;   // 前腕（肘→ペン先）  60 mm
float baslenmid = baselen / 2;  // 2.25 = X の原点オフセット
float topstart = 3;             // 3.0  = Y の原点オフセット
int divby = 50;                 // 受信値 → cm の換算（1 単位 = 0.2 mm）
float initialangle = 60;        // サーボ角度の固定オフセット
```

**単位はすべて cm** です。実測とずれる場合はここを書き換えることで校正できます
（[07-calibration-and-troubleshooting.md](07-calibration-and-troubleshooting.md) 参照）。

### 3-3. 受信データの座標変換

```cpp
selx = (rotate1 / divby) + baslenmid;   // = X/50 + 2.25 [cm]
sely = (rotate2 / divby) + topstart;    // = Y/50 + 3.0  [cm]
```

つまりアプリから来る整数 `X` `Y` は「0.2 mm 単位のオフセット座標」で、
**原点 (X=0, Y=0) は 2 つの肩の中点から 30 mm 上** の位置です。

### 3-4. 逆運動学（`anglecalc`）

各肩について、次の三角形に余弦定理を適用しています。

```
        ペン先
        /  \
  前腕 /    \  ← arm2len = 6.0
      /      \
   肘●        \
     |         \  arm3lens1（肩→ペン先の直線距離）
上腕 |          \
     ●───────────
    肩
```

```cpp
arm3lens1 = 肩1からペン先までの距離
arm3lens2 = 肩2からペン先までの距離

S1angle = 上腕と「肩1→ペン先」の成す角   （三角形 arm1, arm3lens1, arm2）
C1angle = 「肩1→肩2」と「肩1→ペン先」の成す角（三角形 baselen, arm3lens1, arm3lens2）

S1Totangle = S1angle + C1angle   ← 上腕がベースラインとなす絶対角
```

そして `loop()` 側で:

```cpp
S1Totangle = S1Totangle - initialangle;         // servo1 の指令角
S2Totangle = 180 - (S2Totangle - initialangle); // servo2 は左右対称なので反転
```

**ここが「手順⑫でホーンを水平に付ける」理由**です。
`initialangle = 60` という固定オフセットは、
「サーボが初期位置のとき上腕が水平」という前提で決め打ちされています。

### 3-5. 動作範囲の安全チェック

```cpp
if (S1Totangle >= 0 && S1Totangle <= 180) {
  if (S2Totangle >= 0 && S2Totangle <= 180) {
     ... サーボを動かす ...
  }
} else {
  if (penpos == 1) { penpos = 0; penupdown(); }   // 届かない座標ならペンを上げる
}
```

到達できない座標が来た場合は **ペンを上げて何もしません**。
「アプリで描いたのに一部が描かれない」場合、この分岐に入っている可能性が高いです
（[06-serial-protocol.md](06-serial-protocol.md) の描画範囲を参照）。

### 3-6. 直線補間

```cpp
s1diff = servo1Langle - S1Totangle;   // 現在角との差
s2diff = servo2Langle - S2Totangle;

// 変化量が大きいほうを 1° ずつ刻み、小さいほうを比例配分する
s1step = s1diff / abs(s1diff);
s2step = s2diff / abs(s1diff);
for (pos = 0; pos <= abs(s1diff); pos += 1) {
    servo1.write(servo1Langle -= s1step);
    servo2.write(servo2Langle -= s2step);
    delay(msdelay);     // msdelay = 3
}
```

**サーボ角度空間での線形補間**です。厳密な直線ではありませんが、
1 コマンドあたりの移動量が小さければ実用上は直線に見えます。

`msdelay` を大きくすると **遅く・滑らか** に、小さくすると **速く・ガタつく** ようになります。

### 3-7. ハンドシェイク

```cpp
Serial.print("N");   // 1 コマンド完了 → アプリに "N" を返す
```

アプリ側は `N` を受け取ってから次の点を送ります（[06](06-serial-protocol.md)）。
このフロー制御があるため、**アプリは Arduino の処理速度に自動的に追従します**。

---

## 4. 既知の弱点（改造する場合の注意）

| 箇所 | 内容 |
|---|---|
| `String` の多用 | `serialEvent()` で `inputString += inChar` を繰り返しており、ヒープが断片化します。長時間動かすと不安定になる可能性があります |
| `serialEvent()` の 'R' 判定 | 受信文字列に 'R' が混ざると誤って区切られます。数値と ',' しか来ない前提のコードです |
| カンマが 3 個未満のとき | `updown` が更新されず、直前の値が使われます。エラー通知はありません |
| `acos` の範囲外 | 到達不能座標では `acos` が NaN を返しますが、その後の `>= 0 && <= 180` 判定で弾かれるため、結果的に安全側に倒れています |
| 補間の刻み | 角度差が 0 のとき `s1diff/abs(s1diff)` は 0 除算になりますが、`abs(s2diff) > 0` 側の分岐に入るため実害はありません |

---

## 5. 日本語コメント版について

`firmware/Drawing/Drawing.ino` に、**公式版と完全に同じ動作をする** 日本語コメント付きの版を置いています。

- 変更したのは「コメントの追加」と「紛らわしい 2 つの `findangle` オーバーロードの改名」だけです。
- 同一性は `tools/equivalence_check/` のテストで検証しています。
  公式版と解説版を同じ入力で実行し、**全サーボ書き込み値と全シリアル出力が一致すること** を確認済みです。

検証済みの結果:

```
[OK] 公式版と日本語コメント版の動作は完全に一致しました（1685 件の操作を比較）
```

### 手元で再検証する方法

公式ファームウェアはリポジトリに含めていないため、付属の `Drawing.ino` を
次の場所に置いてから実行してください（`.gitignore` 済みでコミットされません）。

```bash
mkdir -p official-manual/2.Code_Drawing
cp <付属の Drawing.ino> official-manual/2.Code_Drawing/Drawing.ino
python3 tools/equivalence_check/run.py
```

ファイルが無い場合は比較をスキップし、日本語コメント版が単体でビルド・実行できることだけを確認します。
検証に使った公式版の SHA-256 は `933670b86acaa96c0d8575f49459844b199f9a434edb11945e75317cb09924b2` です。

---

次へ → [05. Android アプリ](05-android-app.md)
