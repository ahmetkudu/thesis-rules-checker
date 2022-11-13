import argparse
import sys
from pprint import pprint
from PyPDF2 import PdfReader

parser = argparse.ArgumentParser(
    prog="Thesis Rules Checker",
    description="A format checking software for the theses of BOUN grad students")

parser.add_argument(
    "-i", "--input",
    metavar="FILE",
    help="The path of the file to be checked",
    required=False)


def main() -> int:
    args = parser.parse_args()

    filename = args.input

    while filename is None:
        filename = input("Enter the path of the file to be checked: ")

    try:
        reader = PdfReader(filename)
    except FileNotFoundError:
        print("File not found", file=sys.stderr)
        return 1

    for page in reader.pages:
        page.extract_text(visitor_text=visitor_text)

    return 0


def visitor_text(text, cm, tm, fontDict, fontSize):
    if text is None or fontDict is None:
        return
    print("Text: " + str(text))
    pprint(cm)
    pprint(tm)
    print("x: {}, y: {}".format(tm[4], tm[5]))
    print("fontDict: " + str(fontDict["/BaseFont"]))
    print("fontSize: " + str(fontSize))
    input()


if __name__ == "__main__":
    sys.exit(main())
