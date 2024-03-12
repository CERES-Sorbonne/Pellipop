import json
import re
import subprocess
from math import ceil, floor
from typing import Optional

from tqdm.auto import tqdm

from pellipop.Video import Video
from pellipop.file_finder import file_finder, how_many_files
from pellipop.path_fixer import Path
from pellipop.speech_to_text import whisperMode  # , extractText

default_output_path = (Path.home() / "Documents" / "Pellipop").__str__()


class Pellipop:
    default_whisper_config = Path.home() / ".whisperrc"
    map_parts = {
        "audio_part": '-acodec copy -vn "$OUTPUT_FOLDER_AUDIO/$FILE_STEM.aac" ',
        "i-frame_part": "-skip_frame nokey ",
        "i-frame_part2": "-fps_mode vfr -frame_pts true ",
        "const_freq_part": "-r $FREQ ",
    }

    base = "ffmpeg -hide_banner -loglevel panic -nostdin -y "
    # base = "ffmpeg -hide_banner -nostdin -y -hwaccel cuda -hwaccel_output_format cuda "

    ## To get the fps of a video file (we now use the Video class) which is doing only one call to ffprobe
    # probe = "ffprobe -v panic -select_streams v:0 -show_entries stream=r_frame_rate -of default=noprint_wrappers=1:nokey=1 $INPUT_FILE"
    # def get_fps(self, video: str | Path) -> int:
    #     command_instance = self.probe.replace("$INPUT_FILE", str(video))
    #     # print(command_instance)
    #     result = subprocess.run(command_instance, shell=True, capture_output=True)
    #     # print(result)
    #     result = result.stdout.decode("utf-8").strip().split("/")
    #     if len(result) == 2:
    #         return int(result[0]) // int(result[1])
    #     elif len(result) == 1:
    #         return int(result[0])
    #     else:
    #         raise ValueError("La commande n'a pas retourné un résultat valide")

    # To parse frame numbers: 000000.jpg
    ending_digits = re.compile(r"\d+$")
    # To parse back times: 00h_00m_00s.jpg or 00h_00m_00s or 00h_00m_00s_to_
    ending_time = re.compile(r"(\d{2}h_\d{2}m_\d{2}s)(?:.jpg|_to_|$)")

    def __init__(
            self,
            *args,
            intervale: float,
            input_folder: str | Path,
            output_folder: str | Path = Path.home() / "Documents" / "Pellipop",
            delete_duplicates: bool = False,
            decouper: bool = True,
            retranscrire: bool = False,
            csv: bool = False,
            with_text: bool = False,
            only_text: bool = False,
            reduce: int = -1,
            offset: int = 0,
            parents_in_name: int = 0,

            on_progress: callable = None,  # TODO: Add a progress bar

            whisper_config: dict = None,
            keep_audio: bool = False,
    ):
        if args:
            raise

        self.intervale = intervale if intervale else 1
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.delete_duplicates = delete_duplicates
        self.decouper = decouper
        self.retranscrire = retranscrire
        self.csv = csv
        self.with_text = with_text and not only_text
        self.only_text = only_text

        self.whisper_config = whisper_config
        self.keep_audio = keep_audio

        self.completed = False
        self.outputs: dict[str, Optional[Path]] = {
            "audio": None,
            "text": None,
            "image": None,
            "image_no_duplicates": None,
            "csv": None,
        }

        self.fichiers = sorted(file_finder(self.input_folder), key=lambda x: x.name)
        self.fichiers_stems = {f.stem for f in self.fichiers}
        self.hm = len(self.fichiers)

        self.reduce = reduce
        self.offset = offset

        self.videos = [Video(f, reduce=reduce, offset=offset, parents_in_name=parents_in_name) for f in self.fichiers]

    def launch(self) -> Optional[Path]:
        exec_dir = Path(__file__).parent
        print(exec_dir)

        if not isinstance(self.input_folder, Path):
            self.input_folder = Path(self.input_folder)
        if not isinstance(self.output_folder, Path):
            self.output_folder = Path(self.output_folder)

        if not self.input_folder.exists():
            raise FileNotFoundError("Le dossier d'entrée n'existe pas")
        if not self.input_folder.is_dir():
            raise NotADirectoryError("Le chemin d'entrée n'est pas un dossier")
        if not self.output_folder.exists():
            print("Le dossier de sortie n'existe pas, il sera créé")
            self.output_folder.mkdir(parents=True)
        if self.output_folder.is_file():
            raise NotADirectoryError("Le chemin de sortie est un fichier")

        self.decouper_et_audio()

        if self.retranscrire:
            self.extract_text()

        if self.csv:
            print("Création du fichier CSV")
            self.create_csv()

        if self.with_text:
            self._with_text()

        if self.only_text:
            self._only_text()

        self.final_names()

        self.completed = True

        return self.outputs["csv"]

    def decouper_et_audio(
            self,
    ) -> tuple[Optional[Path], Optional[Path]]:
        self.outputs["image"] = self.output_folder / "image"
        self.outputs["image"].mkdir(parents=True, exist_ok=True)

        command = self.base
        frequence = 1 / self.intervale

        if self.decouper and self.delete_duplicates:
            command += self.map_parts["i-frame_part"]

        command += '-i "$VIDEO_PATH" '

        if self.decouper:
            if self.delete_duplicates:
                command += self.map_parts["i-frame_part2"]
            else:
                command += self.map_parts["const_freq_part"]

            command += '"$OUTPUT_FOLDER/$FILE_STEM_%d.jpg" '

        if self.retranscrire:
            self.outputs["audio"] = self.output_folder / "audio"
            self.outputs["audio"].mkdir(parents=True, exist_ok=True)
            command += self.map_parts["audio_part"]

        command = command.replace("$FREQ", str(frequence))

        for video in tqdm(self.videos, desc="Découpage des vidéos", unit=" vidéos", total=self.hm):
            fichier = video.path
            output_folder = self.outputs["image"] / fichier.stem.replace(' ', '_')
            video.image_folder = output_folder
            if output_folder.exists():
                for img in output_folder.iterdir():
                    img.unlink()
            else:
                output_folder.mkdir(parents=True, exist_ok=True)

            commmand_instance = (
                command
                .replace("$OUTPUT_FOLDER_AUDIO", str(self.outputs["audio"]))
                .replace("$OUTPUT_FOLDER", str(output_folder))
                .replace("$FILE_STEM", fichier.stem)
                .replace("$VIDEO_PATH", str(fichier))
            )

            subprocess.run(commmand_instance, shell=True)

            video.audio = self.outputs["audio"] / video.with_suffix(".aac").name if self.retranscrire else None

            if self.delete_duplicates:
                self.from_frame_to_time(video, video.fps)
            else:
                self.from_frame_to_time(video)

            self._from_time_to_timespan_folder(video)

        return self.outputs["image"], self.outputs["audio"]

    def from_frame_to_time(self, video: Video, fps: int = 0):
        lst_img = sorted(video.image_folder.glob("*.jpg"))

        if self.delete_duplicates:
            rename_func = self._ftt_no_duplicates
        else:
            rename_func = self._ftt_duplicates

        for img in lst_img:
            new_img = rename_func(img, fps)
            if new_img.exists():
                print(f"Collision détectée: {img.name} -> {new_img.name}")
                continue
            img.rename(new_img)
            pass

        video.images = sorted(video.image_folder.glob("*.jpg"))

    def _ftt_no_duplicates(self, img: Path, fps: int) -> Path:
        frame_number = int(self.ending_digits.findall(img.stem)[0])
        time = self.format_time(frame_number // fps)
        new_name = time.join(img.name.rsplit(str(frame_number), 1))
        return img.with_name(new_name)

    def _ftt_duplicates(self, img: Path, *args) -> Path:
        frame_number = int(self.ending_digits.findall(img.stem)[0])
        time = self.format_time(frame_number * self.intervale)
        new_name = time.join(img.name.rsplit(str(frame_number), 1))
        return img.with_name(new_name)

    def _from_time_to_timespan_folder(self, video: Video):
        imgs = video.images
        imgs += imgs[-1],  # Add the last image to the list to have a duration for the last image

        for i, img in enumerate(imgs[:-1]):
            next_img = imgs[i + 1]
            img.rename(img.parent / self.format_fime_span(img.name, next_img.name))

        video.images = sorted(video.image_folder.glob("*.jpg"))

    @staticmethod
    def format_time(frame: int) -> str:
        heures, reste = divmod(frame, 3600)
        minutes, secondes = divmod(reste, 60)
        return f'{heures:02d}h_{minutes:02d}m_{secondes:02d}s'

    def format_fime_span(self, start: str, end: str) -> str:
        time_start = self.ending_time.findall(start)[0]
        time_end = self.ending_time.findall(end)[0]
        timespan = f"{time_start}_to_{time_end}"
        return start.replace(time_start, timespan)

    @staticmethod
    def parse_back_time(time: str) -> int:
        heures, minutes, secondes = time.split("_")
        return int(heures[:-1]) * 3600 + int(minutes[:-1]) * 60 + int(secondes[:-1])

    def parse_back_timespan(self, timespan: str) -> tuple[int, int]:
        start, end = self.ending_time.findall(timespan)
        start, end = (start, end) if start < end else (end, start)  # Never know with regexes
        return self.parse_back_time(start), self.parse_back_time(end)

    def parse_back_timespan_file(self, timespan: str) -> tuple[int, int]:
        start, end = self.ending_time.findall(timespan)
        start, end = (start, end) if start < end else (end, start)  # Never know with regexes
        return self.parse_back_time(start), self.parse_back_time(end)

    @staticmethod
    def json_time_to_int(start: float, end: float) -> tuple[int, int]:
        return floor(start), ceil(end)

    def find_text(self, json_file: dict, start: int, end: int) -> str:
        return "\n\n".join(
            [x["text"].strip() for x in json_file["segments"] if start <= x["start"] <= end or start <= x["end"] <= end]
        )

    def get_reduced_prefix(self, prefix: str) -> str:
        if self.reduce != -1 or self.offset:
            offset = min(self.offset, len(prefix) - 1)
            reduce = max(self.reduce, len(prefix) - 1) if self.reduce != -1 else self.reduce
            prefix = prefix[offset:reduce]
        return prefix

    def extract_text(self) -> Optional[Path]:
        self.outputs["text"] = self.output_folder / "text"
        self.outputs["text"].mkdir(parents=True, exist_ok=True)

        for video in self.videos:
            video.json = self.outputs["text"] / video.with_suffix(".json").name

        print("Extraction du texte")
        if self.whisper_config is not None or self.default_whisper_config.exists():
            try:
                whisperMode.main(
                    self.whisper_config or self.default_whisper_config,
                    videos=self.videos,
                    mode="full",
                    folder=True,
                )
            except Exception as e:
                print(e)
                print("Erreur lors de l'extraction du texte avec Whisper")
                raise e
        else:
            raise FileNotFoundError("Aucun fichier de configuration Whisper passé en argument ou présent à "
                                    f"l'emplacement par défaut ({Path.home() / '.whisperrc'})")
        #         extractText.toTextFolder(self.outputs["audio"], self.outputs["text"])
        #
        # else:
        #     print("Aucun fichier de configuration Whisper passé en argument, "
        #           "extraction du texte avec Google Speech-to-Text")
        #     extractText.toTextFolder(self.outputs["audio"], self.outputs["text"])

        print("Extraction du texte terminée !")

        if not self.keep_audio:
            for video in self.videos:
                video.audio.unlink()
                video.audio = None
            self.outputs["audio"] = None

        return self.outputs["text"]

    def create_csv(self) -> Optional[Path]:
        csv = self.output_folder / "csv"
        csv.mkdir(parents=True, exist_ok=True)
        self.outputs["csv"] = csv

        if self.retranscrire:
            self._create_csv_with_text()
        else:
            self._create_csv_without_text()

        return csv

    def _create_csv_with_text(self):
        assert self.outputs["image"] is not None and self.outputs["text"] is not None, (
            "Erreur de découpage ou d'extraction de texte, "
            "cette méthode doit s'exécuter après le découpage et l'extraction de texte !"
        )
        for video in self.videos:
            video.csv = self.outputs["csv"] / video.with_suffix(".csv").name
            with video.csv.open(mode="w", encoding="utf-8") as f:
                json_file = json.loads(video.json.read_text(encoding="utf-8"))
                f.write("img,start,end,text\n")
                for img in video.images:
                    start, end = self.parse_back_timespan_file(img.stem)
                    text = self.find_text(json_file, start, end)
                    f.write(f'{img},{start},{end},"{text}"\n')

    def _create_csv_without_text(self):
        assert self.outputs["image"] is not None, (
            "Erreur de découpage, "
            "cette méthode doit s'exécuter après le découpage !"
        )
        for video in self.videos:
            video.csv = self.outputs["csv"] / video.with_suffix(".csv").name
            with video.csv.open(mode="w", encoding="utf-8") as f:
                f.write("img,start,end\n")
                for img in video.images:
                    start, end = self.parse_back_timespan_file(img.stem)
                    f.write(f'{img},{start},{end}\n')

    def _with_text(self):
        """Go from json to txt"""
        self._get_text(delete_json=False)

    def _only_text(self):
        """Go from json to txt and delete the jsons"""
        self._get_text(delete_json=True)

    def _get_text(self, delete_json: bool = False):
        if not self.outputs["text"]:
            return
        if not self.outputs["text"].exists():
            raise FileNotFoundError("Le dossier de sortie n'existe pas")
        if not self.outputs["text"].is_dir():
            raise NotADirectoryError("Le chemin de sortie n'est pas un dossier")

        for video in self.videos:
            if not video.json:
                continue
            video.text = video.json.with_suffix(".txt")

            with video.json.open(mode="r", encoding="utf-8") as f:
                data = json.load(f)

            with video.text.open(mode="w", encoding="utf-8") as f:
                f.write(data["text"])

            if delete_json:
                video.json.unlink()
                video.json = None

    def final_names(self):
        for video in self.videos:
            video.final_names()


if __name__ == "__main__":
    # testdir = "/home/marceau/PycharmProjects/tksel/videos-collecte1"
    testdir = "/home/marceau/Téléchargements/pelli/"
    print(how_many_files(testdir))

    p = Pellipop(
        intervale=4,
        input_folder=testdir,
        output_folder=default_output_path,
        delete_duplicates=True,
        decouper=True,
        retranscrire=True,
        csv=True,
        with_text=True,
        only_text=False,
        keep_audio=True,

        reduce=10,
        offset=5,
        parents_in_name=2,
    )
    p.launch()

    ## Csv only test
    # p.output_folder = Path("/home/marceau/Documents/Pellipop")
    # videos = list(file_finder(testdir, file_type="video"))
    # videos_stems = {v.stem for v in videos}
    # p.fichiers_stems = videos_stems
    #
    # p.outputs["image"] = Path("/home/marceau/Documents/Pellipop/image")
    # p.outputs["audio"] = Path("/home/marceau/Documents/Pellipop/audio")
    # p.outputs["text"] = Path("/home/marceau/Documents/Pellipop/text")
    #
    # a =list(file_finder(p.outputs["audio"], file_type="audio"))
    # b =list(file_finder(p.outputs["text"], file_type="json"))
    #
    # p.create_csv()

    print(p.outputs)
