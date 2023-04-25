#!/usr/bin/env python2

import argparse
import serial
from datetime import datetime

class Serial:
    def __init__(self, exec=False):
        parser = argparse.ArgumentParser()

        parser.add_argument('port', nargs=1)
        parser.add_argument('-b', '--baud', default=115198)
        if exec:
            parser.add_argument('filename', nargs=1)

        args = parser.parse_args()
        #print(args)

        self.ser = serial.Serial(args.port[0], args.baud, timeout=0.1)

        if exec:
            self.filename = args.filename[0]

    def exec(self):
        self.key(b'\x03') # ctrl-c
        dt = datetime.now().strftime('(%Y, %m, %d, 0, %H, %M, %S, 0)')
        self.command(("from machine import RTC; rtc = RTC(); rtc.datetime("+dt+")").encode('utf-8'))
        self.key(b'\x05') # ctrl-e
        with open(self.filename) as exec_file:
            for line in exec_file:
                self.command(line.encode('utf-8'))
        self.key(b'\x04') # ctrl-d

    def flush(self):
        while True:
            line = self.ser.readline()
            if len(line) == 0:
                return
            print(line.decode('utf8'), end="")

    def key(self, s):
        print("#", ord(s))
        self.ser.write(s)
        self.flush()

    def command(self, s):
        #print(">", s)
        self.ser.write(s + b'\r\n')
        self.flush()
