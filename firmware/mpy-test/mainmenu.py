import time
from system.hal import buttons, rtc, beep, deepsleep
from utils.datetime import format_date, format_time
from gui.menu import Menu

DATE_INDEX = 2
TIME_INDEX = 3

mainmenu = None

class MainMenu:
    def __init__(self):
        self.start = time.ticks_ms()
        self.items = [
            # volume?
            'theme',
            'brightness',
            'yyy', # date goes here
            'xxx', # time goes here
            'metronome',
            'drone',
        ]
        self.menu = Menu(self.items, TIME_INDEX)
        self.update()
        self.menu.update()

    def update(self):
        self.items[DATE_INDEX] = format_date(rtc.datetime())
        self.items[TIME_INDEX] = format_time(rtc.datetime())
        self.menu.update()

    def tick(self):
        # periodically update the date/time
        if time.ticks_ms() > (self.start + 1000):
            self.update()
            self.start = time.ticks_ms()

        button = self.menu.tick()
        
        if button == buttons.b1:
            # deep sleep
            deepsleep()

        if button == buttons.b3:
            # select menu item
            beep()

def init():
    global mainmenu
    mainmenu = MainMenu()

def tick():
    global mainmenu
    if not mainmenu:
        return
    mainmenu.tick()