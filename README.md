# Py-completo

# DLGP+

DLGP+ is an extension of [DLGP](https://graphik-team.github.io/graal/doc/dlgp) that that 
supports the specification of disjunctive existential rules and negated atoms in queries.


Disjunction is specified in the head of a rule by writing a list in squared brackets. The disjoint elements can be a single atom or several atoms enclosed in brackets, e.g.,
```
[disj] [leaf(X), (inner_node(X), edge(X,Y))] :- node(X).
```
Negation in queries with negated atoms is specified with the minus symbol, e.g.,
```
[q] ?(X) :- person(X), -marriedTo(X,Y). 
```