import math
import re

import fitz

from thesis_rules_checker.iterators import SpanIterator
from thesis_rules_checker.rules_base import Rule, RuleViolation, RuleSeverity
from thesis_rules_checker.wrappers import SpanWrapper


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


computer_modern_regex = re.compile(
    "^cm[a-z]+[0-9]{1,2}|"
    "^(sf|ec|tc|la|lb|lc|rx)(rm|sl|ti|cc|ui|sc|ci|bx|bl|bi|xc|oc|rb|bm|ss|si|sx|so|tt|st|it|tc)[0-9]{4}$")


class FontFamilyMustBeTimesOrTimesNewRomanOrComputerModernRule(Rule):
    """
    A rule that checks whether the font family is Times, Times New Roman or Computer Modern.
    """

    def __init__(self):
        super().__init__(
            description="Font family must be Times, Times New Roman or Computer Modern",
            severity=RuleSeverity.HIGH)

    def apply(self, document: fitz.Document) -> list['RuleViolation']:
        violations = []
        span_iterator = SpanIterator(document)
        span: SpanWrapper
        for span in span_iterator:
            if span.text not in ["Times", "Times New Roman"] and not self.__is_computer_modern(span.font):
                violations.append(RuleViolation(self, span_iterator.page_index, span.bounding_box, span.font))
        return violations

    @staticmethod
    def __is_computer_modern(font_name: str) -> bool:
        """
        Checks whether the given font name is a computer modern font.
        """

        font_shapes = [
            "sflq8", "sfli8", "sflb8", "sflo8", "sfltt8",
            "isflq8", "isfli8", "isflb8", "isflo8", "isfltt8",
            "sfsq8", "sfqi8", "sfssdc10"]

        lower_font_name = font_name.lower()

        return computer_modern_regex.match(lower_font_name) or lower_font_name in font_shapes

