import re

time_pat = re.compile(r'^\d+(?:\:\d+)+$')


def parse_time(time_str: str) -> int:
    M = 60
    H = 60 * M
    match = time_pat.match(time_str)
    if not match:
        return -1
    parts = time_str.split(':')
    if len(parts) == 3:
        return int(parts[0]) * H + int(parts[1]) * M + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * M + int(parts[1])
    elif len(parts) == 1:
        return int(parts[0])
    return -1


def base36(num: int) -> str:
    neg = False
    if num < 0:
        neg = True
        num = -num
    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    res = ''
    while not res or num > 0:
        num, i = divmod(num, 36)
        res = digits[i] + res
    if neg:
        res = '-' + res
    return res
