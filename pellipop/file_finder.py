from pathlib import Path
from typing import Generator, Optional, Set
from enum import Enum

video_formats = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg", ".3gp", ".3g2"}
image_formats = {".jpg"}
audio_formats = {".wav", ".aac", ".mp3"}
text_formats = {".txt"}
csv_formats = {".csv"}
json_formats = {".json"}

map_formats = {
    "video": video_formats,
    "image": image_formats,
    "audio": audio_formats,
    "text": text_formats,
    "csv": csv_formats,
    "json": json_formats,
}

class FileType(Enum):
    video = video_formats
    image = image_formats
    audio = audio_formats
    text = text_formats
    csv = csv_formats
    json = json_formats

def file_finder(
        path: str | Path,
        *args,
        deep: int = -1,
        file_type: FileType | str = FileType.video,
        only_stems: Optional[Set[str]] = None,
        **kwargs
) -> Generator[Path, None, None]:
    if isinstance(path, str):
        path = Path(path)
    elif not isinstance(path, Path):
        raise ValueError(f"ERROR : invalid path : {path}")

    if isinstance(deep, str):
        try:
            deep = int(deep)
        except ValueError:
            raise ValueError(f"ERROR : invalid deepness treshold : {deep}")
    elif not isinstance(deep, int):
        raise ValueError(f"ERROR : invalid deepness treshold : {deep}")


    if isinstance(file_type, FileType):
        pass
    elif isinstance(file_type, str):
        try:
            file_type = FileType[file_type]
        except KeyError:
            raise ValueError(f"ERROR : invalid format : {file_type}")
    else:
        raise ValueError(f"ERROR : invalid format : {file_type}")

    for file in path.glob("*"):
        if file.is_dir():
            if deep == -1:
                yield from file_finder(
                    file,
                    deep=deep,
                    file_type=file_type,
                    only_stems=only_stems
                )
            elif deep > 0:
                yield from file_finder(
                    file,
                    deep=deep - 1,
                    file_type=file_type,
                    only_stems=only_stems
                )
        elif file.suffix in file_type.value:
            if only_stems is not None:
                if file.stem in only_stems or any(file.stem.startswith(stem) for stem in only_stems):
                    yield file
            else:
                yield file


def how_many_files(path: str | Path, deep: int = -1, format: str = "video") -> int:
    return len(list(file_finder(path, deep, format)))


if __name__ == "__main__":
    path = Path("/home/marceau/Documents/Pellipop/image")
    print(how_many_files(path, format="image"))
    # print(list(file_finder(path)))

    path = Path("/home/marceau/Documents/Pellipop/audio")
    print(how_many_files(path, format="audio"))
    # print(list(file_finder(path)))

    path = Path("/home/marceau/Documents/Pellipop/text")
    print(how_many_files(path, format="json"))
    # print(list(file_finder(path)))

