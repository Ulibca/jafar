import sounddevice as sd
import numpy as np
import speech_recognition as sr
import webbrowser
import wave
import io
import os
import subprocess


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
    "яндекс": "C:/Program Files (x86)/Yandex/YandexBrowser/Application/browser.exe",
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
    "": "",
    "": "",
    "": "",
    "": "",
    "": "",
    "": "",
}
running_processes ={}
#НАПИСАТЬ СЛОВАРЬ СИНОНИМОВ
YANDEX_BROWSER = "C:/Program Files (x86)/Yandex/YandexBrowser/Application/browser.exe"
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
            proc = subprocess.Popen(path)
            running_processes[name] = proc
            print(f"Открываю приложение {name}")
        except Exception as e:
            print(f"Не удалось запустить: {e}")

def close_app_by_process(name):
    proc = running_processes.get(name)
    if proc:
        proc.terminate()        # вежливо завершить
        # proc.kill()           # если не закрывается — принудительно
        del running_processes[name]
        print(f"Закрыл {name}")
    else:
        print(f"Приложение {name} не было запущено через меня")

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
            close_app_by_process(name)
        else:
            name = text  # если сказано просто "яндекс"

        # Открываем
        open_app(name)
    except sr.UnknownValueError:
        print("Извините, я не расслышал.")
    except sr.RequestError:
        print("Ошибка подключения к Google Speech Recognition. Проверьте интернет.")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")