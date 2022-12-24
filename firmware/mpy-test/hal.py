import time
last_time = time.ticks_ms()

def bench(name):
    global last_time
    new_time = time.ticks_ms()
    print(name, new_time - last_time)
    last_time = new_time

from fonts.romfonts import vga1_bold_16x32 as big_font
from fonts.romfonts import vga1_8x16 as small_font
#from fonts.truetype import NotoSansMono_32 as font
bench("import fonts")
from machine import SPI, I2C, ADC, Pin, RTC, deepsleep
bench("import machine")
import gc9a01py
bench("import gc9a01py")
import esp32
bench("import esp32")

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
    'LCD_BACKLIGHT': 19
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
#lcd.text(font, string, 120-16*(len(string)//2), 120-16, gc9a01py.WHITE, gc9a01py.BLACK)

#esp32.wake_on_ext1((buttons["b1"], buttons["b2"]), esp32.WAKEUP_ANY_LOW)
esp32.wake_on_ext0(buttons["b3"], esp32.WAKEUP_ALL_LOW)
bench("pins")

def read_angle():
    while True:
        try:
            return int.from_bytes(i2c.readfrom_mem(ENCODER_ADDRESS, 0x0E, 2), 'big')
        except OSError:
            pass

rtc = RTC()

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

MIN_TEXT_Y_POS = 7
MAX_TEXT_Y_POS = 7

class Display:
    def __init__(self):
        self.spi = SPI(1, 60000000, sck=Pin(PINS["SCK"]), mosi=Pin(PINS["MOSI"]))

        self.lcd = gc9a01py.GC9A01(self.spi, dc=Pin(PINS["LCD_DC"], Pin.OUT), cs=Pin(PINS["LCD_CS"], Pin.OUT), reset=Pin(PINS["LCD_RESET"], Pin.OUT))
        self.lcd.fill(gc9a01py.BLACK)

        self.lcd_backlight = Pin(PINS["LCD_BACKLIGHT"], Pin.OUT)
        self.lcd_backlight.value(True) # enable backlight

    def center_text(self, pos, string):
        if pos < -MIN_TEXT_Y_POS or pos > MAX_TEXT_Y_POS:
            return

        if pos == 0:
            half_width = HALF_BIG_FONT_WIDTH * len(string)
            # TODO: only clear the line if necessary
            self.lcd.fill_rect(0, HALF_DISPLAY_HEIGHT - HALF_BIG_FONT_HEIGHT, DISPLAY_WIDTH, BIG_FONT_HEIGHT, gc9a01py.BLACK)
            self.lcd.text(big_font, string, HALF_DISPLAY_WIDTH - half_width, HALF_DISPLAY_HEIGHT - HALF_BIG_FONT_HEIGHT, gc9a01py.WHITE, gc9a01py.BLACK)
        else:
            half_width = HALF_SMALL_FONT_WIDTH * len(string)
            if pos < 0:
                y_pos = HALF_DISPLAY_HEIGHT - HALF_BIG_FONT_HEIGHT - HALF_SMALL_FONT_HEIGHT - ((pos + 1) * -1 * SMALL_FONT_HEIGHT)

            else:
                y_pos = HALF_DISPLAY_HEIGHT + HALF_BIG_FONT_HEIGHT + HALF_SMALL_FONT_HEIGHT + ((pos - 1) * SMALL_FONT_HEIGHT)
            # TODO: only clear the line if necessary
            self.lcd.fill_rect(0, y_pos, DISPLAY_WIDTH, SMALL_FONT_HEIGHT, gc9a01py.BLACK)
            self.lcd.text(small_font, string, HALF_DISPLAY_WIDTH - half_width, y_pos, gc9a01py.WHITE, gc9a01py.BLACK)

display = Display()
bench("display")
    
"""
while True:
    start = time.ticks_ms()
    string = formatTime(rtc.datetime())
    width = 16*(len(string)//2)
    #width = lcd.write_width(font, string)
    lcd.text(font, string, 120-16*(len(string)//2), 120-16, gc9a01py.WHITE, gc9a01py.BLACK)
    #lcd.write(font, string, 120-width//2, 120-16, gc9a01py.WHITE, gc9a01py.BLACK)
    while time.ticks_ms() < (start + 1000):
        if buttons["b1"].value() == False:
            deepsleep()
"""

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
        lcd.fill_rect(0, 120-16, 240, 32, gc9a01py.BLACK)
        previousLength = len(string)
        previousWidth = width
    lcd.text(font, string, 120-width//2, 120-16, gc9a01py.WHITE, gc9a01py.BLACK)
    #lcd.write(font, string, 120-width//2, 120-16, gc9a01py.WHITE, gc9a01py.BLACK)

    if buttons["b1"].value() == False:
        deepsleep()

    time.sleep_ms(10)
"""

"""
import font(vga2_bold_16x32) 294
import machine 18
import gc9a01py 594
import esp32 18
spi 2
lcd 502
fill 53
i2c 2
pins 2
starting
"""

"""
-rw-r--r--   1 lerouxb  staff  12853 Jun 18  2022 vga1_16x16.py
-rw-r--r--   1 lerouxb  staff  25141 Jun 18  2022 vga1_16x32.py
-rw-r--r--   1 lerouxb  staff   6741 Jun 18  2022 vga1_8x16.py
-rw-r--r--   1 lerouxb  staff   3667 Jun 18  2022 vga1_8x8.py
-rw-r--r--   1 lerouxb  staff  12853 Jun 18  2022 vga1_bold_16x16.py
-rw-r--r--   1 lerouxb  staff  25141 Jun 18  2022 vga1_bold_16x32.py
-rw-r--r--   1 lerouxb  staff  34128 Jun 18  2022 vga2_16x16.py
-rw-r--r--   1 lerouxb  staff  66896 Jun 18  2022 vga2_16x32.py
-rw-r--r--   1 lerouxb  staff  17781 Jun 18  2022 vga2_8x16.py
-rw-r--r--   1 lerouxb  staff   9587 Jun 18  2022 vga2_8x8.py
-rw-r--r--   1 lerouxb  staff  34128 Jun 18  2022 vga2_bold_16x16.py
-rw-r--r--   1 lerouxb  staff  66896 Jun 18  2022 vga2_bold_16x32.py
"""