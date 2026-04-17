# main.py — entry point for Plain: run a file or start the REPL

import sys
import os
from lexer import Lexer
from parser import Parser, ParseError
from evaluator import Evaluator, PlainError


def run_source(source, evaluator=None, base_dir=None):
    """Lex, parse, and evaluate a Plain source string. Returns the evaluator."""
    if evaluator is None:
        evaluator = Evaluator()
    if base_dir is not None:
        evaluator.base_dir = base_dir
    try:
        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse()
        evaluator.evaluate(ast)
    except ParseError as e:
        print(f"Oops! Line {e.line}: {e}")
    except PlainError as e:
        print(f"Oops! Line {e.line}: {e}")
    except Exception as e:
        print(f"Oops! Something went wrong: {e}")
    return evaluator


def run_file(path):
    """Read a .plain file and execute it."""
    try:
        with open(path, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Oops! I couldn't find the file '{path}'.")
        sys.exit(1)
    base_dir = os.path.dirname(os.path.abspath(path))
    run_source(source, base_dir=base_dir)


def run_repl():
    """Interactive REPL — type Plain code line by line."""
    print("Plain language REPL — type your code below.")
    print("Type 'quit' or 'exit' to leave.\n")

    evaluator = Evaluator()  # shared state across REPL lines
    buffer = []              # accumulate multi-line blocks

    # keywords that open a block needing 'end'
    BLOCK_STARTERS = ("fn ", "if ", "repeat ", "while ")

    def needs_more(lines):
        """Count unmatched block openers to decide if we need more lines."""
        depth = 0
        for line in lines:
            stripped = line.strip()
            if any(stripped.startswith(k) for k in BLOCK_STARTERS):
                depth += 1
            elif stripped == "end":
                depth -= 1
        return depth > 0

    while True:
        prompt = "... " if buffer else ">>> "
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if line.strip() in ("quit", "exit"):
            print("Bye!")
            break

        buffer.append(line)

        # keep collecting until all blocks are closed
        if needs_more(buffer):
            continue

        source = "\n".join(buffer)
        buffer = []
        run_source(source, evaluator)


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--compile":
        from compiler import compile_file
        in_path = sys.argv[2]
        out_path = os.path.splitext(in_path)[0] + ".py"
        python_source = compile_file(in_path)
        if python_source is not None:
            with open(out_path, "w") as f:
                f.write(python_source)
            print(f"Compiled to {out_path}")
    elif len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        run_repl()
