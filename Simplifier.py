import json
import os
import win32com.client
import shutil
import threading
import subprocess
import sys
import ctypes
from tkinter import messagebox, Tk, Entry, Label, Button, Listbox, StringVar, Toplevel, BooleanVar, Checkbutton, Frame
from tkinter import Scrollbar, Menu as TkMenu
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageTk
from screeninfo import get_monitors
import time
import pygetwindow as gw
from pywinauto import Application


# Chemin du fichier JSON pour stocker les favoris et l'option de démarrage
JSON_PATH = "bookmarks.json"
ICON_PATH = "simplifier.png"
ADD_ICON_PATH = "add_icon.png"
REMOVE_ICON_PATH = "remove_icon.png"

# Initialise le fichier JSON s'il n'existe pas ou s'il est mal structuré
def initialize_bookmarks_file():
    if not os.path.exists(JSON_PATH):
        save_data({
            "bookmarks": [],
            "show_at_startup": True,
            "window_position": {"x": 100, "y": 100},
            "preferred_browser": "chrome"
        })

# Fonction pour charger les données du fichier JSON
def load_data():
    try:
        with open(JSON_PATH, 'r', encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Incorrect structure")
        return data
    except (json.JSONDecodeError, ValueError, FileNotFoundError):
        initialize_bookmarks_file()
        with open(JSON_PATH, 'r', encoding="utf-8") as f:
            return json.load(f)

# Fonction pour sauvegarder les données dans le fichier JSON
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
# Fonction pour ouvrir un favori dans le navigateur
def open_bookmark_in_position(url, screen_index, position):
    # Charge les données et configure le navigateur
    data = load_data()
    browser = data.get("preferred_browser", "chrome")
    browser_command = {}

    if is_browser_available("chrome"):
        browser_command["chrome"] = ["chrome", "--app=" + url]
    if is_browser_available("firefox"):
        browser_command["firefox"] = ["firefox", url]
    if is_browser_available("msedge"):
        browser_command["msedge"] = ["msedge", "--app=" + url]
    if is_browser_available("safari"):
        browser_command["safari"] = ["open", "-a", "Safari", url]

    # Lance le navigateur et récupère son processus pour obtenir le PID
    command = browser_command.get(browser, browser_command.get("chrome", ["chrome", "--app=" + url]))
    process = subprocess.Popen(command)
    pid = process.pid
    print(f"Navigateur ouvert avec PID : {pid}")

    # Pause pour donner le temps au navigateur de s’ouvrir
    time.sleep(2)

    # Récupérer la fenêtre du navigateur par PID
    app_window = None
    for window in gw.getAllWindows():
        if window._hWnd == pid:  # Vérification de l'identifiant PID (ou utilisation d’un autre attribut)
            app_window = window
            break

    if app_window:
        print(f"Fenêtre trouvée avec PID : {pid}")
        # Calcul des coordonnées de position
        monitors = get_monitors()
        monitor = monitors[screen_index]
        x, y, width, height = monitor.x, monitor.y, monitor.width, monitor.height
        half_width = width // 2
        half_height = height // 2

        if position == "HG":  # Haut Gauche
            width, height = half_width, half_height
        elif position == "HD":  # Haut Droit
            x += half_width
            width, height = half_width, half_height
        elif position == "BG":  # Bas Gauche
            y += half_height
            width, height = half_width, half_height
        elif position == "BD":  # Bas Droit
            x += half_width
            y += half_height
            width, height = half_width, half_height
        elif position == "G":  # Gauche
            width = half_width
        elif position == "D":  # Droite
            x += half_width
            width = half_width
        elif position == "fullscreen":
            pass  # Garde les valeurs par défaut pour l’écran entier

        # Positionner et redimensionner la fenêtre
        app_window.moveTo(x, y)
        app_window.resizeTo(width, height)
        print(f"Fenêtre positionnée à ({x}, {y}) avec dimensions {width}x{height}")
    else:
        print("Fenêtre non trouvée pour le processus PID donné.")


# Fonction pour afficher le menu contextuel
def show_context_menu(event):
    # Trouver l'URL du favori sélectionné
    selected = bookmark_listbox.curselection()
    if not selected:
        return
    item_text = bookmark_listbox.get(selected)
    url = item_text.split(" - ")[1]

    # Créer le menu contextuel
    context_menu = TkMenu(main_window, tearoff=0)  # Utilisez TkMenu ici

    # Ajouter les options pour chaque écran et position
    monitors = get_monitors()
    for i, monitor in enumerate(monitors):
        screen_menu = TkMenu(context_menu, tearoff=0)
        for position in ["HG", "HD", "BG", "BD", "fullscreen", "G", "D"]:
            screen_menu.add_command(
                label=position,
                command=lambda u=url, idx=i, pos=position: open_bookmark_in_position(u, idx, pos)
            )
        context_menu.add_cascade(label=f"Écran {i + 1}", menu=screen_menu)

    # Afficher le menu contextuel à la position du clic
    context_menu.post(event.x_root, event.y_root)


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

# Fonction pour rafraîchir la liste des favoris
def refresh_bookmark_list():
    bookmark_listbox.delete(0, 'end')
    data = load_data()
    for bookmark in data.get("bookmarks", []):
        bookmark_listbox.insert('end', f"{bookmark['name']} - {bookmark['url']}")

# Création de l'interface principale
main_window = Tk()
main_window.title("Gestionnaire de Favoris SimplyLaunch")
main_window.geometry("600x400")
main_window.attributes("-topmost", True)

# Chargement de l'icône de l'application
try:
    main_icon = ImageTk.PhotoImage(Image.open(ICON_PATH))
    main_window.iconphoto(False, main_icon)
except (FileNotFoundError, IOError):
    main_icon = None

# Variables Tkinter
title_var = StringVar()
url_var = StringVar()
show_at_startup_var = BooleanVar()

# Charger l'état de la case "Toujours afficher au démarrage"
data = load_data()
show_at_startup_var.set(data.get("show_at_startup", True))

# Structure principale de la fenêtre
main_frame = Frame(main_window, padx=10, pady=10)
main_frame.pack(fill="both", expand=True)

# Liste des favoris avec scrollbar
bookmark_frame = Frame(main_frame)
bookmark_frame.pack(side="left", fill="both", expand=True)
bookmark_listbox = Listbox(bookmark_frame, width=50, height=20)
bookmark_listbox.pack(side="left", fill="both", expand=True)
scrollbar = Scrollbar(bookmark_frame)
scrollbar.pack(side="right", fill="y")
bookmark_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=bookmark_listbox.yview)

# Lier le clic droit à l'événement pour afficher le menu contextuel
bookmark_listbox.bind("<Button-3>", show_context_menu)

# Panneau de commande (à droite)
command_frame = Frame(main_frame, padx=10)
command_frame.pack(side="right", fill="y")

# Champs d'entrée pour le titre et l'URL dans command_frame
title_label = Label(command_frame, text="Titre:")
title_label.pack(anchor="w")
title_entry = Entry(command_frame, textvariable=title_var, width=30)
title_entry.pack()

url_label = Label(command_frame, text="URL:")
url_label.pack(anchor="w")
url_entry = Entry(command_frame, textvariable=url_var, width=30)
url_entry.pack()

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
# Chemin du dossier Startup pour les applications lancées au démarrage
def get_startup_folder():
    return os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

# Crée ou supprime un raccourci pour lancer le programme au démarrage de Windows
def set_startup_launch(enable):
    startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    shortcut_path = os.path.join(startup_folder, "Simplifier.lnk")
    target = os.path.abspath(__file__)

    if enable:
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(shortcut_path)
            if shortcut:
                shortcut.TargetPath = target
                shortcut.WorkingDirectory = os.path.dirname(target)
                shortcut.IconLocation = target
                shortcut.save()
                print("Raccourci créé pour le démarrage automatique.")
            else:
                print("Erreur : Impossible de créer le raccourci.")
        except Exception as e:
            print("Erreur lors de la création du raccourci :", e)
    else:
        try:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                print("Raccourci supprimé du démarrage automatique.")
        except Exception as e:
            print("Erreur lors de la suppression du raccourci :", e)

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
add_button = Button(command_frame, image=add_icon, command=on_add_bookmark, compound='left', text="Ajouter", padx=5)
add_button.pack(pady=5, fill="x")

remove_button = Button(command_frame, image=remove_icon, command=on_remove_bookmark, compound='left', text="Supprimer", padx=5)
remove_button.pack(pady=5, fill="x")

open_button = Button(command_frame, text="Ouvrir", command=on_open_bookmark)
open_button.pack(pady=5, fill="x")

# Case à cocher "Toujours afficher au démarrage"
def on_show_at_startup_toggle():
    data = load_data()
    current_state = data.get("launch_at_startup", False)
    new_state = not current_state
    data["launch_at_startup"] = new_state
    save_data(data)
    set_startup_launch(new_state)
    return new_state

# Initialisation de la liste des favoris
def refresh_bookmark_list():
    bookmark_listbox.delete(0, 'end')
    data = load_data()
    for bookmark in data.get("bookmarks", []):
        bookmark_listbox.insert('end', f"{bookmark['name']} - {bookmark['url']}")

# Initialiser la liste des favoris
refresh_bookmark_list()
# Fonction pour créer le menu du systray
def run_systray():
    def quit_application(icon, item):
        icon.stop()
        main_window.destroy()

    def toggle_launch_at_startup():
        # Charger les données actuelles depuis le fichier JSON
        data = load_data()
        
        # Récupérer l'état actuel de "launch_at_startup" et le basculer
        current_state = data.get("launch_at_startup", False)
        new_state = not current_state
        data["launch_at_startup"] = new_state
        
        # Sauvegarder les modifications dans le fichier JSON
        save_data(data)
        
        # Créer ou supprimer le raccourci dans le dossier de démarrage en fonction du nouvel état
        set_startup_launch(new_state)
        
        # Retourner le nouvel état pour mettre à jour le menu
        return new_state

    def toggle_main_window(icon, item=None):
        if main_window.state() == "withdrawn":
            main_window.after(0, main_window.deiconify)
        else:
            main_window.after(0, main_window.withdraw)

    def open_browser_choice(icon, item):
        main_window.after(0, choose_browser)

    # Créer un élément de menu avec l'état de démarrage
    def create_launch_menu_item():
        data = load_data()
        launch_enabled = data.get("launch_at_startup", False)
        return MenuItem(
            f"Lancer au démarrage {'✔' if launch_enabled else ''}",
            lambda: toggle_launch_at_startup() and icon.update_menu()
        )

    # Menu pour le systray (utilise Menu de pystray)
    menu = Menu(
        MenuItem("Afficher/Cacher", toggle_main_window),
        MenuItem("Choisir Navigateur", open_browser_choice),
        create_launch_menu_item(),  # Ajout du menu pour le démarrage auto
        MenuItem("Quitter", quit_application)
    )

    systray_icon = Icon("SimplyLaunch", Image.open(ICON_PATH), menu=menu, on_double_click=toggle_main_window)
    systray_icon.run()

def on_close():
    main_window.withdraw()

main_window.protocol("WM_DELETE_WINDOW", on_close)
# Fonction pour démarrer le systray dans un thread secondaire
def start_systray():
    threading.Thread(target=run_systray, daemon=True).start()

start_systray()

# Double-clic pour ouvrir le bookmark
def on_double_click(event):
    selected = bookmark_listbox.curselection()
    if selected:
        item_text = bookmark_listbox.get(selected)
        url = item_text.split(" - ")[1]
        open_bookmark(url)

bookmark_listbox.bind("<Double-1>", on_double_click)

# Initialiser et lancer l'interface principale

# Affichage conditionnel au démarrage
if show_at_startup_var.get():
    main_window.deiconify()
else:
    main_window.withdraw()

# Lancer la fenêtre principale
main_window.mainloop()
