# hack during development so that mpremote mount is faster
import sys
sys.path.insert(0, "/")

import time
from hal import HALF_DISPLAY_WIDTH, HALF_DISPLAY_HEIGHT, DISPLAY_WIDTH, display, read_angle, font, rtc, buttons, deepsleep, boop
from util import format_date, format_time

#scale = 3

"""
time
date
angle
buttons
connected
charge status
battery voltage
theme
"""

def run():
    print("running")
    lcd = display.lcd
    theme = display.theme

    previousWidth = 0
    while True:
        string = format_time(rtc.datetime())
        #string = str(read_angle())
        #if not string:
        #    string = "error"
        width = font.WIDTH * len(string)
        #width = lcd.draw_len(font, string, scale)
        #lcd.fill_rect(0, HALF_DISPLAY_HEIGHT-font.HEIGHT*scale//2 - 1, DISPLAY_WIDTH, font.HEIGHT*scale + 2, theme.background)
        if width != previousWidth:
            lcd.fill_rect(0, HALF_DISPLAY_HEIGHT-font.HEIGHT//2, DISPLAY_WIDTH, font.HEIGHT, theme.background)
            previousWidth = width

        lcd.text(font, string, HALF_DISPLAY_WIDTH-width//2, HALF_DISPLAY_HEIGHT-font.HEIGHT//2, theme.f_low, theme.background)
        #lcd.draw(font, string, HALF_DISPLAY_WIDTH-width//2, HALF_DISPLAY_HEIGHT, theme.f_low, scale)
    
        if buttons.b1.value() == False:
            while buttons.b1.value() == False:
                pass
            boop()
            deepsleep()

        time.sleep_ms(1000)

run()