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
b7 = KeyboardButton('Рассылка')


button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load, button_delete, b7, b5)
break_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button_remove)
button_case_admin2 = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(b1, b2, b3, b4, b5, b6, button_remove)

