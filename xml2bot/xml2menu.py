from argparse import ArgumentError
from typing import Callable, Optional
import untangle
from telegram import Update
from telegram.ext import CallbackContext
from tools._utility_functions import _func_path_to_callable
from errors import MenuParseError


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
        except AttributeError or IndexError:
            return False


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


def parse_menu(xml: str, **kwargs) -> XMLMenu:
    menu_xml = untangle.parse(xml)

    try:
        root = menu_xml.menu
    except:
        raise MenuParseError(
            xml, "The XML isn't a menu. The root tag must be a 'menu' tag."
        )

    menu_name = root.get_attribute("name")
    if not menu_name:
        if "name" in kwargs and kwargs["name"]:
            menu_name = kwargs["name"]
        else:
            raise MenuParseError(
                xml,
                "No name provided for the menu."
                'Tip: You can provide a name through the "name" attribute'
                "in the menu tag or as a keyword argument for this method.",
            )

    formats = root.get_attribute("formats")
    menu_formats = formats.split(",") if formats else None
    try:
        raw_menu_text = root.text.cdata.strip("\n ")
        menu_text = "\n".join([l.strip("\n ") for l in raw_menu_text.splitlines()])
    except AttributeError:
        raise MenuParseError(xml, 'A menu must contain a "text" element.')

    buttons = []
    try:
        button_elements = root.buttons.get_elements("button")
    except AttributeError:
        raise MenuParseError(xml, 'A menu must contain a "buttons" element.')

    if not button_elements:
        raise MenuParseError(xml, "A menu can't be defined without buttons.")

    for button in button_elements:
        try:
            button_text = "\n".join(
                [l.strip("\n ") for l in button.text.cdata.strip("\n ").splitlines()]
            )
        except AttributeError:
            raise MenuParseError(
                xml, 'A button can\'t be defined without a "text" element.'
            )

        button_row = (
            int(button.get_attribute("row")) if button.get_attribute("row") else -1
        )

        try:
            button_function = (
                _func_path_to_callable(button.callback.get_attribute("function"))
                if button.callback.get_attribute("function")
                else None
            )
        except AttributeError:
            raise MenuParseError(xml, "A button can't be defined without a callback.")
        except:
            raise MenuParseError(
                xml,
                "Error loading callback function in a button, check"
                "the module and function name is correct. Also check"
                "that the package directory is in `sys.path`. If in doubt check"
                "out http://stackoverflow.com/questions/14132789/ddg#14132912.",
            )
        button_menu_link = button.callback.get_attribute("menu_link")
        button_prompt_link = button.callback.get_attribute("prompt_link")

        if not button_function and not button_menu_link and not button_prompt_link:
            raise MenuParseError(xml, "A button can't be defined without a callback.")

        buttons.append(
            XMLMenuButton(
                text=button_text,
                row=button_row,
                callback_function=button_function,
                prompt_link=button_prompt_link,
                menu_link=button_menu_link,
            )
        )

    return XMLMenu(menu_name, menu_text, menu_formats, buttons)
