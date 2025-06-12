#!/usr/bin/env python3
"""
PyFTDI I2C Scanner
FT232H/FT2232H デバイスを使用してI2Cバス上のデバイスをスキャンします
"""
from pyftdi.ftdi import Ftdi
from pyftdi.i2c import I2cController


def scan_i2c_devices():
    """I2Cバス上のデバイスをスキャンしてアドレス一覧を表示"""

    # 使用可能なFTDIデバイスを表示
    print("Available FTDI devices:")
    devices = Ftdi.list_devices()
    if not devices:
        print("No FTDI devices found!")
        return

    for device in devices:
        device_desc, interface = device
        print(f"  {device_desc} - Interface {interface}")

    # 最初のデバイスを使用（複数ある場合は手動で選択可能）
    device_desc = devices[0][0]
    print(f"\nUsing device: {device_desc}")

    # I2Cコントローラーを初期化
    i2c = I2cController()
    # 3相クロックを無効化（FT2232HでのI2C使用時に必要）
    i2c._disable_3phase_clock = True

    # I2Cバスを設定（FTDIデバイスのURL文字列を作成）
    device_url = (
        f"ftdi://0x{device_desc.vid:03x}:0x{device_desc.pid:04x}"
        f":{device_desc.bus}:{device_desc.address}/1"
    )
    print(f"Configuring I2C controller with URL: {device_url}")

    try:
        i2c.configure(device_url)

        print("\nPriming I2C bus (performing a dummy read)...")
        try:
            # 本番スキャン前に一度「捨て読み」を行い、バスの状態を安定させる
            # この読み込みは失敗することが期待される
            # アドレスはスキャン範囲外の有効なものなら何でも良い
            i2c.get_port(0x00).read(1)
        except Exception:
            # エラーは想定内なので無視する
            pass

        print("\nScanning I2C bus...")
        print("     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f")

        found_devices = []

        for addr in range(0x00, 0x78):
            # 0x08-0x77 の範囲をスキャン（I2Cの有効アドレス範囲）
            if addr < 0x08:
                device_marker = "--"
            else:
                try:
                    # 1バイト読み取りを試行してデバイスの存在を確認
                    port = i2c.get_port(addr)
                    port.read(1)
                    found_devices.append(addr)
                    device_marker = f"{addr:02x}"
                except Exception:
                    device_marker = "--"

            # 16進数表示のフォーマット
            if addr % 16 == 0:
                print(f"{addr:02x}: ", end="")

            print(f"{device_marker} ", end="")

            if (addr + 1) % 16 == 0:
                print()

        print("\n")

        # 見つかったデバイスを報告
        if found_devices:
            print(f"Found {len(found_devices)} I2C device(s):")
            for addr in found_devices:
                print(f"  0x{addr:02X} ({addr})")
        else:
            print("No I2C devices found.")

    except Exception as e:
        print(f"Error during I2C scan: {e}")

    finally:
        # I2Cコントローラーを閉じる
        i2c.terminate()


if __name__ == "__main__":
    scan_i2c_devices()
