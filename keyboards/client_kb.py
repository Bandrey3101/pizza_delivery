from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('Режим работы')
b2 = KeyboardButton('Расположение')
b3 = KeyboardButton('Меню')
b4 = KeyboardButton('Поделиться номером', request_contact=True)
b5 = KeyboardButton('Отправить где я', request_location=True)
b6 = KeyboardButton('Пицца')
b7 = KeyboardButton('Напитки')
b8 = KeyboardButton('Роллы')
b9 = KeyboardButton('Назад')
basket = KeyboardButton('Корзина')


kb_client = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(b3, b1, b2)
#kb_client.add(b3, b1, b2)
kb_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(b6, b7, b8, b9, basket)




