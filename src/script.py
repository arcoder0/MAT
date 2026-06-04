#!/usr/bin/env python3
from requests import get, post
from json import loads
from time import sleep

TEAM_NAME = "mixailov_alex_team"
TOURNEY_NAME = "15 DOLLARS SWISS QUALIFIER"

# Если вам нехрен делать, кроме как записываться в левые турниры,
# то Бог вам судья. Больше прав у токенов нет

TOKENS = ["lip_x0XM4YKNPcJQnZN6XfMK",
          "lip_Rwo9qC1rAz5s7pWflPia",
          "lip_rcbxM3BvI95GtvgKLnIp",
          "lip_7VsQmGe4ZdcBhymuMRXT",
          "lip_l4RDuGQf4riodk4TMF6u",
          "lip_nc0jL8yzzAX3JuBAYevm",
          "lip_RQPiXynOrz85lOo3cwUk"]

"""Получаем предстоящие турниры"""

# самые поздние турниры идут первыми, а надо наоборот, а нельзя
# пздц...
tournaments = get(f"https://lichess.org/api/team/{TEAM_NAME}/swiss",
                  params={
                      "max": 100, # а чё ещё делать, надеемся, что Даня не создаст триллиард турниров
                      "status": "created",
                      "name": TOURNEY_NAME
                  }).content

tournaments = str(tournaments, encoding="utf-8")[:-1].split("\n")[::-1]

if len(tournaments) == 0:
    exit()

# Покидаем предстоящий турнир
for token in TOKENS:
    sleep(2)
    post(
        f"https://lichess.org/api/swiss/{loads(tournaments[0])["id"]}/withdraw",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {token}"
        },
    )

if len(tournaments) == 1:
    exit()

# Заходим в следующий турнир
for token in TOKENS:
    sleep(2)
    post(
        f"https://lichess.org/api/swiss/{loads(tournaments[1])["id"]}/join",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {token}"
        },
    )
