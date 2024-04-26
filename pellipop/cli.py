from argparse import ArgumentParser
from sys import argv

from pellipop.__about__ import __version__
from pellipop.path_fixer import Path

# Possibilité de paramétrage dans le terminal/l'invite de commandes
parser = ArgumentParser()
parser.add_argument(
    "--input", type=str,  # required=True,
    help="Dossier racine contenant les vidéos"
)
parser.add_argument(
    "--interval", type=int, default=5,
    help="Définition de l'intervalle de temps (en secondes) à laquelle réaliser des captures d'écran. Il faut simplement indiqué une valeur numérique."
)
parser.add_argument(
    "--output", type=str, default=Path.cwd(),  # required=True,
    help="Dossier de sortie pour les images extraites, les fichiers audio et le fichier CSV"
)
parser.add_argument(
    "--i-frame-mode", type=bool, default=True, nargs='?', const=True,
    help="Permet de supprimer les doublons d'images pour un même film en utilisant les images clés (keyframes)"
)
parser.add_argument(
    "--keep-audio", type=bool, default=False, nargs='?', const=True,
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
parser.add_argument(
    "-v", "--version", action="version", version=f"%(prog)s {__version__}"
)


def main() -> dict[str, Path | None]:
    args = parser.parse_args()

    if args.gui or len(argv) < 2:
        from pellipop.gui import main as gui
        return gui()

    input_folder = Path(args.input)
    if not input_folder.exists():
        raise FileNotFoundError(f"Le dossier {input_folder} n'existe pas !")

    if not input_folder.is_dir():
        raise NotADirectoryError(f"{input_folder} n'est pas un dossier !")

    if not input_folder.glob("*.mp4"):
        raise FileNotFoundError(f"Aucun fichier .mp4 trouvé dans {input_folder} !")

    if not args.output:
        raise FileNotFoundError("Le dossier de sortie n'a pas été spécifié !")

    assert args.interval or args.i_frame_mode, "Il faut spécifier un intervalle ou activer le mode i-frame"

    from pellipop.main import Pellipop

    pellipop = Pellipop(
        intervale=args.interval,
        input_folder=args.input,
        output_folder=args.output,
        i_frame_mode=(args.i_frame_mode and not args.interval),
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
