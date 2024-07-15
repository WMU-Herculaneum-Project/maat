import lxml.etree as ET
import pytest

from maat.utils import (
    children,
    is_element,
    is_inside_element,
    is_text,
    replace_element,
    replace_element_with_text,
    tag_localname,
    to_string,
    mode,
    mode_length,
)


def test_to_string():
    q = ET.Element("test")
    assert to_string(q) == "<test/>"
    q = ET.fromstring("<test>Test</test>")
    assert to_string(q) == "<test>Test</test>"


def test_tag_localname():
    assert tag_localname(ET.Element("test")) == "test"
    assert tag_localname(ET.Element("{http://www.example.com}test")) == "test"


def test_is_text():
    assert is_text("Test")
    assert not is_text(ET.Element("test"))
    assert not is_text(ET.Element("test", text="Test"))


def test_is_element():
    assert is_element(ET.Element("test"))
    assert not is_element("Test")
    assert is_element(ET.Element("test", text="Test"))
    assert not is_element(23)


def test_children():
    q = ET.fromstring("<test>Test<child>Child</child>Test2</test>")
    ql = list(children(q))
    assert len(ql) == 3
    assert ql[0] == "Test"
    assert ql[1].tag == "child"
    assert ql[2] == "Test2"


def test_replace_element():
    s = "<test>Test<child>Child</child>Test2</test>"
    q = ET.fromstring(s)
    child = q.find("child")
    replace_element(child, ET.Element("new"))
    assert q.find("new") is not None
    assert q.find("child") is None
    t = to_string(q)
    assert t == "<test>Test<new/>Test2</test>"


def test_replace_element_with_text_tail():
    s = "<test>Before:<child>Child</child>:After</test>"
    q = ET.fromstring(s)
    child = q.find("child")
    replace_element_with_text(child, "NEW")
    t = to_string(q)
    assert t == "<test>Before:NEW:After</test>"


def test_replace_element_with_text_tail_false():
    s = "<test>Before:<child>Child</child>:After</test>"
    q = ET.fromstring(s)
    child = q.find("child")
    replace_element_with_text(child, "NEW", keep_element_tail=False)
    t = to_string(q)
    assert t == "<test>Before:NEW</test>"


def test_replace_element_with_text_at_higher_index():
    s = "<test><sib>Sibling</sib>Before:<child>Child</child>:After</test>"
    q = ET.fromstring(s)
    child = q.find("child")
    replace_element_with_text(child, "NEW")
    t = to_string(q)
    assert t == "<test><sib>Sibling</sib>Before:NEW:After</test>"


@pytest.fixture
def inside_test_doc():
    return ET.fromstring(
        """
        <root>
            <parent>
                <child>Text</child>
            </parent>
            <sibling>
                <child>Text</child>
            </sibling>
        </root>
        """
    )


def test_is_inside_element_true(inside_test_doc):
    child = inside_test_doc.find(".//parent/child")
    assert is_inside_element(child, "parent")


def test_is_inside_element_false(inside_test_doc):
    child = inside_test_doc.find(".//sibling/child")
    assert not is_inside_element(child, "parent")


def test_is_inside_element_root(inside_test_doc):
    parent = inside_test_doc.find(".//parent")
    assert is_inside_element(parent, "root")


def test_is_inside_element_not_found(inside_test_doc):
    child = inside_test_doc.find(".//parent/child")
    assert not is_inside_element(child, "nonexistent")


def test_mode():
    numbers = [1, 2, 3, 4, 5, 5, 5, 6, 7, 8, 9]
    assert mode(numbers) == 5


def test_mode_length():
    strings = [
        "one",
        "two",
        "three",
        "four",
        "five",
        "five",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
    ]
    assert mode_length(strings) == 4
