from aiogram.enums import ParseMode


async def send_notification(chat_id: int, text: str, bot):
    await bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)

