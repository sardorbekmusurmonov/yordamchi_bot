# bot/handlers/currency.py
import aiohttp
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.filters.command import CommandObject

router = Router()

# Markaziy Bank API manzili
CBU_API_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
# Agar foydalanuvchi aniq valyuta kiritmasa ko'rsatiladigan standart valyutalar
DEFAULT_CURRENCIES = ['USD', 'EUR', 'RUB'] 

@router.message(Command("kurs", "valyuta")) # /kurs yoki /valyuta buyrug'i uchun
async def get_currency_rates(message: types.Message, command: CommandObject):
    """
    /kurs yoki /valyuta buyrug'iga javob beradi.
    Agar argument berilsa (masalan, /kurs USD), o'sha valyutani qidiradi.
    Aks holda, DEFAULT_CURRENCIES ro'yxatidagilarni ko'rsatadi.
    """
    target_currency_code = None
    if command.args:
        target_currency_code = command.args.strip().upper()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CBU_API_URL) as response:
                if response.status == 200:
                    rates_data = await response.json() # API javobini JSON dan Python ro'yxatiga o'tkazamiz
                    
                    if not rates_data:
                        await message.answer("😕 Markaziy Bankdan hozircha ma'lumot olib bo'lmadi.")
                        return

                    # Kurslar sanasini olamiz (odatda birinchi elementda bo'ladi)
                    rates_date = rates_data[0].get('Date', 'N/A')
                    reply_parts = [f"<b>🇺🇿 O'zbekiston Markaziy Banki valyuta kurslari ({rates_date}):</b>\n"]
                    
                    found_any_currency = False

                    if target_currency_code: # Aniq valyuta so'ralgan bo'lsa
                        for rate_info in rates_data:
                            if rate_info['Ccy'] == target_currency_code:
                                nominal = rate_info.get('Nominal', '1')
                                rate_value = rate_info.get('Rate', 'N/A')
                                ccy_name_uz = rate_info.get('CcyNm_UZ', target_currency_code)
                                
                                reply_parts.append(
                                    f"<b>{nominal} {ccy_name_uz} ({rate_info['Ccy']}):</b> {rate_value} UZS"
                                )
                                found_any_currency = True
                                break
                        if not found_any_currency:
                            reply_parts.append(f"😕 <b>{target_currency_code}</b> uchun ma'lumot topilmadi.")
                    else: # Standart valyutalar uchun
                        for rate_info in rates_data:
                            if rate_info['Ccy'] in DEFAULT_CURRENCIES:
                                nominal = rate_info.get('Nominal', '1')
                                rate_value = rate_info.get('Rate', 'N/A')
                                ccy_name_uz = rate_info.get('CcyNm_UZ', rate_info['Ccy'])
                                
                                reply_parts.append(
                                    f"<b>{nominal} {ccy_name_uz} ({rate_info['Ccy']}):</b> {rate_value} UZS"
                                )
                                found_any_currency = True
                        if not found_any_currency:
                             reply_parts.append("😕 Asosiy valyutalar uchun ma'lumot topilmadi.")
                    
                    await message.answer("\n".join(reply_parts))

                else:
                    await message.answer(
                        f"Markaziy Bank API'sidan ma'lumot olishda xatolik (status: {response.status}).\n"
                        "Iltimos, keyinroq qayta urinib ko'ring."
                    )
    except aiohttp.ClientConnectorError as e:
        print(f"CBU API ga ulanishda xatolik: {e}") # Siz uchun log
        await message.answer("Valyuta kurslari xizmatiga ulanib bo'lmadi. Internet aloqangizni tekshiring yoki keyinroq urinib ko'ring.")
    except Exception as e:
        print(f"Valyuta kursi handlerida kutilmagan xatolik: {e}") # Siz uchun log
        await message.answer("Valyuta kurslarini ko'rsatishda kutilmagan xatolik yuz berdi.")
        
@router.message(Command("kursfull"))
async def get_all_currency_rates(message: types.Message):
    """
    /kursfull buyrug'iga javob beradi va Markaziy Bankdagi
    barcha valyuta kurslarini chiqaradi.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CBU_API_URL) as response:
                if response.status == 200:
                    rates_data = await response.json()
                    
                    if not rates_data:
                        await message.answer("😕 Markaziy Bankdan hozircha ma'lumot olib bo'lmadi.")
                        return

                    rates_date = rates_data[0].get('Date', 'N/A')
                    reply_parts = [f"<b>🇺🇿 O'zbekiston Markaziy Banki valyuta kurslari ({rates_date}):</b>\n\n<b>Barcha mavjud valyutalar:</b>\n"]
                    
                    for rate_info in rates_data:
                        nominal = rate_info.get('Nominal', '1')
                        rate_value = rate_info.get('Rate', 'N/A')
                        ccy_name_uz = rate_info.get('CcyNm_UZ', rate_info.get('Ccy', 'Noma\'lum'))
                        ccy_code = rate_info.get('Ccy', '')
                        
                        reply_parts.append(
                            f"<b>{nominal} {ccy_name_uz} ({ccy_code}):</b> {rate_value} UZS"
                        )
                    
                    # Xabar juda uzun bo'lib ketmasligi uchun tekshiruv (shart emas, lekin yaxshi amaliyot)
                    # Telegram xabarining maksimal uzunligi 4096 belgidan iborat.
                    # Hozircha bu tekshiruvsiz yuboramiz. Agar muammo bo'lsa, keyin qo'shishimiz mumkin.
                    await message.answer("\n".join(reply_parts))

                else:
                    await message.answer(
                        f"Markaziy Bank API'sidan ma'lumot olishda xatolik (status: {response.status}).\n"
                        "Iltimos, keyinroq qayta urinib ko'ring."
                    )
    except aiohttp.ClientConnectorError as e:
        print(f"CBU API ga ulanishda xatolik ( /kursfull ): {e}") # Siz uchun log
        await message.answer("Valyuta kurslari xizmatiga ulanib bo'lmadi. Internet aloqangizni tekshiring yoki keyinroq urinib ko'ring.")
    except Exception as e:
        print(f"Valyuta kursi (/kursfull) handlerida kutilmagan xatolik: {e}") # Siz uchun log
        await message.answer("Barcha valyuta kurslarini ko'rsatishda kutilmagan xatolik yuz berdi.")