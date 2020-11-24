import telebot
from telebot import types


def start_keyabord():
    start_keyabord = telebot.types.ReplyKeyboardMarkup(True, True)
    start_keyabord.row('Поиск квартир', 'Поиск комнат')
    start_keyabord.row('Мои объявления')
    return start_keyabord


def keyabord_radius():
    keyboard_radius = telebot.types.ReplyKeyboardMarkup(True)
    keyboard_radius.row('3 км', '5 км', '10 км')
    keyboard_radius.add('Вернутся в меню')
    return keyboard_radius


def keyboard_loc():
    keyboard_loc = telebot.types.ReplyKeyboardMarkup(True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard_loc.add(button_geo)
    keyboard_loc.row('Назад')
    return keyboard_loc


def keyboard_phone():
    keyboard_phone = telebot.types.ReplyKeyboardMarkup(True)
    button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    keyboard_phone.add(button_phone)
    keyboard_phone.add('Назад')
    return keyboard_phone


def keyboard_search():
    keyboard_search = telebot.types.ReplyKeyboardMarkup(True, True)
    button_search = types.KeyboardButton(text="Показать все объявления")
    keyboard_search.add(button_search)
    keyboard_search.add('Поменять геолокацию')
    keyboard_search.add('Вернутся в меню')
    return keyboard_search


def keyboard_return():
    keyboard_return = telebot.types.ReplyKeyboardMarkup(True,True)
    keyboard_return.row('Назад')
    return keyboard_return


def keyboard_lc():
    keyabord_lc = telebot.types.ReplyKeyboardMarkup(True, True)
    keyabord_lc.row('Показать свои объявления')
    keyabord_lc.row('В главное меню')
    return keyabord_lc


def keyboard_repeat():
    keyboard_repeat = telebot.types.ReplyKeyboardMarkup(True,True)
    keyboard_repeat.row('Повторить вход')
    keyboard_repeat.row('В главное меню')
    return keyboard_repeat


def inline_keyboard_pre_step():
    inline_keyboard_pre_step = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Войти в личный кабинет", callback_data='yes')
    item2 = types.InlineKeyboardButton("Зарегистрироваться", callback_data='no')

    inline_keyboard_pre_step.add(item1)
    inline_keyboard_pre_step.add(item2)
    return inline_keyboard_pre_step


def inline_url(url):
    inline_url = types.InlineKeyboardMarkup(True)
    btn_my_site = types.InlineKeyboardButton(text='Перейти к объявлению', url=url)
    inline_url.add(btn_my_site)
    return inline_url


def lc_keyboard_choice():
    lc_keyboard_choice = types.ReplyKeyboardMarkup(True, True)
    lc_keyboard_choice.row("Квартиры", "Комнаты")
    lc_keyboard_choice.row("В главное меню")
    return lc_keyboard_choice

def lc_keyboard_ads():
    lc_keyboard_ads = types.ReplyKeyboardMarkup(True, True)
    lc_keyboard_ads.row("Ещё")
    lc_keyboard_ads.row("Вернутся в меню")
    return lc_keyboard_ads

