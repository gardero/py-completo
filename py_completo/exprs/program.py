from itertools import groupby

from pydantic import BaseModel

from py_completo.exprs.query import Query
from py_completo.exprs.rule import Rule


class Program(BaseModel):
    headers: dict[str, str]
    statements: list[Rule]
    queries: list[Query]

    @classmethod
    def from_statements(cls, headers, statements):
        rules = [s for s in statements if isinstance(s, Rule)]
        queries = [s for s in statements if isinstance(s, Query)]
        return Program(
            headers=headers,
            statements=rules,
            queries=queries
        )

    def __str__(self):
        headers = "\n".join(f"{k}:{v}" for k, v in self.headers.items())
        statements = "\n".join(str(s) for s in self.statements)
        queries = "\n".join(str(q) for q in self.queries)
        return f"""
{headers}

{statements}

{queries}
"""
