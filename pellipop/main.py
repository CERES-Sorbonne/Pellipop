import json
import re
import subprocess
from pathlib import Path
from typing import Optional

from tqdm.auto import tqdm

from pellipop.fileFinder import file_finder, how_many_files
from pellipop.speech_to_text import extractText, whisperMode

default_output_path = (Path.home() / "Documents" / "Pellipop").__str__()


class Pellipop:
    default_whisper_config = Path.home() / ".whisperrc"
    video_formats = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg", ".3gp", ".3g2"}
    map_parts = {
        "audio_part": "-acodec copy -vn $OUTPUT_FOLDER_AUDIO/$FILE_STEM.aac ",
        "i-frame_part": "-skip_frame nokey ",
        "i-frame_part2": "-fps_mode vfr -frame_pts true ",
        "const_freq_part": "-r $FREQ ",
    }

    base = "ffmpeg -hide_banner -loglevel panic -nostdin -y "
    # base = "ffmpeg -hide_banner -nostdin -y "
    probe = "ffprobe -v panic -select_streams v:0 -show_entries stream=r_frame_rate -of default=noprint_wrappers=1:nokey=1 $INPUT_FILE"

    ending_digits = re.compile(r"\d+$")

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
            only_text: bool = False,

            on_progress: callable = None,

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
        self.hm = len(self.fichiers)

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

        if self.only_text:
            self._only_text()

        self.completed = True

        return self.outputs["csv"]

    @staticmethod
    def format_time(frame: int) -> str:
        heures, reste = divmod(frame, 3600)
        minutes, secondes = divmod(reste, 60)
        return f'{heures:02d}h_{minutes:02d}m_{secondes:02d}s'

    @staticmethod
    def format_fime_span(start: str, end: str) -> str:
        return f"{start}TO{end}.jpg"

    def extract_text(self) -> Optional[Path]:
        self.outputs["text"] = self.output_folder / "text"
        self.outputs["text"].mkdir(parents=True, exist_ok=True)

        print("Extraction du texte")
        if self.whisper_config is not None or self.default_whisper_config.exists():
            try:
                whisperMode.main(
                    self.whisper_config or self.default_whisper_config,
                    self.outputs["audio"],
                    self.outputs["text"],
                    mode="full",
                    folder=True,
                )
            except Exception as e:
                print(e)
                print("Erreur lors de l'extraction du texte avec Whisper")
                extractText.toTextFolder(self.outputs["audio"], self.outputs["text"])

        else:
            print("Aucun fichier de configuration Whisper passé en argument, "
                  "extraction du texte avec Google Speech-to-Text")
            extractText.toTextFolder(self.outputs["audio"], self.outputs["text"])

        print("Extraction du texte terminée !")

        if not self.keep_audio:
            for audio in self.outputs["audio"].glob("*"):
                audio.unlink()
            self.outputs["audio"].rmdir()
        else:
            self.outputs["audio"] = None

        return self.outputs["text"]

    def _only_text(self):
        """Go from json to txt"""
        if not self.outputs["text"]:
            return
        if not self.outputs["text"].exists():
            raise FileNotFoundError("Le dossier de sortie n'existe pas")
        if not self.outputs["text"].is_dir():
            raise NotADirectoryError("Le chemin de sortie n'est pas un dossier")

        jsons = list(file_finder(self.outputs["text"], format="json"))

        for json_file in tqdm(jsons, desc="Conversion des fichiers json en txt", unit="fichier", total=len(jsons)):
            with json_file.open(mode="r", encoding="utf-8") as f:
                data = json.load(f)

            with json_file.with_suffix(".txt").open(mode="w", encoding="utf-8") as f:
                f.write(data["text"])

            json_file.unlink()

    def create_csv(self):
        pass

    def decouper_et_audio(
            self,
    ):
        self.outputs["image"] = self.output_folder / "image"
        self.outputs["image"].mkdir(parents=True, exist_ok=True)

        command = self.base
        frequence = 1 / self.intervale

        if self.decouper and self.delete_duplicates:
            command += self.map_parts["i-frame_part"]

        command += "-i $VIDEO_PATH "

        if self.decouper:
            if self.delete_duplicates:
                command += self.map_parts["i-frame_part2"]
            else:
                command += self.map_parts["const_freq_part"]

            command += "$OUTPUT_FOLDER/$FILE_STEM_%d.jpg "

        if self.retranscrire:
            self.outputs["audio"] = self.output_folder / "audio"
            self.outputs["audio"].mkdir(parents=True, exist_ok=True)
            command += self.map_parts["audio_part"]

        command = command.replace("$FREQ", str(frequence))

        for fichier in tqdm(self.fichiers, desc="Découpage des vidéos", unit=" videos", total=self.hm):
            output_folder = self.outputs["image"] / fichier.stem.replace(' ', '_')
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

            # print(commmand_instance)
            subprocess.run(commmand_instance, shell=True)

            if self.delete_duplicates:
                fps = self.get_fps(fichier)
                self.from_frame_to_time(fichier.stem, fps)
            else:
                self.from_frame_to_time(fichier.stem)

        return self.outputs["image"], self.outputs["audio"]

    def get_fps(self, video: str | Path) -> int:
        command_instance = self.probe.replace("$INPUT_FILE", str(video))
        # print(command_instance)
        result = subprocess.run(command_instance, shell=True, capture_output=True)
        # print(result)
        result = result.stdout.decode("utf-8").strip().split("/")
        if len(result) == 2:
            return int(result[0]) // int(result[1])
        elif len(result) == 1:
            return int(result[0])
        else:
            raise ValueError("La commande n'a pas retourné un résultat valide")

    def from_frame_to_time(self, video_stem: str, fps: int = 0):
        lst_img = sorted((self.outputs["image"] / video_stem).glob("*.jpg"))

        if self.delete_duplicates:
            rename_func = self._ftt_no_duplicates
        else:
            rename_func = self._ftt_duplicates

        for img in lst_img:
            new_img = rename_func(img, fps)
            if new_img.exists():
                print(f"Collision détectée: {img.name} -> {new_img.name}")
            img.rename(new_img)
            pass

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


if __name__ == "__main__":
    testdir = "/home/marceau/PycharmProjects/tksel/videos-collecte1"

    print(how_many_files(testdir))

    p = Pellipop(
        intervale=4,
        input_folder=testdir,
        output_folder=default_output_path,
        delete_duplicates=True,
        decouper=True,
        retranscrire=True,
        csv=True,
        only_text=True,
        keep_audio=True,
    )
    p.launch()
    print(p.outputs)
