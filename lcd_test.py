#!/usr/bin/env python3
"""
LCD I2C Test using PyFTDI
FT2232H/FT232H デバイスを使用してI2C LCD を制御します
"""
from pyftdi.ftdi import Ftdi
from pyftdi.i2c import I2cController
import time
from lcd_i2c import LCDI2C

# LCDのパラメータ
LCD_COLUMNS = 16
LCD_ROWS = 2

# 調べたI2Cアドレスに書き換える（一般的なLCD I2Cバックパックのアドレス）
I2C_ADDR = 0x27  # または 0x3F, 0x20, 0x38 など


def find_ftdi_device() -> str:
    """FTDIデバイスを検索してURL文字列を返す"""

    # 使用可能なFTDIデバイスを確認
    print("Available FTDI devices:")
    devices = Ftdi.list_devices()
    if not devices:
        print("No FTDI devices found!")
        print("Zadigでドライバが正しく設定されているか確認してください。")
        raise RuntimeError("No FTDI devices found")

    for device in devices:
        device_desc, interface = device
        print(f"  {device_desc} - Interface {interface}")

    # 最初のデバイスを使用
    device_desc = devices[0][0]
    print(f"\nUsing device: {device_desc}")

    # FTDIデバイスのURL文字列を作成
    device_url = (
        f"ftdi://0x{device_desc.vid:03x}:0x{device_desc.pid:04x}"
        f":{device_desc.bus}:{device_desc.address}/1"
    )
    print(f"Device URL: {device_url}")
    return device_url


def setup_i2c_controller():
    """FT2232H を使用してI2Cコントローラーを初期化"""

    # FTDIデバイスのURLを取得
    try:
        device_url = find_ftdi_device()
    except RuntimeError:
        return None

    # I2Cコントローラーを初期化
    i2c = I2cController()
    # 3相クロックを無効化（FT2232HでのI2C使用時に必要）
    i2c._disable_3phase_clock = True

    print(f"Configuring I2C controller with URL: {device_url}")

    try:
        i2c.configure(device_url)

        # I2Cバスのプライミング（安定化のための捨て読み）
        print("Priming I2C bus...")
        try:
            i2c.get_port(0x00).read(1)
        except Exception:
            pass  # エラーは想定内

        print("I2C controller initialized successfully")
        return i2c

    except Exception as e:
        print(f"Failed to configure I2C controller: {e}")
        return None


def main():
    """メイン処理"""

    # I2Cコントローラーを初期化
    i2c = setup_i2c_controller()
    if not i2c:
        print("I2C初期化に失敗しました。")
        return

    try:
        # I2Cポートを取得
        lcd_port = i2c.get_port(I2C_ADDR)

        print(f"Initializing LCD at address 0x{I2C_ADDR:02X}...")

        # LCDオブジェクトを作成
        lcd = LCDI2C(lcd_port, backlight=True)

        # LCD初期化
        lcd.init_lcd()
        print("LCD initialization completed!")

        # テストメッセージを表示
        print("Displaying test message...")
        lcd.clear()
        lcd.write_string("Hello, FT2232!\nI2C LCD Test")

        # 5秒待機
        time.sleep(5)

        # 日本語テストメッセージを表示
        print("Testing Japanese characters...")
        lcd.clear()
        lcd.write_string("こんにちは!\nカタカナテスト")

        # 5秒待機
        time.sleep(5)

        # 濁点分解テストメッセージを表示
        print("Testing dakuten decomposition...")
        lcd.clear()
        lcd.write_string_dakuten("がんばって!\nダクテンテスト")

        # 5秒待機
        time.sleep(5)

        # 別のメッセージを表示
        lcd.clear()
        lcd.set_cursor(0, 0)
        lcd.write_string("Test OK!")
        lcd.set_cursor(0, 1)
        lcd.write_string("PyFTDI works")

        print("Test completed successfully!")

        # 3秒後にバックライトオフ
        time.sleep(3)
        lcd.set_backlight(False)
        lcd.clear()

        print("LCD test finished.")

    except Exception as e:
        print(f"LCD test failed: {e}")

    finally:
        # I2Cコントローラーを閉じる
        i2c.terminate()


if __name__ == "__main__":
    main()
