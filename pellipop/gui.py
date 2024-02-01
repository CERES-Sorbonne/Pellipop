import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import ttkbootstrap as ttk

from pellipop.main import Pellipop, default_output_path
from pellipop.fileFinder import how_many_files
from pellipop.whisper_from_url import WhisperFromUrl, URLImportError


class URLImportGUIError(Exception):
    def __init__(self, message):
        super().__init__(message)
        import_label["text"] = message
        import_label["foreground"] = "red"
        import_entry.config(state="normal")


def url_import():
    global wu
    url = import_file.get()

    if not url:
        return

    wu.set_url(url)

    if not wu.valid:
        import_error()
        return

    import_entry.config(state="disabled")
    import_button.config(state="disabled")

    import_label["foreground"] = "grey"

    import_label["text"] = "Importation en cours..."
    try:
        wu.import_and_set()
    except URLImportError as e:
        import_error()
        raise URLImportGUIError(e.message)
    except json.decoder.JSONDecodeError as err:
        import_error()
        raise URLImportGUIError(f"Erreur JSON : {err}")

    print("Le format du fichier de configuration est correct")

    import_label["text"] = "Importation terminée !"
    import_label["foreground"] = "green"


def browse(
        path_var,
        default_path=Path.home(),
        add_suffix=None,
        mustexist: bool = False,
        title: str = "Choisissez un dossier",
):
    path = path_var.get()

    if path == "Entrez le chemin du dossier à analyser":
        path = default_path
    else:
        path = Path(path)

    if not path.exists():
        path = default_path

    if not path.is_dir():
        path = path.parent

    path = filedialog.askdirectory(
        initialdir=path,
        title=title,
        mustexist=mustexist,
    )

    if not path:
        return

    print(path)

    if add_suffix:
        path = Path(path) / add_suffix
        if not path.exists():
            path.mkdir(parents=True)

    path_var.set(path)

    return path


def browse_input():
    path = browse(input_folder, mustexist=True, title="Choisissez le dossier à analyser")

    if not path:
        return

    how_many_str.set(f"{how_many_files(path)} fichiers trouvés")


def browse_output():
    browse(
        output_folder,
        default_path=Path().cwd(),
        add_suffix="pellipop_output",
        title="Choisissez le dossier de sortie"
    )


def validatepositiveint(var):
    if not isinstance(var.get(), str):
        return 0

    try:
        int(var.get())
    except ValueError:
        return 0

    return 1


def validate_freq():
    if mode.get() == "i":
        return 1

    return validatepositiveint(freq_int)


def validate_prefix():
    return validatepositiveint(prefix_length)


def validate_url():
    url = import_file.get()
    wu.set_url(url)
    return int(wu.validate_url())  # Boolean output but tkinter needs int


def freq_error():
    freq_entry.bell()
    freq_int.set("5")


def prefix_error():
    prefix_entry.bell()
    prefix_length.set("10")


def import_error():
    import_entry.bell()


def disable_freq():
    if mode.get() == "i":
        freq_entry.config(state="disabled")
        hamming_slider.config(state="normal")
    else:
        freq_entry.config(state="normal")
        hamming_slider.config(state="disabled")


def disable_prefix():
    if prefix.get():
        prefix_entry.config(state="normal")
        prefix_label["foreground"] = "black"
    else:
        prefix_entry.config(state="disabled")
        prefix_label["foreground"] = "grey"


def validate():
    errors = []
    out_fold = output_folder.get()
    if out_fold != default_output_path and (not out_fold or not Path(out_fold).exists()):
        errors.append("Veuillez entrer un dossier de sortie pour les images")

    if mode.get() != "i" and not validate_freq():
        errors.append("Veuillez entrer une fréquence de découpage valide")

    if prefix.get() and not validate_prefix():
        errors.append("Veuillez entrer une longueur de préfixe valide")

    if errors:
        root.bell()
        print(errors)
        return False

    return True

def lancer():
    print("Lancer")

    if not validate():
        return

    lancer_button.config(state="disabled")

    if mode.get() == "s":
        freq = int(freq_int.get())
    elif mode.get() == "s-1":
        freq = None
    else:
        freq = None

    config = {
        "intervale": freq,
        "input_folder": input_folder.get(),
        "output_folder": output_folder.get(),
        "delete_duplicates": mode.get() == "i",
        "decouper": decouper.get(),
        "retranscrire": retranscrire.get(),
        "csv": csv.get(),
        "hamming": int(hamming_int.get()),
    }

    try:
        pelli = Pellipop(**config)
        csv_outp = pelli.launch()

    except Exception as e:
        print(e)
        lancer_button.config(state="normal")
        lancer_button.bell()
        lancer_button["text"] = "Erreur"
        # lancer_button["foreground"] = "red"
        return

    lancer_button.config(state="normal")
    lancer_button["text"] = "Lancer"
    # lancer_button["foreground"] = "green"
    # TODO : Alternative to foreground

    if csv_outp:
        print(f"Le fichier csv a été généré : {csv_outp}")

    root.focus_force()

## ROOT

root = ttk.Window(
    "Pellipop",
    themename="journal",
    iconphoto="pellipop.ico",
    size=(1400, 900),
    resizable=(True, True),
    minsize=(950, 750),
)

main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill="both", expand=True)

main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)
main_frame.rowconfigure(1, weight=1)
main_frame.rowconfigure(2, weight=1)

## TOP FRAME - Titre + Input
top_frame = ttk.Frame(main_frame, padding=10, height=800, width=500)
top_frame.grid(row=0, column=0, columnspan=2, sticky="sew")

ttk.Label(
    top_frame,
    text='Pellipop, votre ami pour la vie',
    font=("Jetbrains Mono", 30, "bold")
).pack()

input_frame = ttk.Frame(top_frame, padding=10)
input_frame.pack()
input_label = ttk.Label(input_frame, text='Entrez le chemin du dossier à analyser')
input_label.grid(row=0, column=0, columnspan=6)
input_folder = tk.StringVar(value="Entrez le chemin du dossier à analyser")
input_entry = ttk.Entry(input_frame, textvariable=input_folder)
input_button = ttk.Button(input_frame, text="Browse", command=browse_input)
input_entry.grid(row=1, column=0, columnspan=5, ipadx=250, pady=5)
input_button.grid(row=1, column=5, padx=10)
how_many_str = tk.StringVar(value="0 fichiers trouvés")
how_many_label = ttk.Label(input_frame, textvariable=how_many_str)
how_many_label.grid(row=2, column=2, columnspan=4)

output_frame = ttk.Frame(top_frame, padding=10)
output_frame.pack()
output_label = ttk.Label(output_frame, text='Entrez le chemin du dossier de sortie')
output_label.grid(row=0, column=0, columnspan=6)
output_folder = tk.StringVar(value=default_output_path)
output_entry = ttk.Entry(output_frame, textvariable=output_folder)
output_button = ttk.Button(output_frame, text="Browse", command=browse_output)
output_entry.grid(row=1, column=0, columnspan=5, ipadx=250, pady=5)
output_button.grid(row=1, column=5, padx=10)

## LEFT FRAME - Découper les vidéos
left_select_frame = ttk.Frame(main_frame)
left_select_frame.grid(row=1, column=0, sticky="s", pady=10)
ttk.Label(
    left_select_frame,
    text='Découper les vidéos',
    font=("Jetbrains Mono", 16, "bold")
).grid(row=0, column=0, columnspan=2)
decouper = tk.BooleanVar(value=True)
decouper_check = ttk.Checkbutton(left_select_frame, variable=decouper)
decouper_check.grid(row=0, column=2, padx=10)

left_frame = ttk.Frame(main_frame, relief="ridge", width=main_frame.winfo_width() / 2, padding=10)
left_frame.grid(row=2, column=0, sticky="nsew")
left_lv2_frame = ttk.Frame(left_frame, padding=10)
left_lv2_frame.pack()

freq_frame = ttk.Frame(left_lv2_frame, padding=10, relief="sunken")
freq_frame.grid(row=2, column=0)
ttk.Label(freq_frame, text='Fréquence de découpage').grid(row=0, column=0, columnspan=6, pady=10)
mode = tk.StringVar(value="s")
# ttk.Radiobutton(
#     freq_frame,
#     text="par seconde",
#     variable=mode,
#     value="s-1",
#     command=disable_freq
# ).grid(row=1, column=0, columnspan=3, pady=10, padx=5)
ttk.Radiobutton(
    freq_frame,
    text="toutes les x secondes",
    variable=mode,
    value="s",
    command=disable_freq,
).grid(row=1, column=0, columnspan=6, pady=10, padx=5)
ttk.Radiobutton(
    freq_frame,
    text="Découpage automatique (selon la similarité des images)",
    variable=mode,
    value="i",
    command=disable_freq,
).grid(row=3, column=0, columnspan=6, pady=10, padx=5)
freq_int = tk.StringVar(value="5")
freq_entry = ttk.Entry(
    freq_frame,
    textvariable=freq_int,
    justify="right",
    validate="focusout",
    validatecommand=validate_freq,
    invalidcommand=freq_error,

)
freq_entry.grid(row=2, column=0, columnspan=6, pady=5)  # /!\ BEFORE the second radiobutton
hamming_int = tk.IntVar(value=5)
hamming_str = tk.StringVar(value="5")
hamming_label = ttk.Label(freq_frame, text='Distance de Hamming')
hamming_label.grid(row=4, column=0, columnspan=6, pady=10)
hamming_slider = ttk.Scale(
    freq_frame,
    from_=0,
    to=10,
    variable=hamming_int,
    orient="horizontal",
    cursor="hand2",
    length=200,
    value=5,
    command=lambda x: hamming_str.set(int(hamming_int.get())),
    state="disabled",
)
hamming_slider.grid(row=5, column=0, columnspan=6, pady=10)
hamming_slider_info = ttk.Label(
    freq_frame,
    textvariable=hamming_str,
    justify="center",
)
hamming_slider_info.grid(row=6, column=0, columnspan=6, pady=10)
prefix_frame = ttk.Frame(left_lv2_frame, padding=10, relief="sunken")
prefix_frame.grid(row=3, column=0)
ttk.Label(
    prefix_frame, text='Souhaitez-vous préfixer les images du nom de la vidéo d\'origine ?'
).grid(row=0, column=0, columnspan=3)
prefix = tk.BooleanVar(value=True)
prefix_check = ttk.Checkbutton(prefix_frame, variable=prefix, command=disable_prefix)
prefix_check.grid(row=0, column=3, padx=10)
prefix_label = ttk.Label(prefix_frame, text='Longueur du préfixe')
prefix_label.grid(row=1, column=0)
prefix_length = tk.StringVar(value="10")
prefix_entry = ttk.Entry(
    prefix_frame,
    textvariable=prefix_length,
    justify="right",
    validate="focusout",
    validatecommand=validate_prefix,
    invalidcommand=prefix_error,
)
prefix_entry.grid(row=1, column=2, pady=5)

## RIGHT FRAME - STT

right_select_frame = ttk.Frame(main_frame)
right_select_frame.grid(row=1, column=1, sticky="s", pady=10)
ttk.Label(
    right_select_frame,
    text='Retranscrire les vidéos',
    font=("Jetbrains Mono", 16, "bold")
).pack(side="left")
retranscrire = tk.BooleanVar(value=False)
retranscrire_check = ttk.Checkbutton(right_select_frame, variable=retranscrire)
retranscrire_check.pack(side="right", padx=10)

right_frame = ttk.Frame(main_frame, relief="ridge", width=main_frame.winfo_width() / 2, padding=10)
right_frame.grid(row=2, column=1, sticky="nsew")
right_lv2_frame = ttk.Frame(right_frame, padding=10)
right_lv2_frame.pack()

import_frame = ttk.Frame(right_lv2_frame, padding=10)
import_frame.grid(row=2, column=1)
import_label = ttk.Label(import_frame, text='Importer le fichier de configuration')
import_label.grid(row=0, column=0, columnspan=2)
import_file = tk.StringVar(value="Entrez l'url du fichier de configuration")
import_entry = ttk.Entry(
    import_frame,
    textvariable=import_file,
    validate="focusout",
    validatecommand=validate_url,
    invalidcommand=import_error,

)
import_entry.grid(row=1, column=0, columnspan=2, sticky="ew")
import_button = ttk.Button(import_frame, text="Importer", command=url_import)
import_button.grid(row=1, column=2)


## BOTTOM FRAME - Bouton lancer
bottom_frame = ttk.Frame(main_frame, padding=10)
bottom_frame.grid(row=3, column=0, columnspan=2)

ttk.Label(
    bottom_frame, text="Souhaitez-vous générer un fichier csv contenant les informations des vidéos ?"
).grid(row=0, column=0, columnspan=2)
csv = tk.BooleanVar(value=True)
csv_check = ttk.Checkbutton(bottom_frame, variable=csv)
csv_check.grid(row=0, column=2, padx=10)

lancer_button = ttk.Button(bottom_frame, text="Lancer", command=lancer)
lancer_button.grid(row=1, column=0, columnspan=3, pady=10, padx=10)

def main():
    global wu
    wu = WhisperFromUrl()
    root.mainloop()

if __name__ == '__main__':
    main()
