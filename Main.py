#!/usr/bin/env python3
# coding: utf8
__author__ = "Juan Manuel Fernández Nácher"

# Clase que maneja la api de telegram
from TelegramBot import TelegramBot

def main():
    TOKEN = open('token', 'r').read().strip()
    telegramBot = TelegramBot(TOKEN)
    telegramBot.startBot()

if __name__ == "__main__":
    main()
