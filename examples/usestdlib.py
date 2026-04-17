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


# --- imported from '../stdlib/math.plain' ---
def square(n):
    return (n * n)

def cube(n):
    return ((n * n) * n)

def abs(n):
    if (n > 0):
        return n
    else:
        return (0 - n)

def max(a, b):
    if (a > b):
        return a
    else:
        return b

def min(a, b):
    if (a < b):
        return a
    else:
        return b

# --- end import ---

# --- imported from '../stdlib/strings.plain' ---
def repeat_str(s, n):
    result = ''
    for _i in range(int(n)):
        result = _plain_add(result, s)
    return result

def is_empty(s):
    if (len(s) == 0):
        return 1
    else:
        return 0

# --- end import ---

print(_plain_str('--- Math functions ---'))
print(_plain_str(_plain_add('square 4 = ', square(4))))
print(_plain_str(_plain_add('cube 3   = ', cube(3))))
neg = (0 - 8)
print(_plain_str(_plain_add('abs -8   = ', abs(neg))))
print(_plain_str(_plain_add('max 12 5 = ', max(12, 5))))
print(_plain_str(_plain_add('min 12 5 = ', min(12, 5))))
print(_plain_str('--- String functions ---'))
print(_plain_str(_plain_add("repeat_str 'ho' 3 = ", repeat_str('ho', 3))))
print(_plain_str(_plain_add("is_empty ''       = ", is_empty(''))))
print(_plain_str(_plain_add("is_empty 'hello'  = ", is_empty('hello'))))
