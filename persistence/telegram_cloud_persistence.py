from typing import DefaultDict, Optional, Tuple
from telegram.ext import BasePersistence
from telegram import Bot
from telegram.ext.utils.types import BD, CD, UD, CDCData, ConversationDict
import pickle
from threading import Timer


class TelegramCloudPersistence(BasePersistence):
    def __init__(
        self,
        bot_token: str,
        cloud_chat_id: int,
        on_flush: bool = False,
        store_user_data: bool = True,
        store_chat_data: bool = True,
        store_bot_data: bool = True,
    ):
        self.bot = Bot(bot_token)
        self.cloud = self.bot.get_chat(cloud_chat_id)
        self.store_user_data = store_user_data
        self.store_chat_data = store_chat_data
        self.store_bot_data = store_bot_data
        self.on_flush = on_flush

        self.upload_scheduled = False
        self.schedule_timer: Timer = None

        pinned = self.cloud.pinned_message
        if pinned:
            f = open("data.pickle", "w+b")
            pinned.document.get_file().download(out=f)

            data = pickle.load(f)
            f.close()

            self.bot_data = data["bot_data"]
            self.chat_data = data["chat_data"]
            self.user_data = data["user_data"]
        else:
            self.bot_data: BD = {}
            self.chat_data: DefaultDict[int, CD] = {}
            self.user_data: DefaultDict[int, UD] = {}

    def schedule_upload(self, time: float):
        if self.upload_scheduled:
            return

        self.schedule_timer = Timer(interval=time, function=self.compile_and_upload)
        self.schedule_timer.start()
        self.upload_scheduled = True

    def compile_and_upload(self) -> None:
        self.upload_scheduled = False
        data = {
            "bot_data": self.bot_data,
            "chat_data": self.chat_data,
            "user_data": self.user_data,
        }

        f = open("data.pickle", "w+b")
        pickle.dump(data, f)
        sent = self.cloud.send_document(f, filename="data.pickle")
        self.cloud.pin_message(sent.message_id)

        f.close()

    def get_bot_data(self) -> BD:
        return self.bot_data

    def refresh_bot_data(self, bot_data: BD) -> None:
        pass

    def update_bot_data(self, data: BD) -> None:
        self.bot_data = data
        if not self.on_flush:
            self.schedule_upload(10)

    def get_chat_data(self) -> DefaultDict[int, CD]:
        return self.chat_data

    def refresh_chat_data(self, chat_id: int, chat_data: CD) -> None:
        pass

    def update_chat_data(self, chat_id: int, data: CD) -> None:
        self.chat_data[chat_id] = data
        if not self.on_flush:
            self.schedule_upload(10)

    def get_user_data(self) -> DefaultDict[int, UD]:
        return self.user_data

    def refresh_user_data(self, user_id: int, user_data: UD) -> None:
        pass

    def update_user_data(self, user_id: int, data: UD) -> None:
        self.user_data[user_id] = data
        if not self.on_flush:
            self.schedule_upload(10)

    def get_callback_data(self) -> Optional[CDCData]:
        pass

    def update_callback_data(self, data: CDCData) -> None:
        pass

    def get_conversations(self, name: str) -> ConversationDict:
        pass

    def update_conversation(
        self, name: str, key: Tuple[int, ...], new_state: Optional[object]
    ) -> None:
        pass

    def flush(self) -> None:
        try:
            self.schedule_timer.cancel()
        finally:
            self.upload_scheduled = False
            self.compile_and_upload()
