from telegram import Bot
import configparser
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# 创建配置解析器对象
config = configparser.ConfigParser()

async def send_telegram_notification(bot_token, chat_id, message):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)
def send_email(sender_email, sender_password, recipient_email, subject, message):
    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # 添加正文内容
    msg.attach(MIMEText(message, 'plain'))

    # 使用Gmail SMTP服务器发送邮件
    with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)
config.read("config.ini")
token=config.get('telegram','bot_token')
chatid=config.get('telegram','chat_id')

sender_email = config.get('mail', 'sender_email')
sender_password = config.get('mail', 'sender_password')
receive_email = config.get('mail', 'receive_email')

subject = 'Test Email'

message = 'Good Night!'
send_email(sender_email, sender_password, receive_email, subject, message)

#asyncio.run(send_telegram_notification(token, chatid, message))