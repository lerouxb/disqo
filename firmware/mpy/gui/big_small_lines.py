import math
from system.hal import lcd, DISPLAY_HEIGHT, HALF_DISPLAY_HEIGHT, DISPLAY_WIDTH, HALF_DISPLAY_WIDTH

def isTTF(obj):
    return hasattr(obj, 'isTTF') and obj.isTTF

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

        if isTTF(self.big_font):
            #lcd.write(self.big_font, string, HALF_DISPLAY_WIDTH - half_width, HALF_DISPLAY_HEIGHT - self.big_font.HEIGHT//2, self.theme.f_med, self.theme.background) 
            # TODO: trim text until it fits
            lcd.render_aligned(self.big_font.name, HALF_DISPLAY_WIDTH, HALF_DISPLAY_HEIGHT - self.big_font.HEIGHT//2, 1, string, self.theme.f_med, self.theme.background)
        elif hasattr(self.big_font, 'WIDTH'):
            half_width = self.big_font.WIDTH//2 * len(string)
            lcd.text(self.big_font, string, HALF_DISPLAY_WIDTH - half_width, HALF_DISPLAY_HEIGHT - self.big_font.HEIGHT//2, self.theme.f_med, self.theme.background) 
        else:
            half_width = lcd.write_len(self.big_font, string) // 2
            lcd.write(self.big_font, string, HALF_DISPLAY_WIDTH - half_width, HALF_DISPLAY_HEIGHT - self.big_font.HEIGHT//2, self.theme.f_med, self.theme.background) 

    def center_text(self, pos, string, clear_bg):
        if pos < self.min_text_y_pos or pos > self.max_text_y_pos:
            return

        if pos == 0:
            self.big_text(string, clear_bg)
            return

        if pos < 0:
            y_pos = HALF_DISPLAY_HEIGHT - self.big_font.HEIGHT//2 - (pos * -1 * self.small_font.HEIGHT)
        else:
            y_pos = HALF_DISPLAY_HEIGHT + self.big_font.HEIGHT//2 + ((pos-1) * self.small_font.HEIGHT)

        if clear_bg:
            lcd.fill_rect(0, y_pos, DISPLAY_WIDTH, self.small_font.HEIGHT, self.theme.background)

        if isTTF(self.small_font):
            # TODO: trim text until it fits
            lcd.render_aligned(self.small_font.name, HALF_DISPLAY_WIDTH, y_pos, 1, string, self.theme.f_low, self.theme.background)

        else:
            if hasattr(self.big_font, 'WIDTH'):
                half_width = self.small_font.WIDTH//2 * len(string)
            else:
                half_width = lcd.write_len(self.small_font, string) // 2
            if hasattr(self.small_font, 'WIDTH'):
                lcd.text(self.small_font, string, HALF_DISPLAY_WIDTH - half_width, y_pos, self.theme.f_low, self.theme.background)
            else:
                lcd.write(self.small_font, string, HALF_DISPLAY_WIDTH - half_width, y_pos, self.theme.f_low, self.theme.background)

    def crop_line(self, line, pos):
        # TODO: probably better to crop the center in most cases
        if pos == 0:
            font = self.big_font
        else:
            font = self.small_font
        
        if isTTF(font):
            while lcd.get_string_width(font.name, line) > DISPLAY_WIDTH:
                line = line[:-1]
            return line
        else:
            width = font.WIDTH if hasattr(font, 'WIDTH') else font.MAX_WIDTH
            return line[:math.ceil(DISPLAY_WIDTH/width)]

    def line_len(self, text, y):
        if y == 0:
            font = self.big_font
        else:
            font = self.small_font
        if isTTF(font):
            return lcd.get_string_width(font.name, text)
        elif hasattr(font, 'WIDTH'):
            return len(text) * font.WIDTH
        else:
            return lcd.write_len(font, text)

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
                length_changed = self.line_len(cropped_line, y) != self.line_len(last_line, y)
                self.last_lines[offset] = cropped_line
                self.center_text(y, cropped_line, length_changed)
    
    def clear_screen(self):
        for offset in range(len(self.last_lines)):
            self.last_lines[offset] = ''
        lcd.fill(self.theme.background)

        