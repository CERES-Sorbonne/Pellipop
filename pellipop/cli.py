from argparse import ArgumentParser
from pathlib import Path

from pellipop.main import Pellipop

# Possibilité de paramétrage dans le terminal/l'invite de commandes
parser = ArgumentParser()
parser.add_argument(
    "--input", type=str, required=True,
    help="Dossier racine contenant les vidéos"
)
parser.add_argument(
    "--frequency", type=int, default=5,
    help="Définition de l'intervalle de temps (en secondes) à laquelle réaliser des captures d'écran. Il faut simplement indiqué une valeur numérique."
)
parser.add_argument(
    "--output", type=str, required=True, default=Path.cwd(),
    help="Dossier de sortie pour les images extraites, les fichiers audio et le fichier CSV"
)
parser.add_argument(
    "--remove_duplicates", type=bool, default=False, nargs='?', const=True,
    help="Permet de supprimer les doublons d'images pour un même film en utilisant l'algorithme average hash"
)
parser.add_argument(
    "--keep_audio", type=bool, default=False, nargs='?', const=True,
    help="Permet de garder les fichiers audio extraits des vidéos"
)
parser.add_argument(
    "--whisper-config", type=str, default=Path.cwd() / "whisper_config.json",
    help="Chemin vers le fichier de configuration de l'API Whisper"
)
parser.add_argument(
    "--frames-only", type=bool, default=False, nargs='?', const=True,
    help="Permet de ne pas extraire le texte des vidéos"
)
parser.add_argument(
    "--hamming", type=int, default=10,
    help="Distance de Hamming pour l'algorithme de comparaison de hash"
)

parser.add_argument(
    "-g", "--gui", type=bool, default=False, nargs='?', const=True,
    help="Permet d'utiliser l'interface graphique"
)

args = parser.parse_args()


def main(args=args):
    if args.gui:
        from gui import main
        main()
        return

    pellipop = Pellipop(
        intervale=args.frequency,
        input_folder=args.input,
        output_folder=args.output,
        delete_duplicates=args.remove_duplicates,
        decouper=not args.frames_only,
        retranscrire=not args.frames_only,
        csv=not args.frames_only,

        whisper_config=args.whisper_config,
        keep_audio=args.keep_audio,
        hamming=args.hamming
    )
    pellipop.launch()

    print("Pellipop a terminé son travail !")

    return pellipop.outputs


if __name__ == "__main__":
    main()
