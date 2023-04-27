
import gc9a01
from system.hal import lcd, rtc
import time

bg = gc9a01.color565(255, 255, 255)
ghost = gc9a01.color565(230,230,230)
fg = gc9a01.color565(0,0,0)

spacing = 10
    
DOW = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

def greeting(dt):
    [Y, M, D, W, h, m, s, u] = dt
    if h>=6 and h < 12:
        return 'Good morning'
    elif h>=12 and h < 18:
        return 'Good afternoon'
    elif h>=18 and h < 21:
        return 'Good evening'
    else:
        return 'Zzz'

def format_time(dt):
    [Y, M, D, W, h, m, s, u] = dt
    return "{h:02d}:{m:02d}".format(h=h, m=m)


def format_seconds(dt):
    [Y, M, D, W, h, m, s, u] = dt
    return "{s:02d}".format(s=s)

def format_date(dt):
    [Y, M, D, W, h, m, s, u] = dt
    dow = DOW[W]
    return "{M}-{D} {dow}".format(M=M, D=D, dow=dow)

big_width = lcd.get_string_width("DSEG14Classic_Bold40", "88:88")
small_width = lcd.get_string_width("DSEG14Classic_Bold20", "88")

total_width = big_width + small_width

buffer = bytearray(lcd.width()*lcd.height()*2)
lcd.fill_buffer_texture(buffer, bg, 0.05, 230, 255, 230, 255, 230, 255)
lcd.render_aligned("DSEG14Classic_Bold40", 120 - total_width//2, 120-20, 0, "88:88", ghost, bg, buffer, True)
lcd.render_aligned("DSEG14Classic_Bold20", 120 + total_width//2, 120-15, 2, "88", ghost, bg, buffer, True)

lcd.blit_buffer(buffer, 0, 0, lcd.width(), lcd.height())

# TODO: update this when the text actually changes
# TODO: charge bar icon? USB vs Battery icon?
dt = rtc.datetime()
lcd.render_aligned("Manrope_SemiBold16", 120, 120-(20+20+spacing), 1, greeting(dt) + " >", fg, bg, buffer)

# TODO: update this dayly
lcd.render_aligned("Manrope_SemiBold16", 120, 120+20+spacing, 1, format_date(dt), fg, bg, buffer)

controlx = 90
controly = 45

lcd.render_aligned("Manrope_SemiBold32", 120-controlx, 120-controly-20, 1, "•", fg, bg, buffer)
lcd.render_aligned("Manrope_SemiBold32", 120-controlx, 120+controly-20, 1, "•", fg, bg, buffer)
lcd.render_aligned("Manrope_SemiBold32", 120+controlx, 120-controly-20, 1, "•", fg, bg, buffer)
lcd.render_aligned("Manrope_SemiBold32", 120+controlx, 120+controly-20, 1, "•", fg, bg, buffer)

while True:
    dt = rtc.datetime()
    time_string = format_time(dt)
    seconds_string = format_seconds(dt)

    lcd.render_aligned("DSEG14Classic_Bold40", 120 - total_width//2, 120-20, 0, time_string, fg, bg, buffer)
    lcd.render_aligned("DSEG14Classic_Bold20", 120 + total_width//2, 120-15, 2, seconds_string, fg, bg, buffer)

    # draw the colon again afterwards because the digit to the right of it will overlap
    lcd.render_aligned("DSEG14Classic_Bold40", 120 - total_width//2 + big_width//2, 120-20, 1, ":", fg, bg, buffer)

    time.sleep(1)
