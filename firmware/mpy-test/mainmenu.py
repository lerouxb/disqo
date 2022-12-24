import time
import gc9a01py
from hal import lcd, font, buttons, rtc, deepsleep
from util import format_time, draw_center_text

def loop():
    start = time.ticks_ms()

    string = format_time(rtc.datetime())
    # TODO: draw_center_text(0, string)
    draw_center_text(0, string)

    while time.ticks_ms() < (start + 1000):
        # TODO: buttons.b1.value somehow
        if buttons["b3"].value() == False:
            # wait for the button to be released so the chip doesn't immediately wake up again
            while buttons["b3"].value() == False:
                pass
            deepsleep()

def run():
    while True:
        loop()