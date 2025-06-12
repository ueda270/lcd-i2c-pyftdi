# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python playground project for interfacing with I2C LCD displays using PyFTDI for USB-to-I2C communication via FT232H/FT2232H devices. The project uses Adafruit's CircuitPython libraries for LCD control.

## Development Environment

### Package Management
This project uses `uv` for Python package management:
```bash
# Install dependencies
uv sync

# Add new dependencies
uv add <package-name>
```

### Key Dependencies
- **pyftdi**: Core FTDI USB-to-I2C interface (primary dependency)

### Hardware Setup
- FT232H or FT2232H USB-to-I2C adapter
- I2C LCD displays with backpack (common addresses: 0x27, 0x3F, 0x20, 0x38)
- Requires proper FTDI driver configuration (Zadig on Windows)

## Common Development Commands

### I2C Device Discovery
```bash
# Scan for I2C devices on the bus
python i2c_scanner.py
```

### Running Tests
```bash
# Test LCD functionality
python lcd_test.py

# Run main application
python main.py
```

## Project Architecture

### Core Files
- `i2c_scanner.py`: PyFTDI-based I2C device scanner with Japanese comments
- `lcd_test.py`: Complete LCD test using Adafruit CircuitPython libraries

### Key Patterns
- Uses PyFTDI's I2cController for low-level I2C scanning
- Implements proper I2C bus priming (dummy read) for stability
- Error handling for missing FTDI devices and incorrect I2C addresses

## Development Notes

- Always run `i2c_scanner.py` first to verify device connectivity and addresses
- The scanner performs a "priming" dummy read to stabilize the I2C bus
- LCD addresses must be verified before use in `lcd_test.py`
- Japanese comments in scanner indicate international development context