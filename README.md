
# SimplyLaunch - Gestionnaire de Favoris

SimplyLaunch est une application de gestion des favoris développée en Python avec une interface graphique Tkinter. Elle permet de stocker, ouvrir, et gérer vos liens favoris facilement, en incluant la possibilité d'utiliser des icônes personnalisées pour les actions (ajout, suppression, etc.).

## Fonctionnalités

- Ajouter et supprimer des favoris.
- Ouvrir un favori dans le navigateur préféré.
- Interface utilisateur avec un design simple.
- Application en mode systray, avec la possibilité de masquer/afficher la fenêtre principale.
- Paramètre "Toujours afficher au démarrage".
- Utilisation de différentes icônes pour représenter les actions.

## Installation

### Prérequis

- Python 3.x
- Bibliothèques Python nécessaires : `tkinter`, `pystray`, `Pillow`

Vous pouvez installer les dépendances en utilisant `pip` avec la commande suivante :

```bash
pip install pillow pystray
```

### Cloner le dépôt

Clonez ce dépôt sur votre machine locale :

```bash
git clone https://github.com/votre-utilisateur/simplylaunch.git
cd simplylaunch
```

### Exécution de l'application

Pour exécuter l'application en mode développement, lancez simplement le script Python principal :

```bash
python bookmarks_manager.py
```

## Création d'un exécutable indépendant (portable)

Pour générer un exécutable indépendant en utilisant PyInstaller :

1. Installez PyInstaller si ce n'est pas déjà fait :

   ```bash
   pip install pyinstaller
   ```

2. Exécutez la commande suivante pour créer un exécutable :

   ```bash
   pyinstaller --onefile --windowed --icon=simplifier.ico --add-data "add_icon.png;." --add-data "remove_icon.png;." bookmarks_manager.py
   ```

   - `--onefile` : Crée un fichier exécutable unique.
   - `--windowed` : Supprime la console (recommandé pour les applications avec interface graphique).
   - `--icon=simplifier.ico` : Utilise une icône personnalisée pour l'application.
   - `--add-data` : Inclut les fichiers nécessaires (`add_icon.png` et `remove_icon.png`) dans l'exécutable.

   L'exécutable final sera généré dans le dossier `dist`.

## Utilisation

1. **Ajouter un favori** : Entrez un titre et une URL valide, puis cliquez sur le bouton "Ajouter".
2. **Supprimer un favori** : Sélectionnez un favori dans la liste, puis cliquez sur le bouton "Supprimer".
3. **Ouvrir un favori** : Sélectionnez un favori dans la liste, puis cliquez sur le bouton "Ouvrir". Vous pouvez également double-cliquer sur un favori pour l'ouvrir.
4. **Systray** : L'application se réduit dans la barre système (systray). Vous pouvez la masquer/afficher en cliquant sur l'icône dans le systray.

## Capture d'écran

<details>
<summary>Exemple d'interface</summary>

Insérez ici des captures d'écran de l'interface, comme l'affichage principal de l'application, le menu du systray, etc.
</details>

## Structure du projet

```
simplylaunch/
├── bookmarks_manager.py  # Code principal de l'application
├── simplifier.ico        # Icône de l'application
├── add_icon.png          # Icône pour le bouton ajouter
├── remove_icon.png       # Icône pour le bouton supprimer
└── README.md             # Documentation de l'application
```

## Configuration des préférences

Un fichier `bookmarks.json` est utilisé pour stocker les favoris et les paramètres de l'application :

- `show_at_startup` : Indique si l'application doit s'afficher au démarrage.
- `bookmarks` : Liste des favoris enregistrés avec leurs titres et URL.

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à forker le projet, proposer des améliorations ou signaler des bugs via des issues sur GitHub.

## Licence

Ce projet est sous licence MIT. Consultez le fichier LICENSE pour plus de détails.
