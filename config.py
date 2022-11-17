from dotenv import load_dotenv
import os

load_dotenv()

# environment variables
token = os.getenv('BOT_API_TOKEN')  # telegram bot token
app_url = os.getenv('APP_URL') + token  # webhook url

shop_name = 'Freak-Butik'
shop_url = 'https://www.freak-butik.ru/'
database_name = 'freak_butik_shop.db'  # database file




