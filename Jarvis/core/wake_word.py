# core/wake_word.py
from core.voice import record_audio, recognize
import speech_recognition as sr
import time


WAKE_WORD = "джарвис"       # поменяешь, когда определишься с именем
CHUNK_DURATION = 1.5        # длительность куска для прослушки (сек)


def listen_for_wake_word() -> bool:
    """
    Бесконечно слушает короткие куски, пока не услышит ключевое слово.
    Возвращает True, когда услышал.
    """
    print(f"(Спит... скажи '{WAKE_WORD}' для активации)")
    while True:
        audio = record_audio(CHUNK_DURATION)
        try:
            text = recognize(audio)
            if text:
                print(f"[фон] {text}")   # для отладки, можно убрать
            if WAKE_WORD in text:
                return True
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            print("Ошибка интернета, ждём...")
            time.sleep(1)