#!/usr/bin/env python3
"""
LCD I2C Control Module
PCF8574ベースのI2C LCD制御クラス
"""
import time
from pyftdi.i2c import I2cPort

# PCF8574 LCD I2C バックパックのピン配置定数
# PCF8574 Pin -> LCD Pin (HD44780) -> Function
RS_PIN = 0  # P0 -> RS (Pin 4) -> Register Select
RW_PIN = 1  # P1 -> RW (Pin 5) -> Read/Write
E_PIN = 2  # P2 -> E (Pin 6) -> Enable
BL_PIN = 3  # P3 -> Backlight Control (via transistor)
D4_PIN = 4  # P4 -> D4 (Pin 11) -> Data 4
D5_PIN = 5  # P5 -> D5 (Pin 12) -> Data 5
D6_PIN = 6  # P6 -> D6 (Pin 13) -> Data 6
D7_PIN = 7  # P7 -> D7 (Pin 14) -> Data 7

# ビットマスク定数
RS_MASK = 1 << RS_PIN
RW_MASK = 1 << RW_PIN
E_MASK = 1 << E_PIN
BL_MASK = 1 << BL_PIN
D4_MASK = 1 << D4_PIN
D5_MASK = 1 << D5_PIN
D6_MASK = 1 << D6_PIN
D7_MASK = 1 << D7_PIN

# HD44780 日本語文字マッピング（カタカナ）
# HD44780のA00 ROM（日本語版）のカタカナ文字コード表
KATAKANA_MAP = {
    "ア": 0xB1,
    "イ": 0xB2,
    "ウ": 0xB3,
    "エ": 0xB4,
    "オ": 0xB5,
    "カ": 0xB6,
    "キ": 0xB7,
    "ク": 0xB8,
    "ケ": 0xB9,
    "コ": 0xBA,
    "サ": 0xBB,
    "シ": 0xBC,
    "ス": 0xBD,
    "セ": 0xBE,
    "ソ": 0xBF,
    "タ": 0xC0,
    "チ": 0xC1,
    "ツ": 0xC2,
    "テ": 0xC3,
    "ト": 0xC4,
    "ナ": 0xC5,
    "ニ": 0xC6,
    "ヌ": 0xC7,
    "ネ": 0xC8,
    "ノ": 0xC9,
    "ハ": 0xCA,
    "ヒ": 0xCB,
    "フ": 0xCC,
    "ヘ": 0xCD,
    "ホ": 0xCE,
    "マ": 0xCF,
    "ミ": 0xD0,
    "ム": 0xD1,
    "メ": 0xD2,
    "モ": 0xD3,
    "ヤ": 0xD4,
    "ユ": 0xD5,
    "ヨ": 0xD6,
    "ラ": 0xD7,
    "リ": 0xD8,
    "ル": 0xD9,
    "レ": 0xDA,
    "ロ": 0xDB,
    "ワ": 0xDC,
    "ヲ": 0xA6,
    "ン": 0xDD,
    "ァ": 0xA7,
    "ィ": 0xA8,
    "ゥ": 0xA9,
    "ェ": 0xAA,
    "ォ": 0xAB,
    "ッ": 0xAF,
    "ャ": 0xD5,
    "ュ": 0xD7,
    "ョ": 0xB0,
    "。": 0xA1,
    "「": 0xA2,
    "」": 0xA3,
    "、": 0xA4,
    "・": 0xA5,
    "ー": 0xB0,
    "゛": 0xDE,
    "゜": 0xDF,
}

# ひらがなをカタカナに変換するマッピング
HIRAGANA_TO_KATAKANA = {
    "あ": "ア",
    "い": "イ",
    "う": "ウ",
    "え": "エ",
    "お": "オ",
    "か": "カ",
    "き": "キ",
    "く": "ク",
    "け": "ケ",
    "こ": "コ",
    "さ": "サ",
    "し": "シ",
    "す": "ス",
    "せ": "セ",
    "そ": "ソ",
    "た": "タ",
    "ち": "チ",
    "つ": "ツ",
    "て": "テ",
    "と": "ト",
    "な": "ナ",
    "に": "ニ",
    "ぬ": "ヌ",
    "ね": "ネ",
    "の": "ノ",
    "は": "ハ",
    "ひ": "ヒ",
    "ふ": "フ",
    "へ": "ヘ",
    "ほ": "ホ",
    "ま": "マ",
    "み": "ミ",
    "む": "ム",
    "め": "メ",
    "も": "モ",
    "や": "ヤ",
    "ゆ": "ユ",
    "よ": "ヨ",
    "ら": "ラ",
    "り": "リ",
    "る": "ル",
    "れ": "レ",
    "ろ": "ロ",
    "わ": "ワ",
    "を": "ヲ",
    "ん": "ン",
    "ぁ": "ァ",
    "ぃ": "ィ",
    "ぅ": "ゥ",
    "ぇ": "ェ",
    "ぉ": "ォ",
    "っ": "ッ",
    "ゃ": "ャ",
    "ゅ": "ュ",
    "ょ": "ョ",
}

# 濁点・半濁点文字を基本文字+濁点記号に分解するマッピング
DAKUTEN_DECOMPOSE = {
    # 濁点文字
    "ガ": "カ゛",
    "ギ": "キ゛",
    "グ": "ク゛",
    "ゲ": "ケ゛",
    "ゴ": "コ゛",
    "ザ": "サ゛",
    "ジ": "シ゛",
    "ズ": "ス゛",
    "ゼ": "セ゛",
    "ゾ": "ソ゛",
    "ダ": "タ゛",
    "ヂ": "チ゛",
    "ヅ": "ツ゛",
    "デ": "テ゛",
    "ド": "ト゛",
    "バ": "ハ゛",
    "ビ": "ヒ゛",
    "ブ": "フ゛",
    "ベ": "ヘ゛",
    "ボ": "ホ゛",
    "ヴ": "ウ゛",
    # 半濁点文字
    "パ": "ハ゜",
    "ピ": "ヒ゜",
    "プ": "フ゜",
    "ペ": "ヘ゜",
    "ポ": "ホ゜",
    # ひらがな濁点
    "が": "か゛",
    "ぎ": "き゛",
    "ぐ": "く゛",
    "げ": "け゛",
    "ご": "こ゛",
    "ざ": "さ゛",
    "じ": "し゛",
    "ず": "す゛",
    "ぜ": "せ゛",
    "ぞ": "そ゛",
    "だ": "た゛",
    "ぢ": "ち゛",
    "づ": "つ゛",
    "で": "て゛",
    "ど": "と゛",
    "ば": "は゛",
    "び": "ひ゛",
    "ぶ": "ふ゛",
    "べ": "へ゛",
    "ぼ": "ほ゛",
    # ひらがな半濁点
    "ぱ": "は゜",
    "ぴ": "ひ゜",
    "ぷ": "ふ゜",
    "ぺ": "へ゜",
    "ぽ": "ほ゜",
}


def decompose_dakuten_text(text):
    """濁点・半濁点文字を基本文字+濁点記号に分解"""
    result = ""
    for char in text:
        if char in DAKUTEN_DECOMPOSE:
            result += DAKUTEN_DECOMPOSE[char]
        else:
            result += char
    return result


class LCDI2C:
    """PCF8574ベースのI2C LCD制御クラス"""

    def __init__(self, i2c_port: I2cPort, backlight=True):
        self.port = i2c_port
        self.backlight_state = backlight

    def _write_pcf8574(self, data):
        """PCF8574に8ビットデータを書き込み"""
        # バックライト制御ビットを追加
        if self.backlight_state:
            data |= BL_MASK
        self.port.write([data])

    def _write_4bits(self, data, rs=False):
        """4ビットデータをLCDに送信（Enable信号付き）"""
        # データビット（上位4ビット）を準備
        output = (data & 0xF0) | (RS_MASK if rs else 0)

        # Enable High でデータ送信
        self._write_pcf8574(output | E_MASK)
        time.sleep(0.001)  # 1ms wait

        # Enable Low でデータ確定
        self._write_pcf8574(output & ~E_MASK)
        time.sleep(0.001)  # 1ms wait

    def _write_byte(self, data, rs=False):
        """8ビットデータを4ビットモードで送信"""
        # 上位4ビットを送信
        self._write_4bits(data & 0xF0, rs)
        # 下位4ビットを送信（4ビット左シフト）
        self._write_4bits((data << 4) & 0xF0, rs)

    def send_command(self, cmd):
        """LCDにコマンドを送信（RS=0）"""
        self._write_byte(cmd, rs=False)
        time.sleep(0.002)  # 2ms wait for command execution

    def send_data(self, data):
        """LCDにデータを送信（RS=1）"""
        self._write_byte(data, rs=True)
        time.sleep(0.001)  # 1ms wait for data write

    def set_backlight(self, state):
        """バックライトの状態を設定"""
        self.backlight_state = state
        # 現在の状態でダミー書き込みしてバックライトを更新
        self._write_pcf8574(0)

    def init_lcd(self):
        """LCD初期化シーケンス（4ビットモード）"""
        # 初期化待機
        time.sleep(0.05)  # 50ms

        # 8ビットモードで初期化開始
        self._write_4bits(0x30)
        time.sleep(0.005)  # 5ms

        self._write_4bits(0x30)
        time.sleep(0.001)  # 1ms

        self._write_4bits(0x30)
        time.sleep(0.001)  # 1ms

        # 4ビットモードに設定
        self._write_4bits(0x20)
        time.sleep(0.001)  # 1ms

        # Function Set: 4-bit, 2 lines, 5x8 dots
        self.send_command(0x28)

        # Display Off
        self.send_command(0x08)

        # Clear Display
        self.send_command(0x01)
        time.sleep(0.002)  # Clear command needs extra time

        # Entry Mode Set: increment cursor, no shift
        self.send_command(0x06)

        # Display On: display on, cursor off, blink off
        self.send_command(0x0C)

    def clear(self):
        """画面をクリア"""
        self.send_command(0x01)
        time.sleep(0.002)  # Clear command needs extra time

    def set_cursor(self, col, row):
        """カーソル位置を設定"""
        # HD44780のDDRAMアドレス計算
        row_offsets = [0x00, 0x40, 0x14, 0x54]  # 1,2,3,4行目の開始アドレス
        if row < len(row_offsets):
            addr = 0x80 + row_offsets[row] + col
            self.send_command(addr)

    def write_char(self, char):
        """1文字をLCDに表示"""
        self.send_data(ord(char))

    def _convert_japanese_char(self, char):
        """日本語文字をHD44780のコードに変換"""
        # ひらがなの場合はカタカナに変換
        if char in HIRAGANA_TO_KATAKANA:
            char = HIRAGANA_TO_KATAKANA[char]

        # カタカナまたは日本語記号の場合はマッピング
        if char in KATAKANA_MAP:
            return KATAKANA_MAP[char]

        # ASCII文字の場合はそのまま
        if ord(char) < 128:
            return ord(char)

        # その他の文字は'?'で代替
        return ord("?")

    def write_japanese_char(self, char):
        """日本語対応の1文字表示"""
        char_code = self._convert_japanese_char(char)
        self.send_data(char_code)

    def write_string(self, text):
        """文字列をLCDに表示（日本語対応）"""
        for char in text:
            if char == "\n":
                # 改行の場合は次の行に移動
                self.set_cursor(0, 1)
            else:
                self.write_japanese_char(char)

    def write_string_dakuten(self, text):
        """濁点分解表示版の文字列表示"""
        # 濁点・半濁点文字を分解
        decomposed_text = decompose_dakuten_text(text)

        for char in decomposed_text:
            if char == "\n":
                # 改行の場合は次の行に移動
                self.set_cursor(0, 1)
            else:
                self.write_japanese_char(char)

    def write_string_ascii(self, text):
        """ASCII文字列のみをLCDに表示（従来版）"""
        for char in text:
            if char == "\n":
                # 改行の場合は次の行に移動
                self.set_cursor(0, 1)
            else:
                self.write_char(char)
