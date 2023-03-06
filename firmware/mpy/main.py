# hack during development so that mpremote mount is faster
import sys
sys.path.insert(0, "/")

# TODO: this should check the rtc memory and load the correct app on startup
# TODO: watchdog
from mainmenu import init, tick

init()

while True:
    tick()
