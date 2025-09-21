# 🚀 Git Auto-Flow v2.0

**🏭 Usine Numérique AIOps - De l'Idée à la Production en 3 Minutes**

AIOps = Intelligence Artificielle + Automatisation DevOps. Git Auto-Flow transforme votre pipeline en un cerveau autonome qui code, teste et déploie.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![UV](https://img.shields.io/badge/UV-Package%20Manager-green.svg)](https://github.com/astral-sh/uv)
[![Typer CLI](https://img.shields.io/badge/CLI-Typer-purple.svg)](https://typer.tiangolo.com)
[![AI Powered](https://img.shields.io/badge/AI-Gemini%20%7C%20Groq-orange.svg)](https://ai.google.dev)

## ⚡ Workflow AIOps Ultra-Rapide (Challenge 3 min)

```bash
# 1. Setup (30s)
git clone https://github.com/votre-org/git-auto-flow.git
cd git-auto-flow/new-project && uv sync && source .venv/bin/activate
gitautoflow repo create mon-utilisateur/mon-projet --force

# 2. Développement (60s)
cd ~/workspace/mon-projet
gitautoflow fs ma-feature --force
# ... Votre code ici ...

# 3. Déploiement (90s)
gitautoflow ac --force                    # Commit IA + Scan Sécurité
gitautoflow pr --force                    # PR auto-mergée vers develop
gitautoflow ra --version 1.0.0 --force   # Release develop → main → binaires
```

**Architecture GitFlow AIOps :** `main` ← `develop` ← `feature/*`

**✅ ROI Immédiat : 95% de Temps Gagné + Binaires Multi-Arch Automatiques**

## 🎯 Commandes Disponibles

```
╭─ Commands ────────────────────────────────────────────────────────────────────╮
│ auto-commit     Commit automatique avec rebase + IA (alias: ac)              │
│ auto-pr         Créer automatiquement une PR avec IA (alias: pr)             │
│ feature-start   Démarre une nouvelle feature branch GitFlow (alias: fs)      │
│ version         Affiche la version du projet                                 │
│ issue           Commandes de gestion des issues GitHub                       │
│ release         Commandes d'automatisation des releases                      │
│ repo            Commandes de gestion des repositories GitHub                 │
╰───────────────────────────────────────────────────────────────────────────────╯
```

## 🏗️ Gestion Complète des Repositories

```bash
# Créer un repository complet (GitFlow + Release v0.1.0)
gitautoflow repo create utilisateur/projet

# Supprimer un repository (sécurisé avec double confirmation)
gitautoflow repo delete ancien-projet --force
```

## 🎫 Issues depuis Compte-Rendu IA

```bash
# Analyser un CR de réunion et créer les tickets GitHub
gitautoflow issue create meeting-notes.md

# Pour un autre repository
gitautoflow issue create notes.md --repo genix-x/mon-projet
```

**Fonctionnalités :**
- 🧠 Analyse IA du compte-rendu → extraction tâches/priorités
- 🏷️ Création labels GitHub (priority-high, enhancement, etc.)
- 🔗 Gestion dépendances entre tickets
- ⏱️ Estimation automatique en jours

## 🚀 Releases Multi-Arch Automatiques

```bash
# Release automatique complète (version calculée par IA)
gitautoflow release auto

# Release avec version forcée (ex: passage en v1.0)
gitautoflow ra --version 1.0.0 --force

# Prévisualiser la prochaine version
gitautoflow release next-version
```

**À chaque release, génération automatique de :**
```
📦 gitautoflow-linux-x64           # Linux Intel/AMD
📦 gitautoflow-linux-arm64         # Linux ARM
📦 gitautoflow-macos-x64           # macOS Intel
📦 gitautoflow-macos-arm64         # macOS M1/M2
📦 gitautoflow-windows-x64.exe     # Windows
📋 checksums.txt                   # SHA256
```

## ⚡ Workflow Ultra-Automatisé Complet

**🏭 Du Meeting au Code Déployé :**

```bash
# 🎯 1. Créer projet complet depuis 0
gitautoflow repo create mon-super-projet    # Repo + GitFlow + README + v0.1.0

# 📋 2. Générer tickets depuis CR réunion
gitautoflow issue create meeting-notes.md   # IA → Issues GitHub avec dépendances

# ⚡ 3. Dev cycle ultra-rapide (pour l'issue #42)
gitautoflow fs auth-system                  # Feature branch
gitautoflow ac --force                      # Commit IA + Gitleaks scan
gitautoflow pr --force --closes 42          # PR qui ferme l'issue #42 ✅

# ♻️ 4. Répéter pour chaque ticket
gitautoflow fs dashboard && gitautoflow ac && gitautoflow pr --force

# 🚀 5. Release automatique avec binaires
gitautoflow ra --version 2.0.0 --force     # → Release + binaires multi-arch
```

**Résultat : De la réunion au code en prod avec binaires distribués ! ⚡**

## 🚀 Installation

La méthode recommandée est d'utiliser le script d'installation qui détecte automatiquement votre système d'exploitation (macOS ou Linux) et votre architecture (Intel ou ARM) pour télécharger le binaire approprié depuis les releases GitHub.

### Installation (macOS / Linux)

Exécutez la commande suivante dans votre terminal. Le script gère les droits `sudo` si nécessaire et sauvegarde toute version existante.

```bash
OWNER=genix-x REPO=git-auto-flow BINARY_PREFIX=gitautoflow INSTALL_NAME=gitautoflow \
  curl -sL https://raw.githubusercontent.com/genix-x/git-auto-flow/main/install.sh | bash
```

### Installer une version spécifique

Pour installer une version précise, ajoutez la variable `VERSION` (remplacez `v2.0.1` par la version souhaitée) :

```bash
OWNER=genix-x REPO=git-auto-flow BINARY_PREFIX=gitautoflow INSTALL_NAME=gitautoflow VERSION=v2.0.1 \
  curl -sL https://raw.githubusercontent.com/genix-x/git-auto-flow/main/install.sh | bash
```

### Désinstallation

Pour supprimer le binaire de votre système :

```bash
curl -sL https://raw.githubusercontent.com/genix-x/git-auto-flow/main/install.sh | bash -- --uninstall
```

### Installation pour le développement

Si vous souhaitez contribuer au projet, vous pouvez l'installer localement :
- **Prérequis :** Python 3.11+, UV, GitHub CLI (`gh auth login`)
- **Installation :**
  ```bash
  git clone https://github.com/genix-x/git-auto-flow.git
  cd git-auto-flow && uv sync && source .venv/bin/activate
  gitautoflow --help
  ```

## ⚙️ Configuration

### GitHub CLI (Requis)
```bash
gh auth login && gh auth status
```

### Clés API IA (Optionnel - Fallback automatique)
```bash
# Créez ~/.env.gitautoflow
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here
WORKING_DIR=/home/user/workspace
```

## 🎯 Avantages v2.0

- 🔒 **Sécurité Ultime** : Scan GitLeaks automatique - ZÉRO risque de fuite
- 🤖 **Zéro Réflexion** : IA analyse et génère tout automatiquement
- ⚡ **Ultra-Rapide** : 1 commande = workflow complet
- 🏗️ **Setup Complet** : Repository → Release → Binaires en 3 minutes
- 🎫 **Issues IA** : Compte-rendus → Tickets GitHub automatiquement
- 📦 **Binaires Multi-Arch** : Linux/macOS/Windows générés à chaque release
- 🛠️ **Architecture Moderne** : Typer + UV + Rich + GitHub Actions
- 🔄 **Renommage Facile** : 1 ligne pour changer le nom du binaire

## 🔄 Renommage du Binaire

```bash
# Éditez pyproject.toml - changez juste cette ligne :
[project.scripts]
mon-nom = "gitautoflow.cli.main:main"  # ← Votre nom ici

# Appliquez
uv sync && mon-nom --help  # ✅ Nouveau nom !
```

*Script automatisé et détails dans [RENAME.md](RENAME.md)*

---

<div align="center">

**🚀 Git Auto-Flow v2.0 - Plus jamais de setup fastidieux ! Binaires inclus ! 🔒✨**

[⭐ Star ce projet](https://github.com/votre-org/git-auto-flow) | [🐛 Issues](https://github.com/votre-org/git-auto-flow/issues) | [💡 Discussions](https://github.com/votre-org/git-auto-flow/discussions) | [📦 Releases](https://github.com/votre-org/git-auto-flow/releases)

*Développé avec ❤️ par l'équipe Git Auto-Flow*

</div>