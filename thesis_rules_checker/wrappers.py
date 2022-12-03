from thesis_rules_checker.rules_base import *


class TocWrapper:
    """
    A wrapper for fitz.Document's table of contents that simplifies adding rule violation entries.
    """

    def __init__(self, document: fitz.Document):
        self.document = document
        self.virtual_toc = {}

    def add_rule_violation(self, violation: RuleViolation) -> None:
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
    def __add_rule_violation_to_toc(toc, violation: RuleViolation) -> None:
        x, y = violation.bounding_box[0], violation.bounding_box[1]
        toc.append([3, str(violation), violation.page_index + 1,
                    {"kind": fitz.LINK_GOTO,
                     "to": fitz.Point(x, y),
                     "color": severity_colors[violation.rule.severity],
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

    def annotate_rule_violation(self, violation: RuleViolation) -> None:
        """
        Adds a rule violation annotation to the document.
        """
        page = self.document.load_page(violation.page_index)
        annotation = page.add_highlight_annot(violation.bounding_box)
        annotation.set_colors(stroke=lighten_color(severity_colors[violation.rule.severity]))
        annotation.set_info(title="Rule Violation", content=str(violation))
        annotation.update()

    def annotate_rule_violations(self, violations: list[RuleViolation]) -> None:
        for violation in violations:
            self.annotate_rule_violation(violation)

    def add_rule_violations_to_toc(self, violations: list[RuleViolation]) -> None:
        for violation in violations:
            self.toc.add_rule_violation(violation)
        self.toc.render()


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

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text
