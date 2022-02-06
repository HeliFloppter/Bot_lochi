import telebot
from telebot import types
import sqlite3
from datetime import datetime

# Создание бота и добалвение токена
token = '2061887249:AAEVAA0fpVrgMtyeBpqBYgN_JhnfRWeOTb0'
bot = telebot.TeleBot(token)

# Подключение базы данных
db = sqlite3.connect('table.db', check_same_thread=False)
sql = db.cursor()
db.commit()
# Создание глобальных переменных и списков
current_datetime = datetime.now()
week_day_rus = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
week_day_str = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
facs = ['FB', 'ASPIRANTURA', 'RTF', 'RKF', 'FVS', 'FSU', 'FET', 'FIT', 'EF', 'GF', 'YUF', 'ZIVF']
years = ['1', '2', '3', '4', '5', '6']
groups = []
callback_fac = None


# Проверка Регистрации
def reg_check(id):
    sql.execute(f"SELECT telegram_id FROM users WHERE telegram_id = {id} ")
    check = sql.fetchone()
    db.commit()

    if check is None:
        return True
    else:
        return False


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name} {message.from_user.last_name}! Чтобы '
                     f'получить руководство пользователя и список команд введите /info')


# Вызов сообщения с командами бота при помощи команды /info
@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id,
                     f'Этот бот создан для студентов ТУСУРа. Бот выдает расписание на текущий день или на текущую '
                     f'неделю. Операции происходят при помощи команд, которые пишутся как сообщение боту в виде '
                     f'/"команда". Существуют такие каманды как:\n '
                     f'/reg - Регистрация вашей учетной записи в базе бота (выбор группы) \n'
                     f'/del - Удаление вашей учетной записи в базе бота\n'
                     f'/current_day - Расписание на сегодняшний день\n'
                     f'/week - Расписание на текущую неделю')


# Вывод расписания на текущюю неделю
@bot.message_handler(commands=['week'])
def table_on_current_week(message):
    if not reg_check(message.from_user.id):
        sql.execute(f'SELECT group_number FROM users WHERE telegram_id = {message.from_user.id}')
        group = sql.fetchone()[0]
        db.commit()
        week = []
        for day in week_day_str:
            sql.execute(f"SELECT * FROM schedule WHERE group_num = '{group}' AND week_day = '{day}'")
            sql_week = sql.fetchall()
            week.append(sql_week)
            db.commit()
        count = 0
        for day in week:
            bot.send_message(message.chat.id, f'{week_day_rus[count]}')
            count += 1
            if day:
                for i in range(len(day)):
                    audit = day[i][3]
                    if audit == 'None':
                        audit = 'Дистант'

                    bot.send_message(message.chat.id, f'пара №{day[i][0]}\n'
                                                      f'{day[i][1]}\n'
                                                      f'{day[i][2]}\n'
                                                      f'{audit}\n'
                                                      f'{day[i][4]}\n')
            else:
                bot.send_message(message.chat.id, 'Пар нет)')


# Вывод расписания на сегодняшний день
@bot.message_handler(commands=['current_day'])
def table_on_current_day(message):
    if not reg_check(message.from_user.id):
        week_day_int = current_datetime.weekday()
        if week_day_int != 6:
            current_day = week_day_str[week_day_int]
            sql.execute(f'SELECT group_number FROM users WHERE telegram_id = {message.from_user.id}')
            group = sql.fetchone()[0]
            db.commit()

            sql.execute(f"SELECT * FROM schedule WHERE group_num = '{group}' AND week_day = '{current_day}'")
            day = sql.fetchall()
            db.commit()
            bot.send_message(message.chat.id, 'Сегодня')
            if day:
                for i in range(len(day)):
                    audit = day[i][3]
                    if audit == 'None':
                        audit = 'Дистант'

                    bot.send_message(message.chat.id, f'пара №{day[i][0]}\n'
                                                      f'{day[i][1]}\n'
                                                      f'{day[i][2]}\n'
                                                      f'{audit}\n'
                                                      f'{day[i][4]}\n')
            else:
                bot.send_message(message.chat.id, 'Пар нет)')
        else:
            bot.send_message(message.chat.id, 'Сегодня воскресение')

    else:
        bot.send_message(message.chat.id, 'Вы еще не зарегестрировались')


# Удаление учетной записи при помощи /del
@bot.message_handler(commands=['del'])
def dell(message):
    if not reg_check(message.from_user.id):
        sql.execute(f"DELETE FROM users WHERE telegram_id = {message.from_user.id}")
        db.commit()
        if reg_check(message.from_user.id):
            bot.send_message(message.chat.id, 'Вы успешно удалили запись о себе')
    else:
        sql.execute(f"SELECT telegram_id FROM users WHERE telegram_id = {message.from_user.id}")
        bot.send_message(message.chat.id, 'Вы еще не зарегестрировались!')


# Регистрация с выбором группы при помощи команды /reg
@bot.message_handler(commands=['reg'])
def fac_ch(message):
    facs = ['FB', 'ASPIRANTURA', 'RTF', 'RKF', 'FVS', 'FSU', 'FET', 'FIT', 'EF', 'GF', 'YUF', 'ZIVF']

    keyboard_fac = types.InlineKeyboardMarkup()
    button = [types.InlineKeyboardButton(text=x, callback_data=x) for x in facs]
    keyboard_fac.add(*button)

    if reg_check(message.from_user.id):

        bot.send_message(message.chat.id, "Выберите факультет", reply_markup=keyboard_fac)

    else:
        bot.send_message(message.chat.id, 'Вы уже зарегестрировались!')


# Создание и удаление кнопок
@bot.callback_query_handler(func=lambda c: True)
def inline(call):
    global facs, years, groups, callback_fac

    if reg_check(call.from_user.id):
        for fac in facs:
            if call.data == fac:

                callback_fac = call.data
                sql.execute(f"SELECT year FROM groups_link WHERE fac = '{fac}'")
                year_cort = sql.fetchall()
                db.commit()
                year_check = []
                for i in year_cort:
                    year_check.append(i[0])

                keyboard_years = types.InlineKeyboardMarkup()
                button = [types.InlineKeyboardButton(text=x, callback_data=x) for x in years if x in year_check]
                keyboard_years.add(*button)
                bot.send_message(call.message.chat.id, "Выберите курс", reply_markup=keyboard_years)
                bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)

    if reg_check(call.from_user.id):
        for year in years:

            if call.data == year:

                sql.execute(f"SELECT group_number FROM groups_link WHERE year = '{year}' AND fac = '{callback_fac}'")
                sql_gr = sql.fetchall()
                db.commit()
                groups = []

                for i in range(len(sql_gr)):
                    groups.append(sql_gr[i][0])

                keyboard_group = types.InlineKeyboardMarkup()
                button = [types.InlineKeyboardButton(text=x, callback_data=x) for x in groups]
                keyboard_group.add(*button)

                bot.send_message(call.message.chat.id, "Выберите группу", reply_markup=keyboard_group)
                bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)

        for group in groups:
            if call.data == group:
                sql.execute("INSERT INTO users VALUES(?,?)", (call.from_user.id, group))
                bot.send_message(call.message.chat.id, f'Вы выбрали {group}!')

                bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
                bot.answer_callback_query(callback_query_id=call.id)


# polling
bot.polling()
