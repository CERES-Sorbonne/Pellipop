import json
from pathlib import Path
from threading import Thread
from typing import Optional

import cv2
from PIL import Image
from imagehash import dhash  # ,average_hash, phash, colorhash, whash
from tqdm.auto import tqdm

from pellipop.fileFinder import file_finder, how_many_files
from pellipop.speech_to_text import extractText, extractAudio, whisperMode

default_output_path = (Path.home() / "Documents" / "Pellipop").__str__()


class Pellipop:
    default_whisper_config = Path.home() / ".whisperrc"
    video_formats = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg", ".3gp", ".3g2"}

    def __init__(
            self,
            *args,
            intervale: float,
            input_folder: str | Path,
            output_folder: str | Path = Path.home() / "Documents" / "Pellipop",
            delete_duplicates: bool = False,
            decouper: bool = False,
            retranscrire: bool = False,
            csv: bool = False,
            only_text: bool = False,

            on_progress: callable = None,

            whisper_config: dict = None,
            keep_audio: bool = False,
            hamming: int = 10,
    ):
        if args:
            raise

        self.t1 = None
        self.t2 = None

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
        self.hamming = hamming

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

        if self.retranscrire:
            if self.whisper_config is None:
                self.whisper_config = exec_dir / "whisper_config.json"
            else:
                self.whisper_config = Path(self.whisper_config)

            if not self.whisper_config.exists():
                print("Le fichier de configuration de l'API Whisper n'a pas été trouvé")
                self.whisper_config = None

            if self.decouper:
                self.t1 = Thread(target=self.extract_audio_then_text)
                self.t1.start()
            else:
                self.extract_audio_then_text()  # (input_folder, output_folder, audio, whisper_config)

        if self.decouper:
            if self.retranscrire:
                self.t2 = Thread(target=self.decouper_video)
                self.t2.start()

            else:
                self.decouper_video()  # (freq, input_folder, output_folder, delete_duplicates)

        # Wait for threads to finish (needed for the csv creation and the only_text conversion to work)
        if self.t1 is not None:
            self.t1.join()
        if self.t2 is not None:
            self.t2.join()

        if self.csv:
            print("Création du fichier CSV")
            self.create_csv()

        if self.only_text:
            self._only_text()

        self.completed = True

        return self.outputs["csv"]

    def del_duplicates_to_new_folder(self, input_path: str | Path) -> Optional[Path]:
        if not self.outputs["image_no_duplicates"]:
            raise FileNotFoundError("Le dossier de sortie n'est pas défini")
        if not self.outputs["image_no_duplicates"].exists():
            raise FileNotFoundError("Le dossier de sortie n'existe pas")
        if not self.outputs["image_no_duplicates"].is_dir():
            raise NotADirectoryError("Le chemin de sortie n'est pas un dossier")

        folder = self.outputs["image_no_duplicates"] / input_path.name
        if folder.exists():
            for image in folder.glob("*"):
                image.unlink()
        else:
            folder.mkdir(parents=True, exist_ok=True)

        actual_hash = None

        for image in tqdm(sorted(file_finder(input_path, format="image")),
                          desc="Suppression des doublons", unit="image"):
            img = Image.open(image)
            ahash = dhash(img)

            # If the hash is None, we're supposed to be at the first iteration
            # Then, we check for the hammering distance between the last saved hash and the current one
            # If the distance is too small, we skip the image
            # Else, we save the image and update the last saved hash with the current one
            if actual_hash is None:
                # print(ahash)
                pass
            elif ahash - actual_hash > self.hamming:
                pass
            else:
                continue  # Skip the image if the hammering distance is too small or if the hash is None

            actual_hash = ahash
            img.save(folder / image.name)

    @staticmethod
    def format_time(frame: int, fps: int) -> str:
        heures, reste = divmod(frame // fps, 3600)
        minutes, secondes = divmod(reste, 60)
        return f'{heures:02d}h_{minutes:02d}m_{secondes:02d}s.jpg'

    @staticmethod
    def format_fime_span(start: str, end: str) -> str:
        return f"{start}TO{end}.jpg"

    def save_frame_range_sec(self, video_path, output_folder):
        video = cv2.VideoCapture(video_path.__str__())

        if not video.isOpened():
            print(f"impossible de lire {video_path}")
            return

        fps = int(video.get(5))  # CAP_PROP_FPS
        frame_count = int(video.get(7))  # CAP_PROP_FRAME_COUNT

        freq = fps * self.intervale

        print()
        print(f"fps : {fps}")
        print(f"frame_count : {frame_count}")
        print(f"image par seconde : {self.intervale}")
        print(f"freq : {freq}")

        pbar = tqdm(
            range(0, frame_count, int(freq)),
            desc=f"Etat d'avancement de : {video_path.name}",
            unit="frame",
            leave=False
        )

        for i in pbar:
            video.set(1, i)  # CAP_PROP_POS_FRAMES

            ret, frame = video.read()
            file_name = output_folder / self.format_time(i, fps)
            if ret:
                if not cv2.imwrite(str(file_name), frame):
                    print("error saving image")
            else:
                break

        video.release()

    def decouper_video(self) -> Optional[Path]:
        print("Découpage des vidéos")
        self.outputs["image"] = self.output_folder / "image"

        if self.delete_duplicates:
            self.outputs["image_no_duplicates"] = self.output_folder / "image_no_duplicates"
            self.outputs["image_no_duplicates"].mkdir(parents=True, exist_ok=True)

        for fichier in tqdm(self.fichiers, desc="Découpage des vidéos", unit=" videos", total=self.hm):
            output_folder = self.outputs["image"] / fichier.stem.replace(' ', '_')
            output_folder.mkdir(parents=True, exist_ok=True)

            self.save_frame_range_sec(fichier, output_folder)

            if self.delete_duplicates:
                self.del_duplicates_to_new_folder(output_folder)

        print("Découpage terminé !")
        return self.outputs["image"]

    def extract_audio_then_text(self) -> Optional[Path]:
        self.outputs["audio"] = self.output_folder / "audio"
        self.outputs["audio"].mkdir(parents=True, exist_ok=True)
        self.outputs["text"] = self.output_folder / "text"
        self.outputs["text"].mkdir(parents=True, exist_ok=True)

        print("Extraction de l'audio")

        extractAudio.toAudioFolder(self.input_folder, self.outputs["audio"])

        print("Extraction de l'audio terminée !")

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


if __name__ == "__main__":
    testdir = "/home/marceau/PycharmProjects/Pellipop/"

    print(how_many_files(testdir))
