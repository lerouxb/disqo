def format_time(dt):
    [Y, M, D, W, h, m, s, u] = dt
    return "{h:02d}:{m:02d}:{s:02d}".format(h=h, m=m, s=s)

# TODO: actually move this to display.center_text()
def draw_center_text(pos, string):
    # TODO: this is for pos 0. negative numbers use the smaller font higher up and positive numbers the smaller font lower down
    width = 16*(len(string)//2)
    #width = lcd.write_width(font, string)
    lcd.text(font, string, 120-16*(len(string)//2), 120-16, gc9a01py.WHITE, gc9a01py.BLACK)
    #lcd.write(font, string, 120-width//2, 120-16, gc9a01py.WHITE, gc9a01py.BLACK)