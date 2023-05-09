
import gc9a01
import time
from system.hal import lcd, rtc, read_voltage, read_angle, buttons

bg_color = gc9a01.color565(255, 255, 255)
ghost_color = gc9a01.color565(230,230,230)
fg_color = gc9a01.color565(0,0,0)

spacing = 10

controlx = 90
controly = 45
    
DOW = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

class Font:
    def __init__(self, name, max_width, height):
        self.isTTF = True
        self.name = name
        self.MAX_WIDTH = max_width
        self.HEIGHT = height

time_font = Font("DSEG7Classic_Bold48", 32, 48)
seconds_font = Font("DSEG7Classic_Bold24", 20, 24)
text_font = Font("Manrope_SemiBold16", 17, 20)
#text_font = Font("Manrope_SemiBold24", 24, 29)
#icon_font = Font("MaterialIcons_Regular16", 8, 14)
icon_font = Font("MaterialIcons_Regular24", 10, 20)
indicator_font = Font("Manrope_SemiBold32", 32, 41)

class Align:
    LEFT = 0
    CENTER = 1
    RIGHT = 2

class Snippet:
    def __init__(self, font, text, fg=fg_color, bg=bg_color, offset=0):
        self.font = font
        self.text = text
        self.fg = fg
        self.bg = bg
        self.offset = offset
        # TODO: isVisible
    
    def __eq__(self, other):
        return (self.font == other.font and
                self.text == other.text and
                self.fg == other.fg and 
                self.bg == other.bg and 
                self.offset == other.offset)

class Line:
    def __init__(self, snippets, x_rel=0, y_rel=0, align=Align.LEFT):
        self.snippets = snippets
        self.x_rel = x_rel
        self.y_rel = y_rel
        self.align = align

    def __eq__(self, other):
        return (self.snippets == other.snippets and
                self.x_rel == other.x_rel and
                self.y_rel == other.y_rel and
                self.align == other.align)

    def render(self, lcd, screen):
        half_screen_width = lcd.width()//2
        half_screen_height = lcd.height()//2
        total_width = 0
        for snippet in self.snippets:
            snippet.width = lcd.get_string_width(snippet.font.name, snippet.text)
            total_width += snippet.width

        # TODO: support alignments other than Align.CENTER
        x = half_screen_width - total_width//2 + self.x_rel
        y = half_screen_height + self.y_rel
        for snippet in self.snippets:
            lcd.render_aligned(
                snippet.font.name,
                x,
                y - snippet.font.HEIGHT//2 + snippet.offset,
                0,
                snippet.text,
                snippet.fg,
                snippet.bg,
                screen)
            x += snippet.width

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

def read_button(button):
    return not button.value()

def render_indicator(lcd, screen, x, y):
    lcd.render_aligned("Manrope_SemiBold32", x, y, 1, "•", fg_color, bg_color, screen)

def run():
    # cache the width once for the ghost text
    big_width = lcd.get_string_width("DSEG7Classic_Bold48", "88:88")
    small_width = lcd.get_string_width("DSEG7Classic_Bold24", "88")
    total_width = big_width + small_width

    background = bytearray(lcd.width()*lcd.height()*2)
    screen = bytearray(lcd.width()*lcd.height()*2)

    # create the background image as a slightly noisy mostly flat white colour
    # TODO: put these in variables to make it easier to theme in one place
    lcd.fill_buffer_texture(background, bg_color, 0.05, 230, 255, 230, 255, 230, 255)

    last_lines = []
    last_b1 = read_button(buttons.b1)
    last_b2 = read_button(buttons.b2)
    last_b3 = read_button(buttons.b3)
    last_angle = read_angle()
    last_voltage = read_voltage()

    renders = 0
    while True:
        dt = rtc.datetime()
        greeting_string = greeting(dt) + ' >'
        time_string = format_time(dt)
        seconds_string = format_seconds(dt)
        # TODO: different icon based on battery level
        battery_icon = "\ue1a3"
        #  only change the voltage value if it changed significantly since last reading
        voltage = read_voltage()
        if abs(voltage - last_voltage) > 0.05:
            last_voltage = voltage
        voltage_string = '{:.1f}V'.format(last_voltage);
        date_string = format_date(dt)

        lines = [
            Line([
                Snippet(text_font, greeting_string)
            ], y_rel=-48),
            Line([
                Snippet(time_font, time_string),
                Snippet(seconds_font, seconds_string, offset=-6)
            ]),
            Line([
                Snippet(text_font, voltage_string),
                Snippet(icon_font, battery_icon, offset=0),
                Snippet(text_font, date_string),
            ], y_rel=48)
        ]

        b1 = read_button(buttons.b1)
        b2 = read_button(buttons.b2)
        b3 = read_button(buttons.b3)
        angle = read_angle()

        angle_changed = abs(angle - last_angle) > 1

        input_changed = b1 != last_b1 or b2 != last_b2 or b3 != last_b3 or angle_changed

        # don't render if nothing changed
        if lines == last_lines and not input_changed:
            continue

        start_time =  time.ticks_ms()
        renders = renders + 1

        # clear the screen
        screen[:] = background

        # render the ghost text for the LCD effect
        lcd.render_aligned("DSEG7Classic_Bold48", 120 - total_width//2, 120-24, 0, "88:88", ghost_color, bg_color, screen)
        lcd.render_aligned("DSEG7Classic_Bold24", 120 + total_width//2, 120-18, 2, "88", ghost_color, bg_color, screen)

        # then the foreground text
        for line in lines:
            line.render(lcd, screen)

        # TODO: these might as well be things added to lines
        # then the input indicators
        if buttons.b1.value() == False:
            render_indicator(lcd, screen, 120-controlx, 120-controly-20)
        if buttons.b2.value() == False:
            render_indicator(lcd, screen, 120-controlx, 120+controly-20)
        if angle_changed:
            render_indicator(lcd, screen, 120+controlx, 120-controly-20)
        if buttons.b3.value() == False:
            render_indicator(lcd, screen, 120+controlx, 120+controly-20)

        # copy the screen buffer
        lcd.blit_buffer(screen, 0, 0, lcd.width(), lcd.height())

        # 108ms :(
        # 50 if we don't blit the buffer
        # 24 if we then also don't copy over the entire background at the start
        # less if we don't re-render all the text
        print(renders, time.ticks_ms() - start_time)

        # cache the values
        last_lines = lines
        last_b1 = b1
        last_b2 = b2
        last_b3 = b3
        # only cache the angle if it changed enough. Otherwise we'll re-cache if
        # something else changed and then we could slowly drift past a big enough
        # change bit by bit
        if angle_changed:
            last_angle = angle
