import re
import lxml.etree as ET

from maat.utils import (
    children,
    is_element,
    is_inside_element,
    is_text,
    tag_localname,
)


def in_supplied_element(element):
    """
    Check if an element is within a `supplied` element
    """
    return is_inside_element(element, "supplied")


def which_test_context(element):
    """
    What is the test context of an element?
    """
    if in_supplied_element(element):
        return "evaluation"
    return "context"


def remove_gaps_from_supplied_text(text):
    """
    If there is a . inside brackets, move it outside, creating new brackets.
    >>> remove_gaps_from_supplied_text("[abd.efg]")
    "[abd].[efg]"
    >>> remove_gaps_from_supplied_text("[abd....efg.....hij]")
    "[abd]....[efg].....[hij]"
    >>> remove_gaps_from_supplied_text("[...abd...efg...hij...]")
    "...[abd]...[efg]...[hij]..."
    >>> remove_gaps_from_supplied_text("[]")
    ''
    >>> remove_gaps_from_supplied_text("[.]")
    "."
    >>> remove_gaps_from_supplied_text("[a]")
    "[a]"
    """
    # first, let's remove the outer brackets
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    # ensure there are no brackets inside brackets
    if "[" in text:
        raise ValueError(f"Nested brackets in {text}")
    if "]" in text:
        raise ValueError(f"Nested brackets in {text}")
    # let's place brackets around the non-dot groups
    return re.sub(r"([^.]+)", r"[\1]", text)


class Converter:
    def __init__(self, raise_on_error=False):
        self.tag_handlers = {}
        self.raise_on_error = raise_on_error
        self.errors = []
        self.iniitalize_tag_handlers()
        self.depth = 0

    def error(self, e):
        self.errors.append(e)
        if self.raise_on_error:
            raise e

    def register_tag_handler(self, tag):
        # the func is the method named `tag` + '_text'
        func = getattr(self, f"{tag}_text")
        self.tag_handlers[tag] = func
        return func

    def iniitalize_tag_handlers(self):
        # TODO: There must be a way to create decorators for this
        self.register_tag_handler("ab")
        self.register_tag_handler("abbr")
        self.register_tag_handler("add")
        self.register_tag_handler("app")
        self.register_tag_handler("certainty")
        self.register_tag_handler("choice")
        self.register_tag_handler("del")
        self.register_tag_handler("expan")
        self.register_tag_handler("ex")
        self.register_tag_handler("figure")
        self.register_tag_handler("foreign")
        self.register_tag_handler("g")
        self.register_tag_handler("gap")
        self.register_tag_handler("handShift")
        self.register_tag_handler("hi")
        self.register_tag_handler("lb")
        self.register_tag_handler("lem")
        self.register_tag_handler("milestone")
        self.register_tag_handler("note")
        self.register_tag_handler("num")
        self.register_tag_handler("orig")
        self.register_tag_handler("q")
        self.register_tag_handler("rdg")
        self.register_tag_handler("seg")
        self.register_tag_handler("sic")
        self.register_tag_handler("subst")
        self.register_tag_handler("supplied")
        self.register_tag_handler("surplus")
        self.register_tag_handler("unclear")

    def post_process(self, text):
        """
        Post-process the text. Remove wholly empty lines.
        """

        def is_empty_line(line):
            return re.match(r"(-- )+", line)

        lines = [
            line
            for line in text.split("\n")
            if line and not line.isspace() and not is_empty_line(line)
        ]
        txt = "\n".join(lines)
        # remove leading and trailing '.' characters
        txt = txt.strip(".")
        # wrap in a <ab> element
        txt = f"<ab>{txt}</ab>"
        return ET.fromstring(
            txt,
            parser=ET.XMLParser(recover=True, remove_blank_text=True),
        )

    def convert(self, element):
        """
        Convert an element to supplied-only ab format
        """
        self.depth = 0
        return self.post_process(self._convert(element))

    def __call__(self, element):
        return self.convert(element)

    def _convert(self, thing):
        # print(f"At {self.depth}, Converting {thing}")
        if is_text(thing):
            return self.handle_text(thing)
        if is_element(thing):
            return self.handle_element(thing)
        self.error(ValueError(f"Cannot handle {thing}"))

    def handle_text(self, text):
        return text

    def handle_element(self, element):
        tag = tag_localname(element)
        handler = self.tag_handlers.get(tag, None)
        if handler is None:
            self.error(ValueError(f"No handler for {tag}"))
            return self.default_handler(element)
        return handler(element)

    def default_handler(self, element):
        if element is None:
            return ""
        text = ""
        for child in children(element):
            self.depth += 1
            text += self._convert(child)
            # self.depth -= 1
        return text

    def ab_text(self, element):
        return self.default_handler(element)

    def abbr_text(self, element):
        return self.default_handler(element)

    def add_text(self, element):
        return self.default_handler(element)

    def app_text(self, element):
        """
        Extract text from app elements.
        """
        t = element.get("type", "unknown")
        if t != "alternative":
            return ""
        ok_tags = ["lem", "rdg"]
        return self.text_from_acceptable_children(element, ok_tags)

    def certainty_text(self, element):
        return ""

    def choice_text(self, element):
        """
        Extract text from choice elements. We take the first choice.
        that is an abbr, choice, orig, sic, or unclear element
        """
        ok_tags = ["abbr", "choice", "orig", "sic", "unclear"]
        return self.text_from_acceptable_children(element, ok_tags)

    def del_text(self, element):
        return ""

    def expan_text(self, element):
        return self.default_handler(element)

    def ex_text(self, element):
        return ""

    def figure_text(self, element):
        return ""

    def foreign_text(self, element):
        return self.default_handler(element)

    def g_text(self, element):
        return ""

    def gap_text(self, element):
        """
        Extract text from gap elements.
        """
        if element.get("unit") == "line":
            return "<gap />"
        amt_txt = element.get("quantity", "unknown")
        if amt_txt == "unknown":
            return "<gap />"
        amt = 0
        try:
            amt = int(amt_txt)
        except ValueError:
            self.error(ValueError(f"Invalid quantity: {amt_txt}"))
            return "<gap />"
        return "." * amt

    def handShift_text(self, element):
        return ""

    def hi_text(self, element):
        return self.default_handler(element)

    def lb_text(self, element):
        return "\n"

    def lem_text(self, element):
        return self.default_handler(element)

    def milestone_text(self, element):
        return ""

    def note_text(self, element):
        return ""

    def num_text(self, element):
        return self.default_handler(element)

    def orig_text(self, element):
        return self.default_handler(element)

    def q_text(self, element):
        return self.default_handler(element)

    def rdg_text(self, element):
        return self.default_handler(element)

    def seg_text(self, element):
        return self.default_handler(element)

    def sic_text(self, element):
        return self.default_handler(element)

    def subst_text(self, element):
        return self.default_handler(element)

    def supplied_text(self, element):
        """
        Extract text from supplied elements.
        """
        if element.get("reason") in ["lost", "illegible"]:
            repaired = remove_gaps_from_supplied_text(
                "[" + self.default_handler(element) + "]"
            )
            # replace brackets with supplied tag
            return re.sub(r"\[([^\[\]]+)\]", r"<supplied>\1</supplied>", repaired)

        else:
            return ""  # some other reason, probably 'omitted' or 'undefined'

    def surplus_text(self, element):
        return self.default_handler(element)

    def unclear_text(self, element):
        return self.default_handler(element)

    # Misc. functions
    def text_from_acceptable_children(self, element, acceptable_tags):
        """
        Extract text from acceptable children of an element.
        """
        ok_children = [
            child for child in element if tag_localname(child) in acceptable_tags
        ]
        if which_test_context(element) == "context":
            if ok_children:
                self.depth += 1
                text = self._convert(ok_children[0])
                # self.depth -= 1
                return text
            else:
                self.error(
                    ValueError(
                        f"No acceptable choice; must be one of {', '.join(acceptable_tags)}"
                    )
                )
                return ""
        elif which_test_context(element) == "evaluation":
            converted = []
            for child in ok_children:
                self.depth += 1
                converted.append(self._convert(child))
                # self.depth -= 1
            if len(converted) == 1:
                return converted[0]
            else:
                return "<alt>" + "</alt><alt>".join(converted) + "</alt>"
        else:
            self.error(ValueError("Unknown context for choice element"))
            return ""
