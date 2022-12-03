import math
from abc import abstractmethod, ABC
from dataclasses import dataclass
from enum import Enum
from functools import reduce
from typing import Any

import fitz

from thesis_rules_checker.iterators import SpanIterator
from thesis_rules_checker.wrappers import SpanWrapper


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


class ThesisTitleMustBeInAllCapsRule(Rule):
    """
    A rule that checks whether the title of the thesis is in all caps.
    """

    def __init__(self):
        super().__init__(
            description="Thesis title must be in all caps",
            severity=RuleSeverity.MEDIUM)

    def apply(self, document: fitz.Document) -> list['RuleViolation']:
        first_page: fitz.Page = document.load_page(0)
        text_dict = first_page.get_text("dict")
        first_line = text_dict["blocks"][0]["lines"][0]["spans"][0]
        if not first_line["text"].isupper():
            return [RuleViolation(self, 0, first_line["bbox"])]
        return []


class FontSizeMustBe12Rule(Rule):
    """
    A rule that checks whether the font size is 12.
    """

    def __init__(self):
        super().__init__(
            description="Font size must be 12",
            severity=RuleSeverity.HIGH)

    def apply(self, document: fitz.Document) -> list['RuleViolation']:
        violations = []
        span_iterator = SpanIterator(document)
        span: SpanWrapper
        for span in span_iterator:
            if not math.isclose(span.size, 12, rel_tol=0.1):
                violations.append(RuleViolation(self, span_iterator.page_index, span.bounding_box, span.size))
        return violations


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
