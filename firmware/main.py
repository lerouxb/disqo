from time2 import run
run()
## hack during development so that mpremote mount is faster
#import sys
#sys.path.insert(0, "/")
#
#import json
#from machine import WDT, RTC, reset
#
## TODO: how can we tell if we're running under a mount?
##wdt = WDT(timeout=10000)
#
#app_module_name = 'clock'
#
#rtc = RTC()
#memory = rtc.memory()
#if memory:
#    # clear to get the default next time in case something goes wrong
#    rtc.memory('') 
#
#    try:
#        data = json.loads(memory)
#        app_module_name = data["app"]
#    except (KeyError, ValueError) as error:
#        sys.print_exception(error)
#
#print(f"starting {app_module_name}")
#
#try:
#    app_module = __import__(f'apps.{app_module_name}', globals(), locals(), [], 0)
#
#    app = app_module.start()
#
#    while True:
#        app.tick()
#        #wdt.feed()
#
#except Exception as error:
#    print(error)
#    reset()
#