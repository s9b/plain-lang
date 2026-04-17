# Plain

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A small, readable programming language that looks like English. No semicolons, no braces, no import boilerplate — just clear statements that do what they say.

```plain
set name to ask "What's your name? "
set score to num ask "Enter your score: "

if score is greater than 90 then
    say "Nice work, " + name + "! That's an A."
else
    say "Keep going, " + name + ". You'll get there."
end
```

Plain is built in ~500 lines of Python and has zero dependencies. It's designed to be readable by anyone, hackable by anyone, and small enough to understand completely in an afternoon.

---

## Installation

You need Python 3.8 or newer. No packages to install.

```bash
git clone https://github.com/your-username/plain-lang
cd plain-lang
```

That's it.

---

## Quick start

Save this as `intro.plain`:

```plain
# A quick tour of Plain

fn factorial n
    if n < 2 then
        return 1
    else
        return n * factorial n - 1
    end
end

set nums to [1, 2, 3, 4, 5, 6, 7, 8]
repeat with n in nums
    say str n + "! = " + factorial n
end
```

Run it:

```bash
python main.py intro.plain
```

---

## Language reference

### Variables

```plain
set name  to "Alice"
set score to 95
set ratio to 3.14
set items to [10, 20, 30]
```

### Output

```plain
say "Hello, world!"
say score
say "Score: " + score    # string + number auto-converts
```

### Input

```plain
set name  to ask "What's your name? "
set age   to num ask "How old are you? "   # num converts to integer
```

### Arithmetic

```plain
set x to 10 + 3    # 13
set x to 10 - 3    # 7
set x to 10 * 3    # 30
set x to 10 / 3    # 3.3333...
```

Parentheses work as expected:

```plain
say (a + b) * c
```

### Comparisons

```plain
# natural English
if score is greater than 90 then ...
if score is less than 50 then ...
if name is equal to "Alice" then ...

# symbolic shorthand
if score > 90 then ...
if score < 50 then ...
if score = 100 then ...
```

### Logic

```plain
if age > 18 and score > 80 then
    say "Eligible"
end

if not done then
    say "Keep going"
end
```

### If / else

```plain
if score is greater than 90 then
    say "A"
else
    if score is greater than 70 then
        say "B"
    else
        say "C"
    end
end
```

### Functions

```plain
fn greet name
    say "Hello, " + name + "!"
end

greet "Alice"
```

Functions can return values. Return stops execution immediately.

```plain
fn add a b
    return a + b
end

set result to add 3 4
say result
```

Recursive functions work:

```plain
fn fib n
    if n < 2 then
        return n
    end
    return fib n - 1 + fib n - 2
end
```

### Repeat N times

```plain
repeat 5 times
    say "tick"
end
```

### While loop

```plain
set i to 1
while i < 11
    say i
    set i to i + 1
end
```

### For-each loop

```plain
set colors to ["red", "green", "blue"]
repeat with color in colors
    say color
end
```

### Lists

```plain
set nums to [1, 2, 3]
add 4 to nums          # append
say nums at 0          # index (0-based)
say len nums           # length → 4
```

### Import

```plain
import "utils.plain"           # relative to current file
import "../stdlib/math.plain"  # navigate directories
```

The imported file runs once in the same scope — all its functions and variables become available immediately.

### Built-in functions

| Function | What it does | Example |
|---|---|---|
| `say` | Print to the terminal | `say "hello"` |
| `ask` | Read a line of input | `set x to ask "? "` |
| `num` | Parse a string as a number | `set n to num "42"` |
| `str` | Convert a value to a string | `set s to str 3.14` |
| `len` | Length of a string or list | `say len "hello"` → 5 |
| `random` | Random integer in `[a, b]` | `set n to random 1 10` |

### Comments

```plain
# full-line comment
set x to 5   # inline comment
```

---

## Running files

```bash
python main.py examples/hello.plain
python main.py examples/fizzbuzz.plain
```

---

## Interactive REPL

```bash
python main.py
```

```
Plain language REPL — type your code below.
Type 'quit' or 'exit' to leave.

>>> set x to 10
>>> say x * 2
20
>>> fn double n
...     return n * 2
... end
>>> say double x
20
```

Multi-line blocks (fn, if, while, repeat) are buffered automatically — the `...` prompt appears until you close the block with `end`.

---

## Compiling to Python

Plain can output a `.py` file you can run directly with Python — useful for sharing programs without requiring the Plain runtime.

```bash
# via compiler directly
python compiler.py examples/hello.plain
# → writes examples/hello.py

# via main.py flag
python main.py --compile examples/fizzbuzz.plain
# → writes examples/fizzbuzz.py
```

The generated Python is clean and readable. Imported files are inlined automatically. Example output for `hello.plain`:

```python
print(_plain_str('Hello, world!'))
name = 'Saaz'
age = 21
if (age > 18):
    print(_plain_str('You are an adult.'))
else:
    print(_plain_str('You are a minor.'))
```

---

## Standard library

Plain ships with a small stdlib written in Plain itself (no Python):

**`stdlib/math.plain`** — `square`, `cube`, `abs`, `max`, `min`

```plain
import "stdlib/math.plain"

say square 5    # 25
say cube 3      # 27
say abs -4      # 4 (use: set n to 0 - 4 then abs n)
say max 10 3    # 10
say min 10 3    # 3
```

**`stdlib/strings.plain`** — `repeat_str`, `is_empty`

```plain
import "stdlib/strings.plain"

say repeat_str "ha" 3   # hahaha
say is_empty ""         # 1
say is_empty "hello"    # 0
```

---

## VSCode syntax highlighting

Copy the extension into your VS Code extensions folder:

```bash
cp -r vscode-extension ~/.vscode/extensions/plain-lang
```

Restart VS Code (or run **Developer: Reload Window**). Files ending in `.plain` will now have full syntax highlighting — keywords, strings, numbers, function names, comments, and built-ins.

See [`vscode-extension/README.md`](vscode-extension/README.md) for details.

---

## Examples

| File | What it shows |
|---|---|
| [`examples/hello.plain`](examples/hello.plain) | Variables, output, if/else |
| [`examples/calculator.plain`](examples/calculator.plain) | Input, arithmetic, division-by-zero guard |
| [`examples/guessgame.plain`](examples/guessgame.plain) | Loops, random numbers, nested if/else |
| [`examples/fizzbuzz.plain`](examples/fizzbuzz.plain) | While loops, counter logic |
| [`examples/utils.plain`](examples/utils.plain) | Defining reusable helper functions |
| [`examples/useutils.plain`](examples/useutils.plain) | Importing a local file |
| [`examples/usestdlib.plain`](examples/usestdlib.plain) | Using the standard library |

---

## Project structure

```
plain-lang/
├── lexer.py          — tokeniser
├── parser.py         — recursive-descent parser → AST
├── evaluator.py      — tree-walking interpreter
├── compiler.py       — AST → Python source
├── main.py           — CLI: run files, REPL, --compile
├── stdlib/
│   ├── math.plain    — square, cube, abs, max, min
│   └── strings.plain — repeat_str, is_empty
├── examples/
│   ├── hello.plain
│   ├── calculator.plain
│   ├── guessgame.plain
│   ├── fizzbuzz.plain
│   ├── utils.plain
│   ├── useutils.plain
│   └── usestdlib.plain
└── vscode-extension/
    ├── package.json
    ├── syntaxes/plain.tmLanguage.json
    └── README.md
```

---

## Contributing

Plain is intentionally small. Good contributions:

- New functions in `stdlib/` — written in Plain, not Python
- More example programs in `examples/`
- Better error messages in `evaluator.py`
- Bug reports and edge-case fixes

Keep the language readable. Every new feature should feel like natural English.

---

## License

MIT
