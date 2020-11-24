from pprint import pprint
import requests
import time  # для запуска бота
import redis  # БД

TOKEN = '1318088130:AAFFPoPjMNp-LRqNfl2p2aiwNM209rwjLfI'  # токен бота
URL = "http://185.251.91.134/api/"  # юрлка
URL_AUTH_Room = 'http://185.251.91.134/api/rooms/owner/ads'
URL_AUTH_Lot = 'http://185.251.91.134/api/lot/owner/ads'
