from sys import argv
from argparse import ArgumentParser

from pellipop.path_fixer import Path

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
    "--reduce", type=int, default=-1,
    help="Permet de réduire le nom des fichiers de sortie à un certain nombre de caractères du nom original"
         "(par défaut, -1 pour ne pas réduire)"
)
parser.add_argument(
    "--offset", type=int, default=0,
    help="Permet de décaler le début du nom des fichiers de sortie de n caractères"
         "(par défaut, 0 pour ne pas décaler)"
)
parser.add_argument(
    "--parents-in-name", type=int, default=0,
    help="Permet d'ajouter le nom des dossiers parents dans le nom des fichiers de sortie"
         ",séparés par des _ (par défaut, 0 pour ne pas ajouter)"
)
parser.add_argument(
    "-g", "--gui", type=bool, default=False, nargs='?', const=True,
    help="Permet d'utiliser l'interface graphique"
)

args = parser.parse_args()


def main(args=args):
    if args.gui or len(argv) < 2:
        from gui import main
        main()
        return

    from pellipop.main import Pellipop

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

        reduce=args.reduce,
        offset=args.offset,
        parents_in_name=args.parents_in_name
    )
    pellipop.launch()

    print("Pellipop a terminé son travail !")

    return pellipop.outputs


if __name__ == "__main__":
    main()
