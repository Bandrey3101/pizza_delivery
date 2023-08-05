from aiogram import types, Dispatcher
from aiogram.types import ContentType
import config
from create_bot import dp, bot
from data_base import sqlite_db
from googlesheets import response


paytoken = config.YOOTOKEN


async def get_game_for_pay(callback_query: types.CallbackQuery):
    for v in sqlite_db.sql_read_sheet(user_id=callback_query.from_user.id):
        vals = v[0]
        return vals


async def callback_pay(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    game_price = sqlite_db.sql_get_price_for_pay(name_game=await get_game_for_pay(callback_query))
    game_price2 = game_price[0]*100
    await bot.send_invoice(chat_id=callback_query.from_user.id,
                           title="Оплата за участие в игре",
                           description=await get_game_for_pay(callback_query),
                           payload="Участие в игре",
                           provider_token=paytoken,
                           currency="RUB",
                           start_parameter="test",
                           prices=[{"label": "Руб", "amount": game_price2}]
                           )


async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def process_pay(message: types.Message):
    if message.successful_payment.invoice_payload == 'Участие в игре':
        await bot.send_message(message.from_user.id, "Оплата прошла успешно, ждите инструкций перед началом игры")
        await response(message)
        for v in sqlite_db.sql_read_sheet(user_id=message.from_user.id):
            await sqlite_db.sql_update_pay(game_name=v[0], game_date=v[1], pay='1', user_id=message.from_user.id)
            await bot.send_message(chat_id=185278320, text=f'Новый участник игры {v[0]}\nДата игры: {v[1]}\n'
                                                           f'Имя игрока: {v[2]}\nusername: @{v[3]}\nТел: {v[5]}', )
            await sqlite_db.sql_add_players(user_id=v[4], username=v[3], phone_number=v[5], game_name=v[0], date=v[1])


def register_handlers_other(dp: Dispatcher):
    dp.register_callback_query_handler(callback_pay, text='paygame')
    dp.register_pre_checkout_query_handler(process_pre_checkout)
    dp.register_message_handler(process_pay, content_types=ContentType.SUCCESSFUL_PAYMENT)