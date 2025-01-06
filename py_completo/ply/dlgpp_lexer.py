import tarfile

import ply.lex as lex
from ply.lex import TOKEN

reserved = {
    "@rules" : 'RULES',
    "@facts" : 'FACTS',
    "@constraints" : 'CONSTRAINTS',
    "@queries" : 'QUERIES',
    "@base": "BASE",
    "@prefix": "PREFIX",
    "@top": "TOP",
    "@una": "UNA"
}

tokens = list(reserved.values()) + [
    "EQUALITY_MARK",
    "END_MARK",
    "ABSURD_MARK",
    "RULE_MARK",
    "QUESTION_MARK",
    "START_STATEMENT_MARK",
    "END_STATEMENT_MARK",
    "START_TERMS_MARK",
    "END_TERMS_MARK",
    "SEPARATOR",
    "NEGATION",
    "TOPTOP",
    "IRIREF",
    "LANGTAG",
    "DOUBLE",
    "DECIMAL",
    "INTEGER",
    "BOOLEAN",
    "STRING",
    "PNAME_LN",
    "PNAME_NS",
    "FLOAT",
    "U_IDENT",
    "L_IDENT",
    "BLANK_NODE_LABEL",
    "LABEL"
]




t_TOPTOP = '\^\^'
t_RULE_MARK = ':-'
t_NEGATION = '-'
t_EQUALITY_MARK = '\='
t_END_MARK = '\.'
t_ABSURD_MARK = '!'
t_QUESTION_MARK = '\?'
t_START_STATEMENT_MARK = '\['
t_END_STATEMENT_MARK = '\]'
t_START_TERMS_MARK = '\('
t_END_TERMS_MARK = '\)'
t_SEPARATOR = '\,'


UPPERCASE_LETTER = r'([A-Z])'
LOWERCASE_LETTER = r'([a-z])'
LETTER = rf'({UPPERCASE_LETTER})|({LOWERCASE_LETTER})'
DIGIT = r'([0-9])'
SIMPLE_CHAR = rf'({LETTER})|({DIGIT})|([\_])'
CHAR = r'([^\n\\\"])'
SIGN = r'([\+\-])'
EXPO = r'([eE])'
SIMPLE_STRING = rf'({SIMPLE_CHAR})+'
NORMAL_STRING = rf'({CHAR})+'
NUMBER = rf'({DIGIT})+'
EXPONENT1 = rf'({EXPO})({SIGN})({NUMBER})'
WHITESPACE = r'([\s\t\n\r])'

t_FLOAT = rf'[\-]{NUMBER}[\.]{DIGIT}*{EXPONENT1}?|[\-][\.]{NUMBER}{EXPONENT1}?|[\-]{NUMBER}{EXPONENT1}'

t_U_IDENT = rf'{UPPERCASE_LETTER}({SIMPLE_CHAR})*'
t_L_IDENT = rf'{LOWERCASE_LETTER}({SIMPLE_CHAR})*'


HEX = r'([0-9]|[A-F]|[a-f])'
UCHAR         = rf'(\\u({HEX})({HEX})({HEX})({HEX}))|(\\U({HEX})({HEX})({HEX})({HEX})({HEX})({HEX})({HEX})({HEX}))'
ECHAR         = r'\\[tbnrf"\'\\]'
PERCENT	      =	rf'(%({HEX})({HEX}))'
PN_CHARS_BASE = r'([A-Z]|[a-z]|[\u00C0-\u00D6]|[\u00D8-\u00F6]|[\u00F8-\u02FF]|[\u0370-\u037D]|[\u037F-\u1FFF]|[\u200C-\u200D]|[\u2070-\u218F]|[\u2C00-\u2FEF]|[\u3001-\uD7FF]|[\uF900-\uFDCF]|[\uFDF0-\uFFFD]|[\U00010000-\U000EFFFF])'
PN_CHARS_U    = rf'(({PN_CHARS_BASE})|_)'
PN_CHARS      = rf'(({PN_CHARS_U})|-|[0-9]|\u00B7|[\u0300-\u036F]|[\u203F-\u2040])'
PN_PREFIX	    =	rf'(({PN_CHARS_BASE})((({PN_CHARS})|\.)*({PN_CHARS}))?)'
PN_LOCAL_ESC  =	r'\\(_|~|\.|\-|\!|\$|\&|\'|\(|\)|\*|\+|\,|\;|\=|\/|\?|\#|\@|\%)'
PLX           =	rf'({PERCENT})|({PN_LOCAL_ESC})'
PN_LOCAL	    =	rf'({PN_CHARS_U}|:|[0-9]|{PLX})(({PN_CHARS}|\.|:|{PLX})*({PN_CHARS}|:|{PLX}))?'
PNAME_NS	    =	rf'{PN_PREFIX}?:'
PNAME_NS_AUX	    =	rf'{PN_PREFIX}?:+(-)?'
PNAME_LN	    =	rf'({PNAME_NS})({PN_LOCAL})'
EXPONENT	=	rf'([eE][+-]?[0-9]+)'
BOOLEAN   = r'true|false'
INTEGER	  =	r'[+-]?[0-9]+'
DECIMAL	  =	r'[+-]?[0-9]*\.[0-9]+'
DOUBLE	  =	rf'[+-]?([0-9]+\.[0-9]*{EXPONENT}|\.[0-9]+{EXPONENT}|[0-9]+{EXPONENT})'
IRIREF = rf'<([^\x00-\x20<>"\u007B\u007D|^`\\]|{UCHAR})*>'
RSTRING_LITERAL_QUOTE              = rf'"([^"\\\n\r]|{ECHAR}|{UCHAR})*"'
STRING_LITERAL_SINGLE_QUOTE	      =	rf'\'([^\'\\\n\r]|{ECHAR}|{UCHAR})*\''
STRING_LITERAL_LONG_SINGLE_QUOTE	=	rf"'''(('|'')?([^'\\]|{ECHAR}|{UCHAR}))*'''"
STRING_LITERAL_LONG_QUOTE	        =	rf'"""(("|"")?([^"\\]|{ECHAR}|{UCHAR}))*"""'
STRING = rf'({RSTRING_LITERAL_QUOTE})|({STRING_LITERAL_SINGLE_QUOTE})|({STRING_LITERAL_LONG_SINGLE_QUOTE})|({STRING_LITERAL_LONG_QUOTE})'
BLANK_NODE_LABEL = rf'_:({PN_CHARS_U}|[0-9])(({PN_CHARS}|\.)*({PN_CHARS}))?'
LANGTAG	=	r'@[a-zA-Z]+(-[a-zA-Z0-9]+)*'


LABEL= rf'\[({PN_CHARS}|\s)*\]'

@TOKEN(LABEL)
def t_LABEL(t):
    t.value = t.value[1:-1]
    return t

@TOKEN(LANGTAG)
def t_LANGTAG(t):
    t.type = reserved.get(t.value, 'LANGTAG')  # Check for reserved words
    return t

@TOKEN(STRING)
def t_STRING(t):
    t.value = quoted_content_str(t.value)
    return t

@TOKEN(IRIREF)
def t_IRIREF(t):
    t.value = quoted_content_str(t.value)
    return t

@TOKEN(DOUBLE)
def t_DOUBLE(t):
    t.value = float(t.value)
    return t

@TOKEN(DECIMAL)
def t_DECIMAL(t):
    t.value = float(t.value)
    return t

@TOKEN(INTEGER)
def t_INTEGER(t):
    t.value = int(t.value)
    return t

@TOKEN(BOOLEAN)
def t_BOOLEAN(t):
    t.value = bool(t.value=="true")
    return t

@TOKEN(PNAME_LN)
def t_PNAME_LN(t):
    t.value = t.value.split(":")
    return t


@TOKEN(PNAME_NS_AUX)
def t_PNAME_NS_AUX(t):
    t.type = "RULE_MARK" if t.value[-1] == '-' else "PNAME_NS"
    t.value = t.value if t.value[-1] == '-' else t.value[:-1]
    return t

@TOKEN(BLANK_NODE_LABEL)
def t_BLANK_NODE_LABEL(t):
    t.value = t.value[2:]
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'
t_ignore_COMMENT = r"\%[^\n\r]*"

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def quoted_content_str(value):
    return value[1:-1]


# Build the lexer
lexer = lex.lex()


if __name__ == '__main__':

    # Test it out
    data = '''
@base <http://www.example.org/>
@prefix ex: <http://www.example.org/>
@prefix inria-team: <https://team.inria.fr/>
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>
@facts
% use of @base
[f 1] <Pred>(1.5).
% use of @prefix
[f 2] ex:Pred("1.5"^^xsd:decimal).
% absolute IRIs
[f 3] <http://www.example.org/Pred>("1.5"^^<http://www.w3.org/2001/XMLSchema#decimal>).
% use of @base for the predicate and @prefix for the argument
[f 4] team(inria-team:graphik).
team(_:node)
    '''

    # Give the lexer some input
    lexer.input("edf:")

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        print(tok)
