import json
import subprocess
from pathlib import Path
from typing import List, Optional


class Video:
    probe = "ffprobe -v panic -show_streams -of json"  # Using ffmpeg to get video infos

    def __init__(
            self,
            path: Path,
            reduce: int = -1,
            offset: int = 0,
            parents_in_name: int = 0
    ):
        assert isinstance(path, Path), f"{path} is not a Path object"
        assert path.is_file(), f"{path} is not a file"
        assert path.exists(), f"{path} does not exist"

        assert isinstance(reduce, int), f"{reduce} is not an int"
        assert reduce >= -1, f"{reduce} is not a valid reduce value"

        assert isinstance(offset, int), f"{offset} is not an int"
        assert offset >= 0, f"{offset} is not a valid offset value"

        self.path: Path = path

        self.reduce: int = reduce
        self.offset: int = offset
        self.final_stem: Optional[str] = None
        self.get_reduce()
        self.parents_in_name: int = parents_in_name
        self.get_parents()

        self.images: List[Path] = []
        self.image_folder: Optional[Path] = None
        self.audio: Optional[Path] = None
        self.json: Optional[Path] = None
        self.text: Optional[Path] = None
        self.csv: Optional[Path] = None

        self.length: Optional[int] = None
        self.width: Optional[int] = None
        self.height: Optional[int] = None
        self.fps: Optional[int] = None
        self.channels: Optional[int] = None
        self.rate: Optional[int] = None

        self.get_info()

    @property
    def name(self) -> str:
        return self.path.name

    @name.setter
    def name(self, value) -> None:
        self.path = self.path.with_name(value)

    @property
    def stem(self) -> str:
        return self.path.stem

    @stem.setter
    def stem(self, value) -> None:
        self.path = self.path.with_stem(value)

    @property
    def json_or_text(self) -> Path:
        return self.json or self.text

    def with_suffix(self, *args, **kwargs) -> Path:
        return self.path.with_suffix(*args, **kwargs)

    def get_reduce(self) -> None:
        if self.reduce != -1 or self.offset:
            offset = min(self.offset, len(self.stem) - 1)
            reduce = min(self.reduce + offset, len(self.stem) - 1) if self.reduce != -1 else -1
            self.final_stem = self.stem[offset:reduce]

    def get_parents(self) -> None:
        if not self.parents_in_name:
            return

        parents = [e.name for e in self.path.parents if e.name not in [".", "..", "", "C:", "D:", "E:"]]
        parents = parents[:min(self.parents_in_name, len(parents))][::-1]
        self.final_stem = "_".join([p for p in parents] + [self.final_stem])

    def get_info(self) -> None:
        command = f"{self.probe} {self.path}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        data = json.loads(result.stdout)

        video = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
        audio = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
        # text = next((s for s in data["streams"] if s["codec_type"] == "subtitle"), None)

        self.length = float(video["duration"])
        self.width = int(video["width"])
        self.height = int(video["height"])
        self.fps = int(video["r_frame_rate"].split("/")[0]) // int(video["r_frame_rate"].split("/")[1])
        self.channels = int(audio["channels"])
        self.rate = int(audio["sample_rate"])

    def rename_to_final(
            self,
            path: Path,
            old_folder: Optional[Path] = None,
            new_folder: Optional[Path] = None
    ) -> Path:
        if not self.final_stem:
            return path
        path = path.rename(path.with_stem(path.stem.replace(self.stem, self.final_stem)))
        if old_folder and new_folder:
            path = path.rename(new_folder / path.name)
        return path

    def rename_to_final_images(self) -> None:
        if not self.final_stem:
            return

        old_folder = self.image_folder

        self.image_folder = self.image_folder.parent / self.final_stem.replace(" ", "_")
        self.image_folder.mkdir(parents=True, exist_ok=True)
        self.images = [
            self.rename_to_final(img, old_folder=old_folder, new_folder=self.image_folder)
            for img in self.images
        ]

        old_folder.rmdir()

    def final_names(self) -> None:
        if self.images:
            self.rename_to_final_images()

        if self.audio:
            self.audio = self.rename_to_final(self.audio)

        if self.json:
            self.json = self.rename_to_final(self.json)

        if self.text:
            self.text = self.rename_to_final(self.text)

        if self.csv:
            self.csv = self.rename_to_final(self.csv)


if __name__ == "__main__":
    testfile = "/home/marceau/Téléchargements/pelli/Aladdin.1992.REPACK.1080p.BluRay.x264.AAC5.1-[YTS.MX].mp4"

    video = Video(Path(testfile))
    print(video.path, video.name, video.stem, video.reduce, video.offset)
    print(video.length, video.width, video.height, video.fps, video.channels, video.rate)
    print(video.images, video.audio, video.text)
    pass
