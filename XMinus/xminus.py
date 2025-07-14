import shlex

# Token types
TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_STRING = "STRING"
TT_VAR = "VAR"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MULT = "MULT"
TT_DIV = "DIV"
TT_DDIV = "DOUBLE_DIV"
TT_EQUAL = "EQUAL"
TT_PLUEQU = "PLUS_EQUAL"
TT_MINEQU = "MINUS_EQUAL"
TT_MULEQU = "MULT_EQUAL"
TT_DIVEQU = "DIV_EQUAL"
TT_DDIVEQU = "DOUBLE_DIV_EQUAL"
TT_LPAREN = "LEFT_PAREN"
TT_RPAREN = "RIGHT_PAREN"
TT_LOG = "LOG"

OPERATORS = {
    "+": TT_PLUS, "-": TT_MINUS, "*": TT_MULT, "/": TT_DIV, "//": TT_DDIV,
    "=": TT_EQUAL, "+=": TT_PLUEQU, "-=": TT_MINEQU, "*=": TT_MULEQU,
    "/=": TT_DIVEQU, "//=": TT_DDIVEQU, "(": TT_LPAREN, ")": TT_RPAREN,
}

ASSIGNMENTS = {
    "=": TT_EQUAL, "+=": TT_PLUEQU, "-=": TT_MINEQU, "*=": TT_MULEQU,
    "/=": TT_DIVEQU, "//=": TT_DDIVEQU,
}

KEYWORDS = {
    "class", "func", "for", "while", "with", "and", "or", "if",
    "elif", "else", "not", "=", "==", "!=", ">=", "<=", ">", "<", "log"
}

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token(type='{self.type}', value={self.value})"

class Tokenizer:
    def tokenize(self, string):
        if not string:
            return []
        lexer = shlex.shlex(string, posix=False)
        lexer.whitespace_split = True
        lexer.commenters = ''
        return list(lexer)

class Parser:
    def __init__(self):
        self.vars = {}

    def _is_string(self, text):
        return (
            (text.startswith('"') and text.endswith('"')) or
            (text.startswith("'") and text.endswith("'"))
        )

    def _is_float(self, token):
        try:
            float(token)
            return '.' in token
        except ValueError:
            return False

    def parse(self, line):
        raw_tokens = Tokenizer().tokenize(line)
        self.tokens = []

        i = 0
        while i < len(raw_tokens):
            token = raw_tokens[i]

            if self._is_string(token):
                self.tokens.append(Token(TT_STRING, token[1:-1]))
            elif token.isdigit():
                self.tokens.append(Token(TT_INT, int(token)))
            elif self._is_float(token):
                self.tokens.append(Token(TT_FLOAT, float(token)))
            elif token.startswith("log(") and token.endswith(")"):
                inner = token[4:-1]
                if self._is_string(inner):
                    self.tokens.append(Token(TT_LOG, inner[1:-1]))
                else:
                    self.tokens.append(Token(TT_LOG, inner))
            elif token in OPERATORS:
                self.tokens.append(Token(OPERATORS[token], token))
            elif token.isidentifier():
                if token.lower() in KEYWORDS:
                    raise SyntaxError(f"{token} cannot be a keyword.")
                else:
                    self.tokens.append(Token(TT_VAR, token))
            i += 1

        return self.tokens

    def _is_expr(self, expr):
        tokens = self.parse(expr)
        # This now returns True only if there's no assignment
        return not any(token.type in ASSIGNMENTS for token in tokens)


class Lexer:
    def __init__(self):
        self.parser = Parser()

    def evaluate(self, line):
        tokens = self.parser.parse(line)
        if not tokens:
            return None

        if (
            len(tokens) >= 3 and
            tokens[0].type == TT_VAR and
            tokens[1].type == TT_EQUAL
        ):
            var_name = tokens[0].value
            value_token = tokens[2]
            if value_token.type in {TT_STRING, TT_INT, TT_FLOAT}:
                self.parser.vars[var_name] = value_token.value
                return tokens
            else:
                return f"Cannot assign unsupported type '{value_token.type}'"
        return tokens

    def run(self, line):
        tokens = self.evaluate(line)
        code_line = ""

        for i, token in enumerate(tokens):
            if token.type == TT_VAR:
                if i + 1 < len(tokens) and tokens[i + 1].type != TT_EQUAL:
                    if token.value in self.parser.vars:
                        code_line += str(self.parser.vars[token.value]) + " "
                    else:
                        raise SyntaxError(f"{token.value} is not defined")
                else:
                    code_line += token.value + " "
            elif token.type == TT_LOG:
                if token.value in self.parser.vars:
                    code_line += f"print({repr(self.parser.vars[token.value])})"
                elif self.parser._is_string(f'"{token.value}"'):
                    code_line += f"print({repr(token.value)})"
                else:
                    raise SyntaxError(f"{token.value} is not a defined variable or a string.")
                break
            else:
                code_line += str(token.value) + " "
        
        return exec(code_line)

# --- Test Usage ---
if __name__ == "__main__":
    import sys
    lexer = Lexer()
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            for line in f:
                lexer.run(line.strip())
    else:
        print("Usage: python your_script.py '<code_to_parse>'")
