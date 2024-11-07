# bookmarks_manager.py - Logique de gestion des favoris
import json
import os
import shutil
import threading
import subprocess
from tkinter import messagebox, Tk, Entry, Label, Button, Listbox, StringVar, Toplevel
from tkinter import simpledialog, Scrollbar, PhotoImage
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageTk

# Chemin du fichier JSON pour stocker les favoris
JSON_PATH = "bookmarks.json"
ICON_PATH = "simplifier.png"
ADD_ICON_PATH = "add_icon.png"  # Icône pour ajouter un favori
REMOVE_ICON_PATH = "remove_icon.png"  # Icône pour supprimer un favori

# Initialise le fichier JSON s'il n'existe pas ou s'il est mal structuré
def initialize_bookmarks_file():
    if not os.path.exists(JSON_PATH):
        save_data({
            "bookmarks": [],
            "show_at_startup": True,
            "window_position": {"x": 100, "y": 100},
            "preferred_browser": "chrome"
        })

# Charge les données depuis le fichier JSON et s'assure que la structure est correcte
def load_data():
    try:
        with open(JSON_PATH, 'r', encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Incorrect structure")
        return data
    except (json.JSONDecodeError, ValueError, FileNotFoundError):
        # Réinitialise le fichier si erreur de lecture/structure
        initialize_bookmarks_file()
        with open(JSON_PATH, 'r', encoding="utf-8") as f:
            return json.load(f)

# Sauvegarde les données dans le fichier JSON
def save_data(data):
    with open(JSON_PATH, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Fonction pour ajouter un favori
def add_bookmark(title, url):
    if not title or not url or not url.startswith("http"):
        messagebox.showerror("Erreur", "Veuillez entrer une URL valide (commençant par http ou https).")
        return
    data = load_data()
    data["bookmarks"].append({"name": title, "url": url})
    save_data(data)
    refresh_bookmark_list()

# Fonction pour supprimer un favori
def remove_bookmark(url):
    data = load_data()
    data["bookmarks"] = [bookmark for bookmark in data["bookmarks"] if bookmark["url"] != url]
    save_data(data)
    refresh_bookmark_list()

# Fonction pour vérifier la disponibilité d'un navigateur
def is_browser_available(browser_name):
    if shutil.which(browser_name):
        return True
    possible_paths = {
        "chrome": [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        ],
        "firefox": [
            "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
        ],
        "msedge": [
            "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
        ],
        "safari": [
            "/Applications/Safari.app/Contents/MacOS/Safari"
        ]
    }
    for path in possible_paths.get(browser_name, []):
        if os.path.exists(path):
            return True
    return False

# Fonction pour ouvrir un favori dans le navigateur
def open_bookmark(url):
    data = load_data()
    browser = data.get("preferred_browser", "chrome")
    browser_command = {}

    # Définir les commandes de navigateur disponibles
    if is_browser_available("chrome"):
        browser_command["chrome"] = ["chrome", "--app=" + url]
    if is_browser_available("firefox"):
        browser_command["firefox"] = ["firefox", url]
    if is_browser_available("msedge"):
        browser_command["msedge"] = ["msedge", "--app=" + url]
    if is_browser_available("safari"):
        browser_command["safari"] = ["open", "-a", "Safari", url]

    command = browser_command.get(browser, browser_command.get("chrome", ["chrome", "--app=" + url]))
    try:
        subprocess.Popen(command)
    except FileNotFoundError:
        messagebox.showerror("Erreur", f"Navigateur {browser} non trouvé. Veuillez vérifier votre installation.")

# Créer une interface graphique de gestion des favoris
main_window = Tk()
main_window.title("Gestionnaire de Favoris SimplyLaunch")
main_window.geometry("500x500")

# Variables Tkinter
title_var = StringVar()
url_var = StringVar()

# Fonction pour mettre à jour la liste des favoris dans la fenêtre
bookmark_listbox = Listbox(main_window, width=50, height=15)
bookmark_listbox.pack(pady=10, side='left', fill='both')

scrollbar = Scrollbar(main_window)
scrollbar.pack(side='right', fill='y')
bookmark_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=bookmark_listbox.yview)

def refresh_bookmark_list():
    bookmark_listbox.delete(0, 'end')
    data = load_data()
    for bookmark in data.get("bookmarks", []):
        bookmark_listbox.insert('end', f"{bookmark['name']} - {bookmark['url']}")

# Fonction d'ajout de favori via l'interface utilisateur
def on_add_bookmark():
    title = title_var.get()
    url = url_var.get()
    add_bookmark(title, url)
    title_var.set("")
    url_var.set("")

# Fonction de suppression de favori via l'interface utilisateur
def on_remove_bookmark():
    selected = bookmark_listbox.curselection()
    if selected:
        item_text = bookmark_listbox.get(selected)
        url = item_text.split(" - ")[1]
        remove_bookmark(url)
    else:
        messagebox.showerror("Erreur", "Veuillez sélectionner un favori à supprimer.")

# Fonction pour ouvrir un favori sélectionné
def on_open_bookmark():
    selected = bookmark_listbox.curselection()
    if selected:
        item_text = bookmark_listbox.get(selected)
        url = item_text.split(" - ")[1]
        open_bookmark(url)
    else:
        messagebox.showerror("Erreur", "Veuillez sélectionner un favori à ouvrir.")

# Fonction pour choisir le navigateur préféré
def choose_browser():
    browser_window = Toplevel(main_window)
    browser_window.title("Choisir le navigateur")
    browser_window.geometry("300x200")

    def set_browser(browser_choice):
        data = load_data()
        data["preferred_browser"] = browser_choice
        save_data(data)
        browser_window.destroy()

    Label(browser_window, text="Choisissez votre navigateur préféré :").pack(pady=10)
    if is_browser_available("chrome"):
        Button(browser_window, text="Chrome", command=lambda: set_browser("chrome")).pack(pady=5)
    if is_browser_available("firefox"):
        Button(browser_window, text="Firefox", command=lambda: set_browser("firefox")).pack(pady=5)
    if is_browser_available("msedge"):
        Button(browser_window, text="Edge", command=lambda: set_browser("msedge")).pack(pady=5)
    if is_browser_available("safari"):
        Button(browser_window, text="Safari", command=lambda: set_browser("safari")).pack(pady=5)

# Champs d'entrée pour le titre et l'URL
title_label = Label(main_window, text="Titre:")
title_label.pack()
title_entry = Entry(main_window, textvariable=title_var, width=50)
title_entry.pack()

url_label = Label(main_window, text="URL:")
url_label.pack()
url_entry = Entry(main_window, textvariable=url_var, width=50)
url_entry.pack()

# Icônes pour ajouter et supprimer des favoris
try:
    add_image = Image.open(ADD_ICON_PATH).resize((30, 30), Image.LANCZOS)
    add_icon = ImageTk.PhotoImage(add_image)
    remove_image = Image.open(REMOVE_ICON_PATH).resize((30, 30), Image.LANCZOS)
    remove_icon = ImageTk.PhotoImage(remove_image)
except (FileNotFoundError, IOError):
    add_icon = None
    remove_icon = None

# Boutons pour ajouter, supprimer et ouvrir les favoris
add_button = Button(main_window, image=add_icon, command=on_add_bookmark, compound='left')
add_button.pack(pady=5)

remove_button = Button(main_window, image=remove_icon, command=on_remove_bookmark, compound='left')
remove_button.pack(pady=5)

open_button = Button(main_window, text="Ouvrir", command=on_open_bookmark)
open_button.pack(pady=5)

# Initialisation de la liste des favoris
refresh_bookmark_list()

# Fonction pour lancer le systray
def run_systray():
    def quit_application(icon, item):
        icon.stop()
        main_window.quit()

    def toggle_main_window(icon, item):
        if main_window.state() == "withdrawn":
            main_window.after(0, main_window.deiconify)
        else:
            main_window.after(0, main_window.withdraw)

    def open_browser_choice(icon, item):
        main_window.after(0, choose_browser)

    # Menu pour le systray
    menu = Menu(
        MenuItem("Afficher/Cacher", toggle_main_window),
        MenuItem("Choisir Navigateur", open_browser_choice),
        MenuItem("Quitter", quit_application)
    )

    systray_icon = Icon("SimplyLaunch", Image.open(ICON_PATH), menu=menu)
    systray_icon.run()

# Lancer le systray dans un thread secondaire
def start_systray():
    threading.Thread(target=run_systray, daemon=True).start()

# Lancement du systray
start_systray()

# Lancement de l'interface graphique principale
main_window.mainloop()
