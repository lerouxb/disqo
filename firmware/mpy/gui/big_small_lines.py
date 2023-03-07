import math
from system.hal import lcd, DISPLAY_HEIGHT, HALF_DISPLAY_HEIGHT, DISPLAY_WIDTH, HALF_DISPLAY_WIDTH

class BigSmallLines:
    def __init__(self, theme, big_font, small_font):
        self.theme = theme
        self.big_font = big_font
        self.small_font = small_font

        self.max_text_y_pos = math.floor((DISPLAY_HEIGHT - big_font.HEIGHT) / small_font.HEIGHT / 2)
        self.min_text_y_pos = -self.max_text_y_pos

        self.last_lines = ['' for x in range(abs(self.min_text_y_pos)+self.max_text_y_pos+1)]

        lcd.fill(theme.background)
    
    def big_text(self, string, clear_bg):
        if clear_bg:
            lcd.fill_rect(0, HALF_DISPLAY_HEIGHT - self.big_font.HEIGHT//2, DISPLAY_WIDTH, self.big_font.HEIGHT, self.theme.background)

        half_width = self.big_font.WIDTH//2 * len(string)
        lcd.text(self.big_font, string, HALF_DISPLAY_WIDTH - half_width, HALF_DISPLAY_HEIGHT - self.big_font.HEIGHT//2, self.theme.f_med, self.theme.background) 

    def center_text(self, pos, string, clear_bg):
        if pos < self.min_text_y_pos or pos > self.max_text_y_pos:
            return

        if pos == 0:
            self.big_text(string, clear_bg)
            return

        half_width = self.small_font.WIDTH//2 * len(string)
        if pos < 0:
            y_pos = HALF_DISPLAY_HEIGHT - self.big_font.HEIGHT//2 - (pos * -1 * self.small_font.HEIGHT)
        else:
            y_pos = HALF_DISPLAY_HEIGHT + self.big_font.HEIGHT//2 + ((pos-1) * self.small_font.HEIGHT)

        if clear_bg:
            lcd.fill_rect(0, y_pos, DISPLAY_WIDTH, self.small_font.HEIGHT, self.theme.background)

        lcd.text(self.small_font, string, HALF_DISPLAY_WIDTH - half_width, y_pos, self.theme.f_low, self.theme.background)

    def crop_line(self, line, pos):
        # TODO: probably better to crop the center
        if pos == 0:
            return line[:math.ceil(DISPLAY_WIDTH/self.big_font.WIDTH)]
        return line[:math.ceil(DISPLAY_WIDTH/self.small_font.WIDTH)]

    def text_list(self, lines, selected_index):
        for y in range(self.min_text_y_pos, self.max_text_y_pos+1):
            offset = y + (-self.min_text_y_pos)
            index = selected_index + y
            if index < 0 or index >= len(lines):
                line = ''
            else:
                line = lines[index]
            cropped_line = self.crop_line(line, y)
            last_line = self.last_lines[offset]
            if cropped_line != last_line or y == 0:
                length_changed = len(cropped_line) != len(last_line)
                self.last_lines[offset] = cropped_line
                self.center_text(y, cropped_line, length_changed)
    
    def clear_screen(self):
        for offset in range(len(self.last_lines)):
            self.last_lines[offset] = ''
        lcd.fill(self.theme.background)

        