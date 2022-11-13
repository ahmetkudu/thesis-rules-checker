import argparse
import sys
import fitz

from fitz import Point

parser = argparse.ArgumentParser(
    prog="Thesis Rules Checker",
    description="A format checking software for the theses of BOUN grad students")

parser.add_argument(
    "-i", "--input",
    metavar="FILE",
    help="The path of the file to be checked",
    required=False)

parser.add_argument(
    "-o", "--output",
    metavar="FILE",
    help="The path of the output file",
    required=False)


def main() -> int:
    args = parser.parse_args()

    input_file = args.input

    while input_file is None:
        input_file = input("Enter the path of the file to be checked: ")

    output_file = args.output

    if output_file is None:
        parts = input_file.split(".")
        if len(parts) >= 2:
            parts[-2] += "-checked"
        else:
            parts[0] += "-checked"
        output_file = ".".join(parts)

    document = fitz.open(input_file)

    toc = document.get_toc()
    toc.append([1, 'Rule Violations', 1])

    for page_index, page in enumerate(document):
        text_info = page.get_text("dict")
        toc.append([2, 'Page %d' % (page_index + 1), page_index + 1])

        added_toc = False

        for block in text_info["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    if not approximately_equals(span["size"], 12, 0.1):
                        page.add_highlight_annot(span["bbox"])
                        page.add_text_annot((span["bbox"][0] - 20, span["bbox"][1]), "Font size is not 12")
                        toc.append([3, "Font size is not 12", page_index + 1,
                                    {"kind": 1,
                                     "to": Point(span["bbox"][0], span["bbox"][1]),
                                     "color": (1, 1, 0),
                                     "bold": True}])
                        added_toc = True

        if not added_toc:
            toc.pop()

    document.set_toc(toc)
    document.ez_save(output_file)

    return 0


def approximately_equals(a, b, epsilon=1e-5):
    return abs(a - b) < epsilon


if __name__ == "__main__":
    sys.exit(main())
