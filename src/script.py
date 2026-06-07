#!/usr/bin/env python3
import os
import sys
from time import sleep
from datetime import datetime, timezone
from requests import get, post
from tournament_state import load_state, save_state, clear_state

TEAM_NAMES = os.getenv("TEAM_NAMES", "").split(",")
TOURNEY_NAME = os.getenv("TOURNEY_NAME", "15 DOLLARS SWISS QUALIFIER")
TOKENS = [t.strip() for t in os.getenv("LICHESS_TOKENS", "").split(",") if t.strip()]

def log(msg):
    """Выводит сообщение с временем UTC"""
    print(f"{datetime.now(timezone.utc)}: {msg}")

def fetch_all_tournaments(team_name):
    """
    Получает список ID ВСЕХ турниров на сегодня.
    Вызывается только один раз в день (в первый запуск).
    """
    log(f"📡 Запрос к API Lichess для клуба {team_name}...")
    
    try:
        response = get(
            f"https://lichess.org/api/team/{team_name}/swiss",
            params={"max": 100, "status": "created", "name": TOURNEY_NAME},
            timeout=30
        )
        
        if response.status_code != 200:
            log(f"❌ Ошибка API: {response.status_code}")
            return []
        
        tournaments_text = response.text.strip()
        if not tournaments_text:
            log(f"📭 Нет турниров для {team_name}")
            return []
        
        tournaments = []
        for line in tournaments_text.split("\n"):
            if not line:
                continue
            try:
                import json
                data = json.loads(line)
                tournaments.append(data["id"])
            except:
                continue
        
        tournaments = tournaments[::-1]

        return tournaments
        
    except Exception as e:
        log(f"⚠️ Ошибка при запросе к API: {e}")
        return []

def api_request(action, tournament_id, token):
    """Выполняет запрос к API Lichess"""
    url = f"https://lichess.org/api/swiss/{tournament_id}/{action}"
    try:
        resp = post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        if resp.status_code == 200:
            log(f"✅ {token[:8]}... {action} OK")
            return True
        else:
            log(f"❌ {token[:8]}... {action} ошибка {resp.status_code}")
            try:
                error_data = resp.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    log(f"   Причина: {error_data['error']}")
            except:
                pass
            return False
    except Exception as e:
        log(f"⚠️ {token[:8]}... {action} исключение: {e}")
        return False

def process_team(team_name):
    """Обрабатывает один клуб"""
    print()
    log(f"Обработка клуба {team_name}")
    
    # Загружаем сохранённое состояние
    state = load_state(team_name)
    
    if state is None or not state.get("tournaments"):
        log("📡 Список пуст, запрашиваем API")
        tournaments = fetch_all_tournaments(team_name)
        
        if len(tournaments) < 2:
            log(f"⚠️ Недостаточно турниров для переключения (найдено {len(tournaments)})")
            clear_state(team_name)
            return
        
        save_state(team_name, tournaments, 0)
        state = load_state(team_name)
    
    tournaments = state["tournaments"]
    index = state["index"]
    
    if not tournaments:
        log("📭 Нет активных турниров в состоянии")
        return
    
    log(f"📋 Текущий список турниров: {tournaments}")
    log(f"📍 Текущий индекс: {index}")
    
    if index + 1 >= len(tournaments):
        log("🏁 Все турниры обработаны, очищаем состояние")
        clear_state(team_name)
        return
    
    current_id = tournaments[index]
    next_id = tournaments[index + 1]
    
    log(f"🔄 Выход из турнира: {current_id}")
    for token in TOKENS:
        sleep(1.25)
        api_request("withdraw", current_id, token)
    
    log(f"➡️ Вход в турнир: {next_id}")
    for token in TOKENS:
        sleep(1.25)
        api_request("join", next_id, token)
    
    new_index = index + 1
    save_state(team_name, tournaments, new_index)
    log(f"✅ Прогресс сохранён: индекс {new_index} из {len(tournaments)}")
    
    if new_index + 1 >= len(tournaments):
        log("🎯 Это было последнее переключение на сегодня")

def main():  
    log(f"👥 Токенов: {len(TOKENS)}")
    log(f"🏢 Клубы: {TEAM_NAMES}")
    log(f"🏆 Название турнира: {TOURNEY_NAME}")
    
    for team_name in TEAM_NAMES:
        if not team_name.strip():
            continue
        try:
            process_team(team_name.strip())
        except Exception as e:
            log(f"⚠️ Ошибка при обработке {team_name}: {e}")
            continue

if __name__ == "__main__":
    main()
