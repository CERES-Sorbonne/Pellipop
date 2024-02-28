import json
import sys
from pathlib import Path

from tqdm.auto import tqdm
from whisper_client.main import WhisperClient, Mode

from pellipop.Video import Video
from pellipop.file_finder import file_finder


# with open("config.json", "r", encoding="utf-8") as f:
#     config_data = json.load(f)

def rm_tree(pth: Path) -> None:
    """https://stackoverflow.com/questions/50186904/pathlib-recursively-remove-directory
    Removes all content of a directory recursively but not the directory itself"""
    if not pth.exists():
        print(f"{pth} does not exist, creating it")

        pth.mkdir(parents=True)
        return

    for child in pth.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)

    # pth.rmdir()


def toText(
        config_data: dict,
        audioPath: str | Path,
        textPath: str | Path,
        wc: WhisperClient = None,
        mode: Mode = Mode.full,
        timestamped: bool = False,
):
    if isinstance(audioPath, str):
        audioPath = Path(audioPath)
    if isinstance(textPath, str):
        textPath = Path(textPath)

    if isinstance(mode, str):
        mode = Mode(mode)

    if not audioPath.exists():
        print("The audio file does not exist")
        sys.exit(1)

    if textPath.exists():
        print("The text file already exists")

    if not wc:
        wc = WhisperClient(
            **config_data
        )

    response = wc.send_audio(audioPath)
    hash_ = response["hash"]

    wc.wait_for_result(hash_audio=hash_)

    res = wc.get_result_with_mode(
        mode=mode,
        hash_audio=hash_
    )

    with open(textPath, "w", encoding="utf-8") as f:
        if isinstance(res, dict):
            json.dump(res, f, indent=4)
        elif isinstance(res, str):
            f.write(res)
        else:
            raise TypeError(f"ERROR : invalid type for res : {type(res)}")


def toTextFolder(
        config_data: dict,
        audioPath: str | Path,
        textPath: str | Path,
        wc: WhisperClient = None,
        mode: Mode = Mode.full,
):
    if isinstance(audioPath, str):
        audioPath = Path(audioPath)
    if isinstance(textPath, str):
        textPath = Path(textPath)

    if isinstance(mode, str):
        mode = Mode(mode)

    if not audioPath.exists():
        print("The audio folder does not exist")
        sys.exit(1)

    textPath.mkdir(parents=True, exist_ok=True)

    if not wc:
        wc = WhisperClient(
            **config_data
        )

    audios = tqdm(list(file_finder(audioPath, file_type="audio")))
    for audio in audios:
        text = textPath / audio.with_suffix(".json").name \
            if mode != Mode.text else textPath / audio.with_suffix(".txt").name

        toText(config_data, audio, text, wc=wc, mode=mode)



def main(
        config_data: str | dict | Path,
        *args,
        videos: Video | list[Video] = None,
        audioPath: str | Path | list[str | Path] = None,
        textPath: str | Path | list[str | Path] = None,
        wc: WhisperClient = None,
        mode: Mode | str = Mode.full,
        folder: bool = False,
):
    if isinstance(config_data, str):
        config_data = Path(config_data)
    if isinstance(config_data, Path):
        assert config_data.exists(), f"ERROR : {config_data} does not exist"
        with config_data.open(mode="r", encoding="utf-8") as f:
            config_data = json.load(f)
    elif isinstance(config_data, dict):
        pass
    else:
        raise TypeError(f"ERROR : invalid type for config_data : {type(config_data)}")

    if isinstance(audioPath, str):
        audioPath = Path(audioPath)
    elif isinstance(audioPath, Path):
        pass
    elif isinstance(audioPath, list):
        audioPath = [Path(audio) for audio in audioPath]
    elif audioPath is None:
        assert videos is not None, "ERROR : videos is None and audioPath is None"
    else:
        raise TypeError(f"ERROR : invalid type for audioPath : {type(audioPath)}")

    if isinstance(textPath, str):
        textPath = Path(textPath)
        textPath.mkdir(parents=True, exist_ok=True)
    elif isinstance(textPath, Path):
        textPath.mkdir(parents=True, exist_ok=True)
    elif isinstance(textPath, list):
        textPath = [Path(text) for text in textPath]
    elif textPath is None:
        assert videos is not None, "ERROR : videos is None and textPath is None"
    else:
        raise TypeError(f"ERROR : invalid type for textPath : {type(textPath)}")

    # rm_tree(textPath)

    if isinstance(mode, str):
        mode = Mode(mode)

    if not wc:
        wc = WhisperClient(
            **config_data
        )

    if videos:
        for video in videos:
            toText(config_data, video.audio, video.json_or_text, wc=wc, mode=mode)
    elif isinstance(audioPath, list):
        assert isinstance(textPath, list), "ERROR : audioPath is a list but textPath is not"
        for audio, text in zip(audioPath, textPath):
            toText(config_data, audio, text, wc=wc, mode=mode)
    elif folder:
        toTextFolder(config_data, audioPath, textPath, wc=wc, mode=mode)
    else:
        toText(config_data, audioPath, textPath, wc=wc, mode=mode)


if __name__ == "__main__":
    main(
        config_data,
        audioPath="/home/marceau/PycharmProjects/Pellipop/videos-collecte1/extracted_audio",
        textPath="/home/marceau/PycharmProjects/Pellipop/txt-collecte1",
        mode=Mode.text,
        folder=True
    )
