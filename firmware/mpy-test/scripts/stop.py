#!/usr/bin/env python3

from lib.serial import Serial

ser = Serial()

ser.key(b'\x03') # ctrl-c
ser.command(b'from hal import display')
ser.command(b'display.lcd_pwm.deinit()')
print()
