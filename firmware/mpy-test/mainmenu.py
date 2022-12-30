import time
from hal import buttons, read_angle, rtc, display, beep, boop, rmt, square_wave, deepsleep
from util import format_date, format_time

CLICKS_PER_STEP = 256
last_change = 0
DATE_INDEX = 2
TIME_INDEX = 3
selected_index = TIME_INDEX

menu_items = [
    # volume?
    'colours',
    'brightness',
    'yyy', # date goes here
    'xxx', # time goes here
    'metronome',
    'drone',
]

def angle_difference(new_angle, old_angle):
    """
    0 -> 4095: -1 (4095 - 0 - 4096)
    1 -> 4094: -2 (4094 - 1 - 4096)
    4095 -> 0: 1 (0 - 4095 + 4096)
    4094 -> 1: 2 (1 - 4094 + 4096)
    0 -> 1: 1
    1 -> 0: -1
    """

    if new_angle == old_angle:
        return 0

    diff = new_angle - old_angle
    if abs(diff) > 2048:
        if new_angle > old_angle:
            return new_angle - old_angle - 4096
        else:
            return new_angle - old_angle + 4096
    else:
        return diff


def loop():
    global last_change, selected_index

    start = time.ticks_ms()

    menu_items[DATE_INDEX] = format_date(rtc.datetime())
    menu_items[TIME_INDEX] = format_time(rtc.datetime())
    display.text_list(menu_items, selected_index)

    while time.ticks_ms() < (start + 1000):
        # TODO: buttons.b3.value somehow
        angle = read_angle()
        diff = angle_difference(angle, last_change)
        if diff <= -CLICKS_PER_STEP:
            last_change = angle
            if selected_index > 0:
                beep()
                selected_index -= 1
                display.text_list(menu_items, selected_index)
            else:
                boop()
        if diff >= CLICKS_PER_STEP:
            last_change = angle
            if selected_index < len(menu_items) - 1:
                beep()
                selected_index += 1
                display.text_list(menu_items, selected_index)
            else:
                boop()

        if buttons["b1"].value() == False:
            # wait for the button to be released so the chip doesn't immediately wake up again
            while buttons["b1"].value() == False:
                pass
            boop()
            deepsleep()
        

        if buttons["b2"].value() == False:
            rmt.loop(True)
            volume_number = 0
            volume_step = 1
            try:
                while buttons["b2"].value() == False:
                    volume_number += volume_step
                    next_volume = volume_number + volume_step
                    if next_volume > 1000 or next_volume < 0:
                        volume_step *= -1
                        next_volume = volume_number + volume_step
                    volume_number = next_volume
                    volume = volume_number / 1000
                    angle = read_angle()
                    value = angle / 4095;
                    freq = 50 + 2**(value * 10)
                    pulses = square_wave(freq, volume)
                    print(freq, sum(pulses), volume)
                    rmt.write_pulses(pulses)
                    time.sleep_ms(1)
            finally:
                rmt.loop(False)
                last_change = angle

def run():
    global last_change
    last_change = read_angle()

    """
    rmt.loop(True)
    for y in range(100):
        for x in range(10, 0, -1):
            volume = 1/x
            #note(261.6256, volume, 10)
            pulses = square_wave(251.6256, volume)
            #print(pulses)
            rmt.write_pulses(pulses)
            time.sleep_ms(5)
    rmt.loop(False)
    """

    #display.text_list(menu_items, selected_index)
    while True:
        loop()