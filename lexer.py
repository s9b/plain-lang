# lexer.py — breaks Plain source code into a list of tokens

class Token:
    def __init__(self, type, value=None, line=1):
        self.type = type
        self.value = value
        self.line = line  # track line number for error messages

    def __repr__(self):
        if self.value is not None:
            return f"{self.type}({self.value})"
        return self.type


# All reserved keywords and their token types
KEYWORDS = {
    "set":      "SET",
    "to":       "TO",
    "say":      "SAY",
    "if":       "IF",
    "then":     "THEN",
    "else":     "ELSE",
    "end":      "END",
    "fn":       "FN",
    "return":   "RETURN",
    "repeat":   "REPEAT",
    "times":    "TIMES",
    "while":    "WHILE",
    "and":      "AND",
    "or":       "OR",
    "not":      "NOT",
    "is":       "IS",
    "greater":  "GREATER",
    "less":     "LESS",
    "equal":    "EQUAL",
    "than":     "THAN",
    "add":      "ADD",
    "with":     "WITH",
    "in":       "IN",
    "ask":      "ASK",
    "num":      "NUM",
    "str":      "STR",
    "len":      "LEN",
    "random":   "RANDOM",
    "import":   "IMPORT",
}


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.tokens = []
        self.line = 1  # current line number

    def current(self):
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def advance(self):
        if self.current() == '\n':
            self.line += 1
        self.pos += 1

    def tokenize(self):
        while self.current() is not None:
            ch = self.current()

            # skip comments — everything after # until newline
            if ch == '#':
                while self.current() and self.current() != '\n':
                    self.advance()
                continue

            # skip whitespace
            if ch in (' ', '\t', '\r'):
                self.advance()
                continue

            if ch == '\n':
                self.advance()
                continue

            # numbers (support floats)
            if ch.isdigit():
                num = ""
                while self.current() and (self.current().isdigit() or self.current() == '.'):
                    num += self.current()
                    self.advance()
                val = float(num) if '.' in num else int(num)
                self.tokens.append(Token("NUMBER", val, self.line))
                continue

            # strings in double quotes
            if ch == '"':
                self.advance()  # skip opening quote
                string = ""
                while self.current() and self.current() != '"':
                    string += self.current()
                    self.advance()
                self.advance()  # skip closing quote
                self.tokens.append(Token("STRING", string, self.line))
                continue

            # words: keywords or identifiers
            if ch.isalpha() or ch == '_':
                word = ""
                while self.current() and (self.current().isalnum() or self.current() == '_'):
                    word += self.current()
                    self.advance()
                token_type = KEYWORDS.get(word, "IDENT")
                # identifiers store their name; keywords don't need value
                val = word if token_type == "IDENT" else None
                self.tokens.append(Token(token_type, val, self.line))
                continue

            # brackets, parens, comma
            if ch == '[':  self.tokens.append(Token("LBRACKET", None, self.line)); self.advance(); continue
            if ch == ']':  self.tokens.append(Token("RBRACKET", None, self.line)); self.advance(); continue
            if ch == '(':  self.tokens.append(Token("LPAREN",   None, self.line)); self.advance(); continue
            if ch == ')':  self.tokens.append(Token("RPAREN",   None, self.line)); self.advance(); continue
            if ch == ',':  self.tokens.append(Token("COMMA",    None, self.line)); self.advance(); continue

            # arithmetic and comparison operators
            if ch == '+': self.tokens.append(Token("PLUS",   None, self.line)); self.advance(); continue
            if ch == '-': self.tokens.append(Token("MINUS",  None, self.line)); self.advance(); continue
            if ch == '*': self.tokens.append(Token("STAR",   None, self.line)); self.advance(); continue
            if ch == '/': self.tokens.append(Token("SLASH",  None, self.line)); self.advance(); continue
            if ch == '>': self.tokens.append(Token("GT",     None, self.line)); self.advance(); continue
            if ch == '<': self.tokens.append(Token("LT",     None, self.line)); self.advance(); continue
            if ch == '=': self.tokens.append(Token("EQUALS", None, self.line)); self.advance(); continue

            # unknown character — skip silently
            self.advance()

        self.tokens.append(Token("EOF", None, self.line))
        return self.tokens


# --- quick test ---
if __name__ == "__main__":
    code = '''
# this is a comment
set name to "Saaz"
set score to 95
if score is greater than 90 then
    say "A grade"
end
repeat 3 times
    say "hi"
end
'''
    for t in Lexer(code).tokenize():
        print(t)
