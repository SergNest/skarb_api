import asyncio
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from conf.config import settings


# Запуск бота
# async def main():
#     bot = Bot(token=settings.token)
#     dp = Dispatcher()
#
#     @dp.message(Command("start"))  # [2]
#     async def cmd_start(message: Message):
#         # chat_id = message.chat.id
#         # await message.reply(f"Привіт! Я бот, що відправляє сповіщення в групу. Ваш chat_id: {chat_id}")
#         await send_notification(-4076579827, "тук тук")
#
#         await bot.delete_webhook(drop_pending_updates=True)
#         await dp.start_polling(bot)


async def send_notification(chat_id: int, text: str, bot):
    await bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)
    # await bot.session.close()


# if __name__ == "__main__":
#     asyncio.run(main())
