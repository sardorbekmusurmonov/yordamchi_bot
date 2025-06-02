# bot/handlers/common.py
from aiogram import Router, types
from aiogram.filters import CommandStart
# Agar /help kabi boshqa buyruqlarni ham qo'shmoqchi bo'lsak:
# from aiogram.filters import Command

# Bu fayldagi handlerlar uchun alohida router yaratamiz.
# Router - bu turli xil xabarlarni (buyruqlar, matnlar, tugmalar)
# tegishli funksiyalarga (handlerlarga) yo'naltirish mexanizmi.
# Katta botlarda kodni modullarga ajratish uchun juda qulay.
router = Router()

# /start buyrug'iga javob beradigan handler (funksiya).
# @router.message(...) dekoratori bu funksiyani ma'lum bir shartga (bu holda /start buyrug'iga)
# javob beradigan qilib ro'yxatdan o'tkazadi.
@router.message(CommandStart())
async def cmd_start(message: types.Message):
    """
    Bu handler /start buyrug'i kelganda ishga tushadi.
    """
    # message.from_user obyektidan foydalanuvchi haqida ma'lumot olish mumkin.
    user_name = message.from_user.full_name
    user_id = message.from_user.id
    
    # Foydalanuvchiga javob yuboramiz.
    # HTML formatlashdan foydalanishimiz mumkin, chunki bot_instance.py da parse_mode=ParseMode.HTML o'rnatganmiz.
    await message.answer(
        f"Assalomu alaykum, <b>{user_name}</b>!\n"
        f"Men sizning shaxsiy yordamchingizman.\n"
        f"Sizning Telegram ID: <code>{user_id}</code>"
    )

# Kelajakda boshqa umumiy buyruqlarni ham shu routerga qo'shishingiz mumkin:
# Masalan, /help buyrug'i:
# @router.message(Command("help"))
# async def cmd_help(message: types.Message):
#     await message.answer("Bu yordamchi bot. Mavjud buyruqlar:\n/start - Botni ishga tushirish")

# Yoki echo handler (har qanday matnli xabarga javob beradigan):
# @router.message()
# async def echo_handler(message: types.Message):
#     await message.reply(f"Siz yozdingiz: {message.text}")