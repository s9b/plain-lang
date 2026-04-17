# parser.py — turns the token list into an Abstract Syntax Tree (AST)

# ── AST node definitions ──────────────────────────────────────────────────────

class SetNode:
    # set name to <expr>
    def __init__(self, name, value, line=0):
        self.name = name
        self.value = value
        self.line = line

class SayNode:
    # say <expr>
    def __init__(self, value, line=0):
        self.value = value
        self.line = line

class IfNode:
    # if <cond> then ... [else ...] end
    def __init__(self, condition, body, else_body=None, line=0):
        self.condition = condition
        self.body = body
        self.else_body = else_body or []
        self.line = line

class RepeatTimesNode:
    # repeat <n> times ... end
    def __init__(self, count, body, line=0):
        self.count = count
        self.body = body
        self.line = line

class RepeatWithNode:
    # repeat with <var> in <list> ... end
    def __init__(self, var, iterable, body, line=0):
        self.var = var
        self.iterable = iterable
        self.body = body
        self.line = line

class WhileNode:
    # while <cond> ... end
    def __init__(self, condition, body, line=0):
        self.condition = condition
        self.body = body
        self.line = line

class FnNode:
    # fn <name> [params...] ... end
    def __init__(self, name, params, body, line=0):
        self.name = name
        self.params = params
        self.body = body
        self.line = line

class ReturnNode:
    # return <expr>
    def __init__(self, value, line=0):
        self.value = value
        self.line = line

class CallNode:
    # <name> <args...>
    def __init__(self, name, args, line=0):
        self.name = name
        self.args = args
        self.line = line

class AddToNode:
    # add <value> to <list>
    def __init__(self, value, list_name, line=0):
        self.value = value
        self.list_name = list_name
        self.line = line

class BinOpNode:
    # left <op> right
    def __init__(self, left, op, right, line=0):
        self.left = left
        self.op = op
        self.right = right
        self.line = line

class UnaryOpNode:
    # not <expr>
    def __init__(self, op, operand, line=0):
        self.op = op
        self.operand = operand
        self.line = line

class NumberNode:
    def __init__(self, value, line=0):
        self.value = value
        self.line = line

class StringNode:
    def __init__(self, value, line=0):
        self.value = value
        self.line = line

class IdentNode:
    def __init__(self, name, line=0):
        self.name = name
        self.line = line

class ListNode:
    # [1, 2, 3]
    def __init__(self, elements, line=0):
        self.elements = elements
        self.line = line

class IndexNode:
    # items at 0
    def __init__(self, name, index, line=0):
        self.name = name
        self.index = index
        self.line = line

class BuiltinCallNode:
    # ask / num / str / len / random
    def __init__(self, func, args, line=0):
        self.func = func
        self.args = args
        self.line = line

class ImportNode:
    # import "file.plain"
    def __init__(self, path, line=0):
        self.path = path
        self.line = line


# ── Parser ────────────────────────────────────────────────────────────────────

# Token types that can start an expression value (used to detect call args)
EXPR_STARTERS = {"NUMBER", "STRING", "IDENT", "LBRACKET", "LPAREN", "NOT",
                 "ASK", "NUM", "STR", "LEN", "RANDOM"}

# Token types that are statement keywords (used to stop collecting call args)
STATEMENT_KEYWORDS = {"SET", "SAY", "IF", "END", "ELSE", "FN", "RETURN",
                      "REPEAT", "WHILE", "ADD", "IMPORT", "EOF"}

class ParseError(Exception):
    def __init__(self, message, line=0):
        super().__init__(message)
        self.line = line


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def peek(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def eat(self, expected_type):
        token = self.current()
        if token.type != expected_type:
            raise ParseError(
                f"Expected '{expected_type}' but got '{token.type}'",
                token.line
            )
        self.pos += 1
        return token

    def parse(self):
        statements = []
        while self.current().type != "EOF":
            statements.append(self.parse_statement())
        return statements

    def parse_block(self, stop_at=("END",)):
        """Parse statements until we hit one of the stop_at token types."""
        body = []
        while self.current().type not in stop_at and self.current().type != "EOF":
            body.append(self.parse_statement())
        return body

    # ── statements ────────────────────────────────────────────────────────────

    def parse_statement(self):
        token = self.current()
        t = token.type

        if t == "SET":    return self.parse_set()
        if t == "SAY":    return self.parse_say()
        if t == "IF":     return self.parse_if()
        if t == "FN":     return self.parse_fn()
        if t == "RETURN": return self.parse_return()
        if t == "REPEAT": return self.parse_repeat()
        if t == "WHILE":  return self.parse_while()
        if t == "ADD":    return self.parse_add()
        if t == "IMPORT": return self.parse_import()

        # bare function call: identifier followed by argument(s)
        if t == "IDENT":
            return self.parse_call_statement()

        raise ParseError(f"Unexpected token: '{t}'", token.line)

    def parse_set(self):
        line = self.current().line
        self.eat("SET")
        name = self.eat("IDENT").value
        self.eat("TO")
        value = self.parse_expr()
        return SetNode(name, value, line)

    def parse_say(self):
        line = self.current().line
        self.eat("SAY")
        value = self.parse_expr()
        return SayNode(value, line)

    def parse_if(self):
        line = self.current().line
        self.eat("IF")
        condition = self.parse_condition()
        self.eat("THEN")
        body = self.parse_block(stop_at=("END", "ELSE"))
        else_body = []
        if self.current().type == "ELSE":
            self.eat("ELSE")
            else_body = self.parse_block(stop_at=("END",))
        if self.current().type != "END":
            raise ParseError("Expected 'end' to close 'if'", self.current().line)
        self.eat("END")
        return IfNode(condition, body, else_body, line)

    def parse_fn(self):
        line = self.current().line
        self.eat("FN")
        name = self.eat("IDENT").value
        # collect parameter names until something non-IDENT
        params = []
        while self.current().type == "IDENT":
            params.append(self.eat("IDENT").value)
        body = self.parse_block(stop_at=("END",))
        if self.current().type != "END":
            raise ParseError("Expected 'end' to close 'fn'", self.current().line)
        self.eat("END")
        return FnNode(name, params, body, line)

    def parse_return(self):
        line = self.current().line
        self.eat("RETURN")
        value = self.parse_expr()
        return ReturnNode(value, line)

    def parse_repeat(self):
        line = self.current().line
        self.eat("REPEAT")
        # repeat with <var> in <iterable>
        if self.current().type == "WITH":
            self.eat("WITH")
            var = self.eat("IDENT").value
            self.eat("IN")
            iterable = self.parse_expr()
            body = self.parse_block(stop_at=("END",))
            self.eat("END")
            return RepeatWithNode(var, iterable, body, line)
        # repeat <n> times
        count = self.parse_expr()
        self.eat("TIMES")
        body = self.parse_block(stop_at=("END",))
        self.eat("END")
        return RepeatTimesNode(count, body, line)

    def parse_while(self):
        line = self.current().line
        self.eat("WHILE")
        condition = self.parse_condition()
        body = self.parse_block(stop_at=("END",))
        self.eat("END")
        return WhileNode(condition, body, line)

    def parse_import(self):
        line = self.current().line
        self.eat("IMPORT")
        path_token = self.eat("STRING")
        return ImportNode(path_token.value, line)

    def parse_add(self):
        # add <value> to <list>
        line = self.current().line
        self.eat("ADD")
        value = self.parse_expr()
        self.eat("TO")
        list_name = self.eat("IDENT").value
        return AddToNode(value, list_name, line)

    def parse_call_statement(self):
        """Parse a bare function call used as a statement."""
        line = self.current().line
        name = self.eat("IDENT").value
        args = []
        while (self.current().type in EXPR_STARTERS and
               self.current().type not in STATEMENT_KEYWORDS and
               self.current().line == line):
            args.append(self.parse_primary())
        return CallNode(name, args, line)

    # ── conditions ────────────────────────────────────────────────────────────

    def parse_condition(self):
        """Parse a condition with optional and/or chaining."""
        left = self.parse_single_condition()
        while self.current().type in ("AND", "OR"):
            op = self.current().type
            self.pos += 1
            right = self.parse_single_condition()
            left = BinOpNode(left, op, right)
        return left

    def parse_single_condition(self):
        # not <cond>
        if self.current().type == "NOT":
            line = self.current().line
            self.pos += 1
            operand = self.parse_single_condition()
            return UnaryOpNode("NOT", operand, line)

        left = self.parse_expr()
        op_token = self.current()

        # symbolic operators
        if op_token.type in ("GT", "LT", "EQUALS"):
            self.pos += 1
            right = self.parse_expr()
            return BinOpNode(left, op_token.type, right, op_token.line)

        # "is greater than" / "is less than" / "is equal to"
        if op_token.type == "IS":
            self.pos += 1
            nxt = self.current().type
            if nxt == "GREATER":
                self.pos += 1; self.eat("THAN")
                right = self.parse_expr()
                return BinOpNode(left, "GT", right, op_token.line)
            if nxt == "LESS":
                self.pos += 1; self.eat("THAN")
                right = self.parse_expr()
                return BinOpNode(left, "LT", right, op_token.line)
            if nxt == "EQUAL":
                self.pos += 1; self.eat("TO")
                right = self.parse_expr()
                return BinOpNode(left, "EQUALS", right, op_token.line)
            raise ParseError("Expected 'greater than', 'less than', or 'equal to' after 'is'", op_token.line)

        return left

    # ── expressions ──────────────────────────────────────────────────────────

    def parse_expr(self):
        left = self.parse_term()
        while self.current().type in ("PLUS", "MINUS"):
            op = self.current().type
            line = self.current().line
            self.pos += 1
            right = self.parse_term()
            left = BinOpNode(left, op, right, line)
        return left

    def parse_term(self):
        left = self.parse_primary()
        while self.current().type in ("STAR", "SLASH"):
            op = self.current().type
            line = self.current().line
            self.pos += 1
            right = self.parse_primary()
            left = BinOpNode(left, op, right, line)
        return left

    def parse_primary(self):
        token = self.current()

        if token.type == "NUMBER":
            self.pos += 1
            return NumberNode(token.value, token.line)

        if token.type == "STRING":
            self.pos += 1
            return StringNode(token.value, token.line)

        if token.type == "LPAREN":
            self.pos += 1
            expr = self.parse_expr()
            if self.current().type != "RPAREN":
                raise ParseError("Expected ')' to close '('", self.current().line)
            self.pos += 1
            return expr

        if token.type == "LBRACKET":
            return self.parse_list()

        # built-in functions as expressions
        if token.type in ("ASK", "NUM", "STR", "LEN", "RANDOM"):
            return self.parse_builtin()

        if token.type == "IDENT":
            self.pos += 1
            # items at 0 → index access
            if self.current().type == "IDENT" and self.current().value == "at":
                line = token.line
                self.pos += 1  # consume "at"
                index = self.parse_primary()
                return IndexNode(token.value, index, line)
            # user-defined function call used as an expression.
            # only collect args on the same source line to avoid swallowing
            # the next statement when it starts with an identifier.
            fn_line = token.line
            if (self.current().type in EXPR_STARTERS and
                    self.current().type not in STATEMENT_KEYWORDS and
                    self.current().line == fn_line):
                args = []
                while (self.current().type in EXPR_STARTERS and
                       self.current().type not in STATEMENT_KEYWORDS and
                       self.current().line == fn_line):
                    args.append(self.parse_primary())
                return CallNode(token.value, args, token.line)
            return IdentNode(token.value, token.line)

        raise ParseError(
            f"Unexpected token in expression: '{token.type}'",
            token.line
        )

    def parse_list(self):
        line = self.current().line
        self.eat("LBRACKET")
        elements = []
        while self.current().type != "RBRACKET":
            elements.append(self.parse_expr())
            if self.current().type == "COMMA":
                self.pos += 1
        self.eat("RBRACKET")
        return ListNode(elements, line)

    def parse_builtin(self):
        token = self.current()
        func = token.type  # ASK / NUM / STR / LEN / RANDOM
        line = token.line
        self.pos += 1
        args = []
        while (self.current().type in EXPR_STARTERS and
               self.current().type not in STATEMENT_KEYWORDS and
               self.current().line == line):
            args.append(self.parse_primary())
        return BuiltinCallNode(func, args, line)


# --- quick test ---
if __name__ == "__main__":
    from lexer import Lexer
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
'''
    tokens = Lexer(code).tokenize()
    ast = Parser(tokens).parse()
    for node in ast:
        print(type(node).__name__)
