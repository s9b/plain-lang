# evaluator.py — walks the AST and executes Plain programs

import os
import random as _random


# ── Internal signals ──────────────────────────────────────────────────────────

class ReturnSignal(Exception):
    """Raised by 'return' to unwind back to the function call site."""
    def __init__(self, value):
        self.value = value


class PlainError(Exception):
    """Human-friendly runtime error with line number."""
    def __init__(self, message, line=0):
        super().__init__(message)
        self.line = line


# ── Evaluator ─────────────────────────────────────────────────────────────────

class Evaluator:
    def __init__(self):
        self.memory = {}      # global variable store
        self.functions = {}   # user-defined functions: name → FnNode
        self.base_dir = "."   # directory used to resolve import paths

    def evaluate(self, nodes):
        for node in nodes:
            self.eval_node(node)

    def eval_node(self, node):
        name = type(node).__name__

        # ── variable assignment ───────────────────────────────────────────────
        if name == "SetNode":
            self.memory[node.name] = self.eval_node(node.value)

        # ── output ───────────────────────────────────────────────────────────
        elif name == "SayNode":
            value = self.eval_node(node.value)
            print(self._to_str(value))

        # ── if / else ────────────────────────────────────────────────────────
        elif name == "IfNode":
            if self.eval_node(node.condition):
                for stmt in node.body:
                    self.eval_node(stmt)
            elif node.else_body:
                for stmt in node.else_body:
                    self.eval_node(stmt)

        # ── repeat N times ───────────────────────────────────────────────────
        elif name == "RepeatTimesNode":
            count = self.eval_node(node.count)
            if not isinstance(count, (int, float)):
                raise PlainError("'repeat' needs a number", node.line)
            for _ in range(int(count)):
                for stmt in node.body:
                    self.eval_node(stmt)

        # ── repeat with item in list ──────────────────────────────────────────
        elif name == "RepeatWithNode":
            iterable = self.eval_node(node.iterable)
            if not isinstance(iterable, list):
                raise PlainError(
                    f"'repeat with' needs a list, not '{self._type_name(iterable)}'",
                    node.line
                )
            for item in iterable:
                self.memory[node.var] = item
                for stmt in node.body:
                    self.eval_node(stmt)

        # ── while ────────────────────────────────────────────────────────────
        elif name == "WhileNode":
            while self.eval_node(node.condition):
                for stmt in node.body:
                    self.eval_node(stmt)

        # ── function definition ───────────────────────────────────────────────
        elif name == "FnNode":
            self.functions[node.name] = node

        # ── return ───────────────────────────────────────────────────────────
        elif name == "ReturnNode":
            raise ReturnSignal(self.eval_node(node.value))

        # ── function call (statement or expression form) ──────────────────────
        elif name == "CallNode":
            return self._call_function(node.name, node.args, node.line)

        # ── add to list ───────────────────────────────────────────────────────
        elif name == "AddToNode":
            lst = self.memory.get(node.list_name)
            if lst is None:
                raise PlainError(
                    f"Oops! I don't know what '{node.list_name}' is. Did you set it?",
                    node.line
                )
            if not isinstance(lst, list):
                raise PlainError(
                    f"Oops! '{node.list_name}' is not a list.",
                    node.line
                )
            lst.append(self.eval_node(node.value))

        # ── binary operations ─────────────────────────────────────────────────
        elif name == "BinOpNode":
            return self._eval_binop(node)

        # ── unary not ────────────────────────────────────────────────────────
        elif name == "UnaryOpNode":
            if node.op == "NOT":
                return not self.eval_node(node.operand)

        # ── literals ─────────────────────────────────────────────────────────
        elif name == "NumberNode":
            return node.value

        elif name == "StringNode":
            return node.value

        # ── list literal ─────────────────────────────────────────────────────
        elif name == "ListNode":
            return [self.eval_node(e) for e in node.elements]

        # ── index access: items at 0 ──────────────────────────────────────────
        elif name == "IndexNode":
            lst = self.memory.get(node.name)
            if lst is None:
                raise PlainError(
                    f"Oops! I don't know what '{node.name}' is. Did you set it?",
                    node.line
                )
            idx = self.eval_node(node.index)
            try:
                return lst[int(idx)]
            except IndexError:
                raise PlainError(
                    f"Oops! Index {int(idx)} is out of range for '{node.name}'.",
                    node.line
                )

        # ── variable lookup ───────────────────────────────────────────────────
        elif name == "IdentNode":
            if node.name not in self.memory:
                raise PlainError(
                    f"Oops! I don't know what '{node.name}' is. Did you set it?",
                    node.line
                )
            return self.memory[node.name]

        # ── import ────────────────────────────────────────────────────────────
        elif name == "ImportNode":
            self._eval_import(node)

        # ── built-in functions ────────────────────────────────────────────────
        elif name == "BuiltinCallNode":
            return self._eval_builtin(node)

        else:
            raise PlainError(f"Unknown node type: {name}", getattr(node, 'line', 0))

    # ── helpers ───────────────────────────────────────────────────────────────

    def _eval_import(self, node):
        path = node.path
        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(self.base_dir, path))
        if not os.path.exists(path):
            raise PlainError(f"Oops! I couldn't find '{node.path}'", node.line)
        with open(path) as f:
            source = f.read()
        from lexer import Lexer
        from parser import Parser
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        saved_base = self.base_dir
        self.base_dir = os.path.dirname(path)
        self.evaluate(ast)
        self.base_dir = saved_base

    def _eval_binop(self, node):
        left  = self.eval_node(node.left)
        right = self.eval_node(node.right)
        op    = node.op

        if op == "PLUS":
            # string + anything → string concatenation
            if isinstance(left, str) or isinstance(right, str):
                return self._to_str(left) + self._to_str(right)
            return left + right
        if op == "MINUS": return left - right
        if op == "STAR":  return left * right
        if op == "SLASH":
            if right == 0:
                raise PlainError("Oops! Can't divide by zero.", node.line)
            return left / right
        if op == "GT":     return left > right
        if op == "LT":     return left < right
        if op == "EQUALS": return left == right
        if op == "AND":    return bool(left) and bool(right)
        if op == "OR":     return bool(left) or bool(right)
        raise PlainError(f"Unknown operator: {op}", node.line)

    def _call_function(self, name, arg_nodes, line):
        if name not in self.functions:
            raise PlainError(
                f"Oops! I don't know a function called '{name}'. Did you define it?",
                line
            )
        fn = self.functions[name]
        if len(arg_nodes) != len(fn.params):
            raise PlainError(
                f"Oops! '{name}' needs {len(fn.params)} input(s) but you gave {len(arg_nodes)}.",
                line
            )
        # evaluate arguments in current scope
        arg_values = [self.eval_node(a) for a in arg_nodes]
        # save global memory, create local scope
        saved = self.memory.copy()
        self.memory = saved.copy()
        for param, val in zip(fn.params, arg_values):
            self.memory[param] = val
        result = None
        try:
            for stmt in fn.body:
                self.eval_node(stmt)
        except ReturnSignal as r:
            result = r.value
        finally:
            self.memory = saved  # restore outer scope
        return result

    def _eval_builtin(self, node):
        func = node.func
        args = node.args
        line = node.line

        if func == "ASK":
            prompt = self._eval_args(args, 1, "ask", line)[0]
            return input(self._to_str(prompt))

        if func == "NUM":
            val = self._eval_args(args, 1, "num", line)[0]
            try:
                return float(val) if '.' in str(val) else int(val)
            except (ValueError, TypeError):
                raise PlainError(
                    f"Oops! Can't convert '{val}' to a number.",
                    line
                )

        if func == "STR":
            val = self._eval_args(args, 1, "str", line)[0]
            return self._to_str(val)

        if func == "LEN":
            val = self._eval_args(args, 1, "len", line)[0]
            if isinstance(val, (str, list)):
                return len(val)
            raise PlainError(
                f"Oops! 'len' works on strings and lists, not '{self._type_name(val)}'.",
                line
            )

        if func == "RANDOM":
            a, b = self._eval_args(args, 2, "random", line)
            return _random.randint(int(a), int(b))

        raise PlainError(f"Unknown built-in: {func}", line)

    def _eval_args(self, arg_nodes, expected, name, line):
        vals = [self.eval_node(a) for a in arg_nodes]
        if len(vals) != expected:
            raise PlainError(
                f"Oops! '{name}' needs {expected} input(s) but you gave {len(vals)}.",
                line
            )
        return vals

    def _to_str(self, val):
        """Convert any Plain value to a display string."""
        if isinstance(val, bool):
            return "true" if val else "false"
        if isinstance(val, float) and val == int(val):
            return str(int(val))  # show 3 not 3.0
        if isinstance(val, list):
            return "[" + ", ".join(self._to_str(v) for v in val) + "]"
        return str(val)

    def _type_name(self, val):
        if isinstance(val, bool):   return "boolean"
        if isinstance(val, (int, float)): return "number"
        if isinstance(val, str):    return "string"
        if isinstance(val, list):   return "list"
        return type(val).__name__


# --- quick test ---
if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser

    code = '''
fn greet name
    say "Hey " + name
end
set score to 95
greet "Saaz"
if score is greater than 90 then
    say "Grade A"
else
    say "Try harder"
end
repeat 3 times
    say "tick"
end
set items to [10, 20, 30]
add 40 to items
say items
say items at 2
'''
    tokens = Lexer(code).tokenize()
    ast = Parser(tokens).parse()
    Evaluator().evaluate(ast)
