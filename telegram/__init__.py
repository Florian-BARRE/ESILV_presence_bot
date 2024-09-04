from configuration import APP_CONFIG

from telegram.bot import Bot

bot_telegram = Bot(
    token=APP_CONFIG.TOKEN,
    chatID=APP_CONFIG.CHATID
)
