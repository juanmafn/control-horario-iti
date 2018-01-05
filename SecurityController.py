#!/usr/bin/env python3
# coding: utf8
__author__ = "Juan Manuel Fernández Nácher"

from requests.auth import HTTPBasicAuth
import requests

class SecurityController:

    __instance = None

    @staticmethod
    def getInstance():
        if SecurityController.__instance is None:
            SecurityController()
        return SecurityController.__instance

    def __init__(self):
        if SecurityController.__instance is None:
            SecurityController.__instance = self
        self.credentials = {}
        self.username = 'user'
        self.password = 'pass'
        self.urlBase = 'https://intranet.iti.upv.es'
        self.urlParcialInicial = '/controlhorario'

    def isLogged(self, chatId):
        return chatId in self.credentials and \
               self.credentials[chatId][self.username] is not None and \
               self.credentials[chatId][self.password] is not None

    def getHTTPBasicAuth(self, chatId):
        username = self.credentials[chatId][self.username]
        password = self.credentials[chatId][self.password]
        return HTTPBasicAuth(username, password)

    def login(self, chatId, username, password):
        self.credentials[chatId] = {self.username: username, self.password: password}

    def setUsername(self, chatId, username):
        if chatId not in self.credentials:
            self.credentials[chatId] = {}
        self.credentials[chatId][self.username] = username

    def setPassword(self, chatId, password):
        if chatId not in self.credentials:
            self.credentials[chatId] = {}
        self.credentials[chatId][self.password] = password

    def logout(self, chatId):
        if chatId in self.credentials:
            del self.credentials[chatId]

    def testCredentials(self, chatId):
        request = requests.get(self.urlBase + self.urlParcialInicial, auth=self.getHTTPBasicAuth(chatId))
        if request.status_code == 200:
            return True
        else:
            self.logout(chatId)
            return False
