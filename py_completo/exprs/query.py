from enum import Enum, auto

from pydantic import BaseModel

class QueryType(Enum):
    CONJUNCTIVE = auto()
    NEGATED = auto()

class Query(BaseModel):
    label: str | None = None
    answer_tuple: list
    body: list
    query_type: QueryType = QueryType.CONJUNCTIVE

    def __str__(self):
        label = f"[{self.label}] " if self.label else ""
        head = ", ".join(str(a) for a in self.answer_tuple) if self.answer_tuple else ""
        answer_atom = f"answer_atom({head})"
        body = (" :- "+ ", ".join(str(a) for a in self.body)) if self.body else ""
        return f"{label}{answer_atom}{body}."