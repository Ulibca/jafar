# features/apps.py
import subprocess
import os
import webbrowser
import psutil

from core.config import load_apps, save_apps, load_aliases


# Путь к Яндекс.Браузеру (для открытия сайтов именно в нём)
YANDEX_BROWSER = r"C:\Program Files\Yandex\YandexBrowser\Application\browser.exe"


def _resolve_name(name: str, apps: dict, aliases: dict):
    """Преобразует синоним в каноническое имя приложения."""
    name = name.lower().strip()
    if name in apps:
        return name
    for canonical, syn_list in aliases.items():
        if name in [s.lower() for s in syn_list]:
            return canonical
    return None


def open_app(name: str) -> str:
    """
    Открывает приложение или сайт по имени.
    Возвращает текстовый отчёт для ассистента.
    """
    apps = load_apps()
    aliases = load_aliases()

    canonical = _resolve_name(name, apps, aliases)
    if not canonical:
        return f"Не знаю, что такое '{name}'"

    path = apps[canonical]

    # Сайт — открываем в Яндекс.Браузере
    if path.startswith("http"):
        try:
            if os.path.exists(YANDEX_BROWSER):
                subprocess.Popen([YANDEX_BROWSER, path])
            else:
                webbrowser.open(path)  # fallback
            return f"Открываю {canonical}"
        except Exception as e:
            return f"Ошибка открытия сайта: {e}"

    # Приложение — проверяем существование файла
    if not os.path.exists(path):
        return f"Путь к '{canonical}' не найден. Запусти настройку."

    try:
        subprocess.Popen(path)
        return f"Запускаю {canonical}"
    except Exception as e:
        return f"Не удалось запустить: {e}"


def close_app(name: str) -> str:
    """
    Закрывает приложение по имени процесса.
    Ищет .exe-файл по имени из config.json.
    """
    apps = load_apps()
    aliases = load_aliases()

    canonical = _resolve_name(name, apps, aliases)
    if not canonical:
        return f"Не знаю, что такое '{name}'"

    path = apps[canonical]
    if path.startswith("http"):
        return "Сайты я закрывать не умею"

    # Имя процесса — последняя часть пути (например, browser.exe)
    process_name = os.path.basename(path).lower()

    killed = False
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == process_name:
                proc.terminate()
                killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if killed:
        return f"Закрываю {canonical}"
    return f"{canonical} не запущен"


def add_app(name: str, path: str) -> str:
    """Добавляет приложение в config.json."""
    apps = load_apps()
    apps[name.lower()] = path.replace("\\", "/")
    save_apps(apps)
    return f"Добавил {name}"