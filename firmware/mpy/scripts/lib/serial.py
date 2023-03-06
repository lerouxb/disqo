#!/usr/bin/env python2

import argparse
import serial

class Serial:
    def __init__(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('port', nargs=1)
        parser.add_argument('-b', '--baud', default=115198)

        args = parser.parse_args()
        #print(args)

        self.ser = serial.Serial(args.port[0], args.baud, timeout=0.1)

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
