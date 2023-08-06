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
                 'description TEXT, price INTEGER)')
    base.execute('CREATE TABLE IF NOT EXISTS basket(user_id, name TEXT, price INTEGER, '
                 'count INTEGER, total_price INTEGER)')
    base.execute('CREATE UNIQUE INDEX IF NOT EXISTS name_product ON basket (user_id, name)')
    base.execute('CREATE TABLE IF NOT EXISTS users(user_id PRIMARY KEY, firstname, username,'
                 ' phone_number, delivery_address, pay)')
    base.execute('CREATE TABLE IF NOT EXISTS ids(user_id PRIMARY KEY)')
    base.commit()
    print('таблицы добавлены')


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT OR IGNORE INTO menu VALUES (?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_read(message, product):
    for ret in cur.execute("SELECT * FROM menu WHERE product == ?", (product,)).fetchall():
        await bot.send_photo(message.from_user.id, ret[1], f'{ret[2]}\nОписание: {ret[3]}\nЦена: {ret[-1]}руб.',
                             reply_markup=InlineKeyboardMarkup()
                             .add(InlineKeyboardButton(f'Добавить в корзину {ret[2]}',
                                                       callback_data=f'add {ret[2]}')))


async def sql_read2(message, product):
    for ret in cur.execute("SELECT * FROM menu WHERE product == ?", (product,)).fetchall():
        await bot.send_photo(message.from_user.id, ret[1], f'{ret[2]}\nОписание: {ret[3]}\nЦена '
                                                           f'{ret[-1]}руб', reply_markup=InlineKeyboardMarkup().
                             add(InlineKeyboardButton(f'Удалить {ret[2]}', callback_data=f'del {ret[2]}')))


async def sql_delete_command(data):
    cur.execute("DELETE FROM menu WHERE name == ?", (data,))
    base.commit()


async def sql_add_users(state):
    async with state.proxy() as data:
        cur.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, ?)", tuple(data.values()))
        base.commit()


async def sql_add_id(user_id):
    cur.execute("INSERT OR IGNORE INTO ids VALUES (?)", (user_id,))
    base.commit()


async def sql_add_product_name(data, user_id):
    cur.execute("INSERT INTO basket (user_id, name, price, total_price, count) "
                "SELECT ids.user_id, menu.name, menu.price, menu.price, '1' FROM "
                "(SELECT user_id FROM ids WHERE user_id == ?) AS ids JOIN "
                "(SELECT name, price FROM menu WHERE name == ?) AS menu", (user_id, data))


async def sql_basket_plus(user_id, name):
    cur.execute("UPDATE basket SET count = count + 1, total_price = total_price + price "
                "WHERE user_id == ? AND name == ?", (user_id, name))
    base.commit()


async def sql_basket_minus(user_id, name):
    cur.execute("UPDATE basket SET count = count - 1, total_price = total_price - price"
                " WHERE user_id == ? AND name == ?", (user_id, name))
    base.commit()


async def sql_delete_product(user_id, name):
    cur.execute("DELETE FROM basket WHERE user_id == ? AND name == ?", (user_id, name))
    base.commit()


async def sql_read_basket(user_id):
    bask = cur.execute("SELECT * FROM basket WHERE user_id == ?", (user_id,)).fetchall()
    return bask


async def sql_read_users(user_id):
    u = cur.execute("SELECT * FROM users WHERE user_id == ?", (user_id,)).fetchall()
    return u


async def sql_delete_user(user_id):
    cur.execute("DELETE FROM users WHERE user_id == ?", (user_id,))
    base.commit()


async def sql_delete_from_basket(user_id):
    cur.execute("DELETE FROM basket WHERE user_id == ?", (user_id,))
    base.commit()


async def sql_spam_all():
    ids = cur.execute("SELECT * FROM ids").fetchall()
    return ids


