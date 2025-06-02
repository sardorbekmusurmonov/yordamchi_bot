# bot/config_reader.py
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

API_TOKEN = os.getenv("API_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY") # <<< BU QATOR QO'SHILDI

if API_TOKEN is None:
    print("Xatolik: API_TOKEN .env faylida topilmadi yoki sozlanmagan!")
    exit()

if WEATHER_API_KEY is None:
    print("Xatolik: WEATHER_API_KEY .env faylida topilmadi yoki sozlanmagan!")
    exit()

if NEWS_API_KEY is None: # <<< BU BLOK QO'SHILDI
    print("Xatolik: NEWS_API_KEY .env faylida topilmadi yoki sozlanmagan!")
    exit()