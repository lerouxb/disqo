# remember to set the PORT env var to point to your serial port

mpremote connect ${PORT} cp -r utils :
mpremote connect ${PORT} cp -r apps :
mpremote connect ${PORT} cp -r gui :
mpremote connect ${PORT} cp -r system :
mpremote connect ${PORT} cp -r fonts :
mpremote connect ${PORT} cp main.py :

DT=$(python3 -c "from datetime import datetime; print(datetime.now().strftime('(%Y, %m, %d, 0, %H, %M, %S, 0)'))")
mpremote connect ${PORT} exec "from machine import RTC; rtc = RTC(); rtc.datetime($DT)"

