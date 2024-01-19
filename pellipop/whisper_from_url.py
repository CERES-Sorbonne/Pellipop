import json
from pathlib import Path
import requests

import validators


class URLImportError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class WhisperFromUrl:
    def __init__(self, url=None):
        self.url = None
        self.config = None
        self.valid = False

        if url is not None:
            self.set_url(url)

    def set_url(self, url: str):
        self.url = url
        self.valid = self.validate_url()

    def validate_url(self) -> bool:
        if not self.url.startswith("http"):
            if self.url.count(".") < 2:
                self.url = "www." + self.url
            self.url = "https://" + self.url
        else:
            if self.url.count(".") < 2:
                self.url = self.url.replace("https://", "https://www.")
                self.url = self.url.replace("http://", "http://www.")

        if validators.url(self.url):
            return True

        return False

    def pull_config(self) -> dict:
        try:
            r = requests.get(self.url)
            r.raise_for_status()
            self.config = r.json()
        except requests.exceptions.HTTPError as errh:
            raise URLImportError(f"Erreur HTTP : {errh}")
        except requests.exceptions.ConnectionError as errc:
            raise URLImportError(f"Erreur de connexion : {errc}")
        except requests.exceptions.Timeout as errt:
            raise URLImportError(f"Timeout : {errt}")
        except requests.exceptions.RequestException as err:
            raise URLImportError(f"Erreur : {err}")
        except json.decoder.JSONDecodeError as err:
            raise URLImportError(f"Erreur JSON : {err}")

        return self.config

    def write_config(self, file: str | Path = None) -> bool:
        if not self.config:
            print("Aucune configuration n'a été chargée")

        if file is None:
            file = Path.home() / ".whisperrc"

        if not isinstance(file, Path):
            file = Path(file)

        if file.exists():
            print(f"Le fichier {file} existe déjà")

        if file.is_dir() or (not file.is_file() and file.exists()):
            print(f"Le chemin {file} existe déjà et n'est pas un fichier")
            return False

        with file.open(mode="w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

        return True

    def read_config(self, file: str | Path = None) -> dict:
        if file is None:
            file = Path.home() / ".whisperrc"

        if not isinstance(file, Path):
            file = Path(file)

        if not file.exists():
            raise FileNotFoundError(f"Le fichier {file} n'existe pas")

        if file.is_dir():
            raise IsADirectoryError(f"{file} est un dossier")

        if not file.is_file():
            raise FileNotFoundError(f"{file} n'est pas un fichier")

        with file.open(mode="r", encoding="utf-8") as f:
            config = json.load(f)

        return config

    def import_and_set(self) -> bool:
        self.pull_config()
        return self.write_config()
