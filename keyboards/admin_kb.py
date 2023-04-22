from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_load = KeyboardButton('Загрузить')
button_delete = KeyboardButton('Удалить')
button_remove = KeyboardButton('Отмена')

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load)\
    .add(button_delete)\
    .add(button_remove)