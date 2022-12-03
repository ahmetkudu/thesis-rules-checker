from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import reduce
from typing import Any

import fitz


class RuleSeverity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


severity_colors = {
    RuleSeverity.LOW: (0, 0.2, 0.8),
    RuleSeverity.MEDIUM: (1, 0.8, 0),
    RuleSeverity.HIGH: (1, 0, 0.2)
}


@dataclass
class Rule(ABC):
    """
    A rule for checking the format of a document.
    """

    description: str
    severity: RuleSeverity

    @abstractmethod
    def apply(self: 'Rule', document: fitz.Document) -> list['RuleViolation']:
        """
        Applies the rule to the given document.
        """
        raise NotImplementedError()

    @staticmethod
    def apply_all(document: fitz.Document, rules: list['Rule']) -> list['RuleViolation']:
        """
        Applies all rules to the given document.
        """
        return reduce(lambda a, b: a + b, [rule.apply(document) for rule in rules], [])


@dataclass
class RuleViolation:
    """
    A violation of a rule.
    """

    rule: Rule
    page_index: int
    bounding_box: list[float] = None
    actual_value: Any = None

    def __str__(self):
        result = self.rule.description
        if self.actual_value is not None:
            result += f", got {self.format_value()} instead"
        return result

    def format_value(self):
        if isinstance(self.actual_value, float):
            return f"{self.actual_value:.2f}"
        return self.actual_value
