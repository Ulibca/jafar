import sounddevice as sd
import numpy as np
import speech_recognition as sr
import webbrowser
import wave
import io
import os
import subprocess
import psutil
import win32gui
import win32con
import win32process
import time

# Настройки записи
SAMPLE_RATE = 16000
DURATION = 5  # секунд

def record_audio():
    print("Слушаю...")
    audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()
    with io.BytesIO() as wav_io:
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data.tobytes())
        wav_io.seek(0)
        return sr.AudioData(wav_io.read(), SAMPLE_RATE, 2)

# Словарь приложений и сайтов
apps = {
    "яндекс": "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "steam": "C:/Program Files (x86)/Steam/Steam.exe",  # сырая строка
    "ютуб": "https://www.youtube.com",
    "github": "https://github.com/Ulibca",
    "музыка": "https://music.yandex.ru",
    "калькулятор": "calc.exe",  # можно и системные команды
    "дипсик": "",
    "kimi": "C:/Users/ADMIN F/AppData/Local/Programs/Kimi/Kimi.exe",
    "юнити": "",
    "грок": "",
    "ivi": "https://www.ivi.ru/programs",
    "telergrem": "https://web.telegram.org/k/#@Koteikin69",
    "hub": "C:/Program Files/FlyFrogLLC/Happ/Happ.exe",
    "хаб": "C:/Program Files/FlyFrogLLC/Happ/Happ.exe",
    "teamspeak": "C:/Users/ADMIN F/AppData/Local/Programs/TeamSpeak/TeamSpeak.exe",
    "": "",
    "": "",
    "": "",
    "": "",
    "": "",
}
running_processes ={}
#НАПИСАТЬ СЛОВАРЬ СИНОНИМОВ
YANDEX_BROWSER = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
def open_app(name):
    """Открывает приложение или сайт по его имени"""
    path = apps.get(name.lower())
    if not path:
        print(f"Приложение '{name}' не найдено в списке.")
        return

    if path.startswith("http"):
        subprocess.Popen([YANDEX_BROWSER, path])
        print(f"Открываю сайт {name}")
    else:
        try:
            proc = subprocess.Popen([path])
            running_processes[name] = proc
            print(f"Открываю приложение {name}")
        except Exception as e:
            print(f"Не удалось запустить: {e}")

def _graceful_close(process_name, app_path):
    """
    Пытается закрыть приложение мягко.
    Для Steam использует специальную команду -shutdown.
    Для остальных — посылает WM_CLOSE в окно (как крестик).
    """
    # --- Особый случай для Steam ---
    if process_name.lower() == "steam.exe":
        print("Обнаружен Steam. Отправляю команду -shutdown...")
        try:
            subprocess.run([app_path, "-shutdown"], timeout=10)
            # Ждём, пока процесс завершится
            for _ in range(20):
                time.sleep(0.5)
                if not any(
                    p.info.get('name', '').lower() == process_name
                    for p in psutil.process_iter(['name'])
                ):
                    print("Steam успешно закрыт через -shutdown ✅")
                    return True
            print("Steam не завершился после команды -shutdown.")
            return False
        except Exception as e:
            print(f"Ошибка при вызове -shutdown: {e}")
            return False

    # --- Стандартное мягкое закрытие для остальных приложений ---
    closed = False

    def enum_handler(hwnd, _):
        nonlocal closed
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            proc = psutil.Process(pid)
            if proc.name().lower() == process_name:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                closed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    win32gui.EnumWindows(enum_handler, None)
    return closed


# def _force_close(process_name):
#     """Жёстко убивает все процессы с указанным именем."""
#     killed = False
#     for proc in psutil.process_iter(['pid', 'name']):
#         try:
#             if proc.info['name'].lower() == process_name:
#                 proc.terminate()
#                 try:
#                     proc.wait(timeout=3)
#                 except psutil.TimeoutExpired:
#                     proc.kill()
#                 killed = True
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             pass
#     return killed


def close_app(name):
    """Закрывает приложение мягко, если не вышло — жёстко."""
    path = apps.get(name.lower())
    if not path:
        print(f"Приложение '{name}' не найдено.")
        return

    if path.startswith("http"):
        print(f"'{name}' — это сайт, я его не закрываю.")
        return

    process_name = os.path.basename(path).lower()

    # 1. Пробуем мягко
    print(f"Пробую закрыть {name} мягко...")
    if _graceful_close(process_name, path):
        # Даём приложению время на корректное завершение
        for _ in range(10):
            time.sleep(0.5)
            if not any(
                p.info.get('name', '').lower() == process_name
                for p in psutil.process_iter(['name'])
            ):
                print(f"Закрыл {name} корректно ✅")
                return
        print(f"{name} не закрылся мягко, пробую жёстко...")

    # # 2. Жёстко
    # if _force_close(process_name):
    #     print(f"Закрыл {name} принудительно ⚠️")
    # else:
    #     print(f"{name} не найден (возможно, не запущен).")
# Основной цикл
r = sr.Recognizer()
print("Привет, я Джарвис. Чем могу помочь?")

while True:
    audio = record_audio()
    try:
        text = r.recognize_google(audio, language="ru_RU").lower()
        print(f"Вы сказали: {text}")
        
        # Проверка на выход
        if text in ("стоп", "выход", "пока", "заверши", 'закончи', 'закончим'):
            print("До свидания!")
            break

        # Извлекаем имя приложения из команды "открой ..."
        # Открытие
        if text.startswith("джарвис открой "):
            name = text.replace("джарвис открой ", "").strip()
            open_app(name)
        
        # Закрытие
        elif text.startswith("джарвис закрой "):
            name = text.replace("джарвис закрой ", "").strip()
            # Позже закрываем
            # proc.terminate()
            # proc.wait()
            close_app(name)                 # ✅ правильное имя функции
        else:
            name = text  # если сказано просто "яндекс"

        # Открываем

    except sr.UnknownValueError:
        print("Извините, я не расслышал.")
    except sr.RequestError:
        print("Ошибка подключения к Google Speech Recognition. Проверьте интернет.")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")