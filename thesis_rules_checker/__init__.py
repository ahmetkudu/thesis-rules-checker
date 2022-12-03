import fitz

import thesis_rules_checker.rules
import thesis_rules_checker.wrappers


def get_output_filename(input_file: str) -> str:
    """
    Appends "-checked" to the input file name.

    Example:
        get_output_filename("thesis.pdf") -> "thesis-checked.pdf"
        get_output_filename("thesis") -> "thesis-checked"
    """
    if "." in input_file:
        dot_index = input_file.rindex(".")
        filename = input_file[:dot_index]
        extension = input_file[dot_index:]
        return f"{filename}-checked{extension}"
    else:
        return f"{input_file}-checked"


all_rules: list[rules.Rule] = [
    rules.ThesisTitleMustBeInAllCapsRule(),
    rules.FontSizeMustBe12Rule(),
    rules.FontFamilyMustBeTimesOrTimesNewRomanOrComputerModernRule(),
]


def process_document(document: fitz.Document) -> None:
    """
    Finds rule violations in the given document and annotates them.
    """
    violations = rules.Rule.apply_all(document, all_rules)

    if not violations:
        return

    doc = wrappers.DocumentWrapper(document)
    doc.annotate_rule_violations(violations)
    doc.add_rule_violations_to_toc(violations)
