# -*- coding: utf-8 -*-
import telebot
import cherrypy
import os
from telebot import types

# Мои файлы
from config import *
from webhook import *

# WEBHOOK_START

# Наш вебхук-сервер
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

# WEBHOOK_FINISH

# Запуск бота
bot = telebot.TeleBot(TOKEN)

# Команды
commands = []

# Приветствие
# Вход: Сообщение
# Выход: -
@bot.message_handler(commands=['start'])
def start(message):
    mid = message.chat.id

    if mid != admin_id:
        return
    bot.send_message(mid, 'Добро пожаловать! Введите команду')

def edit_list(cmd):
    commands.reverse()
    if cmd in commands:
        commands.remove(cmd)
    commands.append(cmd)
    if len(commands) > 10:
        commands.pop(0)
    commands.reverse()

# Главная функция, обработка всего приходящего текста
# Вход: Сообщение
# Выход: -
@bot.message_handler(content_types=['text'])
def main(message):
    mid = message.chat.id
    cmd = message.text

    if mid != admin_id:
        return

    edit_list(cmd)

    markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    for elem in commands:
        markup.row(elem)

    code = os.system(cmd + ' >tmp_file 2>tmp_error')
    ans = ''
    FILE = open('tmp_file')
    ans = FILE.read()
    FILE.close()
    if code != 0:
        FILE = open('tmp_error')
        ans += '\nERROR: ' + str(code) + '\n' + FILE.read()
        FILE.close()
    bot.send_message(mid, ans, reply_markup=markup)    
        
# WEBHOOK_START

# Снимаем вебхук перед повторной установкой (избавляет от некоторых проблем)
bot.remove_webhook()

# Ставим заново вебхук
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Указываем настройки сервера CherryPy
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

 # Собственно, запуск!
cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})

# WEBHOOK_FINISH

