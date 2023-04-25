from utils.encoder import angle_difference
from utils.font import Font
from system.hal import read_angle, buttons
from gui.big_small_lines import BigSmallLines
from gui.themes import current_theme

#import fonts.vga2_8x16 as small_font
#import fonts.vga2_bold_16x32 as big_font

#import fonts.squarewave as small_font
#import fonts.squarewave_bold as big_font

small_font = Font("Manrope_SemiBold16", 17, 20)
#small_font = Font("Manrope_SemiBold24", 24, 29)
big_font = Font("Manrope_SemiBold32", 32, 41)


CLICKS_PER_STEP = 256


class Menu:
    def __init__(self, items, selected):
        self.items = items
        self.last_change = read_angle()
        self.selected_index = selected
        self.big_small_lines = BigSmallLines(current_theme, big_font, small_font)
    
    def update(self):
        self.big_small_lines.text_list(self.items, self.selected_index)

    def tick(self):
        angle = read_angle()
        diff = angle_difference(angle, self.last_change)

        if diff <= -CLICKS_PER_STEP:
            self.last_change = angle
            if self.selected_index > 0:
                #beep()
                self.selected_index -= 1
                # TODO: debounce?
                self.update()
            else:
                # we've reached the end
                ##boop()
                pass

        if diff >= CLICKS_PER_STEP:
            self.last_change = angle
            if self.selected_index < len(self.items) - 1:
                #beep()
                self.selected_index += 1
                # TODO: debounce?
                self.update()
            else:
                # we've reached the end
                #boop()
                pass

        for button in [buttons.b1, buttons.b2, buttons.b3]:
            if button.value() == False:
                # wait for the button to be released
                while button.value() == False:
                    pass
                return button

        return None
