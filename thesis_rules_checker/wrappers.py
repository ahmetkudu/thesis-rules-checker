import math

import fitz

from . import iterators
from . import rules_base


class TocWrapper:
    """
    A wrapper for fitz.Document's table of contents that simplifies adding rule violation entries.
    """

    def __init__(self, document: fitz.Document):
        self.document = document
        self.virtual_toc = {}

    def add_rule_violation(self, violation: rules_base.RuleViolation) -> None:
        """
        Adds a rule violation to the table of contents.
        """
        if violation.page_index not in self.virtual_toc:
            self.virtual_toc[violation.page_index] = []
        self.virtual_toc[violation.page_index].append(violation)

    def render(self) -> None:
        """
        Updates the table of contents of the document.
        """
        toc = self.document.get_toc()
        toc.append([1, "Rule Violations", 0])
        for page_index, page_violations in self.virtual_toc.items():
            toc.append([2, f"Page {page_index + 1}", page_index + 1])
            for page_violation in page_violations:
                self.__add_rule_violation_to_toc(toc, page_violation)
        self.document.set_toc(toc)

    @staticmethod
    def __add_rule_violation_to_toc(toc, violation: rules_base.RuleViolation) -> None:
        x, y = violation.bounding_box[0], violation.bounding_box[1]
        toc.append([3, str(violation), violation.page_index + 1,
                    {"kind": fitz.LINK_GOTO,
                     "to": fitz.Point(x, y),
                     "color": rules_base.severity_colors[violation.rule.severity],
                     "bold": True}])


def lighten_color(color: tuple[float, float, float], amount: float = 0.5) -> tuple[float, float, float]:
    """
    Lightens the given color by the given amount.
    """
    return tuple(min(amount + (1 - amount) * c, 1) for c in color)


class DocumentWrapper:
    """
    A wrapper for fitz.Document.
    """

    def __init__(self, document: fitz.Document):
        self.document = document
        self.toc = TocWrapper(document)
        self.bounds = self.__calculate_bounds()

    def __getitem__(self, item):
        return self.document[item]

    def annotate_rule_violation(self, violation: rules_base.RuleViolation) -> None:
        """
        Adds a rule violation annotation to the document.
        """
        page = self.document.load_page(violation.page_index)
        annotation = page.add_highlight_annot(violation.bounding_box)
        annotation.set_colors(stroke=lighten_color(rules_base.severity_colors[violation.rule.severity]))
        annotation.set_info(title="Rule Violation", content=str(violation))
        annotation.update()

    def annotate_rule_violations(self, violations: list[rules_base.RuleViolation]) -> None:
        for violation in violations:
            self.annotate_rule_violation(violation)

    def add_rule_violations_to_toc(self, violations: list[rules_base.RuleViolation]) -> None:
        for violation in violations:
            self.toc.add_rule_violation(violation)
        self.toc.render()

    def __calculate_bounds(self):
        bounds = [math.inf, math.inf, 0, 0]
        span: SpanWrapper
        for span in iterators.SpanIterator(self):
            if span.bounding_box[0] < bounds[0]:
                bounds[0] = span.bounding_box[0]
            if span.bounding_box[1] < bounds[1]:
                bounds[1] = span.bounding_box[1]
            if span.bounding_box[2] > bounds[2]:
                bounds[2] = span.bounding_box[2]
            if span.bounding_box[3] > bounds[3]:
                bounds[3] = span.bounding_box[3]
        return bounds


class SpanWrapper:
    """
    A wrapper for a span.
    """

    def __init__(self, span):
        self.span = span

    @property
    def font(self):
        return self.span["font"]

    @property
    def size(self):
        return self.span["size"]

    @property
    def bounding_box(self):
        return self.span["bbox"]

    @property
    def text(self):
        return self.span["text"]

    @property
    def flags(self):
        return self.span["flags"]

    def is_centered(self, bounds) -> bool:
        """
        Returns True if the span is centered horizontally.
        """
        left_offset = self.bounding_box[0] - bounds[0]
        right_offset = bounds[2] - self.bounding_box[2]
        return math.isclose(left_offset, right_offset, rel_tol=0.1)

    def is_bold(self):
        return self.flags & fitz.TEXT_FONT_BOLD

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text
