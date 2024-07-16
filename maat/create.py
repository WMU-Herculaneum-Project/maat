import re
import lxml.etree as ET
from maat.utils import (
    children,
    is_text,
    replace_element,
    replace_element_with_text,
    mode_length,
    to_string,
)


def texts_from_supplied(element):
    """
    Assume there is either only text or alts with only text
    """
    for child in children(element):
        if is_text(child):
            yield child
        else:
            yield child.text


def create_training_text(element):
    """
    Create a training case
     1. find all the supplied elements
     2. for each of these:
        a. find the text of the first alt of the supplied element
        b. replace the supplied element with the text of the first alt
    """
    for el in element.iter():
        if el.text is not None and not el.text.strip():
            el.text = None
    elements = element.findall(".//supplied")
    for supplied in elements:
        base_supplied_values = list(texts_from_supplied(supplied))
        if not base_supplied_values:
            replace_element_with_text(supplied, "")
        else:
            first_alt_text = base_supplied_values[0]
            replace_element_with_text(supplied, f"[{first_alt_text}]")
    return element


def create_test_cases(text):
    """
    Create test cases from the training text.
    1. count the number of /\][^\]*]\]/
    2. One at a time,
        - make a copy and replace each with one mask
        - yield each case
    """
    matches = re.finditer(r"\[[^\]]+\]", text)
    for match in matches:
        start, end = match.start(), match.end()
        pre_masked_text = text[:start].replace("[", "").replace("]", "")
        post_masked_text = text[end:].replace("[", "").replace("]", "")
        mask = "." * (end - start - 2)
        yield f"{pre_masked_text}[{mask}]{post_masked_text}"
