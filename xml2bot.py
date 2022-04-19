from typing import Callable, Optional, Union
from click import prompt
from telegram import Chat, Update
from telegram.ext import CallbackContext
import untangle
from menus import BotMenu
from prompts import BotPrompt, send_prompt


class XMLMenu:
    def __init__(
        self,
        name: str,
        text: str,
        formats: list[str],
        buttons: list["XMLMenuButton"],
    ) -> None:
        self.name = name
        self.text = text
        self.formats = formats
        self.buttons = buttons


class XMLMenuButton:
    def __init__(
        self,
        text: str,
        callback_function: Optional[Callable[[Update, CallbackContext], None]] = None,
        prompt_link: Optional[str] = None,
        menu_link: Optional[str] = None,
    ) -> None:
        self.text = text
        self.callback_function = callback_function
        self.prompt_link = prompt_link
        self.menu_link = menu_link


class XMLPrompt:
    def __init__(
        self,
        name: str,
        text: str,
        formats: list[str],
        validator: str,
        callback: str,
        cancel_text: str,
        cancel_callback: str,
    ) -> None:
        self.name = name
        self.text = text
        self.formats = formats
        self.validator = validator
        self.callback = callback
        self.cancel_text = cancel_text
        self.cancel_callback = cancel_callback


def import_xml_menu(xml: str) -> XMLMenu:
    menu_xml = untangle.parse(xml)

    try:
        root = menu_xml.menu
    except:
        raise ValueError("The XML isn't a menu. The root tag must be a 'menu' tag.")

    menu_name = root["name"]
    formats = root.get_attribute("formats")
    menu_formats = formats.split(",") if formats else None
    menu_text = root.text.cdata

    buttons = [
        XMLMenuButton(
            button.text.cdata,
            button.callback.get_attribute("function"),
            button.callback.get_attribute("prompt_link"),
            button.callback.get_attribute("menu_link"),
        )
        for button in root.buttons.get_elements("button")
    ]

    return XMLMenu(menu_name, menu_text, menu_formats, buttons)


def import_xml_prompt(xml: str) -> XMLPrompt:
    prompt_xml = untangle.parse(xml)

    try:
        root = prompt_xml.prompt
    except:
        raise ValueError("The XML isn't a prompt. The root tag must be a 'prompt' tag.")

    prompt_name = root["name"]
    formats = root.get_attribute("formats")
    prompt_formats = formats.split(",") if formats else None
    prompt_text = root.text.cdata

    try:
        prompt_validator = root.validator["function"]
    except:
        prompt_validator = None

    prompt_callback = root.callback["function"]

    try:
        prompt_cancel_text = root.cancel.text.cdata
        prompt_cancel_callback = root.cancel.callback["function"]
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


def _func_path_to_callable(path: str) -> Callable:
    import importlib

    module_name, func_name = path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, func_name)


def send_xml_prompt(
    xml_prompt: XMLPrompt,
    chat: Chat,
    chat_data: dict,
    resize_keyboard: bool = True,
    **kwargs,
):
    callback = _func_path_to_callable(xml_prompt.callback)
    validator = _func_path_to_callable(xml_prompt.validator)

    if xml_prompt.cancel_callback:
        cancel_callback = _func_path_to_callable(xml_prompt.cancel_callback)
    else:
        cancel_callback = None

    prompt_text = xml_prompt.text.format(**kwargs)
    cancel_text = xml_prompt.cancel_text.format(**kwargs)

    prompt = BotPrompt(
        prompt_text,
        callback,
        validator,
        cancel_callback,
        cancel_text,
        resize_keyboard,
    )

    send_prompt(chat, chat_data, prompt)


def send_xml_menu(
    xml_menu: XMLMenu,
    chat: Chat,
    chat_data: dict,
    resize_keyboard: bool = True,
    **kwargs,
):
    pass


# It is necessary to cache all menus and prompts
# before sending them, this is a major design change
# and should be well thought
