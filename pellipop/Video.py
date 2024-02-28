import json
import subprocess
from pathlib import Path


class Video:
    probe = "ffprobe -v panic -show_streams -of json"

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

        self.path = path

        self.reduce = reduce
        self.offset = offset
        self.final_stem = None
        self.get_reduce()
        self.parents_in_name = parents_in_name
        self.get_parents()

        self.images = []
        self.audio = None
        self.json = None
        self.text = None
        self.csv = None

        self.length = None
        self.width = None
        self.height = None
        self.fps = None
        self.channels = None
        self.rate = None

        self.get_info()

    @property
    def name(self):
        return self.path.name

    @name.setter
    def name(self, value):
        self.path = self.path.with_name(value)

    @property
    def stem(self):
        return self.path.stem

    @stem.setter
    def stem(self, value):
        self.path = self.path.with_stem(value)

    def with_suffix(self, *args, **kwargs):
        return self.path.with_suffix(*args, **kwargs)

    def get_reduce(self):
        if self.reduce != -1 or self.offset:
            offset = min(self.offset, len(self.stem) - 1)
            reduce = min(self.reduce + offset, len(self.stem) - 1) if self.reduce != -1 else -1
            self.final_stem = self.stem[offset:reduce]

    def get_parents(self):
        if not self.parents_in_name:
            return

        parents = [e.name for e in self.path.parents if e.name not in [".", "..", "", "C:", "D:", "E:"]]
        parents = parents[:min(self.parents_in_name, len(parents))][::-1]
        self.final_stem = "_".join([p for p in parents] + [self.final_stem])

    def get_info(self):
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

    def do_reduce(self, path: Path) -> Path:
        if not self.final_stem:
            return path
        return path.rename(path.with_stem(path.stem.replace(self.stem, self.final_stem)))

    def reduce_all(self):
        self.images = [self.do_reduce(img) for img in self.images]

        if self.audio:
            self.audio = self.do_reduce(self.audio)

        if self.text:
            self.text = self.do_reduce(self.text)

        if self.csv:
            self.csv = self.do_reduce(self.csv)


if __name__ == "__main__":
    testfile = "/home/marceau/Téléchargements/pelli/Aladdin.1992.REPACK.1080p.BluRay.x264.AAC5.1-[YTS.MX].mp4"

    video = Video(Path(testfile))
    print(video.path, video.name, video.stem, video.reduce, video.offset)
    print(video.length, video.width, video.height, video.fps, video.channels, video.rate)
    print(video.images, video.audio, video.text)
    pass
