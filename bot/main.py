# bot/main.py
import asyncio
import logging
import sys

from .bot_instance import bot, dp
# handlers papkasidan common, weather va ENDI currency modullarini import qilamiz
from .handlers import common, weather, currency # <<< 'currency' MODULINI IMPORT QILAMIZ

async def main():
    """
    Botni ishga tushiruvchi asosiy asinxron funksiya.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        stream=sys.stdout,
    )

    # Routerlarni dispatcherga ulaymiz
    dp.include_router(common.router)     # umumiy buyruqlar uchun
    dp.include_router(weather.router)    # ob-havo buyruqlari uchun
    dp.include_router(currency.router)   # <<< VALYUTA KURSLARI UCHUN ROUTERNI QO'SHING

    # Bot ishga tushishidan oldin to'plangan, lekin qayta ishlanmagan
    # xabarlarni o'chirib yuborish.
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Pollingni boshlash.
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot ishlashi foydalanuvchi tomonidan to'xtatildi.")