#!/usr/bin/env python3

from lib.serial import Serial

ser = Serial()

ser.key(b'\x03') # ctrl-c
ser.command(b'from system.hal import lcd_pwm')
ser.command(b'lcd_pwm.deinit()')
print()
