from pyrogram import Client, filters
from datetime import datetime
import sqlite3 as sql

app = Client('getBarista')
with open('config.ini', 'r') as f:
    data = f.read().splitlines()
    donor = data[3].split('=')[1]  # список доноров
    moder = data[4].split('=')[1]  # канал модерации
    channel = data[5].split('=')[1]  # канал для постинга


    @app.on_message(filters.chat(eval(donor)))
    def get_post(client, message):
        username = message.chat.username
        message_id = message.message_id

        con = sql.connect('bd.db')
        cur = con.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS DataBase(username,message_id)""")
        con.commit()

        # прверяем есть ли в БД такой message_id
        # если есть, то добавляем в БД и отправляем на модерацию

        cur.execute("""SELECT message_id FROM DataBase WHERE message_id=?""", (message_id,))
        if not cur.fetchall():
            cur.execute("""INSERT INTO DataBase VALUES(?,?)""", (username, message_id))
            con.commit()

            # получаем последний ROWID

            for a in cur.execute("""SELECT ROWID, * FROM DataBase LIMIT 1 OFFSET (SELECT COUNT (*) FROM DataBase)-1"""):
                last_id = a[0]

            # пересылаем пост на модерацию
            message.forward(eval(moder))
            client.send_message(eval(moder), last_id)
        else:
            pass


    @app.on_message(filters.chat(eval(moder)))
    def send_post(client, message):
        con = sql.connect('bd.db')
        cur = con.cursor()

        # получаем запись в таблице
        for _ in cur.execute(f"""SELECT * FROM DataBase WHERE ROWID = {message.text}"""):
            username = _[0]
            msg_id = _[1]

        send = app.get_messages(username, msg_id)
        send.forward(eval(channel))

if __name__ == '__main__':
    print(datetime.today().strftime(f'%H:%M:%S | Bot lunched.'))
    app.run()
