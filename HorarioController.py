#!/usr/bin/env python3
# coding: utf8
__author__ = "Juan Manuel Fernández Nácher"

# Librería bot telegram
# doc: https://github.com/python-telegram-bot/python-telegram-bot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import requests
import re, json
from datetime import datetime
from enum import Enum

from SecurityController import SecurityController

class Action(Enum):
    IMPUTAR = '1'
    LOGIN_USER = '2'
    LOGIN_PASS = '3'

class HorarioController:

    def __init__(self):
        self.urlBase = 'https://intranet.iti.upv.es'
        self.urlParcialInicial = '/controlhorario'
        self.urlParcialImputar = '/controlhorario/actividad/nueva'
        self.estado = {}
        self.securityController = SecurityController.getInstance()
        self.reUrlHoras = 'src="(/controlhorario/_fragment\?_path=.*?)"'
        self.reHoras = \
            '<h5>.*?Horas mes.*?</h5>.*?<h2.*?>.*?(\d+:\d+).*?</h2>.*?<h2.*?>.*?(\d+:\d+).*?</h2>.*?' \
            '<h5>.*?Al final del día.*?</h5>.*?<h2.*?>.*?(\d+:\d+).*?</h2>.*?<h2.*?>.*?([+-]\d+:\d+).*?</h2>.*?' \
            '<h5>.*?Días hasta fin de mes.*?</h5>.*?<h2.*?>.*?(\d+).*?</h2>.*?<h2.*?>.*?([+-]\d+:\d+).*?</h2>'
        self.reFormularioOpciones = '<form.*action="/controlhorario/actividad/nueva".*?<option.*?</option>(.*?)</form>'
        self.reOpcionesImputar = '<option.*?value="(\d+)".*?>(.*?)</option>'
        self.reTokenImputar = '<form.*?action="/controlhorario/actividad/nueva".*?<input type="hidden".*?value="(.*?)"'

    def login(self, bot, update):
        chatId = update.message.chat.id
        self.estado[chatId]=Action.LOGIN_USER
        update.message.reply_text('Introduce el nombre de usuario')

    def getDatosHorario(self, bot, update):
        chatId = update.message.chat.id
        if not self.securityController.isLogged(chatId):
            update.message.reply_text('Debes loguearte /login')
            return
        [HoraMesRealizadas,
         HoraMesEstipuladas,
         FinalDiaEstipuladas,
         FinalDiaDiferencia,
         DiasHastaFinMesLaborables,
         DiasHastaFinMesHorasDia] = self.__getDatosHorario__(chatId)

        result = 'Horas mes\n  - Realizadas: {0}\n  - Estipuladas: {1}\n\n' \
                 'Al final del día\n  - Estipuladas: {2}\n  - Diferencia: {3}\n\n' \
                 'Días hasta fin de mes\n  - Laborables: {4}\n  - Horas / día: {5}'.format(HoraMesRealizadas,
                                                                                           HoraMesEstipuladas,
                                                                                           FinalDiaEstipuladas,
                                                                                           FinalDiaDiferencia,
                                                                                           DiasHastaFinMesLaborables,
                                                                                           DiasHastaFinMesHorasDia)
        update.message.reply_text(result)

    def imputar(self, bot, update):
        chatId = update.message.chat.id
        if not self.securityController.isLogged(chatId):
            update.message.reply_text('Debes loguearte /login')
            return
        keyboard = []
        options = self.__getOptions__(chatId)
        for option in options:
            callback = json.dumps({'action': Action.IMPUTAR.value, 'option': option[0]})
            keyboard.append([InlineKeyboardButton(option[1], callback_data=callback)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Selecciona opción', reply_markup=reply_markup)

    def buttonController(self, bot, update):
        query = update.callback_query
        data = json.loads(query.data)

        if data['action'] == Action.IMPUTAR.value:
            self.__imputar__(bot, update, data['option'], query.message.chat_id)
        else:
            bot.editMessageText(text="Has seleccionado: {0}".format(query.data),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)

    def messagesController(self, bot, update):
        chatId = update.message.chat.id
        if chatId in self.estado:
            text = update.message.text
            if self.estado[chatId] == Action.LOGIN_USER:
                self.securityController.setUsername(chatId, text)
                self.estado[chatId] = Action.LOGIN_PASS
                update.message.reply_text('Introduce el password')
            elif self.estado[chatId] == Action.LOGIN_PASS:
                self.securityController.setPassword(chatId, text)
                del self.estado[chatId]
                if self.securityController.testCredentials(chatId):
                    update.message.reply_text('Login correcto')
                else:
                    update.message.reply_text('Las credenciales no son válidas, vuelva a intentarlo /login')

    def __getDatosHorario__(self, chatId):
        request = requests.get(self.urlBase + self.urlParcialInicial, auth=self.securityController.getHTTPBasicAuth(chatId))
        urlParcialHoras = re.findall(self.reUrlHoras, request.text)[1].replace('amp;', '')
        request = requests.get(self.urlBase + urlParcialHoras, auth=self.securityController.getHTTPBasicAuth(chatId))
        return re.findall(self.reHoras, request.text, re.DOTALL)[0]

    def __getOptions__(self, chatId):
        request = requests.get(self.urlBase + self.urlParcialInicial, auth=self.securityController.getHTTPBasicAuth(chatId))
        form = re.findall(self.reFormularioOpciones, request.text, re.DOTALL)[0]
        options = re.findall(self.reOpcionesImputar, form, re.DOTALL)
        return options

    def __imputar__(self, bot, update, option, chatId):
        query = update.callback_query
        request = requests.get(self.urlBase + self.urlParcialInicial, auth=self.securityController.getHTTPBasicAuth(chatId))
        token = re.findall(self.reTokenImputar, request.text, re.DOTALL)[0]
        payload = {
            'daily_activity[action]': option,
            'daily_activity[timestamp]': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'daily_activity[comment]': '',
            'daily_activity[Guardar]': '',
            'daily_activity[_token]': token
        }
        request = requests.post(self.urlBase + self.urlParcialImputar, data=payload,
                                auth=self.securityController.getHTTPBasicAuth(chatId), cookies=request.cookies)
        bot.editMessageText(text='Imputación correcta',
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)