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

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
    def __getattr__(self, name):
        return self[name]

PINS = AttrDict(
    SCK=14,
    MOSI=13,
    SCL=22,
    SDA=21,
    B1=37,
    B2=38,
    B3=39,
    POWER_DISABLE=27,
    USB_CONNECTED=7,
    BATTERY_CHARGING=4,
    BATTERY_ADC=34,
    LCD_RESET=8,
    LCD_DC=20,
    LCD_CS=15,
    LCD_BACKLIGHT=19,
    PIEZO=5
)

piezo = Pin(PINS.PIEZO, Pin.OUT)
piezo.value(False) # a known value
piezo_pwm = PWM(piezo)

i2c = I2C(0, scl=Pin(PINS.SCL), sda=Pin(PINS.SDA), freq=400000)
bench("i2c")

buttons = AttrDict(
    b1=Pin(PINS.B1, Pin.IN),
    b2=Pin(PINS.B2, Pin.IN),
    b3=Pin(PINS.B3, Pin.IN)
)

power_disable = Pin(PINS.POWER_DISABLE, Pin.OUT)
power_disable.value(False) # enable power

usb_connected = Pin(PINS.USB_CONNECTED, Pin.IN)

# necessity of PULL kinda depends on how to deal with various High-Z states
# and whether it is MCP73831 or MCP73832
# MCP73831 is Charge Complete – Standby HIGH
# MCP73832 is Charge Complete – Standby HIGH-Z
# Both are Preconditioning, Constant-Current Fast Charge and Constant Voltage LOW
# Both are Shutdown and No Battery Present HIGH-Z
battery_charging = Pin(PINS.BATTERY_CHARGING, Pin.IN, Pin.PULL_UP) 
battery_adc = ADC(Pin(PINS.BATTERY_ADC, Pin.IN), atten=ADC.ATTN_11DB)
# battery_adc.read_uv() / 1000000 * 1.465

esp32.wake_on_ext0(buttons.b1, esp32.WAKEUP_ALL_LOW)
bench("pins")

rtc = RTC()
bench("rtc")

DISPLAY_WIDTH = 240
HALF_DISPLAY_WIDTH = 120
DISPLAY_HEIGHT = 240
HALF_DISPLAY_HEIGHT = 120

def beep():
    piezo_pwm.duty_u16(261)
    piezo_pwm.freq(261)
    time.sleep(0.1)
    piezo_pwm.duty_u16(0)

def boop():
    piezo_pwm.duty_u16(130)
    piezo_pwm.freq(130)
    time.sleep(0.1)
    piezo_pwm.duty_u16(0)

beep()
bench("beep")

from fonts import vga1_bold_16x32 as font
bench("import fonts")

class Theme:
    def __init__(self, name, background, f_high, f_med, f_low, f_inv, b_high, b_med, b_low, b_inv):
        self.name = name
        self.background = background
        self.f_high = f_high
        self.f_med = f_med
        self.f_low = f_low
        self.f_inv = f_inv
        self.b_high = b_high
        self.b_med = b_med
        self.b_low = b_low
        self.b_inv = b_inv

themes = [];

def hex565(color):
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[4:6], 16)
    return gc9a01.color565(r, g, b)

themes.append(Theme(
    name = "pico8",
    background = hex565("#000000"),
    f_high = hex565("#ffffff"),
    f_med = hex565("#fff1e8"),
    f_low = hex565("#ff78a9"),
    f_inv = hex565("#ffffff"),
    b_high = hex565("#c2c3c7"),
    b_med = hex565("#83769c"),
    b_low = hex565("#695f56"),
    b_inv = hex565("#00aefe")
))        

class Display:
    def __init__(self):
        self.theme = themes[0]

        self.spi = SPI(1, baudrate=60000000, sck=Pin(PINS.SCK), mosi=Pin(PINS.MOSI))

        # no idea what buffer size we need
        self.lcd = gc9a01.GC9A01(self.spi, width=240, height=240, buffer_size=1024, dc=Pin(PINS.LCD_DC, Pin.OUT), cs=Pin(PINS.LCD_CS, Pin.OUT), reset=Pin(PINS.LCD_RESET, Pin.OUT))
        self.lcd.init()

        self.lcd.fill(self.theme.background)

        self.lcd_backlight = Pin(PINS.LCD_BACKLIGHT)
        self.lcd_pwm = PWM(self.lcd_backlight)
        self.lcd_pwm.duty(128) # 0 to 1023

        #self.last_lines = ['' for x in range(abs(MIN_TEXT_Y_POS)+MAX_TEXT_Y_POS+1)]
        #self.last_hilight = ()

#
#    def center_text(self, pos, string, clear_bg):
#        if pos < MIN_TEXT_Y_POS or pos > MAX_TEXT_Y_POS:
#            return
#
#        if pos == 0:
#            self.big_text(string, clear_bg)
#            return
#
#        half_width = HALF_SMALL_FONT_WIDTH * len(string)
#        if pos < 0:
#            y_pos = HALF_DISPLAY_HEIGHT - HALF_BIG_FONT_HEIGHT - (pos * -1 * SMALL_FONT_HEIGHT)
#        else:
#            y_pos = HALF_DISPLAY_HEIGHT + HALF_BIG_FONT_HEIGHT + ((pos-1) * SMALL_FONT_HEIGHT)
#
#        if clear_bg:
#            self.lcd.fill_rect(0, y_pos, DISPLAY_WIDTH, SMALL_FONT_HEIGHT, self.bg)
#        self.lcd.text(small_font, string, HALF_DISPLAY_WIDTH - half_width, y_pos, self.fg, self.bg)
#
#    def crop_line(self, line, pos):
#        # TODO: probably better to crop the center
#        if pos == 0:
#            return line[:math.ceil(DISPLAY_WIDTH/BIG_FONT_WIDTH)]
#        return line[:math.ceil(DISPLAY_WIDTH/SMALL_FONT_WIDTH)]
#
#    def text_list(self, lines, selected_index):
#        for y in range(MIN_TEXT_Y_POS, MAX_TEXT_Y_POS+1):
#            offset = y + (-MIN_TEXT_Y_POS)
#            index = selected_index + y
#            if index < 0 or index >= len(lines):
#                line = ''
#            else:
#                line = lines[index]
#            cropped_line = self.crop_line(line, y)
#            last_line = self.last_lines[offset]
#            if cropped_line != last_line or (y == 0 and self.last_hilight != ()):
#                self.last_higlight = () # always clear the last highlight
#                length_changed = len(cropped_line) != len(last_line)
#                self.last_lines[offset] = cropped_line
#                self.center_text(y, cropped_line, length_changed)
#    
#    def clear_screen(self):
#        for offset in range(len(self.last_lines)):
#            self.last_lines[offset] = ''
#        self.last_higlight = ()
#        self.lcd.fill(self.bg)
#
#
#    # TODO: a method for highlighting all or part of the big text

display = Display()
bench("display")


def read_angle():
    while True:
        try:
            return int.from_bytes(i2c.readfrom_mem(ENCODER_ADDRESS, 0x0E, 2), 'big')
        except OSError:
            print("error")
            pass
