from typing import Iterator

import fitz

from thesis_rules_checker.wrappers import SpanWrapper


class SpanIterator(Iterator):
    """
    An iterator that iterates over all spans in a document.
    """

    def __init__(self, document: fitz.Document):
        self.document = document
        self.generator = self._generator()

    def __next__(self) -> SpanWrapper:
        return next(self.generator)

    def _generator(self) -> Iterator[SpanWrapper]:
        for page_index, page in enumerate(self.document):
            self.page_index = page_index
            text_info = page.get_text("dict")
            for block in text_info["blocks"]:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        yield SpanWrapper(span)
