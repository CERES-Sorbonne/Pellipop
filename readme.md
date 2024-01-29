# Pellipop

## Installation

`pip install pellipop`

## Usage

Pellipop est un outil en ligne de commande Python qui permet de découper des vidéos en images fixes.
Par défaut, des captures d'écran sont réalisées toutes les 5 secondes.

Il prend en entrée les formats suivants:
- `".mov"`
- `".avi"`
- `".mp4"`
- `".flv"`
- `".wmv"`
- `".webm"`
- `".mkv"`
- `".svf"`

Il se lance avec `pellipop` dans un terminal, par défaut les vidéos sont cherchées dans le dossier où la commande est lancée, et les images créées sont également stockées au même endroit. Les paramètres peuvent toutefois être changés:

- `--input` : pour spécifier le dossier d'entrée où chercher les vidéos
- `--output` : pour spécifier l'endroit où stocker les images en sortie
- `--frequency` : pour spécifier la fréquence temporelle de capture des images (en s)
- `--remove_duplicates` : permet de supprimer les doublons d'images pour un même film, note: cela peut ralentir la conversion.

Exemple d'usage:
`pellipop --input C:\Users\Utilisateur\Videos\Captures --output D:\Users\Bureau\Output --frequency 1 --remove_duplicates`

> Note: Le temps de découpe de chaque vidéo dépend de la qualité de la vidéo découpée.
