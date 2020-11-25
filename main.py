from keyboard import *  # импортирование, включая библиотеки
import config
from config import *
import user_class

bot = telebot.TeleBot(config.TOKEN)
User = user_class.User()


@bot.message_handler(commands=["start"])
def start(message):
    if User.get_current_state() == 0:  # при первом запуске
        User.set_id(message.chat.id)
        User.set_first_name(message.chat.first_name)
        User.set_last_name(message.chat.last_name)
        User.set_new_state(1)
    bot.send_message(message.chat.id, f"Привет, *{message.chat.first_name}*! " + set_emoji(":wave:") +
                                      "\nВас приветствует бот проекта Циан для студентов!\n" 
                                      "Выберите нужный пункт из меню.", reply_markup=start_keyabord(), parse_mode="Markdown")  # удаляем клавиатуру

@bot.message_handler(commands=["reset"])
def reset(message):
    User.set_new_state(0)
    User.set_id(None)
    User.set_auth_token(None)
    User.set_phone(None)
    User.set_password(None)
    User.set_first_name(None)
    User.set_last_name(None)
    bot.send_message(message.chat.id, "*Перезапуск!* " + set_emoji(":warning:")+ "\nТеперь вы идентифицируетесь как новый пользователь\n"
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
        bot.send_message(call.message.chat.id, 'Вход в личный кабинет ' + set_emoji(":door:"))
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
    bot.send_message(message.chat.id, set_emoji(":arrow_down_small:") + " Нажмите на кнопку и перейдите на наш сайт "
                     +set_emoji(":arrow_down_small:"), reply_markup=markup)


def set_emoji(smile):
    return emoji.emojize(smile, use_aliases=True)


def auth_login(message):
    if message.text == 'Назад':
        start(message)
        return

    if message.content_type == 'contact':
        User.set_phone(message.contact.phone_number)   # ключ, в нашем случае телефон
    else:
        User.set_phone(message.text)

    bot.send_message(message.chat.id, 'Введите пароль ' + set_emoji(":key:"), reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, check_auth)


def check_auth(message):
    if User.get_phone()[0] == '8':
        User.set_phone('+7' + User.get_phone()[1:])
    r = requests.post('http://185.251.91.134/api/login', json={'telephoneNumber': User.get_phone(), 'password': message.text}).json()
    try:
        User.set_auth_token(r['access_token'])
    except KeyError:
        bot.send_message(message.chat.id, set_emoji(":x: ") + r['error'][33:] + set_emoji(" :x:"), reply_markup=keyboard_repeat())
        bot.register_next_step_handler(message, first_step)
        return
    bot.send_message(message.chat.id, '*Вход успешно выполнен!*', parse_mode='Markdown', reply_markup=keyboard_lc())
    bot.register_next_step_handler(message, show_lc_ads)


def show_lc_ads(message):
    if message.text == 'Показать свои объявления':
        bot.send_message(message.chat.id, "Выберите пункт в меню.", reply_markup=lc_keyboard_choice())
        bot.register_next_step_handler(message, show_results)
    elif message.text == 'В главное меню':
        start(message)
    else:
        first_step(message)


def check_exists_client(id_client):
    if id_client == User.get_id():
        return 1
    else:
        return 0


def get_headers():
    AUTH_TOKEN = User.get_auth_token()
    headers = {"Authorization": "Bearer " + AUTH_TOKEN}
    return headers


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
        headers = get_headers()  # Забор заголовка с токеном из bd
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
                         'К сожалению в выбранном диапазоне на данный момент квартиры *отсутствуют* ' + set_emoji(":pensive:"),
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

    bot.send_message(message.chat.id, "Отправьте ваш номер телефона" + set_emoji(":iphone:"), reply_markup=keyboard_phone())
    bot.register_next_step_handler(message, auth_login)


def second_step(message):
    if message.text == '/start' or message.text == 'Назад':
        start(message)
        return
    elif message.text == 'Поиск комнат': User.set_flag_room()
    elif message.text == 'Поиск квартир': User.set_flag_lot()

    if message.content_type != 'location':
        bot.send_message(message.chat.id, "Поделитесь геопозицией!" + set_emoji(":paperclip:"), reply_markup=keyboard_loc())
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

    bot.send_message(message.chat.id, "Выберите радиус поиска " + set_emoji(":mag:"), reply_markup=keyabord_radius())
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
