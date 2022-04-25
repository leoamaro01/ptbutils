from argparse import ArgumentError
from multiprocessing import reduction
from typing import Callable, Optional
import untangle
from telegram import Update
from telegram.ext import CallbackContext
from tools._utility_functions import _func_path_to_callable


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

    def __eq__(self, __o: object) -> bool:
        try:
            if self.buttons:
                l = len(self.buttons)
                if l != len(__o.buttons):
                    return False
                for i in range(l):
                    if self.buttons[i] != __o.buttons[i]:
                        return False
            elif __o.buttons:
                return False

            if self.formats:
                l = len(self.formats)
                if l != len(__o.formats):
                    return False
                for i in range(l):
                    if self.formats[i] != __o.formats[i]:
                        return False
            elif __o.formats:
                return False

            return self.name == __o.name and self.text == __o.text
        except:
            return False

    def __str__(self) -> str:
        return str(
            {
                "name": self.name,
                "text": self.text,
                "formats": self.formats,
                "buttons": str([str(button) for button in self.buttons]),
            }
        )


class XMLMenuButton:
    def __init__(
        self,
        text: str,
        row: Optional[int] = None,
        callback_function: Optional[Callable[[Update, CallbackContext], None]] = None,
        prompt_link: Optional[str] = None,
        menu_link: Optional[str] = None,
    ) -> None:
        if not callback_function and not prompt_link and not menu_link:
            raise ArgumentError(message="No callback provided")

        self.text = text
        self.row = row if row is not None and row >= 0 else -1
        self.callback_function = callback_function
        self.prompt_link = prompt_link
        self.menu_link = menu_link

    def __eq__(self, __o: object) -> bool:
        try:
            return (
                self.text == __o.text
                and self.row == __o.row
                and self.callback_function == __o.callback_function
                and self.prompt_link == __o.prompt_link
                and self.menu_link == __o.menu_link
            )
        except:
            return False

    def __str__(self) -> str:
        return str(
            {
                "text": self.text,
                "row": self.row,
                "function": self.callback_function,
                "prompt": self.prompt_link,
                "menu": self.menu_link,
            }
        )


def xml2menu(xml: str) -> XMLMenu:
    menu_xml = untangle.parse(xml)

    try:
        root = menu_xml.menu
    except:
        raise ValueError("The XML isn't a menu. The root tag must be a 'menu' tag.")

    menu_name = root["name"]
    formats = root.get_attribute("formats")
    menu_formats = formats.split(",") if formats else None
    raw_menu_text = root.text.cdata.strip("\n ")
    menu_text = "\n".join([l.strip("\n ") for l in raw_menu_text.splitlines()])
    buttons = [
        XMLMenuButton(
            "\n".join(
                [l.strip("\n ") for l in button.text.cdata.strip("\n ").splitlines()]
            ),
            int(button.get_attribute("row")) if button.get_attribute("row") else -1,
            (
                _func_path_to_callable(button.callback.get_attribute("function"))
                if button.callback.get_attribute("function")
                else None
            ),
            button.callback.get_attribute("prompt_link"),
            button.callback.get_attribute("menu_link"),
        )
        for button in root.buttons.get_elements("button")
    ]

    return XMLMenu(menu_name, menu_text, menu_formats, buttons)
