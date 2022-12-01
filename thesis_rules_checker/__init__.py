import fitz


def get_output_filename(input_file: str) -> str:
    parts = input_file.split(".")
    if len(parts) >= 2:
        parts[-2] += "-checked"
    else:
        parts[0] += "-checked"
    return ".".join(parts)


def process_document(document: fitz.Document):
    toc = document.get_toc()
    toc.append([1, 'Rule Violations', 1])
    for page_index, page in enumerate(document):
        text_info = page.get_text("dict")
        toc.append([2, 'Page %d' % (page_index + 1), page_index + 1])

        added_toc = False

        # Check font size for all text blocks
        for block in text_info["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    if not approximately_equals(span["size"], 12, 0.1):
                        add_rule_violation("Font size is not 12", span["bbox"], page, page_index, toc)
                        added_toc = True

        if not added_toc:
            toc.pop()
    document.set_toc(toc)


def add_rule_violation(message, bounding_box, page, page_index, toc):
    x, y = bounding_box[0], bounding_box[1]
    page.add_highlight_annot(bounding_box)
    page.add_text_annot((x - 20, y), message)
    toc.append([3, message, page_index + 1,
                {"kind": 1,
                 "to": fitz.Point(x, y),
                 "color": (1, 1, 0),
                 "bold": True}])


def approximately_equals(a, b, epsilon=1e-5):
    return abs(a - b) < epsilon
