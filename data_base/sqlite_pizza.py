import sqlite3 as sq
from create_bot import dp, bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def sql_start():
    global base, cur
    base = sq.connect('pizza_delivery.db')
    cur = base.cursor()
    if base:
        print('Data base connected')
    base.execute('CREATE TABLE IF NOT EXISTS menu(product TEXT, img TEXT, name TEXT PRIMARY KEY, '
                 'description TEXT, price TEXT)')
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS ids(user_id PRIMARY KEY)')
    base.commit()
    print('таблицы добавлены')


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT OR IGNORE INTO menu VALUES (?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_read(message, product):
    for ret in cur.execute("SELECT * FROM menu WHERE product == ?", (product,)).fetchall():
        await bot.send_photo(message.from_user.id, ret[1], f'{ret[2]}\nОписание: {ret[3]}\n Цена: {ret[-1]}')
        await bot.send_message(message.from_user.id, text='^^^', reply_markup=InlineKeyboardMarkup(). \
                               add(InlineKeyboardButton(f'Добавить в корзину {ret[2]}',
                                                        callback_data=f'add {ret[2]}')))


# async def sql_read(message):
#     for ret in cur.execute("SELECT * FROM menu").fetchall():
#         await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание: {ret[2]}\n Цена: {ret[-1]}')


# async def sql_read2(product):
#     return cur.execute("SELECT * FROM menu WHERE product == ?", (product,)).fetchall()


async def sql_read2(message, product):
    for ret in cur.execute("SELECT * FROM menu WHERE product == ?", (product,)).fetchall():
        await bot.send_photo(message.from_user.id, ret[1], f'{ret[2]}\nОписание: {ret[3]}\nЦена '
                                                           f'{ret[-1]}')
        await bot.send_message(message.from_user.id, text='^^^', reply_markup=InlineKeyboardMarkup().
                               add(InlineKeyboardButton(f'Удалить {ret[2]}', callback_data=f'del {ret[2]}')))


async def sql_delete_command(data):
    cur.execute("DELETE FROM menu WHERE name == ?", (data,))
    base.commit()


async def sql_basket():
    base.execute('CREATE TABLE IF NOT EXISTS basket(number, user_id, '
                 'name TEXT, price, count, total_price)')
    base.commit()


#async def sql_ids():


async def sql_add_id(user_id):
    cur.execute("INSERT OR IGNORE INTO ids VALUES (?)", (user_id,))
    base.commit()


async def sql_add_product_name(data, user_id):
    cur.execute("INSERT INTO basket (user_id, name, price) SELECT ids.user_id, menu.name, menu.price FROM (SELECT user_id FROM ids WHERE user_id == ?) AS ids JOIN (SELECT name, price FROM menu WHERE name == ?) AS menu", (user_id, data,))
    base.commit()

# async def sql_add_product_name(user_id, product_id):
#     cur.execute("INSERT OR IGNORE INTO basket (user_id, product_name) VALUES (?, ?)", [user_id, product_id]).fetchall() ##VALUES (?, ?, ?)", (data)"SELECT name, price FROM menu WHERE name == ?", (data,))
#     base.commit()

#async def sql_insert_basket():
