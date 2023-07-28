# remember to set the PORT env var to point to your serial port

mpremote connect ${PORT} cp -r src/utils :
mpremote connect ${PORT} cp -r src/apps :
mpremote connect ${PORT} cp -r src/gui :
mpremote connect ${PORT} cp -r src/system :
mpremote connect ${PORT} cp src/main.py :

# temporary
mpremote connect ${PORT} cp scripts/time2.py :

DT=$(python3 -c "from datetime import datetime; print(datetime.now().strftime('(%Y, %m, %d, 0, %H, %M, %S, 0)'))")
mpremote connect ${PORT} exec "from machine import RTC; rtc = RTC(); rtc.datetime($DT)"

