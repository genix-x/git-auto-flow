

````markdown
# GAF - Gestion Automatisée de Fonctionnalités

Un client **CLI** écrit en Python avec [Typer](https://typer.tiangolo.com/) et packagé en binaire via Nuitka/PyInstaller.  
Support de **l’auto-update** via [tufup](https://github.com/dennisvang/tufup).

---

## 🚀 Installation & Setup

### 1. Initialiser le projet
```bash
uv init
````

### 2. Créer un environnement virtuel

```bash
uv venv
```

### 3. Installer les dépendances

```bash
uv add typer[all] tufup
```

### 4. Activer l’environnement

```bash
source .venv/bin/activate
```

*(Sur Windows : `.\.venv\Scripts\activate`)*

---

## 🛠️ Développement

Lancer le client en local :

```bash
python gaf.py --help
```

Exemples :

```bash
python gaf.py init
python gaf.py release
python gaf.py branch pull-request
python gaf.py branch pr   # alias
python gaf.py repo create
python gaf.py repo update
```

---

## 📦 Build en binaire

### Nuitka

```bash
python -m nuitka --onefile --output-filename=gaf gaf.py
./gaf --help
```

### PyInstaller (optionnel)

```bash
pyinstaller --onefile gaf.py
./dist/gaf --help
```

---

## 🔄 Auto-update avec tufup

L’intégration de [tufup](https://github.com/dennisvang/tufup) permet au client de vérifier et télécharger automatiquement les mises à jour sécurisées.

Exemple minimal :

```python
import tufup

def check_for_update():
    updater = tufup.Updater(
        app_name="gaf",
        current_version="0.1.0",
        update_url="https://mon-serveur-updates/gaf/"
    )
    updater.run()
```

À l’exécution, le client pourra :

* vérifier si une version plus récente existe,
* télécharger la mise à jour,
* remplacer l’exécutable automatiquement.

---

## 📖 Commandes disponibles

* `gaf init` → Initialiser un projet
* `gaf release` → Créer une release
* `gaf branch pull-request` → Créer une PR
* `gaf branch pr` → Alias pour `pull-request`
* `gaf issue` → Gérer les issues (placeholder)
* `gaf repo create` → Créer un dépôt
* `gaf repo update` → Mettre à jour un dépôt

---

## ✅ Roadmap

* [ ] Ajout des fonctionnalités réelles dans chaque commande
* [ ] Intégration complète de `tufup` pour les mises à jour OTA
* [ ] Tests automatisés
* [ ] Publication de releases précompilées (Linux, Mac, Windows)

---

```

---

👉 Veux-tu que je t’ajoute aussi une **section Makefile** dans le README (genre `make build`, `make run`, `make update`) pour automatiser tout ça ?
```
