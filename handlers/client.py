from aiogram import types, Dispatcher
from create_bot import dp, bot
from keyboards import kb_client, kb_menu
from aiogram.types import ReplyKeyboardRemove
from data_base import sqlite_pizza
from handlers import admin

# @dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    # sqlite_pizza.sql_ids()
    await bot.send_message(message.from_user.id, "Приступаем)", reply_markup=kb_client)


# @dp.message_handler(commands=['Режим_работы'])
async def pizza_open_command(message: types.Message):
    await bot.send_message(message.from_user.id, "Пн-пт с 9:00 до 23:00, Сб-вс с 6:00 до 02:00")


# @dp.message_handler(commands=['Расположение'])
async def pizza_place_command(message: types.Message):
    await bot.send_message(message.from_user.id, 'ул. Колбасная 69', reply_markup=kb_client)


# @dp.message_handler(commands=['Меню'])
async def menu_command(message: types.Message):
    await bot.send_message(message.from_user.id, "Что желаете?", reply_markup=kb_menu)


# @dp.message_handler(text='Пицца')
async def pizza_menu_command(message: types.Message):
    await sqlite_pizza.sql_read(message, product=message.text)


async def add_basket_cb(callback_query: types.CallbackQuery): #state: FSMContext):
    await sqlite_pizza.sql_add_id(user_id=callback_query.from_user.id)
    await sqlite_pizza.sql_basket()
    await sqlite_pizza.sql_add_product_name(callback_query.data.replace('add ', ''),
                                            user_id=callback_query.from_user.id)
    await callback_query.answer(text=f'{callback_query.data.replace("add ", "")} добавлено.')
    #await FSMAdmin.delete.set()

menu = ('Пицца', 'Напитки', 'Роллы')


async def basket(message: types.Message):
    await sqlite_pizza.sql_read_basket(message, user_id=message.from_user.id)

async def basket_plus(callback_query: types.CallbackQuery):
    await callback_query.answer(text=f'{callback_query.data.replace("+ ", "")} добавлено 1 шт.')


async def basket_minus(callback_query: types.CallbackQuery):
    await callback_query.answer(text=f'{callback_query.data.replace("- ", "")} удалено 1 шт.')


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(command_start, text='Назад')
    dp.register_message_handler(pizza_open_command, text='Режим работы')
    dp.register_message_handler(pizza_place_command, text='Расположение')
    dp.register_message_handler(pizza_menu_command, text=menu)
    dp.register_message_handler(menu_command, text='Меню')
    dp.register_message_handler(basket, text='Корзина')
    dp.register_callback_query_handler(add_basket_cb, (lambda x: x.data and x.data.startswith('add ')))
    dp.register_callback_query_handler(basket_plus, (lambda x: x.data and x.data.startswith('+ ')))
    dp.register_callback_query_handler(basket_minus, (lambda x: x.data and x.data.startswith('- ')))

