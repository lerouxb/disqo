#!/usr/bin/env python3

from lib.serial import Serial

ser = Serial()
ser.ser.timeout = 2 # rebooting is slower

ser.key(b'\x03') # ctrl-c
ser.key(b'\x04') # ctrl-d
print()
