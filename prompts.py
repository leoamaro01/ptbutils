from telegram import Chat, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext
from typing import Callable


class BotPrompt:
    def __init__(
        self,
        text: str,
        callback: Callable[[Update, CallbackContext], None],
        validator: Callable[[Update, CallbackContext], bool] = None,
        on_cancel: Callable[[Update, CallbackContext], None] = None,
        cancel_button_text: str = None,
        resize_keyboard: bool = True,
        **kwargs
    ) -> None:
        """
        Simple prompt that expects user input with optional
        input validation and on correct validation, callback"""

        self.resize_keyboard = resize_keyboard
        self.text = text
        self.validator = validator
        self.callback = callback
        self.on_cancel = on_cancel
        self.cancel_button_text = cancel_button_text
        self.kwargs = kwargs


def send_prompt(chat: Chat, chat_data: dict, prompt: BotPrompt):
    if not prompt.on_cancel or not prompt.cancel_button_text:
        chat.send_message(text=prompt.text, **prompt.kwargs)
    else:
        chat.send_message(
            text=prompt.text,
            reply_markup=ReplyKeyboardMarkup.from_button(
                button=prompt.cancel_button_text,
                resize_keyboard=prompt.resize_keyboard,
            ),
            **prompt.kwargs,
        )

    chat_data["current_prompt"] = prompt


def prompt_listener(update: Update, context: CallbackContext):
    PROMPT_LITERAL = "current_prompt"
    current_prompt: BotPrompt = context.chat_data[PROMPT_LITERAL]
    if not current_prompt:
        return

    validator = current_prompt.validator
    callback = current_prompt.callback
    on_cancel = current_prompt.on_cancel
    cancel_text = current_prompt.cancel_button_text
    msg = update.message.text

    if on_cancel and cancel_text and cancel_text == msg:
        on_cancel(update, context)
        context.chat_data[PROMPT_LITERAL] = None
        return

    if callback and (not validator or validator(update, context)):
        callback(update, context)
        context.chat_data[PROMPT_LITERAL] = None
