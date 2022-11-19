import argparse
import sys
import fitz
import thesis_rules_checker

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

    output_file = args.output or thesis_rules_checker.get_output_filename(input_file)

    document = fitz.open(input_file)

    thesis_rules_checker.process_document(document)
    document.ez_save(output_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())
