import sys
from pathlib import Path

import speech_recognition as sr
from tqdm.auto import tqdm


def toText(audioPath: str | Path, textPath: str | Path, recognizer: sr.Recognizer = None):
    if isinstance(audioPath, str):
        audioPath = Path(audioPath)
    if isinstance(textPath, str):
        textPath = Path(textPath)

    if not audioPath.exists():
        print("The audio file does not exist")
        sys.exit(1)

    if textPath.exists():
        print("The text file already exists")

    if not recognizer:
        recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audioPath.as_posix()) as source:
            recognizer.adjust_for_ambient_noise(source)
            data = recognizer.record(source)

        text = recognizer.recognize_google(data, language="fr-FR")

        with open(textPath, "w", encoding="utf-8") as f:
            f.write(text)

    except Exception as e:
        print(e)
        print(f"Error with {audioPath.name}")


def toTextFolder(audioPath: str | Path, textPath: str | Path, recognizer: sr.Recognizer = None):
    if isinstance(audioPath, str):
        audioPath = Path(audioPath)
    if isinstance(textPath, str):
        textPath = Path(textPath)

    if not audioPath.exists():
        print("The audio folder does not exist")
        sys.exit(1)

    if not textPath.exists():
        textPath.mkdir(parents=True)

    if not recognizer:
        recognizer = sr.Recognizer()

    audios = tqdm(list(audioPath.glob("*.wav")))
    for audio in audios:
        text = textPath / audio.with_suffix(".txt").name

        toText(audio, text, recognizer=recognizer)


if __name__ == "__main__":
    toTextFolder("../../audio-collecte1", "../../txt-collecte1")
