import time
from system.hal import buttons, rtc, beep, restart
from utils.datetime import format_date, format_time
from gui.menu import Menu

class MainMenu:
    def __init__(self):
        self.items = [
            'date/time',
            'alarm',
            'theme',
            'brightness',
            'metronome',
            'drone',
        ]
        self.menu = Menu(self.items, 0)
        self.menu.update()

    def tick(self):
        button = self.menu.tick()
        
        if button == buttons.b1:
            # let the launcher go back to the default app (the clock)
            restart()
            

        if button == buttons.b3:
            # select menu item
            beep()

def start():
    return MainMenu()