# Pellipop

[![PyPI - Version](https://img.shields.io/pypi/v/pellipop.svg)](https://pypi.org/project/pellipop)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pellipop.svg)](https://pypi.org/project/pellipop)

This readme is also available in [English](https://github.com/CERES-Sorbonne/Pellipop/blob/master/readme_en.md)

## Table des matières
1. [Description](#description)
2. [Installation](#installation)
    1. [PyPi](#pypi)
    2. [Exécutable](#exécutable)
    3. [Développement](#développement)
3. [Usage](#usage)
    1. [Interface graphique](#interface-graphique)
    2. [Ligne de commande](#ligne-de-commande)
4. [License](#license)


## Description
Pellipop est un outil de découpe de vidéos en images fixes, avec extraction de texte et audio.
Il permet de découper des vidéos en images fixes, en extrayant le texte et l'audio des vidéos.
Il permet également d'obtenir un fichier csv contenant les informations des images extraites et facilitant l'exportation
des données dans des logiciels de traitement de corpus d'image,
comme [Panoptic](https://github.col/CERES-Sorbonne/panoptic).

Il prend en entrée les formats suivants:

- `".mov"`
- `".avi"`
- `".mp4"`
- `".flv"`
- `".wmv"`
- `".webm"`
- `".mkv"`
- `".svf"`

## Installation
### PyPi
Pellipop est disponible sur PyPi, vous pouvez l'installer avec pip à l'aide de la commande suivante:
```bash
pip install pellipop
```
Vous pouvez ensuite vérifier que l'installation s'est bien passée en lançant la commande `pellipop --version`
Une fois installé, vous pouvez lancer l'interface graphique avec la commande `pellipop`.

### Exécutable
Des exécutables sont disponibles pour Windows, MacOS et Linux sur la page de [releases](https://github.com/CERES-Sorbonne/Pellipop/releases/latest).
Vous pouvez télécharger l'exécutable correspondant à votre système d'exploitation, et lancer l'interface graphique en double-cliquant dessus.

### Développement
Pour installer Pellipop en mode développement, vous pouvez cloner le dépôt git et installer les dépendances avec pip:
```bash
git clone https://github.com/CERES-Sorbonne/Pellipop.git.
cd Pellipop
pip install -e .
```


## Usage
### Interface graphique
Elle se lance avec `pellipop`, sans aucun argument, pour ouvrir l'interface graphique.

Alternativement, vous pouvez télécharger l'executable correspondant à votre système d'exploitation sur la page
de [releases](https://github.com/CERES-Sorbonne/Pellipop/releases/latest).

### Ligne de commande
La cli se lance avec `pellipop` dans un terminal, par défaut les vidéos sont cherchées dans le dossier où la commande
est lancée, et les images créées sont également stockées au même endroit. Les paramètres peuvent toutefois être changés:

- `--input` : pour spécifier le dossier d'entrée où chercher les vidéos (recursif)
- `--output` : pour spécifier l'endroit où stocker les images en sortie

- `--interval` : intervalle de temps (en secondes) à laquelle réaliser des captures d'écran
- `--i-frame-mode` : permet de supprimer les doublons d'images pour un même film en utilisant les images clés (
  keyframes) de la vidéo

- `--keep-audio` : permet de garder les fichiers audio extraits des vidéos
- `--whisper-config` : pour préciser le chemin vers le fichier de configuration de l'API Whisper, au lieu du chemin par
  défaut (`~\.whisperrc`)

- `--frames-only` : permet de ne pas extraire le texte des vidéos
- `--reduce` : permet de réduire le nom des fichiers de sortie à un certain nombre de caractères du nom original
- `--offset` : permet de décaler le début du nom des fichiers de sortie de n caractères
- `--parents-in-name` : permet d'ajouter le nom des dossiers parents dans le nom des fichiers de sortie, séparés par des _

- `-g` ou `--gui` : permet d'utiliser l'interface graphique
- `-v` ou `--version` : affiche la version de l'installation actuelle de Pellipop

> Note: Le temps de découpe de chaque vidéo dépend de la qualité de la vidéo découpée, de la fréquence de découpe, de la durée de la vidéo et de la puissance de l'ordinateur.

#### Exemple d'usage:
```bash
pellipop --input C:\Users\Utilisateur\Videos\Captures --output D:\Users\Bureau\Output --i-frame-mode
```


## License
Ce projet est sous licence MPL-2.0 - voir le fichier [LICENSE](https://github.com/CERES-Sorbonne/Pellipop/blob/master/LICENSE.txt) pour plus de détails.
