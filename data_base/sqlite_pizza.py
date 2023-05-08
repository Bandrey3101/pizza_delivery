import sqlite3 as sq
from create_bot import dp, bot


def sql_start():
    global base, cur
    base = sq.connect('pizza_delivery.db')
    cur = base.cursor()
    if base:
        print('Data base connected')
    base.execute('CREATE TABLE IF NOT EXISTS menu(product TEXT, img TEXT, name TEXT PRIMARY KEY, '
                 'description TEXT, price TEXT)')
    base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT OR IGNORE INTO menu VALUES (?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_read(message, product):
    for ret in cur.execute("SELECT * FROM menu WHERE product == ?", (product,)).fetchall():
        await bot.send_photo(message.from_user.id, ret[1], f'{ret[2]}\nОписание: {ret[3]}\n Цена: {ret[-1]}')


# async def sql_read(message):
#     for ret in cur.execute("SELECT * FROM menu").fetchall():
#         await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание: {ret[2]}\n Цена: {ret[-1]}')


async def sql_read2(product):
    return cur.execute("SELECT * FROM menu WHERE product == ?", (product,)).fetchall()


async def sql_delete_command(data):
    cur.execute("DELETE FROM menu WHERE name == ?", (data,))
    base.commit()
