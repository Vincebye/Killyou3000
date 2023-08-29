from telegram import Bot
import configparser
import asyncio
# 创建配置解析器对象
config = configparser.ConfigParser()

async def send_telegram_notification(bot_token, chat_id, message):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)

config.read("config.ini")
token=config.get('telegram','bot_token')
chatid=config.get('telegram','chat_id')
# 使用您的Telegram Bot Token和Chat ID调用函数发送通知
message = 'Good Night!'

asyncio.run(send_telegram_notification(token, chatid, message))