import sounddevice as sd
import numpy as np
import speech_recognition as sr
import wave
import io
import os
import subprocess
import psutil
import win32gui
import win32con
import win32process
import time
# python -m pip install sounddevice
# python -m pip install numpy
# python -m pip install SpeechRecognition
# python -m pip install pyaudio
# python -m pip install psutil
# python -m pip install pywin32
# python -m pip install sounddevice numpy SpeechRecognition pyaudio psutil pywin32

# ==================== НАСТРОЙКИ ====================
SAMPLE_RATE = 16000
DURATION = 5  # секунд записи команды

# Путь к браузеру (для открытия сайтов). Сейчас — Edge.
BROWSER_PATH = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
BROWSER_PATH_2 = "C:/Program Files (x86)/Yandex/YandexBrowser/Application/browser.exe"

# ==================== СЛОВАРЬ ПРИЛОЖЕНИЙ ====================
apps = {
    # Браузер (открытие сайтов идёт через BROWSER_PATH)
    "edge":   BROWSER_PATH,
    "яндекс": BROWSER_PATH_2,

    # Приложения
    "steam":     "C:/Program Files (x86)/Steam/Steam.exe",
    "kimi":      "C:/Users/ADMIN F/AppData/Local/Programs/Kimi/Kimi.exe",
    "hub":       "C:/Program Files/FlyFrogLLC/Happ/Happ.exe",
    "хаб":       "C:/Program Files/FlyFrogLLC/Happ/Happ.exe",
    "teamspeak": "C:/Users/ADMIN F/AppData/Local/Programs/TeamSpeak/TeamSpeak.exe",
    "мизери": 'steam://rungameid/2119830',
    "мызери": 'steam://rungameid/2119830',
    "калькулятор": "calc.exe",
    "калькулятор": "calc.exe",
    "калькулятор": "calc.exe",
    "калькулятор": "calc.exe",

    # Сайты
    "ютуб":      "https://www.youtube.com",
    "github":    "https://github.com/Ulibca",
    "музыка":    "https://music.yandex.ru",
    "ivi":       "https://www.ivi.ru/programs",
    "telegram":  "https://web.telegram.org/k/#@Koteikin69",
}


# ==================== ЗАПИСЬ АУДИО ====================
def record_audio():
    print("Слушаю...")
    audio_data = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='int16'
    )
    sd.wait()

    with io.BytesIO() as wav_io:
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data.tobytes())
        wav_io.seek(0)
        return sr.AudioData(wav_io.read(), SAMPLE_RATE, 2)


# ==================== ОТКРЫТИЕ ====================
def open_app(name):
    """Открывает приложение или сайт по его имени."""
    path = apps.get(name.lower())
    if not path:
        print(f"Приложение '{name}' не найдено в списке.")
        return
    if path.startswith('steam://'):
        os.startfile(path)
        print(f'Запускаю {name} через Steam')
        return
    if path.startswith("http"):
        # Сайт — открываем в указанном браузере
        try:
            subprocess.Popen([BROWSER_PATH, path])
            print(f"Открываю сайт {name}")
        except Exception as e:
            print(f"Не удалось открыть сайт: {e}")
    else:
        # Приложение — запускаем .exe
        try:
            subprocess.Popen([path])
            print(f"Открываю приложение {name}")
        except Exception as e:
            print(f"Не удалось запустить: {e}")


# ==================== ЗАКРЫТИЕ (МЯГКОЕ) ====================
def _graceful_close(process_name, app_path):
    """
    Пытается закрыть приложение мягко.
    Для Steam использует команду -shutdown.
    Для остальных — посылает WM_CLOSE в окна (как крестик).
    Возвращает True, если удалось отправить сигнал закрытия.
    """
    process_name = process_name.lower()

    # --- Особый случай: Steam ---
    if process_name == "steam.exe":
        print("Обнаружен Steam. Отправляю команду -shutdown...")
        try:
            subprocess.run([app_path, "-shutdown"], timeout=10)
            # Ждём, пока процесс завершится
            for _ in range(20):  # 10 секунд
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


def _has_visible_windows(process_name):
    """Проверяет, есть ли у процесса хоть одно видимое окно."""
    process_name = process_name.lower()
    found = False

    def enum_handler(hwnd, _):
        nonlocal found
        if not win32gui.IsWindowVisible(hwnd):
            return
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            proc = psutil.Process(pid)
            if proc.name().lower() == process_name:
                found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    win32gui.EnumWindows(enum_handler, None)
    return found


def close_app(name):
    """Закрывает приложение мягко, как крестик. Без жёсткого kill()."""
    path = apps.get(name.lower())
    if not path:
        print(f"Приложение '{name}' не найдено.")
        return

    if path.startswith("http"):
        print(f"'{name}' — это сайт, я его не закрываю.")
        return

    process_name = os.path.basename(path).lower()

    # 1. Пробуем мягко закрыть (Steam обрабатывается внутри _graceful_close)
    if not _graceful_close(process_name, path):
        print(f"У {name} нет видимых окон — возможно, не запущен.")
        return

    print(f"Попросил {name} закрыться...")

    # 2. Ждём, пока пропадут ВИДИМЫЕ ОКНА (а не процесс целиком)
    for _ in range(20):  # 10 секунд
        time.sleep(0.5)
        if not _has_visible_windows(process_name):
            print(f"{name} закрылся ✅")
            return

    print(f"{name} не закрылся (окна всё ещё видны).")


# ==================== ОСНОВНОЙ ЦИКЛ ====================
r = sr.Recognizer()
print("Привет, я Джарвис. Чем могу помочь?")

while True:
    audio = record_audio()
    try:
        text = r.recognize_google(audio, language="ru_RU").lower()
        print(f"Вы сказали: {text}")

        # Выход
        if text in ("стоп", "выход", "пока", "заверши", "закончи", "закончим"):
            print("До свидания!")
            break

        # Открытие
        if text.startswith("джарвис открой "):
            name = text.replace("джарвис открой ", "").strip()
            open_app(name)

        # Закрытие
        elif text.startswith("джарвис закрой "):
            name = text.replace("джарвис закрой ", "").strip()
            close_app(name)

        # Если сказано что-то другое — ничего не делаем
        else:
            print("Команда не распознана.")

    except sr.UnknownValueError:
        print("Извините, я не расслышал.")
    except sr.RequestError:
        print("Ошибка подключения к Google Speech Recognition. Проверьте интернет.")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
