import cv2
import os
import math
from PIL import Image
from imagehash import average_hash
import argparse
from moviepy.editor import VideoFileClip
from tqdm import tqdm

def delete_duplicates(input_path):
    all_hashs = set()
    to_delete = []
    for image in os.listdir(input_path):
        path = os.path.join(input_path, image)
        img = Image.open(path)
        ahash = average_hash(img)
        if ahash in all_hashs:
            to_delete.append(path)
        else:
            all_hashs.add(ahash)
    for path in to_delete:
        os.remove(path)
    print(f"Suppression de {len(to_delete)} doublons !")

def format_time(fps_inv, n):
    duree = int(n * fps_inv)
    heures = duree // 3600  # Nombre d'heures
    minutes = (duree % 3600) // 60  # Nombre de minutes
    secondes = (duree % 60)  # Nombre de secondes
    
    # Formater la durée en une chaîne de caractères dans le format "hh:mm:ss"
    return "{:02d}h_{:02d}m_{:02d}s.jpg".format(heures, minutes, secondes)

def save_frame_range_sec(video_path, duree, step_sec, output_folder):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"impossible de lire {video_path}")
        return
        
    digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fps_inv = 1 / fps

    sec = 0

    with tqdm(total=round(duree / step_sec), desc=f"Etat d'avancement de : {video_path}") as bar:
        while True:
            n = round(fps * sec)
            cap.set(cv2.CAP_PROP_POS_FRAMES, n)
            ret, frame = cap.read()
            file_name = os.path.join(output_folder, format_time(n, fps_inv))
            if ret:
                if not cv2.imwrite(file_name, frame):
                    print("error saving image")
            else:
                return
            bar.update(1)
            sec += step_sec


def main(intervalle_de_temps=5, input_folder=None, output_folder=None, remove_duplicates=False):
    #Inscription des vidéos à traiter dans une liste
    extensions = [".mov", ".avi", ".mp4", ".flv", ".wmv", ".webm", ".mkv", ".svf"]
    fichiers = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(tuple(extensions))]


    #Affichage des informations à l'utilisateur-trice
    print("\n*** Liste des vidéos à découper : ***\n")
    print(fichiers)
    print("\nVous souhaitez découpez " + str(len(fichiers)) + " vidéos. Chaque vidéo va être découpée en images fixes séparées les unes des autres de " + str(intervalle_de_temps) + " secondes.\n")

    #Programme de découpe
    for fichier in tqdm(fichiers, desc="Nombre de vidéos traitées"):
        input_file = os.path.join(input_folder, fichier)
        duree = int(VideoFileClip(input_file).duration) #calcul la durée de la vidéo pour la gestion de l'affichage de l'avancement du traitement pour chaque vidéo.
        
        output_path = os.path.join(output_folder, "output_pellipop", os.path.basename(fichier).split('.')[0].strip().replace(' ', '_'))
        os.makedirs(output_path, exist_ok=True)
        
        save_frame_range_sec(input_file, duree, intervalle_de_temps, output_path)

        if remove_duplicates:
            delete_duplicates(output_path)

    #Note : la valeur 500 (minutes)*60 (pour passer en secondes) est une valeur aléatoire, l'idée est juste de donnée une longueur max de film au-delà de laquelle on ne regarde pas. Mais si le film est plus court ça ne semble pas poser de soucis.

    print("Travail terminé !")

def start():
    #Possibilité de paramétrage dans le terminal/l'invite de commandes
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, help="Dossier racine contenant les vidéos", default=os.getcwd())
    parser.add_argument("--frequency", type=int, help="Définition de l'intervalle de temps (en secondes) à laquelle réaliser des captures d'écran. Il faut simplement indiqué une valeur numérique.", default=5)
    parser.add_argument("--output", type=str, help="Dossier de sortie pour les images extraites", default=os.getcwd())
    parser.add_argument("--remove_duplicates", type=bool, help="Permet de supprimer les doublons d'images pour un même film en utilisant l'algorithme average hash", default=False, nargs='?', const=True)
    args = parser.parse_args()

    main(input_folder=args.input, intervalle_de_temps=args.frequency, output_folder=args.output, remove_duplicates=args.remove_duplicates)

if __name__ == "__main__":
    start()