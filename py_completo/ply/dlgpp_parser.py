# Yacc example
from xml.dom.minidom import Document

import ply.yacc as yacc
from ply import lex
from rdflib import URIRef, Literal

# Get the token map from the lexer.  This is required.
from dlgpp_lexer import tokens
from py_completo.exprs.program import Program
from py_completo.exprs.query import Query, QueryType
from py_completo.exprs.rule import Rule, RuleType
from py_completo.exprs.terms import Variable, Term, Atom

start = 'document'

def p_document(p):
    """
    document : header body
        | body
    """
    body = p[2] if len(p) > 2 else p[1]
    header = p[1] if len(p) > 2 else []
    header = {k: v for k, v in header}
    p[0] = Program.from_statements(header, body)


def p_header(p):
    """
    header : header_one
        | header_one header
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]


def p_header_one(p):
    """
    header_one : BASE IRIREF
        | PREFIX PNAME_NS IRIREF
        | TOP L_IDENT
        | TOP IRIREF
        | UNA
    """
    n = len(p)
    if n > 2:
        pos = 2 if len(p) > 3 else 1
        p[0] = (p[pos], p[pos+1])
    else:
        p[0] = (p[1], p[1])


def p_body(p):
    """
    body : section_list
        | statement_list
    """
    p[0] = p[1]

def p_section_list(p):
    """
    section_list : section
        | section section_list
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2]


def p_section(p):
    """
    section : annotation
        | annotation statement_list
    """
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[2]


def p_annotation(p):
    """
    annotation : RULES
        | FACTS
        | CONSTRAINTS
        | QUERIES
    """
    p[0] = p[1]


def p_statement_list(p):
    """
    statement_list : statement
        | statement statement_list
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_statement(p):
    """
    statement : statement_expr
        | LABEL statement_expr

    """
    p[0] = p[2] if len(p)>2 else p[1]
    if len(p)>2:
        p[0].label = p[1]



def p_statement_expr(p):
    """
    statement_expr : constraint
        | rule
        | drule
        | cquery
        | nquery
        | fact

    """
    p[0] = p[1]


def p_cquery(p):
    """
    cquery : QUESTION_MARK START_TERMS_MARK term_list_or_empty END_TERMS_MARK RULE_MARK conjunction_atoms_or_empty END_MARK
        | QUESTION_MARK RULE_MARK conjunction_atoms_or_empty END_MARK
    """
    n = len(p)
    var_list = p[3] if p[2] == "(" else []
    conjunction_atoms = p[n-2]
    p[0] = Query(
        answer_tuple= var_list,
        body = conjunction_atoms,
    )

def p_nquery(p):
    """
    nquery : QUESTION_MARK START_TERMS_MARK term_list_or_empty END_TERMS_MARK RULE_MARK conjunction_neg END_MARK
        | QUESTION_MARK RULE_MARK conjunction_neg END_MARK
    """
    n = len(p)
    var_list = p[3] if p[2] == "(" else []
    conjunction_atoms = p[n-2] if p[n-2] != ":-" else []
    p[0] = Query(
        answer_tuple= var_list,
        body = conjunction_atoms,
        query_type= QueryType.NEGATED
    )

def p_rule(p):
    """
    rule : conjunction_atoms RULE_MARK conjunction_atoms_or_empty END_MARK
    """
    n = len(p)
    p[0] = Rule(
        head = p[1],
        body = p[n-2],
    )

def p_drule(p):
    """
    drule : START_STATEMENT_MARK conjunction_csf_list END_STATEMENT_MARK RULE_MARK conjunction_atoms_or_empty END_MARK
    """
    n = len(p)
    p[0] = Rule(
        head = p[1],
        body = p[n-2],
        rule_type= RuleType.DISJUNCTIVE
    )

def p_conjunction_csf_list(p):
    """
    conjunction_csf_list : conjunction_csf
        | conjunction_csf SEPARATOR conjunction_csf_list
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_conjunction_csf(p):
    """
    conjunction_csf : atom
        | START_TERMS_MARK conjunction_atoms END_TERMS_MARK
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[2]

def p_constraint(p):
    """
    constraint : ABSURD_MARK RULE_MARK conjunction_atoms END_MARK
    """
    p[0] = Rule(head=[], body=p[3])

def p_fact(p):
    """
    fact : conjunction_atoms END_MARK
    """
    p[0] = Rule(head=p[1], body=[])

def p_conjunction_neg(p):
    """
    conjunction_neg : neg_literal
        | neg_literal SEPARATOR conjunction_atoms
        | atom SEPARATOR conjunction_neg
        | neg_literal SEPARATOR conjunction_neg
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_conjunction_atoms(p):
    """
    conjunction_atoms : atom
        | atom SEPARATOR conjunction_atoms
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_conjunction_atoms_or_empty(p):
    """
    conjunction_atoms_or_empty : conjunction_atoms
        | empty
    """
    if p[1]:
        p[0] = p[1]
    else:
        p[0] = []


def p_neg_literal(p):
    """
    neg_literal : NEGATION std_atom
    """
    p[2].negated = not p[2].negated
    p[0] = p[2]


def p_atom(p):
    """
    atom : equality
        | std_atom
    """
    p[0] = p[1]

def p_equality(p):
    """
    equality : term EQUALITY_MARK term
    """
    p[0] = Atom(
        predicate="=",
        arguments=[p[1], p[3]]
    )

def p_std_atom(p):
    """
    std_atom : predicate START_TERMS_MARK term_list END_TERMS_MARK
    """
    p[0] = Atom(
        predicate = p[1],
        arguments=p[3]
    )

def p_term_list_or_empty(p):
    """
    term_list_or_empty : term_list
        | empty
    """
    p[0] = p[1] if p[1] else []

def p_term_list(p):
    """
    term_list : term
        | term SEPARATOR term_list
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_term(p):
    """
    term : constant
        | variable
    """
    p[0] = p[1]

def p_predicate(p):
    """
    predicate : prefixed_name
            | L_IDENT
            | IRIREF
    """
    p[0] = p[1]

def p_constant(p):
    """
    constant : prefixed_name
            | L_IDENT
            | IRIREF
            | literal
    """
    p[0] = Term(functor=p[1], arguments=[])


def p_variable(p):
    """
    variable : U_IDENT
        | BLANK_NODE_LABEL
    """
    p[0] = Variable(name=p[1])




def p_prefixed_name(p):
    """
    prefixed_name : PNAME_LN
                | PNAME_NS
    """
    p[0] = p[1]


def p_literal(p):
    """
    literal : rdf_literal
            | numeric_literal
            | boolean_literal
    """
    p[0] = p[1]

def p_boolean_literal(p):
    """
    boolean_literal : BOOLEAN
    """
    p[0] = Literal(p[1])

def p_rdf_literal(p):
    """
    rdf_literal : STRING TOPTOP iri
    """
    p[0] = Literal(p[1], datatype=p[3])

def p_rdf_literal2(p):
    """
    rdf_literal : STRING LANGTAG
    """
    p[0] = Literal(p[1], lang=p[3])


def p_rdf_literal3(p):
    """
    rdf_literal : STRING
    """
    p[0] = Literal(p[1])

def p_numeric_literal(p):
    """
    numeric_literal : INTEGER
                   | DECIMAL
                   | DOUBLE
                   | FLOAT
    """
    p[0] = Literal(p[1])



def p_iri(p):
    """iri : IRIREF"""
    p[0] = URIRef(value=p[1])

def p_iri2(p):
    """iri : prefixed_name"""
    p[0] = p[1]


def p_empty(p):
    """empty :"""
    pass


# Error rule for syntax errors
def p_error(p):
    print(f"Syntax error in input! {p}")

# Build the parser
parser = yacc.yacc()
# Build the lexer
# lexer = lex.lex()

data=""" 
@base <http://www.example.org/>
@prefix ex: <http://www.example.org/>
@prefix inria-team: <https://team.inria.fr/>
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>
@facts
% use of @base
[f 1] <Pred>(1.5).
% use of @prefix
[f 2] ex:Pred("1.5"^^xsd:decimal, "some string").
% absolute IRIs
[f 3] <http://www.example.org/Pred>("1.5"^^<http://www.w3.org/2001/XMLSchema#decimal>).
% use of @base for the predicate and @prefix for the argument
[f 4] team(inria-team:graphik, true).
team(_:node).
"""

data1 = """

    [f 1] p(a), relatedTo(a,b), q(b). [f2] p(X), t(X,a,b), s(a,z).
    [c1] !:-relatedTo(X
    % this is a comment
    ,X).
    [q1]?(X) :- p(X), relatedTo(X,Z), t(a,Z).
    t(X,a,b).
    [r1] relatedTo(X,Y) :- p(X), t(X,Z).
    [constraint_2] ! :- X=Y, t(X,Y,b).
    s(X,Y), s(Y,Z) :- % This is another comment
    q(X),t(X,Z).
    [rA_1] p(X)
    :-
    q(X)
    . Y=Z :- t(X,Y),t(X,Z).
    [Query2]
    ? (X,Y) :- relatedTo(X,X), Y=a.
    s(Z) :- a=b, X=Y, X=a, p(X,Y).
    !:- p(X), q(X).
    relatedTo(Y,z).?    :- p(X).
"""
data2="""
@una
@top all
@facts
    [f1] p(a), relatedTo(a,b), q(b).
    [f2] p(X), t(X,a,b), s(a,z).
    t(X,a,b), relatedTo(Y,z).
    @constraints
    [c1] ! :- relatedTo(X,X).
    [constraint_2] ! :- X=Y, t(X,Y,b).
    ! :- p(X), q(X).
    @rules
    [r1] relatedTo(X,Y) :- p(X), t(X,Z).
    s(X,Y), s(Y,Z) :- q(X),t(X,Z).
    [rA 1] p(X) :- q(X).
    Y=Z :- t(X,Y),t(X,Z).
    s(a):-.
    s(Z) :- a=b, X=Y, X=a, p(X,Y).
    @queries
    [q1] ? (X) :- p(X), relatedTo(X,Z), t(a,Z).
    [Query2] ? (X,Y, 1) :- relatedTo(X,X), Y=a.
    ? :- p(X).
    ?() :-.
"""


result = parser.parse(data2, debug=True)
print(str(result))
