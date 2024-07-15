import lxml.etree as ET
from lxml.etree import QName


def to_string(element, pretty_print=False):
    """
    Convert an element to a string
    """
    return ET.tostring(element, pretty_print=pretty_print, encoding="utf-8").decode(
        "utf-8"
    )


def tag_localname(element):
    """
    Get the localname of an element
    """
    return QName(element.tag).localname


def children(element):
    """
    Get the children of an element, including text items
    """
    if element.text:
        yield element.text
    for child in element:
        yield child
        if child.tail:
            yield child.tail


def is_text(thing):
    """
    Check if an thing is text
    >>> is_text("test")
    True
    >>> is_text(ET.Element("test"))
    False
    """
    return isinstance(thing, str)


def is_element(thing):
    """
    Check if an thing is an element
    >>> is_element(ET.Element("test"))
    True
    >>> is_element("test")
    False
    """
    return isinstance(thing, ET._Element)


def replace_element(element, new_element):
    """
    Replace an element with a new element
    """
    parent = element.getparent()
    tail = element.tail
    if tail:
        new_element.tail = tail
    index = parent.index(element)
    parent.remove(element)
    parent.insert(index, new_element)


def replace_element_with_text_at_0(parent, element, text, keep_element_tail):
    """
    Replace an element with text at the beginning of the parent
    """
    parent_text = parent.text or ""
    if keep_element_tail:
        element_tail = element.tail or ""
        parent.text = parent_text + text + element_tail
    else:
        parent.text = parent_text + text
    parent.remove(element)
    return parent


def replace_element_with_text_at_higher(
    parent, sibling, element, text, keep_element_tail
):
    """
    Replace an element with text at a higher index
    """
    prior_element_tail = sibling.tail or ""
    if keep_element_tail:
        element_tail = element.tail or ""
        sibling.tail = prior_element_tail + text + element_tail
    else:
        sibling.tail = prior_element_tail + text
    parent.remove(element)
    return parent


def replace_element_with_text(element, text, keep_element_tail=True):
    """
    Replace an element with text
    """
    text = text or ""
    parent = element.getparent()
    index = parent.index(element)
    if index == 0:
        return replace_element_with_text_at_0(parent, element, text, keep_element_tail)
    else:
        sibling = parent[index - 1]
        return replace_element_with_text_at_higher(
            parent, sibling, element, text, keep_element_tail
        )


def is_inside_element(element, parent_tag):
    """
    Check if an element is inside a parent element containing a specific tag
    """
    current_element = element
    while current_element is not None:
        if current_element.tag == parent_tag:
            return True
        current_element = current_element.getparent()
    return False


## Silly stat functions


def mode(ns):
    """
    Get the mode of a list of numbers
    """
    return max(set(ns), key=ns.count)


def mode_length(ns):
    """
    Get the mode of the lengths of a list of strings
    """
    return mode([len(n) for n in ns])
