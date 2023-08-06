from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher
from create_bot import dp, bot
from data_base import sqlite_pizza
from keyboards import admin_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class FSMAdmin(StatesGroup):
    product = State()
    photo = State()
    name = State()
    description = State()
    price = State()
    delete = State()
    spam_all = State()


ID = None


# Начало диалога загрузки новой позиции
# @dp.message_handler(content_types=['text'])
async def password(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Привет, босс. Что делаем?',
                           reply_markup=admin_kb.button_case_admin)


async def choose_product(message: types.Message):
    if message.from_user.id == ID:
        await bot.send_message(message.from_user.id, 'Куда загружаем?',
                               reply_markup=admin_kb.button_case_admin2)
        await FSMAdmin.product.set()


# Отмена ввода
# @dp.message_handler(state="*", commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        current_state = await state.get_state()
        if current_state is None:
            await message.reply('OK')
        else:
            await state.finish()
            await message.reply('OK')
        await password(message)


async def begin(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['product'] = message.text
        await FSMAdmin.next()
        await message.reply('Загрузите фото')


# Ловим первый ответ и пишем словарь
# @dp.message_handler(content_types=['photo'], state=FSMadmin.photo)
async def load_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['photo'] = message.photo[0].file_id
        await FSMAdmin.next()
        await message.reply('Теперь введите название')


# Ловим второй ответ
# @dp.message_handler(state=FSMadmin.name)
async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['name'] = message.text
        await FSMAdmin.next()
        await message.reply('Введите описание')


# Ловим третий ответ
# @dp.message_handler(state=FSMadmin.description)
async def load_description(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['description'] = message.text
        await FSMAdmin.next()
        await message.reply('Теперь введите цену')


# Ловим последний ответ и используем полученные данные
# @dp.message_handler(state=FSMadmin.price)
async def load_price(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['price'] = int(message.text)
        await sqlite_pizza.sql_add_command(state)
        await message.reply('Готово!')
        await FSMAdmin.product.set()
        # await state.finish()


# @dp.callback_query_handlers(lambda x: x.data and x.data.startwith('del '))
async def del_callback_run(callback_query: types.CallbackQuery, state: FSMContext):
    await sqlite_pizza.sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("del ", "")} удалена.', show_alert=True)
    await FSMAdmin.delete.set()


async def choose_del_product(message: types.Message):
    await bot.send_message(message.from_user.id, 'Что удаляем?',
                           reply_markup=admin_kb.button_case_admin2)
    await FSMAdmin.delete.set()


async def delete_item(message: types.Message, state: FSMContext):
    await sqlite_pizza.sql_read2(message, product=message.text)
    await FSMAdmin.delete.set()


async def spam_all(message: types.Message):
    if message.from_user.id == ID:
        await bot.send_message(message.chat.id, text='Введите текст рассыылки:',
                               reply_markup=admin_kb.break_kb)
        await FSMAdmin.spam_all.set()


async def save_spam_all(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['spam'] = message.text
        spam_message = data['spam']
        await state.finish()
        for i in await sqlite_pizza.sql_spam_all():
            try:
                await bot.send_message(chat_id=i[0], text=spam_message)
            except:
                pass
        await bot.send_message(chat_id=ID, text='Рассылка завершена', reply_markup=admin_kb.button_case_admin2)


menu2 = ('Пицца', 'Напитки', 'Роллы', 'Приборы/добавки', 'Роллы (сеты)')


# Регистрируем хендлеры
def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(password, commands='123')
    dp.register_message_handler(choose_product, text='Загрузить', state=None)
    dp.register_message_handler(cancel_handler, state="*", commands='Отмена')
    dp.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state="*")
    dp.register_message_handler(begin, state=FSMAdmin.product)
    dp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin.photo)
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_message_handler(load_description, state=FSMAdmin.description)
    dp.register_message_handler(load_price, state=FSMAdmin.price)
    dp.register_callback_query_handler(del_callback_run, (lambda x: x.data and x.data.startswith('del ')),
                                       state=FSMAdmin.delete)
    dp.register_message_handler(choose_del_product, text='Удалить')
    dp.register_message_handler(delete_item, text=menu2, state=FSMAdmin.delete)
    dp.register_message_handler(spam_all, text='Рассылка')
    dp.register_message_handler(save_spam_all, state=FSMAdmin.spam_all)
