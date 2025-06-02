# bot/handlers/weather.py
import aiohttp
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.filters.command import CommandObject

from ..config_reader import WEATHER_API_KEY

# O'zbekcha ob-havo tavsiflari uchun lug'at (OpenWeatherMap ID kodlari asosida)
WEATHER_CONDITION_CODES_UZ = {
    # === Group 2xx: Thunderstorm (Momaqaldiroq) ===
    200: "Momaqaldiroqli yengil yomg'ir",
    201: "Momaqaldiroqli yomg'ir",
    202: "Momaqaldiroqli kuchli yomg'ir",
    210: "Yengil momaqaldiroq",
    211: "Momaqaldiroq",
    212: "Kuchli momaqaldiroq",
    221: "Biroz momaqaldiroq", # ragged thunderstorm
    230: "Momaqaldiroqli yengil moralsama",
    231: "Momaqaldiroqli moralsama",
    232: "Momaqaldiroqli kuchli moralsama",

    # === Group 3xx: Drizzle (Moralsama yomg'ir) ===
    300: "Yengil moralsama",
    301: "Moralsama",
    302: "Kuchli moralsama",
    # ... (ro'yxatni davom ettirishingiz mumkin)

    # === Group 5xx: Rain (Yomg'ir) ===
    500: "Yengil yomg'ir",
    501: "O'rtacha yomg'ir",
    502: "Kuchli yomg'ir",
    503: "Juda kuchli yomg'ir",
    504: "Ekstremal yomg'ir",
    511: "Muzlaydigan yomg'ir", # freezing rain
    520: "Yengil jala",
    521: "Jala", # shower rain
    522: "Kuchli jala",
    531: "Biroz jala", # ragged shower rain

    # === Group 6xx: Snow (Qor) ===
    600: "Yengil qor",
    601: "Qor",
    602: "Kuchli qor",
    # ... (ro'yxatni davom ettirishingiz mumkin)

    # === Group 7xx: Atmosphere (Atmosfera holatlari) ===
    701: "Tuman", # mist
    711: "Tutun", # Smoke
    721: "Chang-g'ubor", # Haze
    731: "Qum/chang bo'ronlari", # sand/dust whirls
    741: "Quyuq tuman", # fog
    751: "Qum", # sand
    761: "Chang", # dust
    762: "Vulqon kuli", # volcanic ash
    771: "Izg'irin", # squalls
    781: "Tornado", # tornado
    
    # === Group 800: Clear (Ochiq osmon) ===
    800: "Ochiq osmon",

    # === Group 80x: Clouds (Bulutlar) ===
    801: "Kam bulutli (11-25%)",
    802: "Tarqoq bulutlar (25-50%)",
    803: "O'zgaruvchan bulutli (51-84%)",
    804: "To'liq bulutli (85-100%)",
}


router = Router()

@router.message(Command("weather"))
async def get_weather(message: types.Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Iltimos, shahar nomini kiriting.\n"
            "Masalan: <code>/weather Toshkent</code>"
        )
        return

    city_name = command.args.strip()
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric&lang=uz" # lang=uz ni qoldiramiz, fallback sifatida

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(weather_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    main_data = data.get('main', {})
                    weather_info_list = data.get('weather', [{}])
                    wind_data = data.get('wind', {})
                    
                    city = data.get('name', city_name)
                    temp = main_data.get('temp', 'N/A')
                    feels_like = main_data.get('feels_like', 'N/A')
                    humidity = main_data.get('humidity', 'N/A')
                    wind_speed = wind_data.get('speed', 'N/A')

                    # Ob-havo tavsifini olish va tarjima qilish
                    api_description = "Noma'lum" # Default
                    if weather_info_list:
                        weather_id = weather_info_list[0].get('id')
                        api_description_fallback = weather_info_list[0].get('description', "Noma'lum").capitalize()
                        # Bizning lug'atimizdan tarjimani qidiramiz
                        description = WEATHER_CONDITION_CODES_UZ.get(weather_id, api_description_fallback)
                    else:
                        description = "Noma'lum"


                    reply_text = (
                        f"<b>📍 {city} shahrida ob-havo:</b>\n\n"
                        f"🌥 Hozir: {description}\n" # <<< O'ZGARGAN QATOR
                        f"🌡️ Harorat: {temp}°C\n"
                        f"🌬️ His qilinishi: {feels_like}°C\n"
                        f"💧 Namlik: {humidity}%\n"
                        f"💨 Shamol tezligi: {wind_speed} m/s"
                    )
                    await message.answer(reply_text)
                # ... (qolgan xatolikni qayta ishlash kodlari o'zgarishsiz qoladi)
                elif response.status == 401:
                    print(f"WEATHER API KEY bilan muammo bo'lishi mumkin. Status: {response.status}")
                    await message.answer(
                        "Ob-havo ma'lumotini olishda xatolik yuz berdi (API kaliti bilan muammo bo'lishi mumkin).\n"
                        "Iltimos, administratorga xabar bering."
                    )
                elif response.status == 404:
                    await message.answer(
                        f"<b>{city_name}</b> nomli shahar topilmadi.\n"
                        "Iltimos, nomini tekshirib qayta urinib ko'ring."
                    )
                else:
                    await message.answer(
                        f"Ob-havo ma'lumotlarini olishda xatolik yuz berdi (server xatosi: {response.status}).\n"
                        "Iltimos, keyinroq qayta urinib ko'ring."
                    )
    except aiohttp.ClientConnectorError as e:
        print(f"OpenWeatherMap ga ulanishda xatolik: {e}")
        await message.answer("Ob-havo xizmatiga ulanib bo'lmadi. Internet aloqangizni tekshiring yoki keyinroq urinib ko'ring.")
    except Exception as e:
        print(f"Ob-havo handlerida kutilmagan xatolik: {e}")
        await message.answer("Ob-havo ma'lumotini ko'rsatishda kutilmagan xatolik yuz berdi.")