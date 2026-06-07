import json
import os

def get_state_filename(team_name):
    """Возвращает имя файла для сохранения состояния клуба"""
    # Очищаем имя команды от недопустимых символов (на всякий случай)
    safe_name = team_name.replace("/", "_").replace(" ", "_")
    return f"state_{safe_name}.json"

def load_state(team_name):
    """Загружает состояние клуба из файла"""
    filename = get_state_filename(team_name)
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def save_state(team_name, tournaments, index):
    """Сохраняет состояние клуба в файл"""
    filename = get_state_filename(team_name)
    with open(filename, "w") as f:
        json.dump({"tournaments": tournaments, "index": index}, f)

def clear_state(team_name):
    """Очищает состояние клуба (сохраняет пустой список)"""
    save_state(team_name, [], 0)
