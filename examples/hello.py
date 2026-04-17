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


print(_plain_str('Hello, world!'))
name = 'Saaz'
age = 21
print(_plain_str(_plain_add('My name is ', name)))
print(_plain_str(_plain_add(_plain_add('I am ', age), ' years old')))
if (age > 18):
    print(_plain_str('You are an adult.'))
else:
    print(_plain_str('You are a minor.'))
