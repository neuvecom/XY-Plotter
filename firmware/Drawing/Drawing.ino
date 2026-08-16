/*
 * XY-Plotter / Drawing Bot  ファームウェア（日本語コメント版）
 * ============================================================
 *
 * 製品付属の公式版 Drawing.ino と「完全に同じ動作」をします。
 * 変更点は次の 2 つだけです。
 *   1. 日本語コメントの追加
 *   2. 同名で紛らわしかった 2 つの findangle() を
 *      lawOfCosinesDeg() / radToDeg() に改名
 * 計算式・定数・型・実行順序は一切変えていません。
 * 同一性は tools/equivalence_check/ のテストで検証済みです。
 *
 * ------------------------------------------------------------
 * 配線（詳細は docs-dev/manual/03-wiring.md）
 *   D9  : サーボ A  ペン昇降
 *   D10 : サーボ B  肩サーボ 1（servo1）
 *   D11 : サーボ C  肩サーボ 2（servo2）
 *   D0/D1 : HC-06 Bluetooth（9600bps）※書き込み時は必ず抜くこと
 *
 * 通信プロトコル（詳細は docs-dev/manual/06-serial-protocol.md）
 *   受信 : "X,Y,P,R"   X,Y = 0.2mm 単位の座標 / P = 0:ペン上げ 1:ペン下げ
 *                      'R' が来た時点で 1 コマンド確定
 *   送信 : "N"         1 コマンド完了の通知（アプリはこれを待って次を送る）
 * ------------------------------------------------------------
 */

#include <Servo.h>

Servo servo1;   // 肩サーボ 1（D10 / 公式配線図の B）
Servo servo2;   // 肩サーボ 2（D11 / 公式配線図の C）
Servo servoup;  // ペン昇降サーボ（D9 / 公式配線図の A）

// ---- 受信コマンドの解析用 ----
boolean stringComplete = false;  // 'R' を受信して 1 コマンド揃ったか
String inputString;              // 受信中のコマンド文字列
double rotate1;                  // 受信した X（0.2mm 単位）
double rotate2;                  // 受信した Y（0.2mm 単位）
int updown;                      // 受信したペン状態（0=上げ / 1=下げ）

// ---- サーボ補間用 ----
double servo1Langle;   // servo1 の現在角（Last angle）
double servo2Langle;   // servo2 の現在角
double s1diff;         // 目標角までの差分
double s2diff;
double s1step;         // 1 ステップあたりの角度増分
double s2step;
int msdelay = 3;       // 1 ステップごとの待ち時間[ms]。大きい=遅く滑らか

// ---- 文字列分割用 ----
String Splitstr;
int findcomma;
int previouscomma;

int divby = 50;        // 受信値 → cm への換算。1 単位 = 1/50 cm = 0.2mm

int pos;               // 補間ループのカウンタ
int penpos;            // 現在のペン状態（0=上げ / 1=下げ）

// ---- 機体寸法（単位 cm）。実測とズレる場合はここを校正する ----
float baselen = 4.5;   // 肩どうしの距離        45mm
float arm1len = 3.0;   // 上腕（肩→肘）         30mm
float arm2len = 6.0;   // 前腕（肘→ペン先）     60mm
float selx;            // 目標ペン位置 X（肩1を原点とする cm）
float sely;            // 目標ペン位置 Y
float pi = 3.14159;

float baslenmid = baselen / 2;  // 2.25 : X 原点は肩間の中央
float topstart = 3;             // 3.0  : Y 原点は肩の 30mm 上
float arm3lens1;                // 肩1 → ペン先 の直線距離
float arm3lens2;                // 肩2 → ペン先 の直線距離

float S1angle;   // 上腕と「肩→ペン先」の成す角
float S2angle;

float C1angle;   // ベースラインと「肩→ペン先」の成す角
float C2angle;

float S1Totangle;  // 上腕の絶対角（= S1angle + C1angle）
float S2Totangle;

// サーボ角度の固定オフセット。
// 「サーボが初期位置のときホーンが水平」という前提で決め打ちされている。
// 組み立て手順 ⑫ でホーンを水平に取り付けるのはこのため。
float initialangle = 60;

void setup() {
    servo1.attach(10);
    servo2.attach(11);
    servoup.attach(9);
    delay(100);

    // 初期姿勢へ。これが座標 (X=0, Y=0) 付近に対応する。
    servo1Langle = 120;
    servo2Langle = 60;
    servo1.write(servo1Langle);
    servo2.write(servo2Langle);
    servoup.write(10);     // 10 度 = ペン上げ
    //servoup.write(110);  // 110 度 = ペン下げ
    penpos = 0;

    Serial.begin(9600);
}

void loop() {
    if (stringComplete == true) {
        // ---- "X,Y,P" をカンマで 3 分割する ----
        findcomma = 0;
        previouscomma = 0;
        findcomma = inputString.indexOf(",", findcomma);
        if (findcomma > 0) {
            Splitstr = inputString.substring(0, findcomma);
            rotate1 = Splitstr.toDouble();
        }
        previouscomma = findcomma + 1;
        inputString = inputString.substring(previouscomma);

        findcomma = 0;
        findcomma = inputString.indexOf(",", findcomma);
        if (findcomma > 0) {
            Splitstr = inputString.substring(0, findcomma);
            rotate2 = Splitstr.toDouble();
        }

        previouscomma = findcomma + 1;
        inputString = inputString.substring(previouscomma);

        findcomma = 0;
        findcomma = inputString.indexOf(",", findcomma);
        if (findcomma > 0) {
            Splitstr = inputString.substring(0, findcomma);
            updown = Splitstr.toInt();
        }

        // ---- 受信値を cm に変換して逆運動学を解く ----
        selx = (rotate1 / divby) + baslenmid;
        sely = (rotate2 / divby) + topstart;
        anglecalc();
        S1Totangle = S1Totangle - initialangle;
        S2Totangle = 180 - (S2Totangle - initialangle);  // servo2 は左右対称なので反転

        // ---- サーボの可動範囲内なら移動する ----
        if (S1Totangle >= 0 and S1Totangle <= 180) {
            if (S2Totangle >= 0 and S2Totangle <= 180) {
                s1diff = servo1Langle - S1Totangle;
                s2diff = servo2Langle - S2Totangle;

                if (abs(s1diff) > abs(s2diff)) {
                    // servo1 の移動量が大きい → servo1 を 1 度刻み、servo2 を比例配分
                    s1step = s1diff / abs(s1diff);
                    s2step = s2diff / abs(s1diff);
                    for (pos = 0; pos <= abs(s1diff); pos += 1) {
                        servo1Langle = servo1Langle - s1step;
                        servo2Langle = servo2Langle - s2step;
                        servo1.write(servo1Langle);
                        servo2.write(servo2Langle);
                        delay(msdelay);
                    }
                    servo1.write(S1Totangle);
                    servo2.write(S2Totangle);
                }
                else if (abs(s2diff) > 0) {
                    // servo2 の移動量が大きい → servo2 を 1 度刻み、servo1 を比例配分
                    s1step = s1diff / abs(s2diff);
                    s2step = s2diff / abs(s2diff);
                    for (pos = 0; pos <= abs(s2diff); pos += 1) {
                        servo1Langle = servo1Langle - s1step;
                        servo2Langle = servo2Langle - s2step;
                        servo1.write(servo1Langle);
                        servo2.write(servo2Langle);
                        delay(msdelay);
                    }
                    servo1.write(S1Totangle);
                    servo2.write(S2Totangle);
                }

                servo1Langle = S1Totangle;
                servo2Langle = S2Totangle;

                if (updown != penpos) {
                    penpos = updown;
                    penupdown();
                }
            }
        }
        else {
            // 到達不能な座標。安全のためペンを上げるだけで何もしない。
            if (penpos == 1) {
                penpos = 0;
                penupdown();
            }
        }

        Serial.print("N");        // 完了通知。アプリはこれを見て次の点を送る
        inputString = "";
        stringComplete = false;
    }
}

// ペンの上げ下げ。急に動かすと機体が揺れるので 1 度ずつ動かす。
void penupdown()
{
    if (penpos == 1) {
        for (pos = 10; pos <= 110; pos += 1) {   // 上げ → 下げ
            servoup.write(pos);
            delay(msdelay);
        }
    }
    else {
        for (pos = 110; pos > 10 ; pos -= 1) {   // 下げ → 上げ
            servoup.write(pos);
            delay(msdelay);
        }
    }
}

// 目標座標 (selx, sely) から 2 つの上腕の絶対角を求める（逆運動学）
void anglecalc()
{
    // 肩からペン先までの直線距離
    arm3lens1 = sqrt((pow((selx - 0), 2)) + (pow((sely - 0), 2)));
    arm3lens2 = sqrt((pow((selx - baselen), 2)) + (pow((sely - 0), 2)));

    // 三角形（上腕, 肩→ペン先, 前腕）から、上腕と肩→ペン先の成す角
    S1angle = lawOfCosinesDeg(arm1len, arm3lens1, arm2len);
    S2angle = lawOfCosinesDeg(arm1len, arm3lens2, arm2len);

    // 三角形（肩間, 肩→ペン先, 反対の肩→ペン先）から、ベースラインとの成す角
    C1angle = lawOfCosinesDeg(baselen, arm3lens1, arm3lens2);
    C2angle = lawOfCosinesDeg(baselen, arm3lens2, arm3lens1);

    // 両者を足すと、上腕がベースラインとなす絶対角になる
    S1Totangle = round((S1angle + C1angle) * 100) / 100.00;
    S2Totangle = round((S2angle + C2angle) * 100) / 100.00;
}

// 余弦定理。辺 opp と辺 adj が成す角を「度」で返す（対辺が hyp）。
// 到達不能な座標では acos の引数が ±1 を超え NaN になるが、
// 呼び出し側の 0〜180 度チェックで弾かれるため安全側に倒れる。
float lawOfCosinesDeg(float opp, float adj, float hyp)
{
    float Scal;
    float Scal2;
    Scal2 = (pow(opp, 2) + pow(adj, 2) - pow(hyp, 2)) / (2.0 * opp * adj);
    Scal = acos(Scal2);
    Scal = radToDeg(Scal);
    return Scal;
}

// ラジアン → 度
float radToDeg(float radians)
{
    float degree;
    degree = radians * (180 / pi);
    return degree;
}

// Arduino が loop() の後に自動で呼ぶ。'R' が来るまで文字を溜める。
void serialEvent() {
    while (Serial.available()) {
        char inChar = (char)Serial.read();
        if (inChar == 'R') {
            stringComplete = true;
        }
        else {
            inputString += inChar;
        }
    }
}
