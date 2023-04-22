from __future__ import print_function
from create_bot import dp
import logging
from aiogram.utils import executor
from handlers import client, admin, other
from data_base import sqlite_pizza
logging.basicConfig(level=logging.INFO)


async def on_startup(_):
    print("Бот онлайн")
    sqlite_pizza.sql_start()


client.register_handlers_client(dp)
admin.register_handlers_admin(dp)

executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
