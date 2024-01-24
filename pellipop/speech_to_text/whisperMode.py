import json
import sys
from pathlib import Path

from tqdm.auto import tqdm
from whisper_client.main import WhisperClient, Mode


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

    if not textPath.exists():
        textPath.mkdir(parents=True)

    if not wc:
        wc = WhisperClient(
            **config_data
        )

    audios = tqdm(list(audioPath.glob("*.wav")))
    for audio in audios:
        text = textPath / audio.with_suffix(".json").name \
            if mode != Mode.text else textPath / audio.with_suffix(".txt").name

        toText(config_data, audio, text, wc=wc, mode=mode)


def main(
        config_data: str | dict | Path,
        audioPath: str | Path,
        textPath: str | Path,
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
    if isinstance(textPath, str):
        textPath = Path(textPath)

    if not audioPath.exists():
        try:
            audioPath.mkdir(parents=True)
        except:
            raise

    rm_tree(textPath)

    if isinstance(mode, str):
        mode = Mode(mode)

    if not wc:
        wc = WhisperClient(
            **config_data
        )

    if folder:
        toTextFolder(config_data, audioPath, textPath, wc=wc, mode=mode)
    else:
        toText(config_data, audioPath, textPath, wc=wc, mode=mode)


if __name__ == "__main__":
    main(
        config_data,
        "/home/marceau/PycharmProjects/Pellipop/videos-collecte1/extracted_audio",
        "/home/marceau/PycharmProjects/Pellipop/txt-collecte1",
        mode=Mode.text,
        folder=True
    )
