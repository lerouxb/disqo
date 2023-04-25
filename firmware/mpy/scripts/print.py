#!/usr/bin/env python3

from lib.serial import Serial

ser = Serial()

ser.key(b'\x03') # ctrl-c
ser.command(b'import gc9a01')
ser.command(b'from system.hal import lcd')
ser.command(b'lcd.fill(gc9a01.color565(255, 255, 255))')
ser.command(b'lcd.render_aligned("ChivoMono_Medium24", 120, 120-12, 1, "hello world", gc9a01.color565(0,0,0), gc9a01.color565(255, 255, 255))')

print()

"""
string = "hello world"
while True:
    for x in range(len(string)+1):
        lcd.fill_rect(0, 120-16, 240, 32, 0)
        lcd.render_aligned("Manrope_SemiBold32", 120, 120-16, 1, string[:x])
        time.sleep_ms(15)
    time.sleep(1)
    for x in range(len(string), -1, -1):
        lcd.fill_rect(0, 120-16, 240, 32, 0)
        lcd.render_aligned("Manrope_SemiBold32", 120, 120-16, 1, string[:x])
        time.sleep_ms(15)
"""