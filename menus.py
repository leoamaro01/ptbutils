from typing import Callable, Optional, Union
from telegram import Bot, Chat, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext
from prompts import BotPrompt, send_prompt


class BotMenu:
    def __init__(
        self,
        text: str,
        markup: ReplyKeyboardMarkup,
        callbacks: list[
            Union[
                Callable[[Update, CallbackContext], None],
                "BotMenu",
                BotPrompt,
            ]
        ],
        **kwargs,
    ) -> None:
        """
        A simple menu that consists of a message and several ReplyKeyboard
        buttons, where each button creates a callback when pressed. Callbacks can
        be either a function, prompt or another menu.
        """
        button_count = 0
        for row in markup.keyboard:
            for _ in row:
                button_count += 1

        if button_count != len(callbacks):
            raise ValueError(
                "Attempted to create BotMenu containing a"
                "different amount of callbacks and buttons."
                f"{button_count} buttons and {len(callbacks)} callbacks"
            )

        self.text = text
        self.markup = markup
        self.callbacks = callbacks
        self.kwargs = kwargs


def send_menu(chat: Chat, chat_data: dict, menu: BotMenu):
    """Sends a "menu" to a chat, and defines callbacks for each answer."""

    chat.send_message(text=menu.text, reply_markup=menu.markup, **menu.kwargs)

    menu_callbacks = chat_data.get("menu_callbacks")
    # Clear any previous callbacks
    if menu_callbacks:
        menu_callbacks.clear()

    buttons = []
    for row in menu.markup.keyboard:
        for button in row:
            if isinstance(button, KeyboardButton):
                buttons.append(button.text)
            else:
                buttons.append(button)

    menu_callbacks = {
        button: callback for (button, callback) in zip(buttons, menu.callbacks)
    }


def menu_listener(update: Update, context: CallbackContext):
    """Listens to buttons pressed in defined menus"""
    menu_callbacks = context.chat_data.get("menu_callbacks")

    if not menu_callbacks:
        return

    text = update.message.text
    if not text in menu_callbacks:
        return

    callback = menu_callbacks[text]

    if isinstance(callback, BotMenu):
        send_menu(update.effective_chat, context.chat_data, callback)
    elif isinstance(callback, BotPrompt):
        send_prompt()
