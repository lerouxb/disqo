
from gc9a01 import color565

class Theme:
    def __init__(self, name, background, f_high, f_med, f_low, f_inv, b_high, b_med, b_low, b_inv):
        self.name = name
        self.background = background
        self.f_high = f_high
        self.f_med = f_med
        self.f_low = f_low
        self.f_inv = f_inv
        self.b_high = b_high
        self.b_med = b_med
        self.b_low = b_low
        self.b_inv = b_inv

themes = [];

def hex565(color):
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[4:6], 16)
    return color565(r, g, b)

themes.append(Theme(
    name = "pico8",
    background = hex565("#000000"),
    f_high = hex565("#ffffff"),
    f_med = hex565("#fff1e8"),
    f_low = hex565("#ff78a9"),
    f_inv = hex565("#ffffff"),
    b_high = hex565("#c2c3c7"),
    b_med = hex565("#83769c"),
    b_low = hex565("#695f56"),
    b_inv = hex565("#00aefe")
))

# TODO: pull this out of non-volatile memory somewhere
current_theme = themes[0]