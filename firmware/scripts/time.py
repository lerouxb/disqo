import gc9a01
from system.hal import lcd, rtc
from utils.datetime import format_date
import time

#bg = gc9a01.color565(137, 154, 64)
bg = gc9a01.color565(255, 255, 255)
#ghost = gc9a01.color565(131,147,60)
ghost = gc9a01.color565(230,230,230)
#ghost = gc9a01.color565(255, 255, 255)
fg = gc9a01.color565(0,0,0)

colon_color = fg

spacing = 10

def format_time(dt):
    [Y, M, D, W, h, m, s, u] = dt
    return "{h:02d} {m:02d} {s:02d}".format(h=h, m=m, s=s)

mid_width = lcd.get_string_width("DSEG14Classic_Bold40", ":88:")

def bake_colons(color):
    lcd.render_aligned("DSEG14Classic_Bold40", 120 - mid_width//2, 120-20, 0, ":", color, bg, buffer, True)
    lcd.render_aligned("DSEG14Classic_Bold40", 120 + mid_width//2, 120-20, 2, ":", color, bg, buffer, True)

buffer = bytearray(lcd.width()*lcd.height()*2)
#lcd.fill_buffer_texture(buffer, bg, 0.05, 137, 161, 154, 180, 64, 79)
lcd.fill_buffer_texture(buffer, bg, 0.05, 230, 255, 230, 255, 230, 255)
lcd.render_aligned("DSEG14Classic_Bold40", 120, 120-20, 1, "88:88:88", ghost, bg, buffer, True)

lcd.blit_buffer(buffer, 0, 0, lcd.width(), lcd.height())

# TODO: update this when the text actually changes
# TODO: charge bar icon? USB vs Battery icon?
lcd.render_aligned("Manrope_SemiBold24", 120, 120-(20+29+spacing), 1, "4.2V USB ***", fg, bg, buffer)

# TODO: update this dayly
lcd.render_aligned("Manrope_SemiBold24", 120, 120+20+spacing, 1, format_date(rtc.datetime()), fg, bg, buffer)

while True:
    time_string = format_time(rtc.datetime())

    if colon_color == fg:
        colon_color = ghost
    else:
        time_string = time_string.replace(' ', ':')
        colon_color = fg
    
    bake_colons(colon_color)

    if colon_color == ghost:
        lcd.render_aligned("DSEG14Classic_Bold40", 120 - mid_width//2, 120-20, 0, ":", colon_color, bg, buffer)
        lcd.render_aligned("DSEG14Classic_Bold40", 120 + mid_width//2, 120-20, 2, ":", colon_color, bg, buffer)

    lcd.render_aligned("DSEG14Classic_Bold40", 120, 120-20, 1, time_string, fg, bg, buffer)

    time.sleep(1)
