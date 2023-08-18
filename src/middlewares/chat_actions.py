from typing import Callable, Dict, Any, Awaitable, Literal

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from aiogram_dialog import DialogManager


class ChatActions(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        chat_action = get_flag(data, 'chat_action')
        if not chat_action:
            return await handler(event, data)

        async with ChatActionSender(bot=data['bot'], action=chat_action, chat_id=event.chat.id):
            return await handler(event, data)


ChatActionType = Literal[
    "cancel", "typing", "playing", "choose_contact", "upload_photo", "record_video",
    "upload_video", "record_audio", "upload_audio", "upload_document", "find_location",
    "record_video_note", "upload_video_note"
]


class SimpleActions:
    def __init__(self, dialog_manager: 'DialogManager', chat_action: ChatActionType):
        self.dialog_manager = dialog_manager
        self.chat_action = chat_action
        self.action_sender = None

    async def aenter(self):
        self.action_sender = ChatActionSender(
            bot=self.dialog_manager.middleware_data.get("bot"),
            action=self.chat_action,
            chat_id=self.dialog_manager.event.chat.id
        )
        await self.action_sender.__aenter__()
        return self.action_sender

    async def aexit(self, exc_type, exc_val, exc_tb):
        await self.action_sender.aexit(exc_type, exc_val, exc_tb)
