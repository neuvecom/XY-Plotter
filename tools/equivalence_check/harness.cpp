// 公式版と日本語コメント版の .ino を同じ入力で実行し、
// サーボへの書き込み値とシリアル送信をすべてログに出すテストハーネス。
//
// ビルド時に -DSKETCH_PATH="..." で対象の .ino を指定します。
#include "arduino_shim.h"

// Arduino IDE は .ino から関数プロトタイプを自動生成しますが、
// 素の C++ にはその機能がないのでここで宣言しておきます。
// （両版のどちらか一方にしか存在しない名前も含みますが、未定義でも呼ばれなければ問題ありません）
void setup();
void loop();
void serialEvent();
void penupdown();
void anglecalc();
float findangle(float opp, float adj, float hyp);
float findangle(float radians);
float lawOfCosinesDeg(float opp, float adj, float hyp);
float radToDeg(float radians);

#include SKETCH_PATH

// 検証に使うコマンド列。
//   到達可能な点／到達不能な点／ペン上げ下げ／
//   servo1 側が大きく動く場合と servo2 側が大きく動く場合の両分岐を通す。
static const char *kCommands[] = {
    "0,0,0,R",         // 原点・ペン上げ
    "0,0,1,R",         // ペン下げ（penupdown の下げ側）
    "100,100,1,R",     // 斜め移動
    "-100,100,1,R",    // 反対側へ大きく移動
    "250,20,1,R",      // 右端付近
    "-250,20,1,R",     // 左端付近
    "0,280,1,R",       // 上端付近
    "0,205,1,R",
    "5,205,1,R",       // 微小移動（片側だけ動く分岐）
    "0,205,0,R",       // ペン上げ（penupdown の上げ側）
    "9999,9999,1,R",   // 到達不能 → 何もしないはず
    "0,0,1,R",
    "abc,def,1,R",     // 数値でない入力
    "1,2,R",           // カンマ不足
};

int main() {
    setup();

    std::string stream;
    for (size_t i = 0; i < sizeof(kCommands) / sizeof(kCommands[0]); ++i) {
        stream += kCommands[i];
    }

    // 実機と同様に 1 バイトずつ受信させ、そのつど serialEvent() → loop() を回す
    for (size_t i = 0; i < stream.size(); ++i) {
        Serial.feed(std::string(1, stream[i]));
        serialEvent();
        loop();
    }

    for (size_t i = 0; i < trace().lines.size(); ++i) {
        printf("%s\n", trace().lines[i].c_str());
    }
    return 0;
}
