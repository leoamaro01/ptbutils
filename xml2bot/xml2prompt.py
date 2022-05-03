from typing import Callable
from telegram import Update
import untangle
from telegram.ext import CallbackContext
from tools._utility_functions import _func_path_to_callable


class XMLPrompt:
    def __init__(
        self,
        name: str,
        text: str,
        formats: list[str],
        validator: Callable[[str], bool] = None,
        callback: Callable[[Update, CallbackContext], None] = None,
        cancel_text: str = None,
        cancel_callback: Callable[[Update, CallbackContext], None] = None,
    ) -> None:
        self.name = name
        self.text = text
        self.formats = formats
        self.validator = validator
        self.callback = callback
        self.cancel_text = cancel_text
        self.cancel_callback = cancel_callback

    def __eq__(self, __o: object) -> bool:
        try:
            assert (
                self.name == __o.name
                and self.text == __o.text
                and self.validator == __o.validator
                and self.callback == __o.callback
                and self.cancel_text == __o.cancel_text
                and self.cancel_callback == __o.cancel_callback
                and (
                    (self.formats and __o.formats)
                    or (not self.formats and not __o.formats)
                )
            )

            l = len(self.formats)
            assert l == len(__o.formats)

            for i in range(l):
                assert self.formats[i] == __o.formats[i]
        except AttributeError or AssertionError:
            return False


def xml2prompt(xml: str) -> XMLPrompt:
    prompt_xml = untangle.parse(xml)

    try:
        root = prompt_xml.prompt
    except:
        raise ValueError("The XML isn't a prompt. The root tag must be a 'prompt' tag.")

    prompt_name = root["name"]
    formats = root.get_attribute("formats")
    prompt_formats = formats.split(",") if formats else None
    raw_prompt_text = root.text.cdata.strip("\n ")
    prompt_text = "\n".join([l.strip("\n ") for l in raw_prompt_text.splitlines()])

    v_attr = root.validator.get_attribute("function")
    prompt_validator = _func_path_to_callable(v_attr) if v_attr else None

    c_attr = root.callback.get_attribute("function")
    prompt_callback = _func_path_to_callable(c_attr) if c_attr else None

    try:
        raw_cancel_text = root.cancel.text.cdata.strip("\n ")
        prompt_cancel_text = "\n".join(
            [l.strip("\n ") for l in raw_cancel_text.splitlines()]
        )
        prompt_cancel_callback = _func_path_to_callable(
            root.cancel.callback["function"]
        )
    except:
        prompt_cancel_text = None
        prompt_cancel_callback = None

    return XMLPrompt(
        prompt_name,
        prompt_text,
        prompt_formats,
        prompt_validator,
        prompt_callback,
        prompt_cancel_text,
        prompt_cancel_callback,
    )
