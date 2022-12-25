import time
last_time = time.ticks_ms()

def bench(name):
    global last_time
    new_time = time.ticks_ms()
    print(name, new_time - last_time)
    last_time = new_time

from machine import SPI, I2C, ADC, Pin, PWM, RTC, deepsleep
bench("import machine")
import gc9a01
bench("import gc9a01")
import esp32
bench("import esp32")
import math
bench("import math")

ENCODER_ADDRESS = 54


PINS = {
    'SCK': 14,
    'MOSI': 13,
    'SCL': 22,
    'SDA': 21,
    'B1': 37,
    'B2': 38,
    'B3': 39,
    'POWER_DISABLE': 27,
    'USB_CONNECTED': 7,
    'BATTERY_CHARGING': 4,
    'BATTERY_ADC': 34,
    'LCD_RESET': 8,
    'LCD_DC': 20,
    'LCD_CS': 15,
    'LCD_BACKLIGHT': 19,
    'PIEZO': 5
}


i2c = I2C(0, scl=Pin(PINS["SCL"]), sda=Pin(PINS["SDA"]), freq=400000)
bench("i2c")

# TODO: make this an object so we can use dot notation
buttons = {
    'b1': Pin(PINS["B1"], Pin.IN),
    'b2': Pin(PINS["B2"], Pin.IN),
    'b3': Pin(PINS["B3"], Pin.IN)
}

power_disable = Pin(PINS["POWER_DISABLE"], Pin.OUT)
power_disable.value(False) # enable power

usb_connected = Pin(PINS["USB_CONNECTED"], Pin.IN)

# necessity of PULL kinda depends on how to deal with various High-Z states
# and whether it is MCP73831 or MCP73832
# MCP73831 is Charge Complete – Standby HIGH
# MCP73832 is Charge Complete – Standby HIGH-Z
# Both are Preconditioning, Constant-Current Fast Charge and Constant Voltage LOW
# Both are Shutdown and No Battery Present HIGH-Z
battery_charging = Pin(PINS["BATTERY_CHARGING"], Pin.IN, Pin.PULL_UP) 
battery_adc = ADC(Pin(PINS["BATTERY_ADC"], Pin.IN), atten=ADC.ATTN_11DB)
# battery_adc.read_uv() / 1000000 * 1.465

# TODO: RTC?
# TODO: PWM the backlight

#string = "hello"
#lcd.text(font, string, 120-16*(len(string)//2), 120-16, gc9a01.WHITE, gc9a01.BLACK)

#esp32.wake_on_ext1((buttons["b1"], buttons["b2"]), esp32.WAKEUP_ANY_LOW)
esp32.wake_on_ext0(buttons["b3"], esp32.WAKEUP_ALL_LOW)
bench("pins")

rtc = RTC()
bench("rtc")

DISPLAY_WIDTH = 240
HALF_DISPLAY_WIDTH = 120
DISPLAY_HEIGHT = 240
HALF_DISPLAY_HEIGHT = 120

BIG_FONT_WIDTH = 16
HALF_BIG_FONT_WIDTH = 8
BIG_FONT_HEIGHT = 32
HALF_BIG_FONT_HEIGHT = 16

SMALL_FONT_WIDTH = 8
HALF_SMALL_FONT_WIDTH = 4
SMALL_FONT_HEIGHT = 16
HALF_SMALL_FONT_HEIGHT = 8

MIN_TEXT_Y_POS = -7
MAX_TEXT_Y_POS = 7

rmt = esp32.RMT(0, pin=Pin(PINS['PIEZO']), clock_div=8, idle_level=1, tx_carrier=(10000000, 50, 1))
bench("rmt")

def square_wave(freq, volume=1):
    units = 4000000 / freq
    half = units / 2
    if volume == 1:
        pulses = (round(half), round(half))
    else:  
        ontime = half * volume
        offtime = half - ontime
        oncount = round(ontime / 3)
        offcount = round(offtime / 2)
        pulses = (oncount, offcount, oncount, offcount, oncount, round(half))
    return pulses


def saw_wave(freq, volume=1):
    units = 4000000 / freq
    units_per_step = units / 32
    pulses = []
    for x in range(32, 0, -1):
        ontime = math.ceil(units_per_step / x * volume)
        pulses.append(ontime)
        pulses.append(max(round(units_per_step) - ontime, 1))
    return pulses

def beep():
    rmt.loop(True)
    for x in range(1, 11):
        volume = 1/x
        pulses = square_wave(251.6256, volume)
        rmt.write_pulses(pulses)
        time.sleep_ms(1)
    rmt.loop(False)

def boop():
    rmt.loop(True)
    for x in range(10, 0, -1):
        volume = 1/x
        pulses = square_wave(123.4708, volume)
        rmt.write_pulses(pulses)
        time.sleep_ms(1)
    rmt.loop(False)

beep()
bench("beep")

from fonts.romfonts import vga1_bold_16x32 as big_font
# if we just display the time first we can load just the large font at first
from fonts.romfonts import vga1_8x16 as small_font
#from fonts.truetype import NotoSansMono_32 as font
bench("import fonts")

class Display:
    def __init__(self):
        self.spi = SPI(1, baudrate=60000000, sck=Pin(PINS["SCK"]), mosi=Pin(PINS["MOSI"]))

        # no idea what buffer size we need
        self.lcd = gc9a01.GC9A01(self.spi, width=240, height=240, buffer_size=1024, dc=Pin(PINS["LCD_DC"], Pin.OUT), cs=Pin(PINS["LCD_CS"], Pin.OUT), reset=Pin(PINS["LCD_RESET"], Pin.OUT))
        self.lcd.init()

        self.bg = gc9a01.BLACK
        self.fg = gc9a01.WHITE
        self.hl = gc9a01.MAGENTA

        #self.lcd.fill(self.bg)

        #self.lcd_backlight = Pin(PINS["LCD_BACKLIGHT"], Pin.OUT)
        self.lcd_backlight = Pin(PINS["LCD_BACKLIGHT"])
        #self.lcd_backlight.value(True) # enable backlight
        self.lcd_pwm = PWM(self.lcd_backlight)
        self.lcd_pwm.duty(128) # 0 to 1023

        self.last_lines = ['' for x in range(abs(MIN_TEXT_Y_POS)+MAX_TEXT_Y_POS+1)]
        self.last_hilight = ()

    def big_text(self, string, clear_bg=False):
        # TODO: support reversed text for some characters

        half_width = HALF_BIG_FONT_WIDTH * len(string)
        if clear_bg:
            self.lcd.fill_rect(0, HALF_DISPLAY_HEIGHT - HALF_BIG_FONT_HEIGHT, DISPLAY_WIDTH, BIG_FONT_HEIGHT, self.bg)
        self.lcd.text(big_font, string, HALF_DISPLAY_WIDTH - half_width, HALF_DISPLAY_HEIGHT - HALF_BIG_FONT_HEIGHT, self.hl, self.bg)

    def center_text(self, pos, string, clear_bg):
        if pos < MIN_TEXT_Y_POS or pos > MAX_TEXT_Y_POS:
            return

        if pos == 0:
            self.big_text(string, clear_bg)
            return

        half_width = HALF_SMALL_FONT_WIDTH * len(string)
        if pos < 0:
            y_pos = HALF_DISPLAY_HEIGHT - HALF_BIG_FONT_HEIGHT - (pos * -1 * SMALL_FONT_HEIGHT)
        else:
            y_pos = HALF_DISPLAY_HEIGHT + HALF_BIG_FONT_HEIGHT + ((pos-1) * SMALL_FONT_HEIGHT)

        if clear_bg:
            self.lcd.fill_rect(0, y_pos, DISPLAY_WIDTH, SMALL_FONT_HEIGHT, self.bg)
        self.lcd.text(small_font, string, HALF_DISPLAY_WIDTH - half_width, y_pos, self.fg, self.bg)

    def crop_line(self, line, pos):
        # TODO: probably better to crop the center
        if pos == 0:
            return line[:math.ceil(DISPLAY_WIDTH/BIG_FONT_WIDTH)]
        return line[:math.ceil(DISPLAY_WIDTH/SMALL_FONT_WIDTH)]

    def text_list(self, lines, selected_index):
        for y in range(MIN_TEXT_Y_POS, MAX_TEXT_Y_POS+1):
            offset = y + (-MIN_TEXT_Y_POS)
            index = selected_index + y
            if index < 0 or index >= len(lines):
                line = ''
            else:
                line = lines[index]
            cropped_line = self.crop_line(line, y)
            last_line = self.last_lines[offset]
            if cropped_line != last_line or (y == 0 and self.last_hilight != ()):
                self.last_higlight = () # always clear the last highlight
                length_changed = len(cropped_line) != len(last_line)
                self.last_lines[offset] = cropped_line
                self.center_text(y, cropped_line, length_changed)
    
    def clear_screen(self):
        for offset in range(len(self.last_lines)):
            self.last_lines[offset] = ''
        self.last_higlight = ()
        self.lcd.fill(self.bg)


    # TODO: a method for highlighting all or part of the big text

display = Display()
bench("display")



def read_angle():
    while True:
        try:
            return int.from_bytes(i2c.readfrom_mem(ENCODER_ADDRESS, 0x0E, 2), 'big')
        except OSError:
            print("error")
            pass


"""
start = time.ticks_ms()
previousLength = 0
previousWidth = 0
#while time.ticks_ms() < (start + 5000):
while True:
    string = str(read_angle())
    if not string:
        string = "error"
    width = 16 * (len(string)//2)
    #width = lcd.write_width(font, string)
    if len(string) != previousLength:
    #if width != previousWidth
        lcd.fill_rect(0, 120-16, 240, 32, gc9a01.BLACK)
        previousLength = len(string)
        previousWidth = width
    lcd.text(font, string, 120-width//2, 120-16, gc9a01.WHITE, gc9a01.BLACK)
    #lcd.write(font, string, 120-width//2, 120-16, gc9a01.WHITE, gc9a01.BLACK)

    if buttons["b1"].value() == False:
        deepsleep()

    time.sleep_ms(10)
"""
