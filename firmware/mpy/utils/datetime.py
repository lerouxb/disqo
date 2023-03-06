
def format_date(dt):
    [Y, M, D, W, h, m, s, u] = dt
    return "{Y:04d}/{M:02d}/{D:02d}".format(Y=Y, M=M, D=D)

def format_time(dt):
    [Y, M, D, W, h, m, s, u] = dt
    return "{h:02d}:{m:02d}:{s:02d}".format(h=h, m=m, s=s)
