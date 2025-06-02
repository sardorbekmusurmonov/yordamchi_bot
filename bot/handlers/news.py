# bot/handlers/news.py
import aiohttp
from aiogram import Router, types
from aiogram.filters import Command

from deep_translator import GoogleTranslator # Tarjima uchun

# NEWS_API_KEY ni config_reader dan import qilamiz
# Bu import oldingi fayllardagi kabi (handlers papkasidan bir yuqoridagi bot papkasiga murojaat)
from ..config_reader import NEWS_API_KEY

router = Router()

NEWS_API_ENDPOINT = "https://newsapi.org/v2/top-headlines"
# Ko'rsatiladigan yangiliklar soni (tarjima vaqti va xabar uzunligini hisobga olib)
ARTICLES_TO_SHOW = 3 

@router.message(Command("news", "yangiliklar"))
async def get_latest_news(message: types.Message):
    """
    /news yoki /yangiliklar buyrug'iga javob beradi.
    NewsAPI.org dan so'nggi yangiliklarni olib, tarjima qilib yuboradi.
    """
    # NewsAPI uchun parametrlar
    # AQSH dan umumiy yangiliklarni olamiz (ko'proq va tez-tez yangilanadigan kontent uchun)
    # Siz 'country' ni 'gb', 'de', 'ru' kabi boshqa davlatlarga o'zgartirishingiz
    # yoki 'category': 'technology' kabi kategoriya qo'shishingiz mumkin.
    # NewsAPI 'uz' (O'zbekiston) uchun top-headlines da yaxshi natija bermasligi mumkin.
    params = {
        'country': 'us', 
        'apiKey': NEWS_API_KEY,
        'pageSize': ARTICLES_TO_SHOW 
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(NEWS_API_ENDPOINT, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', [])

                    if not articles:
                        await message.answer("😕 Kechirasiz, hozirda yangiliklar topilmadi.")
                        return

                    # Tarjima qilingan yangiliklarni yig'ish uchun
                    news_items_texts = []
                    for article_index, article in enumerate(articles, 1):
                        title = article.get('title', "Sarlavha yo'q")
                        description = article.get('description', "Qisqacha mazmun yo'q")
                        url = article.get('url', '#') # Agar URL bo'lmasa
                        source_name = article.get('source', {}).get('name', 'Noma\'lum manba')

                        translated_title = title
                        translated_description = description
                        
                        # Faqat haqiqiy matn bo'lsa tarjima qilishga urinish
                        if title and title not in ["Sarlavha yo'q", "[Removed]"]:
                            try:
                                translated_title = GoogleTranslator(source='auto', target='uz').translate(text=title)
                                if not translated_title: translated_title = title # Agar tarjima None qaytarsa
                            except Exception as e:
                                print(f"Sarlavhani ('{title}') tarjima qilishda xato: {e}")
                                # translated_title o'zgarishsiz qoladi (original)
                        
                        if description and description not in ["Qisqacha mazmun yo'q", "[Removed]"]:
                            try:
                                translated_description = GoogleTranslator(source='auto', target='uz').translate(text=description)
                                if not translated_description: translated_description = description # Agar tarjima None qaytarsa
                            except Exception as e:
                                print(f"Tavsifni ('{description[:50]}...') tarjima qilishda xato: {e}")
                                # translated_description o'zgarishsiz qoladi (original)
                        
                        news_items_texts.append(
                            f"<b>{article_index}. {translated_title if translated_title else 'Sarlavha yo\'q'}</b>\n"
                            f"📄 <i>{translated_description if translated_description else 'Qisqacha mazmun yo\'q'}</i>\n"
                            f"🔗 <a href='{url}'>Batafsil ({source_name})</a>\n"
                        )
                    
                    header = f"<b>⚡️ So'nggi {len(articles)} ta tarjima qilingan yangilik (AQSH manbalaridan):</b>\n"
                    full_reply = header + "\n".join(news_items_texts)
                    
                    await message.answer(full_reply, disable_web_page_preview=True) # Linklar uchun oldindan ko'rishni o'chirish

                elif response.status == 401: # Unauthorized - API kaliti bilan muammo
                    print(f"NewsAPI KEY bilan muammo. Status: {response.status}")
                    await message.answer(
                        "Yangiliklarni olishda xatolik: API kaliti bilan muammo bo'lishi mumkin.\n"
                        "Iltimos, administratorga xabar bering."
                    )
                else: # Boshqa xatoliklar (masalan, 429 - so'rovlar limiti, 500 - server xatosi)
                    error_text = await response.text()
                    print(f"NewsAPI xatosi: {response.status}, Ma'lumot: {error_text[:200]}") # Xato matnini qisqartirib logga yozish
                    await message.answer(
                        f"Yangiliklarni olishda xatolik yuz berdi (status: {response.status}).\n"
                        "Iltimos, keyinroq qayta urinib ko'ring."
                    )
    except aiohttp.ClientConnectorError as e:
        print(f"NewsAPI ga ulanishda xatolik: {e}")
        await message.answer("Yangiliklar xizmatiga ulanib bo'lmadi. Internet aloqangizni tekshiring yoki keyinroq urinib ko'ring.")
    except Exception as e:
        print(f"Yangiliklar handlerida kutilmagan xatolik: {e}")
        await message.answer("Yangiliklarni ko'rsatishda kutilmagan xatolik yuz berdi.")