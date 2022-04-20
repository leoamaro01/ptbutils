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


def xml2prompt(xml: str) -> XMLPrompt:
    prompt_xml = untangle.parse(xml)

    try:
        root = prompt_xml.prompt
    except:
        raise ValueError("The XML isn't a prompt. The root tag must be a 'prompt' tag.")

    prompt_name = root["name"]
    formats = root.get_attribute("formats")
    prompt_formats = formats.split(",") if formats else None
    prompt_text = root.text.cdata

    v_attr = root.validator.get_attribute("function")
    prompt_validator = _func_path_to_callable(v_attr) if v_attr else None

    c_attr = root.callback.get_attribute("function")
    prompt_callback = _func_path_to_callable(c_attr) if c_attr else None

    try:
        prompt_cancel_text = root.cancel.text.cdata
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
