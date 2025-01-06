import ply.lex as lex

tokens = (
   'ID',
    'PLUS'
)

t_PLUS    = r'\+'

def t_ID(t):
    r'4"
    print(t.value)
    return t.value


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

if __name__ == '__main__':

    # Test it out
    data = '''4'''

    # Give the lexer some input
    lexer.input(data)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        print(tok)
