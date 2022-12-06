import fitz

import thesis_rules_checker.rules
import thesis_rules_checker.rules_base
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


all_rules: list[rules_base.Rule] = [rule_class() for rule_class in rules_base.Rule.__subclasses__()]


def process_document(document: fitz.Document) -> None:
    """
    Finds rule violations in the given document and annotates them.
    """
    doc = wrappers.DocumentWrapper(document)
    violations = rules_base.Rule.apply_all(doc, all_rules)

    if not violations:
        return

    doc.annotate_rule_violations(violations)
    doc.add_rule_violations_to_toc(violations)
