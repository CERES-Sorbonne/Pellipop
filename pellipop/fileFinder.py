from pathlib import Path
from typing import Generator

video_formats = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg", ".3gp", ".3g2"}
image_formats = {".jpg"}
audio_formats = {".wav"}
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

def file_finder(
        path: str | Path,
        deep: int = -1,
        format: str = "video",
) -> Generator[Path, None, None]:
    if isinstance(path, str):
        path = Path(path)

    if format not in map_formats:
        raise ValueError(f"ERROR : invalid format : {format}")
    else:
        format = map_formats[format]

    for file in path.glob("*"):
        if file.is_dir():
            if deep == -1:
                yield from file_finder(file)
            elif deep > 0:
                yield from file_finder(file, deep - 1)

        elif file.suffix in format:
            yield file


def how_many_files(path: str | Path, deep: int = -1) -> int:
    return len(list(file_finder(path, deep)))

