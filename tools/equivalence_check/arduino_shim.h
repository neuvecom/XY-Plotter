// Arduino API の最小シム（PC 上で .ino をコンパイル・実行して挙動を比較するため）
//
// 目的は「公式版 Drawing.ino」と「日本語コメント版 firmware/Drawing/Drawing.ino」が
// 完全に同じサーボ角度列・シリアル出力を生むことの検証だけです。
// 実機用ではありません。
#pragma once

#include <string>
#include <vector>
#include <cstdio>
#include <cmath>
#include <cstdlib>

// ---- Arduino のマクロを再現 ----
// Arduino.h の abs / round は関数ではなくマクロ
#undef abs
#define abs(x) ((x) > 0 ? (x) : -(x))
#undef round
#define round(x) ((x) >= 0 ? (long)((x) + 0.5) : (long)((x) - 0.5))

typedef bool boolean;
typedef unsigned char byte;

// ---- 実行ログ（両版の比較対象） ----
struct Trace {
    std::vector<std::string> lines;
    void add(const std::string &s) { lines.push_back(s); }
};
inline Trace &trace() { static Trace t; return t; }

// ---- Arduino String の必要な部分だけ ----
class String {
public:
    std::string s;
    String() {}
    String(const char *c) : s(c) {}
    String(const std::string &c) : s(c) {}

    String &operator=(const char *c) { s = c; return *this; }
    String &operator+=(char c) { s.push_back(c); return *this; }

    int indexOf(const char *needle, int from) const {
        size_t p = s.find(needle, (size_t)from);
        return p == std::string::npos ? -1 : (int)p;
    }
    String substring(int from) const {
        if ((size_t)from >= s.size()) return String("");
        return String(s.substr((size_t)from));
    }
    String substring(int from, int to) const {
        if ((size_t)from >= s.size()) return String("");
        return String(s.substr((size_t)from, (size_t)(to - from)));
    }
    // Arduino の実装は atof / atoi と同じく、先頭から解釈できる分だけ変換する
    double toDouble() const { return atof(s.c_str()); }
    int toInt() const { return atoi(s.c_str()); }
};

// ---- Servo ----
class Servo {
public:
    int pin = -1;
    void attach(int p) {
        pin = p;
        char buf[64];
        snprintf(buf, sizeof(buf), "attach pin=%d", p);
        trace().add(buf);
    }
    // 実機の Servo::write は int 引数。double を渡すと切り捨てられる点も再現する。
    void write(int value) {
        char buf[64];
        snprintf(buf, sizeof(buf), "write pin=%d val=%d", pin, value);
        trace().add(buf);
    }
};

// ---- Serial ----
class SerialClass {
public:
    std::string inbuf;
    size_t rd = 0;
    void begin(long baud) {
        char buf[64];
        snprintf(buf, sizeof(buf), "serial begin %ld", baud);
        trace().add(buf);
    }
    int available() { return (int)(inbuf.size() - rd); }
    int read() { return rd < inbuf.size() ? (unsigned char)inbuf[rd++] : -1; }
    void print(const char *s) { trace().add(std::string("tx ") + s); }
    void println(const char *s) { trace().add(std::string("tx ") + s + "\n"); }
    void feed(const std::string &s) { inbuf += s; }
};
inline SerialClass Serial;

// ---- その他 ----
inline void delay(unsigned long) {}   // 実時間は比較に不要なので何もしない
