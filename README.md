# LCD I2C PyFTDI

Python project for controlling I2C LCD displays using FT2232H/FT232H USB-to-I2C adapters.

## Setup

1. Connect FT2232H device via USB
2. Install dependencies:
   ```bash
   uv sync
   ```

## Usage

Scan for I2C devices:
```bash
python i2c_scanner.py
```

Run LCD test:
```bash
python lcd_test.py
```


## Required Hardware

- FT2232H USB-to-I2C adapter
- I2C LCD display with backpack
- Proper FTDI driver setup