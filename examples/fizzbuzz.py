import random as _random


def _plain_str(val):
    """Convert a Plain value to its display string."""
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, float) and val == int(val):
        return str(int(val))
    if isinstance(val, list):
        return "[" + ", ".join(_plain_str(v) for v in val) + "]"
    return str(val)


def _plain_add(a, b):
    """Plain + operator: concatenates if either side is a string."""
    if isinstance(a, str) or isinstance(b, str):
        return _plain_str(a) + _plain_str(b)
    return a + b


def _plain_num(val):
    """Convert a value to int or float."""
    s = str(val)
    return float(s) if "." in s else int(s)


print(_plain_str('FizzBuzz 1 to 20:'))
i = 1
fc = 0
bc = 0
while (i < 21):
    fc = _plain_add(fc, 1)
    bc = _plain_add(bc, 1)
    if ((fc == 3) and (bc == 5)):
        print(_plain_str('FizzBuzz'))
        fc = 0
        bc = 0
    else:
        if (fc == 3):
            print(_plain_str('Fizz'))
            fc = 0
        else:
            if (bc == 5):
                print(_plain_str('Buzz'))
                bc = 0
            else:
                print(_plain_str(i))
    i = _plain_add(i, 1)
