import json
import tkinter as tk
from tkinter import filedialog

import ttkbootstrap as ttk

from pellipop.Video import DummyVideo
from pellipop.file_finder import how_many_files
from pellipop.main import Pellipop, default_output_path
from pellipop.path_fixer import Path
from pellipop.whisper_from_url import WhisperFromUrl, URLImportError

dummy_video = DummyVideo()

print(dummy_video)


class URLImportGUIError(Exception):
    def __init__(self, message):
        super().__init__(message)
        import_label.config(foreground="red", text=message, cursor="pirate")
        import_entry.config(state="normal", cursor="arrow")


def dummy_str():
    posix = dummy_video.posix.replace(r"\\", "/")
    final_stem = dummy_video.final_stem.replace(r"\\", "/")
    max_len = max(len(posix), len(final_stem))
    if max_len > 50:
        max_len = 50

    if len(posix) > max_len:
        posix = "..." + posix[-max_len:]

    if len(final_stem) > max_len:
        final_stem = "..." + final_stem[-max_len:]

    posix = posix.rjust(max_len)
    final_stem = final_stem.rjust(max_len)

    return f"Chemin originel:\t{posix}\nBase de nom:\t{final_stem}"


def url_import():
    global wu
    url = import_file.get()

    if not url:
        return

    wu.set_url(url)

    if not wu.valid:
        import_error()
        return

    import_entry.config(state="disabled", cursor="X_cursor")
    import_button.config(state="disabled", cursor="X_cursor")
    import_label.config(cursor="watch", foreground="grey", text="Importation en cours...")

    try:
        wu.import_and_set()
    except URLImportError as e:
        import_error()
        raise URLImportGUIError(e.message)
    except json.decoder.JSONDecodeError as err:
        import_error()
        raise URLImportGUIError(f"Erreur JSON : {err}")

    print("Le format du fichier de configuration est correct")

    import_label.config(text="Importation terminée !", foreground="green", cursor="arrow")


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


def validateint(var):
    try:
        if not isinstance(var.get(), str):
            return 0
        try:
            int(var.get())
        except ValueError:
            return 0
        return 1
    finally:
        update_final_stem()


def update_final_stem():
    if not prefix.get():
        result_str.set("Résultat")
        return

    try:
        reduce = int(reduce_length.get())
        offset = int(offset_length.get())
        parents = int(parents_length.get())
    except ValueError:
        return

    dummy_video.reduce = reduce
    dummy_video.offset = offset
    dummy_video.parents_in_name = parents

    result_str.set(dummy_str())


def validate_freq():
    if mode.get() == "i":
        return 1

    return validateint(freq_int)


def validate_reduce():
    return validateint(reduce_length)


def validate_offset():
    return validateint(offset_length)


def validate_parents():
    return validateint(parents_length)


def validate_url():
    url = import_file.get()
    wu.set_url(url)
    return int(wu.validate_url())  # Boolean output but tkinter needs int


def freq_error():
    freq_entry.bell()
    freq_int.set("5")


def prefix_error():
    reduce_entry.bell()
    reduce_length.set("10")


def import_error():
    import_entry.bell()


def disable_freq():
    if mode.get() == "i":
        freq_entry.config(state="disabled", cursor="X_cursor")
    else:
        freq_entry.config(state="normal", cursor="xterm")


def disable_prefix():
    if prefix.get():
        reduce_entry.config(state="normal", cursor="xterm")
        reduce_label.config(foreground="black", cursor="arrow")

        offset_entry.config(state="normal", cursor="xterm")
        offset_label.config(foreground="black", cursor="arrow")

        parents_entry.config(state="normal", cursor="xterm")
        parents_label.config(foreground="black", cursor="arrow")

    else:
        reduce_entry.config(state="disabled", cursor="X_cursor")
        reduce_label.config(foreground="grey", cursor="X_cursor")

        offset_entry.config(state="disabled", cursor="X_cursor")
        offset_label.config(foreground="grey", cursor="X_cursor")

        parents_entry.config(state="disabled", cursor="X_cursor")
        parents_label.config(foreground="grey", cursor="X_cursor")


def disable_retranscrire():
    if retranscrire.get():
        import_entry.config(state="normal", cursor="xterm")
        import_button.config(state="normal", cursor="gumby")
    else:
        import_entry.config(state="disabled", cursor="X_cursor")
        import_button.config(state="disabled", cursor="X_cursor")


def validate():
    errors = []
    out_fold = output_folder.get()
    if out_fold != default_output_path and (not out_fold or not Path(out_fold).exists()):
        errors.append("Veuillez entrer un dossier de sortie pour les images")

    if mode.get() != "i" and not validate_freq():
        errors.append("Veuillez entrer une fréquence de découpage valide")

    if prefix.get() and not validate_reduce():
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
        "reduce": int(reduce_length.get()),
        "offset": int(offset_length.get()),
        "parents_in_name": int(parents_length.get()),
        "with_text": True,  # TODO : With text or only text ? Should we let the user choose ?
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
    size=(1400, 1000),
    resizable=(True, True),
    minsize=(1050, 900),
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
    font=("Jetbrains Mono", 30, "bold"),
    cursor="heart",
).pack()

input_frame = ttk.Frame(top_frame, padding=10)
input_frame.pack()
input_label = ttk.Label(input_frame, text='Entrez le chemin du dossier à analyser')
input_label.grid(row=0, column=0, columnspan=6)
input_folder = tk.StringVar(value="Entrez le chemin du dossier à analyser")
input_entry = ttk.Entry(input_frame, textvariable=input_folder)
input_button = ttk.Button(input_frame, text="Naviguer", command=browse_input, cursor="sailboat")
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
output_button = ttk.Button(output_frame, text="Naviguer", command=browse_output, cursor="sailboat")
output_entry.grid(row=1, column=0, columnspan=5, ipadx=250, pady=5)
output_button.grid(row=1, column=5, padx=10)

# TODO : Progress bar
# progress_frame = ttk.Frame(top_frame, padding=10)
# progress_frame.pack()
# progress_label = ttk.Label(progress_frame, text='Progression')
# progress_label.grid(row=0, column=0, columnspan=6)
# progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=500, mode="determinate")
# progress_bar.grid(row=1, column=0, columnspan=6, pady=5)

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
mode = tk.StringVar(value="i")
# ttk.Radiobutton(
#     freq_frame,
#     text="par seconde",
#     variable=mode,
#     value="s-1",
#     command=disable_freq
# ).grid(row=1, column=0, columnspan=3, pady=10, padx=5)
ttk.Radiobutton(
    freq_frame,
    text="Découpage automatique (selon la similarité des images)",
    variable=mode,
    value="i",
    command=disable_freq,
).grid(row=1, column=0, columnspan=6, pady=10, padx=5)
ttk.Radiobutton(
    freq_frame,
    text="toutes les x secondes",
    variable=mode,
    value="s",
    command=disable_freq,
).grid(row=2, column=0, columnspan=3, pady=10, padx=5)
freq_int = tk.StringVar(value="5")
freq_entry = ttk.Entry(
    freq_frame,
    textvariable=freq_int,
    justify="right",
    validate="focusout",
    validatecommand=validate_freq,
    invalidcommand=freq_error,
    cursor="xterm",

)
freq_entry.grid(row=2, column=3, columnspan=3, pady=5)  # /!\ BEFORE the second radiobutton

# TODO : Use the Video class to emulate the renaming behavior on a random file of the given dir
# / or do a custom function to be able to test it even if no input folder is given yet ?
prefix_frame = ttk.Frame(left_lv2_frame, padding=10, relief="sunken")
prefix_frame.grid(row=3, column=0)
ttk.Label(
    prefix_frame, text='Souhaitez-vous changer le nom des sorties ?'
).grid(row=0, column=0, columnspan=2)
prefix = tk.BooleanVar(value=False)
prefix_check = ttk.Checkbutton(prefix_frame, variable=prefix, command=disable_prefix)
prefix_check.grid(row=0, column=2, padx=10)
reduce_label = ttk.Label(prefix_frame, text='Longueur maximale du préfixe (-1 pour ne pas réduire)')
reduce_label.grid(row=1, column=0, sticky="w")
reduce_length = tk.StringVar(value="-1")
reduce_entry = ttk.Entry(
    prefix_frame,
    textvariable=reduce_length,
    justify="right",
    validate="focusout",
    validatecommand=validate_reduce,
    invalidcommand=prefix_error,
)
reduce_entry.grid(row=1, column=2, pady=5, rowspan=2)
offset_label = ttk.Label(prefix_frame, text='Décalage du préfixe')
offset_label.grid(row=3, column=0, sticky="w")
offset_length = tk.StringVar(value="0")
offset_entry = ttk.Entry(
    prefix_frame,
    textvariable=offset_length,
    justify="right",
    validate="focusout",
    validatecommand=validate_offset,
    invalidcommand=prefix_error,
)
offset_entry.grid(row=3, column=2, pady=5, rowspan=2)
parents_label = ttk.Label(prefix_frame, text='Nombre de dossiers parents à inclure dans le nom')
parents_label.grid(row=5, column=0, rowspan=2, sticky="w")
parents_length = tk.StringVar(value="0")
parents_entry = ttk.Entry(
    prefix_frame,
    textvariable=parents_length,
    justify="right",
    validate="focusout",
    validatecommand=validate_parents,
    invalidcommand=prefix_error,
)
parents_entry.grid(row=5, column=2, pady=5, rowspan=2)
result_str = tk.StringVar(value=dummy_str())
result_label = ttk.Label(prefix_frame, textvariable=result_str)
result_label.grid(row=7, column=0, columnspan=3, pady=10)

## RIGHT FRAME - STT

right_select_frame = ttk.Frame(main_frame)
right_select_frame.grid(row=1, column=1, sticky="s", pady=10)
ttk.Label(
    right_select_frame,
    text='Retranscrire les vidéos',
    font=("Jetbrains Mono", 16, "bold")
).pack(side="left")
retranscrire = tk.BooleanVar(value=False)
retranscrire_check = ttk.Checkbutton(right_select_frame, variable=retranscrire, command=disable_retranscrire)
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
import_button = ttk.Button(import_frame, text="Importer", command=url_import, cursor="gumby")
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

lancer_button = ttk.Button(bottom_frame, text="Lancer", command=lancer, cursor="gumby")
lancer_button.grid(row=1, column=0, columnspan=3, pady=10, padx=10)

# Disable stuff at start
reduce_entry.config(state="disabled", cursor="X_cursor")
reduce_label.config(foreground="grey", cursor="X_cursor")

offset_entry.config(state="disabled", cursor="X_cursor")
offset_label.config(foreground="grey", cursor="X_cursor")

parents_entry.config(state="disabled", cursor="X_cursor")
parents_label.config(foreground="grey", cursor="X_cursor")

freq_entry.config(state="disabled", cursor="X_cursor")

import_entry.config(state="disabled", cursor="X_cursor")
import_button.config(state="disabled", cursor="pirate")


def main():
    global wu
    wu = WhisperFromUrl()
    root.mainloop()


if __name__ == '__main__':
    main()
