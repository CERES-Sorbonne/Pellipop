from threading import Thread
from typing import Optional

import cv2
import os
from pathlib import Path

from PIL import Image
from imagehash import average_hash
from tqdm.auto import tqdm

from pellipop.speech_to_text import extractText, extractAudio, whisperMode

video_formats = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg", ".3gp", ".3g2"}


def file_finder(path: str | Path, deep: int = -1) -> Path:
    if isinstance(path, str):
        path = Path(path)

    for file in path.glob("*"):
        if file.is_dir():
            if deep == -1:
                yield from file_finder(file)
            elif deep > 0:
                yield from file_finder(file, deep - 1)

        elif file.suffix in video_formats:
            yield file

def how_many_files(path: str | Path, deep: int = -1) -> int:
    return len(list(file_finder(path, deep)))


def launch(
        freq: float,
        input_folder: str | Path,
        output_folder: str | Path = Path.home() / "Documents" / "Pellipop",
        delete_duplicates: bool = False,
        decouper: bool = False,
        audio: bool = False,
        retranscrire: bool = False,
        csv: bool = False,

        whisper_config: dict = None,
) -> Optional[Path]:
    exec_dir = Path(__file__).parent
    print(exec_dir)

    if not isinstance(input_folder, Path):
        input_folder = Path(input_folder)

    if not isinstance(output_folder, Path):
        output_folder = Path(output_folder)

    if not input_folder.exists():
        raise FileNotFoundError("Le dossier d'entrée n'existe pas")

    if not input_folder.is_dir():
        raise NotADirectoryError("Le chemin d'entrée n'est pas un dossier")

    if not output_folder.exists():
        print("Le dossier de sortie n'existe pas, il sera créé")
        output_folder.mkdir(parents=True)

    if output_folder.is_file():
        raise NotADirectoryError("Le chemin de sortie est un fichier")


    if audio:
        if whisper_config is None:
            whisper_config = exec_dir / "whisper_config.json"
        else:
            whisper_config = Path(whisper_config)

        if not whisper_config.exists():
            print("Le fichier de configuration de l'API Whisper n'a pas été trouvé")
            whisper_config = None

    if decouper:
        t1 = Thread(target=extract_audio_then_text, args=(input_folder, output_folder, audio, whisper_config))
        t1.start()
    else:
        extract_audio_then_text(input_folder, output_folder, audio, whisper_config)

    if decouper:
        if retranscrire:
            t2 = Thread(target=decouper_video, args=(freq, input_folder, output_folder, delete_duplicates))
            t2.start()

        else:
            decouper_video(freq, input_folder, output_folder, delete_duplicates)




if __name__ == "__main__":
    testdir = "/home/marceau/PycharmProjects/tksel/"

    print(how_many_files(testdir))
