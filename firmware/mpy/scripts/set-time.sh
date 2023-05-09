DT=$(python3 -c "from datetime import datetime; print(datetime.now().strftime('(%Y, %m, %d, 0, %H, %M, %S, 0)'))")
mpremote connect ${PORT} exec "from machine import RTC; rtc = RTC(); rtc.datetime($DT)"
