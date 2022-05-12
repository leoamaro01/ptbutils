from typing import Callable, Union

from menus import BotMenu, menu_listener
from prompts import BotPrompt, prompt_listener
from telegram import ReplyKeyboardMarkup
from telegram.ext import Dispatcher, Filters, MessageHandler

from xml2menu import XMLMenu, parse_menu
from xml2prompt import XMLPrompt, parse_prompt


class XMLBot:
    def __init__(
        self,
        menus_path: str,
        prompts_path: str,
        add_listeners: bool = False,
        dispatcher: Dispatcher = None,
    ) -> None:
        self.menus: dict[str, XMLMenu] = {}
        self.prompts: dict[str, XMLPrompt] = {}

        self.compiled_menus: dict[str, BotMenu] = {}
        self.compiled_prompts: dict[str, BotPrompt] = {}

        import os

        try:
            files = [file for file in os.listdir(menus_path) if file.endswith(".xml")]
            for file in files:
                menu = parse_menu(file)
                self.menus[menu.name] = menu
        except OSError:
            pass

        try:
            files = [file for file in os.listdir(prompts_path) if file.endswith(".xml")]
            for file in files:
                prompt = parse_prompt(file)
                self.prompts[prompt.name] = prompt
        except OSError:
            pass

        if add_listeners:
            dispatcher.add_handler(MessageHandler(Filters.text, menu_listener))
            dispatcher.add_handler(MessageHandler(Filters.text, prompt_listener))

    def xml_prompt2bot_prompt(
        self,
        prompt: Union[str, XMLPrompt],
        resize_keyboard: bool = True,
        **kwargs,
    ) -> BotPrompt:
        if isinstance(prompt, str):
            assert prompt in self.prompts, f"Can't send unregistered prompt `{prompt}`"
            prompt = self.prompts[prompt]

        if prompt.name in self.compiled_prompts:
            return self.compiled_prompts[prompt.name]

        bot_prompt = BotPrompt(None, None, None, None, None, None)
        self.compiled_prompts[prompt.name] = bot_prompt

        callback = prompt.callback
        validator = prompt.validator

        cancel_callback = prompt.cancel_callback

        prompt_text = prompt.text.format(**kwargs)
        cancel_text = (
            prompt.cancel_text.format(**kwargs) if prompt.cancel_text else None
        )

        bot_prompt.text = prompt_text
        bot_prompt.callback = callback
        bot_prompt.validator = validator
        bot_prompt.on_cancel = cancel_callback
        bot_prompt.cancel_button_text = cancel_text
        bot_prompt.resize_keyboard = resize_keyboard

        return bot_prompt

    def xml_menu2bot_menu(
        self,
        menu: Union[str, XMLMenu],
        resize_keyboard: bool = True,
        **kwargs,
    ):
        if isinstance(menu, str):
            assert menu in self.menus, f"Can't send unregistered menu `{menu}`"
            menu = self.menus[menu]

        if menu.name in self.compiled_menus:
            return self.compiled_menus[menu.name]

        bot_menu = BotMenu(None, None, None)
        self.compiled_menus[menu.name] = bot_menu

        bot_menu.text = menu.text.format(**kwargs)

        buttons: dict[int, list[tuple[str, Union[Callable, BotMenu, BotPrompt]]]] = {}

        for button in menu.buttons:
            if button.callback_function:
                button_callback = button.callback_function
            elif button.menu_link:
                button_callback = self.xml_menu2bot_menu(
                    button.menu_link, resize_keyboard, **kwargs
                )
            elif button.prompt_link:
                button_callback = self.xml_prompt2bot_prompt(
                    button.prompt_link, resize_keyboard, **kwargs
                )

            row = button.row
            if row == -1:
                i = 0
                while i in buttons:
                    i += 1
                row = i

            if buttons.get(row):
                buttons[row].append((button.text, button_callback))
            else:
                buttons[row] = [(button.text, button_callback)]

        max_key = max(buttons.keys)
        menu_markup: list[list[str]] = []
        menu_callbacks: list[Union[Callable, BotMenu, BotPrompt]] = []
        rows = 0

        for i in range(max_key + 1):
            if i not in buttons:
                continue

            menu_markup.append([])
            for button in buttons[i]:
                menu_markup[rows].append(button[0])
                menu_callbacks.append(button[1])

            rows += 1

        bot_menu.markup = ReplyKeyboardMarkup(menu_markup)
        bot_menu.callbacks = menu_callbacks

        return bot_menu
