# core/voice.py
import io
import wave
import sounddevice as sd
import speech_recognition as sr


SAMPLE_RATE = 16000


def record_audio(duration: float) -> sr.AudioData:
    """
    Записывает аудио с микрофона заданной длительности (в секундах).
    Возвращает объект sr.AudioData для распознавания.
    """
    audio_data = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='int16'
    )
    sd.wait()

    # Преобразуем numpy-массив в WAV-формат для speech_recognition
    with io.BytesIO() as wav_io:
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data.tobytes())
        wav_io.seek(0)
        return sr.AudioData(wav_io.read(), SAMPLE_RATE, 2)


# Один общий распознаватель на всё приложение
_recognizer = sr.Recognizer()


def recognize(audio: sr.AudioData, language: str = "ru_RU") -> str:
    """
    Распознаёт речь из аудио через Google Speech.
    Возвращает распознанный текст в нижнем регистре.
    Бросает исключения sr.UnknownValueError / sr.RequestError.
    """
    text = _recognizer.recognize_google(audio, language=language)
    return text.lower()


# --- Заглушка под TTS (реализуем позже) ---
def say(text: str):
    """Произносит текст. Пока просто печатает в консоль."""
    print(f"[Ассистент]: {text}")
    # Позже: pyttsx3 или edge-tts