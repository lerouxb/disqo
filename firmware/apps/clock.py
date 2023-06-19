import time
# TODO: this is too much. maybe just import system.hal as hal
from system.hal import rtc, buttons, usb_connected, read_angle, read_voltage, battery_charging, deepsleep, launch
from utils.datetime import format_date, format_time
from utils.encoder import angle_difference
from utils.font import Font
from gui.big_small_lines import BigSmallLines
from gui.themes import current_theme

#import fonts.vga2_8x16 as small_font
#import fonts.vga2_bold_16x32 as big_font

#import fonts.squarewave as small_font
#import fonts.squarewave_bold as big_font

small_font = Font("Manrope_SemiBold16", 17, 20)
#small_font = Font("Manrope_SemiBold24", 24, 29)
big_font = Font("Manrope_SemiBold32", 32, 41)

def get_power_source():
    if usb_connected.value():
        return 'usb'
    else:
        return 'bat'

def get_charge_status():
    if usb_connected.value():
        if battery_charging.value():
            return 'done'
        else:
            return 'charge'
    else:
        return 'N/A'

def get_buttons_status():
    parts = []
    for button in [buttons.b1, buttons.b2, buttons.b3]:
        parts.append('-' if button.value() else '*')
    return ''.join(parts)

class Clock:
    def __init__(self):
        self.b1 = buttons.b1.value()
        self.b2 = buttons.b2.value()
        self.b3 = buttons.b3.value()
        self.angle = read_angle()

        self.big_small_lines = BigSmallLines(current_theme, big_font, small_font)
        self.last_update = time.ticks_ms()
        self.update()

    def update(self):
        status = [
            get_power_source(),
            '{:.1f}V'.format(read_voltage()),
            get_charge_status()
        ]
        controls = [
            get_buttons_status(),
            '{:04d}'.format(read_angle())
        ]
        items = [
            format_date(rtc.datetime()),
            format_time(rtc.datetime()),
            ' '.join(status),
            ' '.join(controls)
        ]
        self.big_small_lines.text_list(items, 1)
    
    def tick(self):
        # periodically update the date/time
        needs_update = time.ticks_ms() > (self.last_update + 1000)

        # TODO: we need a smarter input poll & tracking mechanism
        b1 = buttons.b1.value()
        b2 = buttons.b2.value()
        b3 = buttons.b3.value()
        angle = read_angle()

        if b1 != self.b1 or b2 != self.b2 or b3 != self.b3 or abs(angle_difference(angle, self.angle)) > 2:
            needs_update = True
            self.b1 = b1
            self.b2 = b2
            self.b3 = b3
            self.angle = angle

            if b1 == False and b3 == False:
                # wait for the buttons to be released so the chip doesn't immediately wake up
                while buttons.b1.value() == False or buttons.b3.value() == False:
                    pass
                deepsleep()

            elif b3 == False:
                launch('mainmenu')

        
        if needs_update:
            self.update()
            self.last_update = time.ticks_ms()


def start():
    return Clock()