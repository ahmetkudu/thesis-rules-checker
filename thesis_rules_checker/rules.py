import math
import re

import fitz

from . import iterators
from . import rules_base
from . import wrappers


class ThesisTitleMustBeInAllCapsRule(rules_base.Rule):
    """
    A rule that checks whether the title of the thesis is in all caps.
    """

    def __init__(self):
        super().__init__(
            description="Thesis title must be in all caps",
            severity=rules_base.RuleSeverity.MEDIUM)

    def apply(self, document: wrappers.DocumentWrapper) -> list['rules_base.RuleViolation']:
        first_page: fitz.Page = document[0]
        text_dict = first_page.get_text("dict")
        first_line = text_dict["blocks"][0]["lines"][0]["spans"][0]
        if not first_line["text"].isupper():
            return [rules_base.RuleViolation(self, 0, first_line["bbox"])]
        return []


class FontSizeMustBe12Rule(rules_base.Rule):
    """
    A rule that checks whether the font size is 12.
    """

    def __init__(self):
        super().__init__(
            description="Font size must be 12",
            severity=rules_base.RuleSeverity.HIGH)

    def apply(self, document: wrappers.DocumentWrapper) -> list['rules_base.RuleViolation']:
        violations = []
        span_iterator = iterators.SpanIterator(document)
        span: wrappers.SpanWrapper
        for span in span_iterator:
            if not math.isclose(span.size, 12, rel_tol=0.1) and not span.is_centered(document.bounds):
                violations.append(
                    rules_base.RuleViolation(self, span_iterator.page_index, span.bounding_box, span.size))
        return violations


computer_modern_regex = re.compile(
    "^cm[a-z]+[0-9]{1,2}|"
    "^(sf|ec|tc|la|lb|lc|rx)(rm|sl|ti|cc|ui|sc|ci|bx|bl|bi|xc|oc|rb|bm|ss|si|sx|so|tt|st|it|tc)[0-9]{4}$")


class FontFamilyMustBeTimesOrTimesNewRomanOrComputerModernRule(rules_base.Rule):
    """
    A rule that checks whether the font family is Times, Times New Roman or Computer Modern.
    """

    def __init__(self):
        super().__init__(
            description="Font family must be Times, Times New Roman or Computer Modern",
            severity=rules_base.RuleSeverity.HIGH)

    def apply(self, document: wrappers.DocumentWrapper) -> list['rules_base.RuleViolation']:
        violations = []
        span_iterator = iterators.SpanIterator(document)
        span: wrappers.SpanWrapper
        for span in span_iterator:
            if span.text not in ["Times", "Times New Roman"] and not self.__is_computer_modern(span.font):
                violations.append(
                    rules_base.RuleViolation(self, span_iterator.page_index, span.bounding_box, span.font))
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


class BoldFaceNotAllowedRule(rules_base.Rule):
    """
    A rule that checks whether bold face is not used.
    """

    def __init__(self):
        super().__init__(
            description="Boldface is not allowed",
            severity=rules_base.RuleSeverity.HIGH)

    def apply(self, document: wrappers.DocumentWrapper) -> list['rules_base.RuleViolation']:
        violations = []
        span_iterator = iterators.SpanIterator(document)
        span: wrappers.SpanWrapper
        for span in span_iterator:
            if span.is_bold() and not span.is_centered(document.bounds):
                violations.append(rules_base.RuleViolation(self, span_iterator.page_index, span.bounding_box))
        return violations


url_regex = re.compile(
    r"https?://(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\."
    r"[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_+.~#?&/=]*)")


class UrlNotAllowedOutsideReferencesRule(rules_base.Rule):
    """
    A rule that checks whether URLs are not used.
    """

    def __init__(self):
        super().__init__(
            description="URLs are not allowed outside references",
            severity=rules_base.RuleSeverity.HIGH)

    def apply(self, document: wrappers.DocumentWrapper) -> list['rules_base.RuleViolation']:
        violations = []
        span_iterator = iterators.SpanIterator(document)
        span: wrappers.SpanWrapper
        for span in span_iterator:
            if url_regex.match(span.text):
                violations.append(rules_base.RuleViolation(self, span_iterator.page_index, span.bounding_box))
        return violations


class TextMustBeWithinMarginsRule(rules_base.Rule):
    """
    A rule that checks whether the text is in the margins.
    """

    def __init__(self):
        super().__init__(
            description="Text must be within margins",
            severity=rules_base.RuleSeverity.HIGH)

    def apply(self, document: wrappers.DocumentWrapper) -> list['rules_base.RuleViolation']:
        violations = []
        span_iterator = iterators.SpanIterator(document)
        span: wrappers.SpanWrapper
        for span in span_iterator:
            if not self.__is_in_margins(span.bounding_box, span_iterator.page.rect):
                violations.append(rules_base.RuleViolation(self, span_iterator.page_index, span.bounding_box))
        return violations

    @staticmethod
    def __is_in_margins(bounding_box, page_rect):
        # Find the ratio
        # A4 paper size is 21 x 29.7 cm
        ratio = page_rect.width / 21

        # Margins for the text shall be 3.5 cm from the top, 2 cm from the right, 2 cm from the bottom, and 3.5 cm
        # from the left

        return \
            bounding_box[0] >= 3.5 * ratio and \
            bounding_box[1] >= 3.5 * ratio and \
            bounding_box[2] <= page_rect.width - 2 * ratio and \
            bounding_box[3] <= page_rect.height - 2 * ratio
