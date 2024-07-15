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
        first_alt_text = base_supplied_values[0]
        replace_element_with_text(supplied, f"[{first_alt_text}]")
    return element


def create_test_cases(element):
    """
    Create test cases
    """
    for el in element.iter():
        if el.text is not None and not el.text.strip():
            el.text = None
    elements = element.findall(".//supplied")
    for base in elements:
        others = [el for el in elements if el != base]
        base_supplied_values = list(texts_from_supplied(base))
        base_mode_length = mode_length(base_supplied_values)
        new_base = ET.Element("eval")
        ET.SubElement(new_base, "mask").text = f"[{'.' * base_mode_length}]"
        for supplied_value in base_supplied_values:
            ET.SubElement(new_base, "alt").text = supplied_value
        replace_element(base, new_base)
        for other in others:
            other_values = list(texts_from_supplied(other))
            other_mode_length = mode_length(other_values)
            replace_element_with_text(other, "." * other_mode_length)
        yield element


def convert_to_test_case(original_text, match_object):
    # copy the original text
    text = original_text
    # replace the match with the mask
    text = (
        text[: match_object.start()]
        + "["
        + "." * len(match_object.group(1))
        + "]"
        + text[match_object.end() :]
    )
    # create the alternatives
    alternatives = match_object.group(1).split("|")
    # replace all the other matches with dots
    text = re.sub(
        r"<supplied>([^<]+)</supplied>", lambda m: "." * len(m.group(1)), text
    )
    # remove any newlines
    text = text.strip("\n")
    # remove the <ab> tags
    if text.startswith("<ab>"):
        text = text[4:]
    if text.endswith("</ab>"):
        text = text[:-5]
    # remove any  newlines
    text = text.strip("\n")
    return {"test_case": text, "alternatives": alternatives}


def convert_to_test_cases(original_text):
    """
    Convert an original text to test cases
    """
    return [
        convert_to_test_case(original_text, m)
        for m in re.finditer(r"<supplied>([^<]+)</supplied>", to_string(original_text))
    ]
