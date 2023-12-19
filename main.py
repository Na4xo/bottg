#Импортируем библиотеки
import telebot,sqlite3
from telebot import types
from dotenv import dotenv_values

#Токен и конфиг
config=dotenv_values('.env')
bot=telebot.TeleBot(config.get('TOKEN'))

#Прописывем логику команды /start.Регаем юзера в бд если его нет.Также создаём кнопашки *клик*
@bot.message_handler(commands=['start'])
def start(message):
    connect = sqlite3.connect(config.get('DB_NAME'))
    cursor = connect.cursor()

    us_id = message.chat.id
    cursor.execute(f"SELECT id FROM users WHERE id = {us_id}")
    all = cursor.fetchone()

    if all == None:
        usersss_id = message.chat.id
        balance = 25 #Деньга за регестрацию так сказать
        cursor.execute("INSERT INTO users (id, balance) VALUES(?, ?);", (usersss_id, balance))
        connect.commit()

    #Собственно кнопки
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Начать закуп🛒', callback_data='buys_menu')
    button2 = types.InlineKeyboardButton('Действия с балансом💰', callback_data='balance')
    button3 = types.InlineKeyboardButton('История покупок📊', callback_data='buy_history')
    button4=types.InlineKeyboardButton('Написать в поддержку📝',url='https://t.me/Akito_17')
    markup.row(button1)
    markup.row(button2,button3)
    markup.row(button4)
    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}!Я бот магазина Akito!У нас ты можешь приобрести предметы из твоих любимых игр', reply_markup=markup)  

#Далее возврат в меню проработал одну кнобку на все остальные
@bot.callback_query_handler(func=lambda call: call.data == 'back')
def balancerss(call):
    if call.data == 'back':
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton('Начать закуп🛒', callback_data='buys_menu')
        button2 = types.InlineKeyboardButton('Действия с балансом💰', callback_data='balance')
        button4 = types.InlineKeyboardButton('История покупок📊', callback_data='buy_history')
        button5=types.InlineKeyboardButton('Написать в поддержку📝',url='https://t.me/Akito_17')
        markup.row(button1)
        markup.row(button2,button4)
        markup.row(button5)
        bot.send_message(call.message.chat.id, f'Привет {call.message.from_user.first_name}!Ты вернулся в меню!', reply_markup=markup) 

#Сразу сделаем баланс ибо я с ним намучался и он был готов на компе
@bot.callback_query_handler(func=lambda call: call.data == 'balance')
def balancerss(call):
   if call.data == 'balance':
        connection = sqlite3.connect(config.get('DB_NAME'))
        cursor = connection.cursor()
        user_id = call.from_user.id

        cursor.execute(f'SELECT balance FROM users WHERE id = {user_id}')
        result = cursor.fetchone()

        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton('Пополнить счёт ШЕКЕЛЯМИ', callback_data='add_balance')
        button2 = types.InlineKeyboardButton('вернуться в меню🟥', callback_data='back')
        markup.row(button1)
        markup.row(button2)

        if result:
            balance = result[0]
            bot.send_message(call.message.chat.id, f'Сейчас у тебя столько ШЕКЕЛЕЙ: {balance}', reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, 'Нет такого юзера', reply_markup=markup)

#Как бы написать но это короче типо мы тут пишем сумму пополнения 
@bot.callback_query_handler(func=lambda call: call.data == 'add_balance')
def balancerss(call):
   if call.data == 'add_balance':
        connection = sqlite3.connect(config.get('DB_NAME'))
        cursor = connection.cursor()
        user_id = call.from_user.id

        cursor.execute(f'SELECT balance FROM users WHERE id = {user_id}')
        result = cursor.fetchone()
        if result:
            balance = result[0]
            bot.send_message(call.message.chat.id, f'Сейчас у тебя столько ШЕКЕЛЕЙ: {balance}')
            bot.send_message(call.message.chat.id, 'Введите сумму пополнения хотя мы не сбербанк но вводи,нам можно доверять:')
            bot.register_next_step_handler(call.message, new_balancers)
        else:
            bot.send_message(call.message.chat.id, 'Такого юзера нет!')

def new_balancers(message):

    try:
        summa_popolnenyia = int(message.text)
        user_id = message.from_user.id
        connection = sqlite3.connect(config.get('DB_NAME'))

        cursor = connection.cursor()
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton('Вернуться в меню🟥', callback_data='back')
        markup.add(button)

        cursor.execute(f'SELECT balance FROM users WHERE id = {user_id}')
        result = cursor.fetchone()
        if result:
            balance = result[0]
            if summa_popolnenyia <= 3500 and summa_popolnenyia > 0:
                new_balance = balance + summa_popolnenyia
                cursor.execute(f'UPDATE users SET balance = {new_balance} WHERE id = {user_id}')
                connection.commit()
                connection.close()
                bot.send_message(message.chat.id, f'Теперь у тебя столько ШЕКЕЛЕЙ: {new_balance}', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, 'нам не надо 0 и не надо больше 3500 твоих ШЕКЕЛЕЙ', reply_markup=markup)
        else:
            connection.close()
            bot.send_message(message.chat.id, 'вас не существует', reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, 'Если  это не цифры то иди нафиг с этого магазина!')

#Получем список категорий
@bot.callback_query_handler(func=lambda call: call.data == 'buys_menu')
def menu_pokupki(call):
    connection = sqlite3.connect(config.get('DB_NAME'))
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM categories")
    data = cursor.fetchall()
    connection.close()
    
    markup = types.InlineKeyboardMarkup()
   
    for item in data:
        id, type = item
        markup.add(types.InlineKeyboardButton(type, callback_data=f'category_{id}'))
        markup.add(types.InlineKeyboardButton('Вернуться в меню🟥', callback_data='back'))
    bot.send_message(call.message.chat.id,f"Сейчас категория одна но тебя это волновать не должно:", reply_markup=markup)

#Теперь,нам нужно чтобы при выборе категории нам выводились товары)
@bot.callback_query_handler(func=lambda call: call.data.startswith('category_'))
def callback_category(call):
       category_id = call.data.split('_')[1]  
       connection = sqlite3.connect(config.get('DB_NAME'))
       cursor = connection.cursor()
       query = f'''
               SELECT items.id, items.name
               FROM items
               INNER JOIN categories ON items.categories_id = categories.id
               WHERE categories.id = {category_id}
               '''
       cursor.execute(query)
       data = cursor.fetchall()
       connection.close()

       markup = types.InlineKeyboardMarkup()
       
       for item in data:
           item_id, item_name = item
           markup.add(types.InlineKeyboardButton(item_name, callback_data=f'item_{item_id}'))
       markup.add(types.InlineKeyboardButton('Вернуться в меню🟥', callback_data='back'))
       bot.send_message(call.message.chat.id,'Выберите товар:', reply_markup=markup)

#При выборе товара выводим инфу о нём
@bot.callback_query_handler(func=lambda call: call.data.startswith('item_'))
def callback_item(call):
    connection = sqlite3.connect(config.get('DB_NAME'))
    cursor = connection.cursor()
    item_id = call.data.split('_')[1]  
    query = f'''
            SELECT name, desc, price
            FROM items
            WHERE id = {item_id}
            '''
    cursor.execute(query)
    data = cursor.fetchone()
    item_name, item_desc, item_price=data
    bot.send_message(call.message.chat.id,f'Название: {item_name}\nОписание: {item_desc}\nЦена: {item_price} ШЕКЕЛЕЙ')
    markup = types.InlineKeyboardMarkup()
    
    markup.add(types.InlineKeyboardButton('Купить', callback_data=f'buy_{item_id}'))
    markup.add(types.InlineKeyboardButton('Вернутсья в меню🟥', callback_data='back'))
    bot.send_message(call.message.chat.id, 'Подтвердить покупку:', reply_markup=markup)

#Теперь покупка
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def callback_buy(call):
    connection = sqlite3.connect(config.get('DB_NAME'))
    cursors = connection.cursor()
    user_id = call.from_user.id
    item_id = call.data.split("_")[1]

    # Достаём инфу о товаре из базы данных
    item_query = '''
            SELECT name, price
            FROM items
            WHERE id = ?'''
    cursors.execute(item_query, (item_id,))
    item_data = cursors.fetchone()
    item_name, item_price_str = item_data
    item_price = int(item_price_str)

    # Достаём баланс по примеру его создания
    balance_query = '''
            SELECT balance
            FROM users
            WHERE id = ?'''
    cursors.execute(balance_query, (user_id,))
    user_balance = cursors.fetchone()[0]

    if user_balance >= item_price:
        # Обновление баланса и заносим в bills
        new_balance = user_balance - item_price
        update_query = '''
                   UPDATE users
                   SET balance = ?
                   WHERE id = ?'''
        cursors.execute(update_query, (new_balance, user_id))
        insert_query = '''
                   INSERT INTO bills (user_id, item_id, date)
                   VALUES (?, ?, CURRENT_TIMESTAMP)'''
        cursors.execute(insert_query, (user_id, item_id))

        connection.commit()

        bot.send_message(call.message.chat.id, f'Молодец твои ШЕКЕЛИ МОИ!УХАХАХУАХУАХ(поздравляем с покупкой):{item_name}! ТВОЙ НОВЫЙ БАЛАНС МОЖНО ПОПОЛНИТЬ')
    else:
        bot.send_message(call.message.chat.id, 'ХПХПХХПХП,ЛОХ У ТЕБЯ НЕТ ШЕКЕЛЕЙ')

#История:


#Создаём цикл,бот работает бесконечно.
bot.polling(none_stop=True)