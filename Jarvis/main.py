# main.py
import speech_recognition as sr

from core.voice import record_audio, recognize, say
from core.wake_word import listen_for_wake_word
from features.apps import open_app, close_app


COMMAND_DURATION = 5  # сколько секунд слушаем команду после активации

# Список фраз для выхода
EXIT_PHRASES = ("стоп", "выход", "пока", "заверши", "спать")


def handle_command(text: str) -> bool:
    """
    Обрабатывает распознанную команду.
    Возвращает False, если нужно завершить программу.
    """
    # Выход
    if text in EXIT_PHRASES:
        say("До связи")
        return False

    # Открыть
    if text.startswith("открой "):
        name = text.replace("открой ", "").strip()
        say(open_app(name))
        return True

    # Закрыть
    if text.startswith("закрой "):
        name = text.replace("закрой ", "").strip()
        say(close_app(name))
        return True

    # Неизвестная команда
    say("Не понял команду")
    return True


def main():
    say("Привет, я твой ассистент. Чем помочь?")

    while True:
        # 1. Ждём активации
        listen_for_wake_word()
        say("Слушаю")

        # 2. Записываем и распознаём команду
        audio = record_audio(COMMAND_DURATION)
        try:
            text = recognize(audio)
            print(f"Вы сказали: {text}")

            if not handle_command(text):
                break

        except sr.UnknownValueError:
            say("Не расслышал")
        except sr.RequestError:
            say("Проблема с интернетом")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()