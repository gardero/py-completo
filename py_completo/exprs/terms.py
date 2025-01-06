from typing import AnyStr, Any

from pydantic import BaseModel


def frepr(v):
    return f"{v[0]}:{v[1]}" if isinstance(v, tuple) or isinstance(v, list) else str(v)

class Variable(BaseModel):
    name: str

    def __str__(self):
        return f"{self.name}"

class Term(BaseModel):
    functor: Any
    arguments: list["Term"]

    def __str__(self):
        functor = frepr(self.functor)
        if self.arguments:
            args = ", ".join(a.__str__() for a in self.arguments)
            return f"{functor}({args})"
        return f"{functor}"



class Atom(BaseModel):
    predicate: Any
    arguments: list[Term | Variable]
    negated: bool = False

    def __str__(self):
        if self.predicate=="=":
            return f"{self.arguments[0]}={self.arguments[1]}"
        sign = "-" if self.negated else ""
        args = ", ".join(a.__str__() for a in self.arguments)
        return f"{sign}{frepr(self.predicate)}({args})"