from utils.font import Font
from gui.big_small_lines import BigSmallLines
from gui.themes import current_theme

small_font = Font("Manrope_SemiBold24", 24, 29)
big_font = Font("Manrope_SemiBold32", 32, 41)

big_small_lines = BigSmallLines(current_theme, big_font, small_font)

big_small_lines.text_list(["sequencer", "metronome", "drone", "dub siren"], 1)