#!/usr/bin/env python3
# coding: utf8
__author__ = "Juan Manuel Fernández Nácher"

# Librería bot telegram
# doc: https://github.com/python-telegram-bot/python-telegram-bot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

from HorarioController import HorarioController

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.horarioController = HorarioController()

    def startBot(self):
        # Create the Updater and pass it your bot's token.
        updater = Updater(self.token)
        #updater.bot.promoteChatMember(10450997, can_delete_messages=True)

        # Listenings - comands
        updater.dispatcher.add_handler(CommandHandler('start', self.__start))
        updater.dispatcher.add_handler(CommandHandler('help', self.__help))
        updater.dispatcher.add_handler(CommandHandler('login', self.horarioController.login))
        updater.dispatcher.add_handler(CommandHandler('horas', self.horarioController.getDatosHorario))
        updater.dispatcher.add_handler(CommandHandler('imputar', self.horarioController.imputar))

        # Listening noncamnd
        updater.dispatcher.add_handler(MessageHandler(Filters.text, self.horarioController.messagesController))

        # Buttons controller
        updater.dispatcher.add_handler(CallbackQueryHandler(self.horarioController.buttonController))

        # log all error
        updater.dispatcher.add_error_handler(self.__error)

        # Start the Bot
        updater.start_polling()

        # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT
        updater.idle()

    def __start(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text="Bienvenido!! Para más ayuda escribe /help")

    def __help(self, bot, update):
        chat = update.message.chat
        update.message.reply_text("Usa la fuerza Luke")

    def __error(self, bot, update, error):
        None