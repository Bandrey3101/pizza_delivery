from asyncio import sleep

from aiogram import types, Dispatcher
from aiogram.utils.exceptions import ChatNotFound
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from create_bot import dp, bot
from keyboards import kb_client, kb_menu, kb_delivery, get_contact, break_kb, back, pay_kb
from aiogram.types import ReplyKeyboardRemove
from data_base import sqlite_pizza
from handlers import admin
import sqlite3
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from config import YOOTOKEN


paytoken = YOOTOKEN


class FSMclient(StatesGroup):
    del_address = State()
    phone_number = State()
    pay = State()


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


async def add_basket_cb(callback_query: types.CallbackQuery):
    await sqlite_pizza.sql_add_id(user_id=callback_query.from_user.id)
    try:
        await sqlite_pizza.sql_add_product_name(callback_query.data.replace('add ', ''),
                                                user_id=callback_query.from_user.id)
        await callback_query.answer(text=f'{callback_query.data.replace("add ", "")} добавлено.')
    except sqlite3.IntegrityError:
        await callback_query.answer(text='Товар уже добавлен.')


menu = ('Пицца', 'Напитки', 'Роллы', 'Приборы/добавки', 'Роллы (сеты)')


async def sum_basket(message):
    total_sum = 0
    for ret in await sqlite_pizza.sql_read_basket(user_id=message.from_user.id):
        total_sum += ret[4]
    return total_sum


last_msg = None


async def basket(message):
    global last_msg
    for ret in await sqlite_pizza.sql_read_basket(user_id=message.from_user.id):
        await bot.send_message(message.from_user.id, f'{ret[1]}: {ret[3]}шт.\nСтоимость {ret[4]}руб.',
                               reply_markup=InlineKeyboardMarkup(row_width=2).
                               add(InlineKeyboardButton('-', callback_data=f'- {ret[1]}'),
                                   InlineKeyboardButton('+', callback_data=f'+ {ret[1]}')))
    last_msg = await bot.send_message(message.from_user.id, f'Итого: {await sum_basket(message)}руб.',
                                      reply_markup=InlineKeyboardMarkup(row_width=2).
                                      add(InlineKeyboardButton('Оформить заказ',
                                                               callback_data=f'sum {await sum_basket(message)}')))


def create_keyboard_markup(ret):
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton('-', callback_data=f'- {ret[1]}'),
        InlineKeyboardButton('+', callback_data=f'+ {ret[1]}')
    )


async def basket_plus(callback_query: types.CallbackQuery):
    try:
        user_id = callback_query.from_user.id
        product_name = callback_query.data.replace("+ ", "")
        # Обрабатываем нажатие на кнопку
        await sqlite_pizza.sql_basket_plus(user_id=user_id, name=product_name)
        # Получаем информацию о товаре из базы данных
        for ret in await sqlite_pizza.sql_read_basket(user_id=user_id):
            if ret[1] == product_name:
                new_text = f'{ret[1]}: {ret[3]}шт.\nСтоимость {ret[4]}руб.'
                markup = create_keyboard_markup(ret)
                # Редактируем только сообщение о продукте с обновленным текстом и разметкой
                await bot.edit_message_text(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id,
                    text=new_text,
                    reply_markup=markup
                )
                # Получаем информацию об итоговой стоимости из базы данных после обновления товара
        total_sum = 0
        for ret in await sqlite_pizza.sql_read_basket(user_id=user_id):
            total_sum += ret[4]
        global last_msg
        # Если это сообщение с итоговой стоимостью, сохраняем его message_id
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=last_msg.message_id,
            text=f'Итого: {total_sum}руб.',
            reply_markup=InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton('Оформить заказ', callback_data=f'sum {total_sum}')))

        await callback_query.answer(text=f'{product_name} добавлено 1 шт.')
    except ChatNotFound:
        print('Чат не найден')
    except Exception as e:
        print("Произошла неожиданная ошибка:", e)


async def basket_minus(callback_query: types.CallbackQuery):
    try:
        user_id = callback_query.from_user.id
        product_name = callback_query.data.replace("- ", "")
        # Обрабатываем нажатие на кнопку
        await sqlite_pizza.sql_basket_minus(user_id=user_id, name=product_name)
        # Получаем информацию о товаре из базы данных
        for ret in await sqlite_pizza.sql_read_basket(user_id=user_id):
            if ret[1] == product_name:
                if ret[4] > 0:  # Если количество больше 0, обновляем сообщение и разметку
                    new_text = f'{ret[1]}: {ret[3]}шт.\nСтоимость {ret[4]}руб.'
                    markup = create_keyboard_markup(ret)
                    # Редактируем только сообщение, на которое нажали, с обновленным текстом и разметкой
                    await bot.edit_message_text(
                        chat_id=callback_query.message.chat.id,
                        message_id=callback_query.message.message_id,
                        text=new_text,
                        reply_markup=markup
                    )
                else:  # Если количество равно 0, удаляем сообщение и запись из базы данных
                    await bot.delete_message(
                        chat_id=callback_query.message.chat.id,
                        message_id=callback_query.message.message_id
                    )
                    await sqlite_pizza.sql_delete_product(user_id=user_id, name=product_name)
        total_sum = 0
        for ret in await sqlite_pizza.sql_read_basket(user_id=user_id):
            total_sum += ret[4]
        global last_msg
        # Если это сообщение с итоговой стоимостью, сохраняем его message_id
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=last_msg.message_id,
            text=f'Итого: {total_sum}руб.', reply_markup=InlineKeyboardMarkup(row_width=2)
            .add(InlineKeyboardButton('Оформить заказ', callback_data=f'sum {total_sum}')))
        await callback_query.answer(text=f'{product_name} удалено 1 шт.')
    except ChatNotFound:
        print('Чат не найден')
    except Exception as e:
        print("Произошла неожиданная ошибка:", e)


async def delivery(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, text='Выберите способ доставки:', reply_markup=kb_delivery)


async def cancel_hand(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await bot.send_message(message.from_user.id, text='Ok', reply_markup=back)
    else:
        await state.finish()
        await bot.send_message(message.from_user.id, text='Ok', reply_markup=back)


async def get_delivery(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        if message.text == 'Доставка':
            await bot.send_message(message.from_user.id, text='Введите адрес доставки, пожалуйста:',
                                   reply_markup=break_kb)
            await FSMclient.del_address.set()
        elif message.text == 'Самовывоз':
            async with state.proxy() as data:
                data['user_id'] = message.from_user.id
                if message.from_user.first_name is None:
                    data['first_name'] = 'Отсутствует'
                else:
                    data['first_name'] = message.from_user.first_name
                if message.from_user.username is None:
                    data['username'] = 'Отсутствует'
                else:
                    data['username'] = message.from_user.username
                data['del_address'] = 'Самовывоз'
            await FSMclient.phone_number.set()
            await bot.send_message(message.from_user.id, text='Введите номер телефона для связи, пожалуйста:',
                                   reply_markup=get_contact)
        # else:
        #     await bot.send_message(message.from_user.id, text='Я вас не понимаю, воспользуйтесь клавиатурой внизу')


async def get_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
        if message.from_user.first_name is None:
            data['first_name'] = 'Отсутствует'
        else:
            data['first_name'] = message.from_user.first_name
        if message.from_user.username is None:
            data['username'] = 'Отсутствует'
        else:
            data['username'] = message.from_user.username
        data['del_address'] = message.text
    await FSMclient.phone_number.set()
    await bot.send_message(message.from_user.id, text='Отлично! Введите номер телефона для связи, пожалуйста:',
                           reply_markup=get_contact)


async def get_phone(message: types.Message, state: FSMContext):
    if len(message.text) == 12 and message.text[0] == '+':
        async with state.proxy() as data:
            data['phone_number'] = message.text
        await FSMclient.pay.set()
        await bot.send_message(message.chat.id, text='Выберите способ оплаты:', reply_markup=pay_kb)
    elif len(message.text) == 11 and message.text[1] == '9':
        async with state.proxy() as data:
            data['phone_number'] = message.text
        await FSMclient.pay.set()
        await bot.send_message(message.chat.id, text='Выберите способ оплаты:', reply_markup=pay_kb)
    else:
        await bot.send_message(message.chat.id, text='Похоже вы ввели не совсем номер телефона. Воспользуйтесь '
                                                     'кнопкой внизу или введите телефон в формате 89113456543',
                               reply_markup=get_contact)


async def get_phone_2(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.contact.phone_number
    await FSMclient.pay.set()
    await bot.send_message(message.chat.id, text='Выберите способ оплаты:', reply_markup=pay_kb)


async def get_order(message):
    orders = []
    for ret in await sqlite_pizza.sql_read_basket(user_id=message.from_user.id):
        product_name = ret[1]
        price = ret[2]
        quantity = ret[3]  # Преобразовываем количество в целое число
        val = f'{product_name} | {price}р. | {quantity}шт'
        orders.append(val)
    order = '\n'.join(orders)
    return order


async def choose_pay(message: types.Message, state: FSMContext):
    if message.text == 'При получении':
        async with state.proxy() as data:
            data['pay'] = message.text
        #await sqlite_pizza.sql_add_users(state)
        await bot.send_message(message.chat.id, text='Спасибо за заказ! В ближайшее время мы свяжемся '
                                                     'с вами для подтверждения!', reply_markup=kb_client)
        await bot.send_message(chat_id=410731842, text=f'Новый заказ:\n\n{await get_order(message)}\n\nСумма: '
                                                       f'{await sum_basket(message)}руб.\n\n'
                                                       f'Клиент: {data["first_name"]}\nUsername: '
                                                       f'@{data["username"]}\n'
                                                       f'Номер телефона: {data["phone_number"]}\nДоставка: '
                                                       f'{data["del_address"]}\nОплата: {data["pay"]}')
        await bot.send_message(message.from_user.id, text=f'Новый заказ:\n\n{await get_order(message)}\n\nСумма: '
                                                       f'{await sum_basket(message)}руб.\n\n'
                                                       f'Клиент: {data["first_name"]}\nUsername: '
                                                       f'@{data["username"]}\n'
                                                       f'Номер телефона: {data["phone_number"]}\nДоставка: '
                                                       f'{data["del_address"]}\nОплата: {data["pay"]}')
        await state.finish()
        await sqlite_pizza.sql_delete_from_basket(user_id=message.from_user.id)
    elif message.text == 'Онлайн':
        async with state.proxy() as data:
            data['pay'] = message.text
        await sqlite_pizza.sql_add_users(state)
        await state.finish()
        tot_price = await sum_basket(message)
        tot_price2 = tot_price * 100
        await bot.send_invoice(chat_id=message.from_user.id,
                               title="Ваш заказ",
                               description="Заказ",
                               payload="Онлайн оплата",
                               provider_token=paytoken,
                               currency="RUB",
                               start_parameter="test",
                               prices=[{"label": "Руб", "amount": tot_price2}]
                               )


async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def process_pay(message: types.Message):
    if message.successful_payment.invoice_payload == 'Онлайн оплата':
        await bot.send_message(message.from_user.id, 'Оплата прошла успешно.\n'
                                                     'Спасибо за заказ! В ближайшее время мы свяжемся '
                                                     'с вами для подтверждения!', reply_markup=kb_client)
        for r in await sqlite_pizza.sql_read_users(user_id=message.from_user.id):
            await bot.send_message(chat_id=410731842,
                                   text=f'Новый заказ:\n\n{await get_order(message)}\n\nСумма: '
                                        f'{await sum_basket(message)}руб.\n\n'
                                        f'Клиент: {r[1]}\nUsername: '
                                        f'@{r[2]}\n'
                                        f'Номер телефона: {r[4]}\nДоставка: '
                                        f'{r[3]}\nОплата: {r[5]}✅')
            await bot.send_message(message.from_user.id,
                                   text=f'Новый заказ:\n\n{await get_order(message)}\n\nСумма: '
                                        f'{await sum_basket(message)}руб.\n\n'
                                        f'Клиент: {r[1]}\nUsername: '
                                        f'@{r[2]}\n'
                                        f'Номер телефона: {r[4]}\nДоставка: '
                                        f'{r[3]}\nОплата: {r[5]}✅')

        await sqlite_pizza.sql_delete_user(user_id=message.from_user.id)
        await sqlite_pizza.sql_delete_from_basket(user_id=message.from_user.id)


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
    dp.register_callback_query_handler(delivery, (lambda x: x.data and x.data.startswith('sum ')))
    dp.register_message_handler(cancel_hand, state="*", commands='Отменить')
    dp.register_message_handler(cancel_hand, Text(equals='Отменить', ignore_case=True), state="*")
    dp.register_message_handler(get_delivery, text=['Доставка', 'Самовывоз'], state=None)
    dp.register_message_handler(get_address, state=FSMclient.del_address)
    dp.register_message_handler(choose_pay, state=FSMclient.pay)
    dp.register_message_handler(get_phone, state=FSMclient.phone_number)
    dp.register_message_handler(get_phone_2, content_types=['contact'], state=FSMclient.phone_number)
    dp.register_pre_checkout_query_handler(process_pre_checkout)
    dp.register_message_handler(process_pay, content_types=ContentType.SUCCESSFUL_PAYMENT)
