from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_load = KeyboardButton('Загрузить')
button_delete = KeyboardButton('Удалить')
button_remove = KeyboardButton('Отмена')
b1 = KeyboardButton('Пицца')
b2 = KeyboardButton('Напитки')
b3 = KeyboardButton('Роллы')
b4 = KeyboardButton('Роллы (сеты)')
b5 = KeyboardButton('Назад')
b6 = KeyboardButton('Приборы/добавки')


button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load).add(button_delete).add(b5)

button_case_admin2 = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(b1, b2, b3, b4, b6, button_remove)

