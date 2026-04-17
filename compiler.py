# compiler.py — compiles .plain source to runnable Python

import sys
import os
from lexer import Lexer
from parser import Parser, ParseError


# ── Runtime helpers injected at the top of every compiled file ────────────────

RUNTIME = '''\
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

'''


# ── Error ─────────────────────────────────────────────────────────────────────

class CompileError(Exception):
    def __init__(self, message, line=0):
        super().__init__(message)
        self.line = line


# ── Compiler ──────────────────────────────────────────────────────────────────

class Compiler:
    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self._indent = 0
        self._out = []

    def _emit(self, line=""):
        self._out.append("    " * self._indent + line)

    def compile(self, nodes):
        self._out = [RUNTIME.rstrip()]
        self._emit("")
        self._emit("")
        for node in nodes:
            self._compile_node(node)
        return "\n".join(self._out) + "\n"

    # ── statements ────────────────────────────────────────────────────────────

    def _compile_node(self, node):
        t = type(node).__name__

        if t == "SetNode":
            self._emit(f"{node.name} = {self._expr(node.value)}")

        elif t == "SayNode":
            self._emit(f"print(_plain_str({self._expr(node.value)}))")

        elif t == "IfNode":
            self._emit(f"if {self._expr(node.condition)}:")
            self._indent += 1
            self._compile_body(node.body)
            self._indent -= 1
            if node.else_body:
                self._emit("else:")
                self._indent += 1
                self._compile_body(node.else_body)
                self._indent -= 1

        elif t == "RepeatTimesNode":
            self._emit(f"for _i in range(int({self._expr(node.count)})):")
            self._indent += 1
            self._compile_body(node.body)
            self._indent -= 1

        elif t == "RepeatWithNode":
            self._emit(f"for {node.var} in {self._expr(node.iterable)}:")
            self._indent += 1
            self._compile_body(node.body)
            self._indent -= 1

        elif t == "WhileNode":
            self._emit(f"while {self._expr(node.condition)}:")
            self._indent += 1
            self._compile_body(node.body)
            self._indent -= 1

        elif t == "FnNode":
            params = ", ".join(node.params)
            self._emit(f"def {node.name}({params}):")
            self._indent += 1
            self._compile_body(node.body)
            self._indent -= 1
            self._emit("")  # blank line after def

        elif t == "ReturnNode":
            self._emit(f"return {self._expr(node.value)}")

        elif t == "CallNode":
            args = ", ".join(self._expr(a) for a in node.args)
            self._emit(f"{node.name}({args})")

        elif t == "AddToNode":
            self._emit(f"{node.list_name}.append({self._expr(node.value)})")

        elif t == "ImportNode":
            self._inline_import(node)

    def _compile_body(self, stmts):
        if stmts:
            for s in stmts:
                self._compile_node(s)
        else:
            self._emit("pass")

    def _inline_import(self, node):
        """Read the imported file, compile its nodes, and inline them."""
        path = node.path
        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(self.base_dir, path))
        if not os.path.exists(path):
            raise CompileError(f"Oops! I couldn't find '{node.path}'", node.line)
        with open(path) as f:
            source = f.read()
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        saved_base = self.base_dir
        self.base_dir = os.path.dirname(path)
        self._emit(f"# --- imported from '{node.path}' ---")
        for n in ast:
            self._compile_node(n)
        self._emit(f"# --- end import ---")
        self._emit("")
        self.base_dir = saved_base

    # ── expressions ───────────────────────────────────────────────────────────

    def _expr(self, node):
        t = type(node).__name__

        if t == "NumberNode":
            return repr(node.value)

        if t == "StringNode":
            return repr(node.value)

        if t == "IdentNode":
            return node.name

        if t == "ListNode":
            elems = ", ".join(self._expr(e) for e in node.elements)
            return f"[{elems}]"

        if t == "IndexNode":
            return f"{node.name}[int({self._expr(node.index)})]"

        if t == "BinOpNode":
            left = self._expr(node.left)
            right = self._expr(node.right)
            if node.op == "PLUS":
                return f"_plain_add({left}, {right})"
            op_map = {
                "MINUS": "-", "STAR": "*", "SLASH": "/",
                "GT": ">", "LT": "<", "EQUALS": "==",
                "AND": "and", "OR": "or",
            }
            op = op_map[node.op]
            return f"({left} {op} {right})"

        if t == "UnaryOpNode":
            if node.op == "NOT":
                return f"(not {self._expr(node.operand)})"

        if t == "BuiltinCallNode":
            return self._builtin(node)

        if t == "CallNode":
            args = ", ".join(self._expr(a) for a in node.args)
            return f"{node.name}({args})"

        return "None"

    def _builtin(self, node):
        f = node.func
        if f == "ASK":
            arg = self._expr(node.args[0]) if node.args else '""'
            return f"input({arg})"
        if f == "NUM":
            arg = self._expr(node.args[0]) if node.args else "0"
            return f"_plain_num({arg})"
        if f == "STR":
            arg = self._expr(node.args[0]) if node.args else '""'
            return f"_plain_str({arg})"
        if f == "LEN":
            arg = self._expr(node.args[0]) if node.args else "[]"
            return f"len({arg})"
        if f == "RANDOM":
            a = self._expr(node.args[0])
            b = self._expr(node.args[1])
            return f"_random.randint(int({a}), int({b}))"
        return "None"


# ── Public API ────────────────────────────────────────────────────────────────

def compile_file(path):
    """Read a .plain file and return compiled Python source (or None on error)."""
    try:
        with open(path) as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Oops! I couldn't find '{path}'.")
        return None

    base_dir = os.path.dirname(os.path.abspath(path))
    try:
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
    except ParseError as e:
        print(f"Oops! Line {e.line}: {e}")
        return None

    compiler = Compiler(base_dir=base_dir)
    try:
        return compiler.compile(ast)
    except CompileError as e:
        print(f"Oops! Line {e.line}: {e}")
        return None


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <file.plain>")
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = os.path.splitext(in_path)[0] + ".py"
    python_source = compile_file(in_path)

    if python_source is not None:
        with open(out_path, "w") as f:
            f.write(python_source)
        print(f"Compiled to {out_path}")
