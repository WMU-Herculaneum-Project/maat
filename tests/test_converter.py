import pytest
import lxml.etree as ET
from maat.converter import (
    remove_gaps_from_supplied_text,
    which_test_context,
    in_supplied_element,
    Converter,
)
from maat.utils import to_string


@pytest.fixture
def sample_xml():
    xml = """
    <root>
        <supplied>
            <element>Text</element>
        </supplied>
        <context>
            <element>Text</element>
        </context>
    </root>
    """
    return ET.fromstring(xml)


def test_in_supplied_element_true(sample_xml):
    element = sample_xml.find(".//supplied/element")
    assert in_supplied_element(element)


def test_in_supplied_element_false(sample_xml):
    element = sample_xml.find(".//context/element")
    assert not in_supplied_element(element)


def test_test_context_evaluation(sample_xml):
    element = sample_xml.find(".//supplied/element")
    assert which_test_context(element) == "evaluation"


def test_test_context_context(sample_xml):
    element = sample_xml.find(".//context/element")
    assert which_test_context(element) == "context"


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ("[abd.efg]", "[abd].[efg]"),
        ("[abd....efg.....hij]", "[abd]....[efg].....[hij]"),
        ("[...abd...efg...hij...]", "...[abd]...[efg]...[hij]..."),
        ("[]", ""),
        ("[.]", "."),
        ("[a]", "[a]"),
    ],
)
def test_remove_gaps_from_supplied_text(input_text, expected_output):
    assert remove_gaps_from_supplied_text(input_text) == expected_output


def test_create_converter():
    assert Converter()


def test_call_converter():
    converter = Converter()
    element = converter(ET.fromstring("<ab><milestone />Text<handShift /></ab>"))
    txt = to_string(element)
    assert not converter.errors
    assert txt == "<ab>Text</ab>"


# Note: These tests are testing the _convert method of the Converter class
# Not the .convert method (which creates a new element)
@pytest.mark.parametrize(
    "xml_string, xpath, expected_text",
    [
        pytest.param("<root><ab>Text</ab></root>", ".//ab", "Text", id="simple_ab"),
        pytest.param(
            "<ab><expan><abbr>f</abbr><ex>iliae</ex></expan></ab>",
            ".//abbr",
            "f",
            id="abbr",
        ),
        pytest.param("<ab><add>Text</add></ab>", ".//add", "Text"),
        pytest.param(
            '<ab><app type="note"><lem>ὠνουμένη</lem><rdg>ὠνουμένῃ</rdg></app></ab>',
            ".//app",
            "",
            id="app_note",
        ),
        pytest.param(
            '<ab><app type="alternative"><lem>ὠνουμένη</lem><rdg>ὠνουμένῃ</rdg></app></ab>',
            ".//app",
            "ὠνουμένη",
            id="app_alternative_lem",
        ),
        pytest.param(
            '<ab><app type="alternative"><rdg>ὠνουμένῃ</rdg><lem>ὠνουμένη</lem></app></ab>',
            ".//app",
            "ὠνουμένῃ",
            id="app_alternative_rdg",
        ),
        pytest.param(
            '<ab><app type="alternative"><certainty>"high"</certainty><lem>ὠνουμένη</lem><rdg>ὠνουμένῃ</rdg></app></ab>',
            ".//certainty",
            "",
            id="certainty",
        ),
    ],
)
def test_converter(xml_string, xpath, expected_text):
    converter = Converter()
    doc = ET.fromstring(xml_string)
    element = doc.find(xpath)
    txt = converter._convert(element)
    assert not converter.errors
    assert txt == expected_text


def test_space_perserved():
    converter = Converter()
    element = ET.fromstring(
        '<ab xmlns="http://www.tei-c.org/ns/1.0" xml:space="preserve">\n    Text\n</ab>'
    )
    txt = converter._convert(element)
    assert txt == "\n    Text\n"


def test_space_default():
    converter = Converter()
    element = ET.fromstring(
        '<ab xmlns="http://www.tei-c.org/ns/1.0" xml:space="default" >\n    Text\n</ab>',
        parser=ET.XMLParser(recover=True, remove_blank_text=True),
    )
    txt = converter._convert(element)
    assert txt == "\n    Text\n"
