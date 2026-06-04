#!/usr/bin/env python3
from os import getenv
from requests import get, post
from json import loads
from time import sleep
from datetime import datetime, timezone

TEAM_NAME = "mixailov_alex_team"
TOURNEY_NAME = "15 DOLLARS SWISS QUALIFIER"

TOKENS = getenv("LICHESS_TOKENS", "").split(",")

# Получаем предстоящие турниры
response = get(f"https://lichess.org/api/team/{TEAM_NAME}/swiss",
               params={
                   "max": 100,
                   "status": "created",
                   "name": TOURNEY_NAME
               })

if response.status_code == 200:
    print(f"{datetime.now(timezone.utc)}: Турниры получены")
else:
    print(f"{datetime.now(timezone.utc)}: Турниры не получены. Ошибка {response.status_code}")
    exit()

# Парсим турниры
tournaments_text = response.text.strip()
if not tournaments_text:
    print(f"{datetime.now(timezone.utc)}: Нет турниров")
    exit()

tournaments = tournaments_text.split("\n")[::-1]

if len(tournaments) == 0:
    print(f"{datetime.now(timezone.utc)}: Нет турниров")
    exit()

# Получаем ID турниров до циклов (чтобы не парсить каждый раз)
try:
    first_tournament_id = loads(tournaments[0])["id"]
    print(f"{datetime.now(timezone.utc)}: Первый турнир ID: {first_tournament_id}")
except Exception as e:
    print(f"{datetime.now(timezone.utc)}: Ошибка парсинга первого турнира: {e}")
    exit()

if len(tournaments) > 1:
    try:
        second_tournament_id = loads(tournaments[1])["id"]
        print(f"{datetime.now(timezone.utc)}: Второй турнир ID: {second_tournament_id}")
    except Exception as e:
        print(f"{datetime.now(timezone.utc)}: Ошибка парсинга второго турнира: {e}")
        second_tournament_id = None
else:
    second_tournament_id = None

# Покидаем предстоящий турнир
for token in TOKENS:
    sleep(2)
    try:
        resp = post(
            f"https://lichess.org/api/swiss/{first_tournament_id}/withdraw",
            headers={"Authorization": f"Bearer {token}"}
        )
        if resp.status_code == 200:
            print(f"{datetime.now(timezone.utc)}: Юзер успешно покинул турнир")
        else:
            print(f"{datetime.now(timezone.utc)}: Юзер не покинул турнир. Ошибка {resp.status_code}")
    except Exception as e:
        print(f"{datetime.now(timezone.utc)}: Ошибка запроса при покидании: {e}")

if second_tournament_id is None:
    print(f"{datetime.now(timezone.utc)}: Больше турниров нет")
    exit()

# Заходим в следующий турнир
for token in TOKENS:
    sleep(2)
    try:
        resp = post(
            f"https://lichess.org/api/swiss/{second_tournament_id}/join",
            headers={"Authorization": f"Bearer {token}"}
        )
        if resp.status_code == 200:
            print(f"{datetime.now(timezone.utc)}: Юзер успешно зашёл в турнир")
        else:
            print(f"{datetime.now(timezone.utc)}: Юзер не зашёл в турнир. Ошибка {resp.status_code}")
    except Exception as e:
        print(f"{datetime.now(timezone.utc)}: Ошибка запроса при присоединении: {e}")
