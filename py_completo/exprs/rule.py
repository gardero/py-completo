from enum import Enum, auto

from pydantic import BaseModel


class RuleType(Enum):
    EXISTENTIAL = auto()
    DISJUNCTIVE = auto()

class Rule(BaseModel):
    label: str | None = None
    head: list
    body: list
    rule_type: RuleType = RuleType.EXISTENTIAL

    def __str__(self):
        label = f"[{self.label}] " if self.label else ""
        head = ", ".join(str(a) for a in self.head) if self.head else "!"
        body = (" :- "+ ", ".join(str(a) for a in self.body)) if self.body else ""
        return f"{label}{head}{body}."