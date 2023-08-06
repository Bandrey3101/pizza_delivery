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
b10 = KeyboardButton('Приборы/добавки')
b11 = KeyboardButton('Доставка')
b12 = KeyboardButton('Самовывоз')
basket = KeyboardButton('Корзина')
b13 = KeyboardButton(text="Отправить номер телефона", request_contact=True)
b14 = KeyboardButton('Отменить')
b15 = KeyboardButton('При получении')
b16 = KeyboardButton('Онлайн')
b17 = KeyboardButton('Роллы (сеты)')


kb_client = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(b3, b1, b2)
#kb_client.add(b3, b1, b2)
kb_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(b6, b7, b8, b17, b10, b9, basket)
kb_delivery = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(b11, b12, b9)
break_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(b14)
get_contact = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(b13, b14)
back = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(b9)
pay_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(b16, b15, b14)








