from keyboard import *  # импортирование, включая библиотеки
import config
from config import *
import user_class

bot = telebot.TeleBot(config.TOKEN)

bd = redis.Redis(db=0)  # БД
bd.set('441914014', '+79778837166')
bd.set('+79778837166', 'secret123456 0')

print(bd.keys())

User = user_class.User()


@bot.message_handler(commands=["start"])
def start(message):
    if User.get_current_state() == 0:  # при первом запуске
        User.set_id(message.chat.id)
        User.set_first_name(message.chat.first_name)
        User.set_last_name(message.chat.last_name)
        User.set_new_state(1)
    bot.send_message(message.chat.id, f"Привет, *{message.chat.first_name}*!\n"
                                      f"Вас приветствует бот проекта Циан для студентов!\n"
                                      f"Выберите нужный пункт из меню.",
                     reply_markup=start_keyabord(), parse_mode="Markdown")  # удаляем клавиатуру

@bot.message_handler(commands=["reset"])
def reset(message):
    User.set_new_state(0)
    User.set_id(None)
    User.set_auth_token(None)
    User.set_phone(None)
    User.set_password(None)
    User.set_first_name(None)
    User.set_last_name(None)
    bot.send_message(message.chat.id, "*Перезапуск!*\nТеперь вы идентифицируетесь как новый пользователь\n"
                                      "Напишите в чат /start для запуска бота", parse_mode="Markdown")


@bot.message_handler(content_types=['location'])
def handle_loc(message):
    try:
        User.set_location([message.location.longitude, message.location.latitude])
    except AttributeError:
        return


@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == 'Поиск квартир' or message.text == 'Поиск комнат':
        second_step(message)
    elif message.text == 'Мои объявления' or message.text == 'Повторить вход':
        bot.send_message(message.chat.id, '*Данный раздел доступен только зарегистрированным пользователям*',
                         parse_mode='Markdown', reply_markup=inline_keyboard_pre_step())
    else:
        bot.send_message(message.chat.id, '*Выберите пункт из меню*\n'
                                          'или напишите /start для того, чтобы запустить бота сначала',
                         parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='*Данный раздел доступен только зарегистрированным пользователям*',
                          reply_markup=None, parse_mode="Markdown")
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Ожидайте...")

    if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки/s
        bot.send_message(call.message.chat.id, 'Вход в личный кабинет')
        first_step(call.message)
    elif call.data == "no":
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Ожидайте...")
        bot.send_message(call.message.chat.id, 'Пройдите регистрацию на нашем сайтe\n'
                                               'После запустите бота *с начала* командой /start',
                         reply_markup=None, parse_mode='Markdown')
        url(call.message)


@bot.message_handler(commands=['url'])
def url(message):
    markup = types.InlineKeyboardMarkup()
    btn_my_site = types.InlineKeyboardButton(text='Наш сайт', url='http://185.251.91.134/')
    markup.add(btn_my_site)
    bot.send_message(message.chat.id, "Нажмите на кнопку и перейдите на наш сайт.", reply_markup=markup)


def auth_login(message):
    # bd.set(message.chat.id, client_phone)
    if message.text == 'Назад':
        start(message)
        return

    if message.content_type == 'contact':
        User.set_phone(message.contact.phone_number)   # ключ, в нашем случае телефон
    else:
        User.set_phone(message.text)

    bot.send_message(message.chat.id, 'Введите пароль: ', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, check_auth)


def check_auth(message):
    # проверка первичной пары(id - phone)
    if check_exists_client(str(message.from_user.id)) == 1 and get_phone(message) == User.get_phone():
        print('success first pair')
        # проверка вторичной пары(phone - password и access token.ы)
        User.set_password(message.text.encode())
        if get_phone(message).encode() in bd.keys() and get_password(message).encode() == User.get_password():
            r = requests.post('http://185.251.91.134/api/login',
                              json={'telephoneNumber': '89778837166',
                                    # client_phone.decode('utf-8'),
                                    'password': message.text}).json()
            User.set_auth_token(r['access_token'])
            bd.set(get_phone(message), str(get_password(message)) + ' ' + User.get_auth_token())

            bot.send_message(message.chat.id, '*Вход успешно выполнен!*', parse_mode='Markdown', reply_markup=keyboard_lc())
            bot.register_next_step_handler(message, show_lc_ads)
        else:
            bot.send_message(message.chat.id, 'Неправильный логин и/или пароль', reply_markup=keyboard_repeat())
            bot.register_next_step_handler(message, first_step)
    else:
        bot.send_message(message.chat.id, 'Такого пользователя не существует', reply_markup=keyboard_repeat())
        bot.register_next_step_handler(message, first_step)


def show_lc_ads(message):
    if message.text == 'Показать свои объявления':
        bot.send_message(message.chat.id, "Выберите пункт в меню.", reply_markup=lc_keyboard_choice())
        bot.register_next_step_handler(message, show_results)
    elif message.text == 'В главное меню':
        start(message)
    else:
        first_step(message)


def check_exists_client(id_client):
    if id_client.encode() in bd.keys():
        return 1
    else:
        return 0


def get_headers(message):
    AUTH_TOKEN = bd[bd[message.chat.id]].split()[1].decode("utf-8")
    headers = {"Authorization": "Bearer " + AUTH_TOKEN}
    return headers


def get_phone(message):
    phone = bd[message.chat.id].decode("utf-8")
    return phone


def get_password(message):
    password = bd[bd[message.chat.id]].split()[0].decode("utf-8")
    return password


def show_results(message):
    global radius
    import random

    if message.text == 'Вернутся в меню':
        third_step(message)
        return
    elif message.text == 'В главное меню':
        start(message)
        return
    elif message.text == 'Ещё':
        User.iteration_number_of_list() # прибавляем единицу

    if message.text != 'Квартиры' and message.text != 'Комнаты':  # проверка на вход в личный кабинет
        # Указываем радиус
        if message.text == '3 км':
            radius = 3000
        elif message.text == '5 км':
            radius = 5000
        elif message.text == '10 км':
            radius = 10000
        elif message.text == 'Ещё':
            pass
        else:
            fourth_step(message)
            return
        # Проверяем, перед нами запрос на комнаты или на квартиры
        if User.get_flag_room():
            URL_Radius = config.URL + "rooms?long=" + str(User.get_location()[1]) + \
                         "&lat=" + str(User.get_location()[0]) + \
                         "&radius=" + str(radius) + "&offset=" + str(User.get_number_of_list())
        elif User.get_flag_lot():
            URL_Radius = config.URL + "lot?long=" + str(User.get_location()[1]) + \
                         "&lat=" + str(User.get_location()[0]) + \
                         "&radius=" + str(radius) + "&offset=" + str(User.get_number_of_list())
        info = requests.get(URL_Radius).json()  # преобразование в json данных
    else:
        headers = get_headers(message)  # Забор заголовка с токеном из bd
        if message.text == 'Комнаты':
            info = requests.get(config.URL_AUTH_Room, headers=headers).json()
            User.set_flag_room()
        elif message.text == 'Квартиры':
            info = requests.get(config.URL_AUTH_Room, headers=headers).json()
            User.set_flag_lot()

    # отбор записей с исключением
    try:
        slen = len(info['result']['data'])
    except TypeError:
        slen = 0
    except KeyError:
        bot.send_message(message.chat.id, "Срок сессии истек, используйте /reset для обновления")
        return

    # проверка на существование записей
    if slen != 0:
        if User.get_flag_room():
            for i in range(slen):  # сколько всего тут записей
                mas = info['result']['data'][i]  # забираем данные
                # переопределяем для нормального использования
                max_resindents = mas['max_residents']
                curr_number_of_residents = mas['curr_number_of_residents']
                floor = mas['floor']
                floor_total = mas['floor_total']
                metro = mas['metro']
                ttmetro_transport = mas['ttmetro_transport']
                area = mas['area']
                address = mas['address']
                site = 'https://vk.com/' + str(random.randint(12344, 21341234))
                info_add = 'Адрес: ' + address + \
                           '\nМетро: ' + str(metro) + '(' + str(ttmetro_transport) + ' минут)' + \
                           "\nПлощадь: " + str(area) + ' кв.м.' + \
                           "\nЭтаж " + str(floor) + ' из ' + str(floor_total) + \
                           "\nСвободно комнат " + str(curr_number_of_residents) + ' из ' + str(max_resindents)
                bot.send_message(message.chat.id, info_add, reply_markup=inline_url(site))  # отправка сообщения в чат
        elif User.get_flag_lot():
            for i in range(slen):  # сколько всего тут записей
                mas = info['result']['data'][i]  # забираем данные
                # переопределяем для нормального использования
                floor = mas['floor']
                floor_total = mas['floor_total']
                metro = mas['metro']
                ttmetro_foot = mas['ttmetro_foot']
                ttmetro_transport = mas['ttmetro_transport']
                area = mas['area']
                address = mas['address']
                site = 'https://vk.com/' + str(random.randint(12344, 21341234))
                info_add = 'Адрес: ' + address + \
                           '\nМетро: ' + str(metro) + \
                           '\n' + str(ttmetro_foot) + ' минут пешком (' + str(ttmetro_transport) + ' минут транспортом)' \
                                                                                                   "\nПлощадь: " + str(
                    area) + ' кв.м.' + \
                           "\nЭтаж " + str(floor) + ' из ' + str(floor_total)
                bot.send_message(message.chat.id, info_add, reply_markup=inline_url(site))  # отправка сообщения в чат
    elif slen == 0 and message.text == 'Ещё':
        bot.send_message(message.chat.id, 'Больше объявлений нет', reply_markup=lc_keyboard_ads())
    else:
        bot.send_message(message.chat.id,
                         'К сожалению в выбранном диапазоне на данный момент квартиры *отсутствуют* :c',
                         parse_mode='Markdown')

    if message.text != 'Квартиры' and message.text != 'Комнаты':
        bot.send_message(message.chat.id, "Выберите пункт в меню.", reply_markup=lc_keyboard_ads())
        bot.register_next_step_handler(message, show_results)
    else:
        bot.send_message(message.chat.id, "Выберите пункт в меню.", reply_markup=keyboard_lc())
        bot.register_next_step_handler(message, show_lc_ads)


# ------------------------------------
# Ход работы
# ------------------------------------


def first_step(message):
    if message.text == 'В главное меню':
        start(message)
        return
    if User.get_auth_token():
        bot.send_message(message.chat.id, '*Вход успешно выполнен!*', parse_mode='Markdown', reply_markup=keyboard_lc())
        bot.register_next_step_handler(message, show_lc_ads)
        return

    bot.send_message(message.chat.id, "Отправьте ваш номер телефона(кнопка в меню):", reply_markup=keyboard_phone())
    bot.register_next_step_handler(message, auth_login)


def second_step(message):
    if message.text == '/start' or message.text == 'Назад':
        start(message)
        return
    elif message.text == 'Поиск комнат': User.set_flag_room()
    elif message.text == 'Поиск квартир': User.set_flag_lot()

    if message.content_type != 'location':
        bot.send_message(message.chat.id, "Поделитесь геопозицией!", reply_markup=keyboard_loc())
        bot.register_next_step_handler(message, handle_loc)
        bot.register_next_step_handler(message, second_step)
    else:
        third_step(message)  # # переходим на 3ий шаг - выбор пунктов меню

def third_step(message):
    User.set_number_of_list(1)  # возвращаемся в истоки
    bot.send_message(message.chat.id, "Выберите нужное в меню:", reply_markup=keyboard_search())
    bot.register_next_step_handler(message, fourth_step)  # переходим на 4ый шаг - указание радиуса


def fourth_step(message):
    if message.text == 'Поменять геолокацию':
        second_step(message)  # возврашаемся к выбору геолокации
        return
    elif message.text == 'Вернутся в меню':
        start(message)
        return

    bot.send_message(message.chat.id, "Выберите радиус поиска:", reply_markup=keyabord_radius())
    bot.register_next_step_handler(message, show_results)


# ------------------------------------
# Ход работы
# ------------------------------------


if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            # или import traceback; traceback.print_exc() для печати полной инфы
            time.sleep(15)
