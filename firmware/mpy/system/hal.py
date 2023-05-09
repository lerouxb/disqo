import time
import json
import machine
import gc9a01
import esp32

Pin = machine.Pin

#LAST_TIME = time.ticks_ms()

#def bench(name):
#    global LAST_TIME
#    new_time = time.ticks_ms()
#    print(name, new_time - LAST_TIME)
#    LAST_TIME = new_time


ENCODER_ADDRESS = 54

class AttrDict(dict):
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
piezo_pwm = machine.PWM(piezo, duty_u16=0)

i2c = machine.I2C(0, scl=Pin(PINS.SCL), sda=Pin(PINS.SDA), freq=400000)

buttons = AttrDict(
    b1=Pin(PINS.B1, Pin.IN),
    b2=Pin(PINS.B2, Pin.IN),
    b3=Pin(PINS.B3, Pin.IN)
)

power_disable = Pin(PINS.POWER_DISABLE, Pin.OUT)
power_disable.value(False) # enable power

usb_connected = Pin(PINS.USB_CONNECTED, Pin.IN, Pin.PULL_DOWN)

# necessity of PULL kinda depends on how to deal with various High-Z states
# and whether it is MCP73831 or MCP73832
# MCP73831 is Charge Complete – Standby HIGH
# MCP73832 is Charge Complete – Standby HIGH-Z
# Both are Preconditioning, Constant-Current Fast Charge and Constant Voltage LOW
# Both are Shutdown and No Battery Present HIGH-Z
battery_charging = Pin(PINS.BATTERY_CHARGING, Pin.IN, Pin.PULL_UP) 
battery_adc = machine.ADC(Pin(PINS.BATTERY_ADC, Pin.IN), atten=machine.ADC.ATTN_11DB)

esp32.wake_on_ext0(buttons.b1, esp32.WAKEUP_ALL_LOW)

rtc = machine.RTC()

DISPLAY_WIDTH = 240
HALF_DISPLAY_WIDTH = 120
DISPLAY_HEIGHT = 240
HALF_DISPLAY_HEIGHT = 120

def beep():
    piezo_pwm.duty_u16(880)
    piezo_pwm.freq(880)
    time.sleep(0.1)
    piezo_pwm.duty_u16(0)

def boop():
    piezo_pwm.duty_u16(261)
    piezo_pwm.freq(261)
    time.sleep(0.1)
    piezo_pwm.duty_u16(0)

#beep()

# TODO: try 80Mhz again?
#spi = machine.SPI(1, baudrate=60000000, sck=Pin(PINS.SCK), mosi=Pin(PINS.MOSI))
spi = machine.SPI(1, baudrate=80000000, sck=Pin(PINS.SCK), mosi=Pin(PINS.MOSI))
# no idea what buffer size we need
lcd = gc9a01.GC9A01(spi, width=240, height=240, buffer_size=1024, dc=Pin(PINS.LCD_DC, Pin.OUT), cs=Pin(PINS.LCD_CS, Pin.OUT), reset=Pin(PINS.LCD_RESET, Pin.OUT))
lcd.init()
lcd.fill(0)

lcd_backlight = Pin(PINS.LCD_BACKLIGHT)
lcd_pwm = machine.PWM(lcd_backlight)
lcd_pwm.duty(128) # 0 to 1023

def read_angle():
    while True:
        try:
            return int.from_bytes(i2c.readfrom_mem(ENCODER_ADDRESS, 0x0E, 2), 'big')
        except OSError:
            print("error")
            pass

def read_voltage():
    return battery_adc.read_uv() / 1000000 * 1.465

def deepsleep():
    lcd.fill(0)
    machine.deepsleep()

def restart():
    lcd.fill(0)
    machine.soft_reset()

def launch(app):
    rtc.memory(json.dumps({ "app": app }))
    restart()