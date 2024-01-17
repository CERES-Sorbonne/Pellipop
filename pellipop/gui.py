import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import ttkbootstrap as ttk
import validators
from whisper_client.main import Mode

video_formats = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg", ".3gp", ".3g2"}


def browse(path_var, default_path=Path.home()):
    assert isinstance(path_var, tk.StringVar)

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
        title="Select a folder",
    )

    if not path:
        return

    print(path)

    path_var.set(path)

    return path


def browse_input():
    path = browse(input_folder)

    if not path:
        return

    how_many_str.set(f"{len([f for f in Path(path).iterdir() if f.suffix in video_formats])} fichiers trouvés")


def browse_pic_output():
    browse(pics_output_folder, default_path=Path().cwd() / "pellipop_pics")


def browse_text_output():
    browse(text_output_folder, default_path=Path().cwd() / "pellipop_text")


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

    # Complete l'url si besoin (ex: www.google.com -> https://www.google.com)
    # Le validateur ne fonctionne pas avec les url sans protocole ni sous-domaine
    if not url.startswith("http"):
        if url.count(".") < 2:
            url = "www." + url
        url = "https://" + url
    else:
        if url.count(".") < 2:
            url = url.replace("https://", "https://www.")
            url = url.replace("http://", "http://www.")

    print(url)

    if validators.url(url):
        return 1
    else:
        return 0


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
    else:
        freq_entry.config(state="normal")


def disable_prefix():
    if prefix.get():
        prefix_entry.config(state="normal")
        prefix_label["foreground"] = "black"
    else:
        prefix_entry.config(state="disabled")
        prefix_label["foreground"] = "grey"


def lancer():
    print("Lancer")


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
input_folder = tk.StringVar(value="Entrez le chemin du dossier à analyser")
input_entry = ttk.Entry(input_frame, textvariable=input_folder)
input_button = ttk.Button(input_frame, text="Browse", command=browse_input)
input_entry.grid(row=0, column=0, columnspan=5, ipadx=100, pady=5)
input_button.grid(row=0, column=5, padx=10)
how_many_str = tk.StringVar(value="0 fichiers trouvés")
ttk.Label(top_frame, textvariable=how_many_str).pack()

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



pics_output_frame = ttk.Frame(left_lv2_frame, padding=10)
pics_output_frame.grid(row=1, column=0)
ttk.Label(pics_output_frame, text='Dossier de sortie').grid(row=0, column=0, columnspan=3)
pics_output_folder = tk.StringVar(value="Entrez le chemin du dossier de sortie")
pics_output_entry = ttk.Entry(pics_output_frame, textvariable=pics_output_folder)
pics_output_button = ttk.Button(pics_output_frame, text="Browse", command=browse_pic_output)
pics_output_entry.grid(row=1, column=0, columnspan=2, pady=5)
pics_output_button.grid(row=1, column=2)

freq_frame = ttk.Frame(left_lv2_frame, padding=10, relief="sunken")
freq_frame.grid(row=2, column=0)
ttk.Label(freq_frame, text='Fréquence de découpage').grid(row=0, column=0, columnspan=6, pady=10)
mode = tk.StringVar(value="s-1")
ttk.Radiobutton(
    freq_frame,
    text="par seconde",
    variable=mode,
    value="s-1",
    command=disable_freq
).grid(row=1, column=0, columnspan=3, pady=10, padx=5)
ttk.Radiobutton(
    freq_frame,
    text="toutes les x secondes",
    variable=mode,
    value="s",
    command=disable_freq,
).grid(row=1, column=3, columnspan=3, pady=10, padx=5)
ttk.Radiobutton(
    freq_frame,
    text="Découpage intelligent (par plan)",
    variable=mode,
    value="i",
    command=disable_freq,
).grid(row=2, column=0, columnspan=6, pady=10, padx=5)
freq_int = tk.StringVar(value="5")
freq_entry = ttk.Entry(
    freq_frame,
    textvariable=freq_int,
    justify="right",
    validate="focusout",
    validatecommand=validate_freq,
    invalidcommand=freq_error,

)
freq_entry.grid(row=3, column=0, columnspan=6, pady=5)

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


text_output_frame = ttk.Frame(right_lv2_frame, padding=10)
text_output_frame.grid(row=1, column=1)
ttk.Label(text_output_frame, text='Dossier de sortie').grid(row=0, column=0, columnspan=3)
text_output_folder = tk.StringVar(value="Entrez le chemin du dossier de sortie")
text_output_entry = ttk.Entry(text_output_frame, textvariable=text_output_folder)
text_output_button = ttk.Button(text_output_frame, text="Browse", command=browse_text_output)
text_output_entry.grid(row=1, column=0, columnspan=2, pady=5)
text_output_button.grid(row=1, column=2)

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
import_button = ttk.Button(import_frame, text="Importer")
import_button.grid(row=1, column=2)

mode_frame = ttk.Frame(right_lv2_frame, padding=10)
mode_frame.grid(row=4, column=1)
ttk.Label(mode_frame, text='Mode de retranscription').grid(row=0, column=0, columnspan=2)
mode = tk.StringVar(value="Full")
box = ttk.Combobox(mode_frame, textvariable=mode, values=[e.value.capitalize() for e in Mode])
box.grid(row=1, column=0, columnspan=2, pady=5)

timestamped_frame = ttk.Frame(right_lv2_frame, padding=10)
timestamped_frame.grid(row=5, column=1)
ttk.Label(timestamped_frame, text='Souhaitez-vous que le texte soit timestampé ?').grid(row=0, column=0, columnspan=2)
timestamped = tk.BooleanVar(value=True)
timestamped_check = ttk.Checkbutton(timestamped_frame, variable=timestamped)
timestamped_check.grid(row=0, column=2, padx=10)

## BOTTOM FRAME - Bouton lancer
bottom_frame = ttk.Frame(main_frame, padding=10)
bottom_frame.grid(row=3, column=0, columnspan=2)

ttk.Label(
    bottom_frame, text="Souhaitez-vous générer un fichier csv contenant les informations des vidéos ?"
).grid(row=0, column=0, columnspan=2)
csv = tk.BooleanVar(value=True)
csv_check = ttk.Checkbutton(bottom_frame, variable=csv)
csv_check.grid(row=0, column=2, padx=10)

ttk.Button(bottom_frame, text="Lancer", command=lancer).grid(row=1, column=0, columnspan=3, pady=10, padx=10)

if __name__ == '__main__':
    root.mainloop()
