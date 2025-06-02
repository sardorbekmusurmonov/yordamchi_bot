# bot/bot_instance.py
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties # <<< BU QATORNI QO'SHING yoki O'ZGARTIRING

# Avval yaratgan config_reader.py faylimizdan API_TOKEN ni import qilamiz.
from .config_reader import API_TOKEN

# Bot obyekti
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

# Dispatcher obyekti
dp = Dispatcher()