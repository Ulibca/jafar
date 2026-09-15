# core/config.py
import json
import os

# Путь к конфигу — относительно корня проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
ALIASES_FILE = os.path.join(BASE_DIR, "aliases.json")


def load_json(path):
    """Загружает JSON-файл. Возвращает {} если файла нет."""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    """Сохраняет данные в JSON-файл."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_apps():
    """Загружает словарь приложений из config.json"""
    return load_json(CONFIG_FILE)


def save_apps(apps):
    """Сохраняет словарь приложений в config.json"""
    save_json(CONFIG_FILE, apps)


def load_aliases():
    """Загружает синонимы из aliases.json"""
    return load_json(ALIASES_FILE)


def save_aliases(aliases):
    save_json(ALIASES_FILE, aliases)