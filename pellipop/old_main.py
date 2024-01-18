from threading import Thread

import cv2
import os
from pathlib import Path
# from datetime import time

from PIL import Image
from imagehash import average_hash
import argparse
# from moviepy.editor import VideoFileClip
from tqdm.auto import tqdm

from pellipop.speech_to_text import extractText, extractAudio, whisperMode

extensions = (".mov", ".avi", ".mp4", ".flv", ".wmv", ".webm", ".mkv", ".svf")

def delete_duplicates(input_path):
    all_hashs = set()
    to_delete = []
    for image in input_path.glob("*"):
        # path = os.path.join(input_path, image)
        img = Image.open(image)
        ahash = average_hash(img)
        if ahash in all_hashs:
            to_delete.append(image)
        else:
            all_hashs.add(ahash)
    for path in to_delete:
        # os.remove(path)
        path.unlink()
    print(f"Suppression de {len(to_delete)} doublons !")

def format_time(frame: int, fps: int) -> str:
    ## Non optimisé
    # duree = int(frame / fps)
    # heures, reste = divmod(duree, 3600)
    # minutes, secondes = divmod(reste, 60)
    # return time(heures, minutes, secondes).strftime("%Hh_%Mm_%Ss.jpg")
    ## Optimisé
    heures, reste = divmod(frame, 3600 * fps)
    minutes, secondes = divmod(reste, 60)
    return f'{heures:02d}h_{minutes:02d}m_{secondes:02d}s.jpg'

def save_frame_range_sec(video_path, step_sec, output_folder):
    video = cv2.VideoCapture(video_path.__str__())

    if not video.isOpened():
        print(f"impossible de lire {video_path}")
        return
        
    fps = video.get(5)  # CAP_PROP_FPS
    frame_count = video.get(7)  # CAP_PROP_FRAME_COUNT

    frame_count = int(frame_count)
    fps = int(fps)

    freq = step_sec / fps

    pbar = tqdm(
        range(0, frame_count, int(fps / freq)),
        desc=f"Etat d'avancement de : {video_path.name}",
        unit="frame",
        leave=False
    )

    # with tqdm(total=round(duree / step_sec), desc=f"Etat d'avancement de : {video_path}") as bar:
    for i in pbar:
        video.set(1, i) # CAP_PROP_POS_FRAMES

        ret, frame = video.read()
        # file_name = os.path.join(output_folder, format_time(n, fps_inv))
        file_name = output_folder / format_time(i, fps)
        if ret:  #  is True différent de == True >
            if not cv2.imwrite(str(file_name), frame):
                print("error saving image")
        else:
            break

    video.release()

def main(intervalle_de_temps=5, input_folder=None, output_folder=None, remove_duplicates=False):
    #Inscription des vidéos à traiter dans une liste
    # fichiers = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(tuple(extensions))]
    fichiers = input_folder.glob("*")
    fichiers = [f for f in fichiers if f.suffix in extensions]

    #Affichage des informations à l'utilisateur-trice
    print("\n*** Liste des vidéos à découper : ***\n")
    print([f.name for f in fichiers])
    print(f"\nVous souhaitez découper {len(fichiers)} vidéos. Chaque vidéo va être découpée en images fixes séparées \
    les unes des autres de {intervalle_de_temps} secondes.\n")

    #Programme de découpe
    for fichier in tqdm(fichiers, desc="Nombre de vidéos traitées"):
        # duree = int(VideoFileClip(str(fichier)).duration) #calcul la durée de la vidéo pour la gestion de l'affichage de l'avancement du traitement pour chaque vidéo.
        
        # output_path = os.path.join(output_folder, "output_pellipop", os.path.basename(fichier).split('.')[0].strip().replace(' ', '_'))
        output_path = output_folder / "output_pellipop" / f"{fichier.stem.replace(' ', '_')}"
        # os.makedirs(output_path, exist_ok=True)
        output_path.mkdir(parents=True, exist_ok=True)
        
        save_frame_range_sec(fichier, intervalle_de_temps, output_path)

        if remove_duplicates:
            delete_duplicates(output_path)

    #Note : la valeur 500 (minutes)*60 (pour passer en secondes) est une valeur aléatoire, l'idée est juste de donnée une longueur max de film au-delà de laquelle on ne regarde pas. Mais si le film est plus court ça ne semble pas poser de soucis.

    print("Découpe des vidéos en images terminée !")

def extract_audio_then_text(
        input_folder,
        output_folder,
        keep_audio=False,
        whisper_config=None,
        whisper_mode="full",
        whisper_timestamped=False,
        # whisper_output=None
):
    output_folder_audio = output_folder / "output_audio"
    output_folder_audio.mkdir(parents=True, exist_ok=True)

    output_folder_text = output_folder / "output_text"
    output_folder_text.mkdir(exist_ok=True)

    extractAudio.toAudioFolder(input_folder, output_folder_audio)
    print("Extraction des fichiers audio terminée !")

    if whisper_config is not None:
        try:
            whisperMode.main(
                whisper_config,
                output_folder_audio,
                output_folder_text,
                mode=whisper_mode,
                folder=True,
                timestamped=whisper_timestamped,
            )
        except Exception as e:
            print(e)
            print("Erreur lors de l'extraction du texte avec Whisper")
            extractText.toTextFolder(output_folder_audio, output_folder_text)
    else:
        extractText.toTextFolder(output_folder_audio, output_folder_text)

    if not keep_audio:
        for audio in output_folder_audio.glob("*"):
            audio.unlink()
        output_folder_audio.rmdir()

    print("Extraction du texte terminée !")


def pied(
        intervalle_de_temps=5,
        input_folder=None,
        output_folder=None,
        remove_duplicates=False,
        keep_audio=False,
        whisper_config=None,
        whisper_mode="full",
        decouper=True,
        retranscrire=False,
        csv=False,
        # whisper_output=None
):
    exec_dir = Path(__file__).parent
    print(exec_dir)

    if not isinstance(input_folder, Path):
        input_folder = Path(input_folder)

    if not isinstance(output_folder, Path):
        output_folder = Path(output_folder)

    if not input_folder.exists():
        raise FileNotFoundError("Le dossier d'entrée n'existe pas")

    if not frames_only:
        if whisper_config is None:
            whisper_config = exec_dir / "whisper_config.json"
        else:
            whisper_config = Path(whisper_config)

        if not whisper_config.exists():
            print("Le fichier de configuration de l'API Whisper n'a pas été trouvé")
            whisper_config = None

        if decouper:
            t1 = Thread(target=extract_audio_then_text, args=(input_folder, output_folder, keep_audio, whisper_config, whisper_mode))
            t1.start()
        else:
            extract_audio_then_text(input_folder, output_folder, keep_audio, whisper_config, whisper_mode, whisper_timestamped)

    if decouper:
        if retranscrire:
            t2 = Thread(target=main, args=(intervalle_de_temps, input_folder, output_folder, remove_duplicates))
            t2.start()

        else:
            main(intervalle_de_temps, input_folder, output_folder, remove_duplicates)

    if csv:
        print("Création du fichier CSV")



def start():
    #Possibilité de paramétrage dans le terminal/l'invite de commandes
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, help="Dossier racine contenant les vidéos", default=os.getcwd())
    parser.add_argument("--frequency", type=int, help="Définition de l'intervalle de temps (en secondes) à laquelle réaliser des captures d'écran. Il faut simplement indiqué une valeur numérique.", default=5)
    parser.add_argument("--output", type=str, help="Dossier de sortie pour les images extraites", default=os.getcwd())
    parser.add_argument("--remove_duplicates", type=bool, help="Permet de supprimer les doublons d'images pour un même film en utilisant l'algorithme average hash", default=False, nargs='?', const=True)
    parser.add_argument("--keep_audio", type=bool, help="Permet de garder les fichiers audio extraits des vidéos", default=False, nargs='?', const=True)
    parser.add_argument("--whisper-config", type=str, help="Chemin vers le fichier de configuration de l'API Whisper", default=os.path.join(os.getcwd(), "whisper_config.json"))
    parser.add_argument("--frames-only", type=bool, help="Permet de ne pas extraire le texte des vidéos", default=False, nargs='?', const=True)
    # parser.add_argument("--whisper-output", type=str, help="Dossier de sortie pour les fichiers de l'API Whisper", default=os.path.join(os.getcwd(), "output_whisper"))
    args = parser.parse_args()

    pied(
        intervalle_de_temps=args.frequency,
        input_folder=args.input,
        output_folder=args.output,
        remove_duplicates=args.remove_duplicates,
        keep_audio=args.keep_audio,
        whisper_config=args.whisper_config,
        # whisper_output=args.whisper_output
    )

if __name__ == "__main__":
    start()
