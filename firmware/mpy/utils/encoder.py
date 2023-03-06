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