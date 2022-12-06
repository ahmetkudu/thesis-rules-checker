from typing import Iterator

from . import wrappers


class SpanIterator(Iterator):
    """
    An iterator that iterates over all spans in a document.
    """

    def __init__(self, document: wrappers.DocumentWrapper):
        self.document = document.document
        self.generator = self._generator()

    def __next__(self) -> wrappers.SpanWrapper:
        return next(self.generator)

    def _generator(self) -> Iterator[wrappers.SpanWrapper]:
        for page_index, page in enumerate(self.document):
            self.page_index = page_index
            text_info = page.get_text("dict")
            for block in text_info["blocks"]:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        yield wrappers.SpanWrapper(span)
