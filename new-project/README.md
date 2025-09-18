# 🚀 Git Auto-Flow v2.0

**Outils de développement Git/GitHub nouvelle génération avec IA intégrée**

Workflow ultra-simplifié : créez des repos complets et commitez avec l'IA en une seule commande.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![UV](https://img.shields.io/badge/UV-Package%20Manager-green.svg)](https://github.com/astral-sh/uv)
[![Typer CLI](https://img.shields.io/badge/CLI-Typer-purple.svg)](https://typer.tiangolo.com)
[![AI Powered](https://img.shields.io/badge/AI-Gemini%20%7C%20Groq-orange.svg)](https://ai.google.dev)

## 📑 Sommaire

- [⚡ Workflow Ultra-Rapide](#-workflow-ultra-rapide)
- [🚀 Installation](#-installation)
- [🏗️ Créer un Repository](#️-créer-un-repository-complet)
- [🌿 Feature Start](#-feature-start)
- [🤖 Commit Automatique avec IA](#-commit-automatique-avec-ia)
- [🚀 Pull Request Automatique avec IA](#-pull-request-automatique-avec-ia)
- [⚙️ Configuration](#️-configuration)
- [🔄 Renommage du Binaire](#-renommage-du-binaire)

## ⚡ Workflow Ultra-Rapide

**Challenge 2 minutes - De zéro à repository en production :**

```bash
# 1. Installation (30s)
git clone https://github.com/votre-org/git-auto-flow.git
cd git-auto-flow/new-project && uv sync && source .venv/bin/activate

# 2. Créer projet complet (60s)
gitautoflow repo create monusername/super-projet --force

# 3. Développer avec feature branch, commiter et créer PR avec IA (30s)
cd ~/workspace/super-projet
gitautoflow fs ma-feature --force
# ... votre code ici ...
gitautoflow ac --force
gitautoflow pr --force

# ✅ Résultat: Repository GitHub + GitFlow + Release v0.1.0 + Commit IA + PR IA !
```

**🎯 ROI Immédiat : 95% de temps gagné sur la création et gestion de projets.**

## 🚀 Installation

### Prérequis
- **Python 3.11+**
- **UV Package Manager** ([installation](https://github.com/astral-sh/uv))
- **GitHub CLI** configuré (`gh auth login`)

### Installation rapide
```bash
# Clone et installation
git clone https://github.com/votre-org/git-auto-flow.git
cd git-auto-flow/new-project

# Installation avec UV (recommandé)
uv sync

# Méthode 1: Script d'activation automatique
./activate.sh

# Méthode 2: Activation manuelle
source .venv/bin/activate

# Vérification
gitautoflow --help
```

### 📋 Commandes Disponibles

```bash
gitautoflow --help
```

```
╭─ Commands ────────────────────────────────────────────────────────────────────╮
│ auto-commit     Commit automatique avec rebase + IA (alias: ac)              │
│ auto-pr         Créer automatiquement une PR avec IA (alias: pr)             │
│ feature-start   Démarre une nouvelle feature branch GitFlow (alias: fs)      │
│ version         Affiche la version du projet                                 │
│ repo            Commandes de gestion des repositories GitHub                 │
╰───────────────────────────────────────────────────────────────────────────────╯
```

## 🏗️ Créer un Repository Complet

### ⚡ Syntaxe Ultra-Simple

```bash
gitautoflow repo create OWNER/REPO-NAME [OPTIONS]
```

### 🎯 Ce qui est Créé Automatiquement

✅ **Repository GitHub** (privé/public)
✅ **Clone local** dans votre workspace
✅ **Branches GitFlow** : `main` + `develop`
✅ **README.md** avec template
✅ **Pull Requests** automatiques (feature → develop → main)
✅ **Release v0.1.0** avec tag Git
✅ **GitHub Actions** permissions configurées

### 🚀 Exemples

```bash
# Repository privé avec workflow complet
gitautoflow repo create genix-x/mon-api

# Repository public en mode force (sans confirmations)
gitautoflow repo create myorg/projet-open --public --force

# Format court (utilise config par défaut)
gitautoflow repo create mon-projet
```

### 📊 Options Disponibles

| Option | Description | Défaut |
|--------|-------------|--------|
| `OWNER/REPO-NAME` | Format explicite recommandé | - |
| `--private/--public` | Visibilité du repository | `private` |
| `--force, -f` | Mode non-interactif | `false` |
| `--debug` | Affiche les commandes exécutées | `false` |

## 🌿 Feature Start

Démarrez une nouvelle feature branch selon GitFlow en une seule commande.

### ⚡ Syntaxe Ultra-Simple

```bash
# Alias ultra-court (recommandé)
gitautoflow fs ma-feature

# Commande complète
gitautoflow feature-start ma-feature

# Avec options
gitautoflow fs api-refactor --base main --force --debug
```

### 🚀 Workflow GitFlow Automatique

1. **🔄 Sync avec base** : Mise à jour automatique de la branche de base (`develop`)
2. **🌿 Création branch** : `feature/ma-feature` depuis la base
3. **📤 Push upstream** : Configuration automatique du tracking distant
4. **✅ Prêt à développer** : Environnement configuré pour le développement

### 📊 Options Disponibles

| Option | Description | Défaut |
|--------|-------------|--------|
| `FEATURE-NAME` | Nom de la feature (sans `feature/`) | - |
| `--base, -b` | Branche de base | `develop` |
| `--force, -f` | Force la création/écrasement | `false` |
| `--debug` | Affiche les commandes Git exécutées | `false` |

### 🎯 Exemples d'Usage

```bash
# Feature standard depuis develop
gitautoflow fs auth-system

# Feature depuis une branche spécifique
gitautoflow fs hotfix --base main

# Force la création (écrase si existe)
gitautoflow fs new-ui --force

# Mode debug pour voir les commandes
gitautoflow fs api-v2 --debug
```

### 📺 Exemple de Sortie

```
🚀 Démarrage feature: auth-system
==================================================
INFO     Branche cible: feature/auth-system
INFO     Branche de base: develop

INFO     Basculement sur develop
INFO     Mise à jour de develop depuis origin
INFO     Création de la branche feature/auth-system
INFO     Push initial de feature/auth-system

✅ Feature branch créée: feature/auth-system
✅ Branche trackée sur origin
💡 Vous pouvez maintenant commencer à développer !
💡 Pour committer: gitautoflow ac
```

## 🤖 Commit Automatique avec IA

### ⚡ Syntaxe Ultra-Courte

```bash
# Aliases rapides (recommandés)
gitautoflow ac              # Ultra-court ⚡
gitautoflow auto-commit     # Explicite
```

### 🧠 Workflow IA Intelligent

1. **🔄 Rebase auto** : Sync avec `develop`/`main`
2. **🔒 Scan sécurité** : GitLeaks sur tous fichiers modifiés
3. **📁 Staging auto** : `git add .`
4. **🤖 Analyse IA** : Diff → Message Conventional Commits
5. **💾 Commit** : Message généré par IA
6. **📤 Push auto** : Vers branche courante

### 🎯 IA Multi-Provider avec Fallback

- **🥇 Gemini AI** (Google) - Provider principal
- **🥈 Groq** - Fallback automatique si Gemini indisponible
- **📝 Format** : Conventional Commits (`type(scope): description`)

### 🚀 Exemples

```bash
# Workflow interactif complet
gitautoflow ac

# Mode force (sans confirmation)
gitautoflow ac --force

# Mode debug (diagnostics détaillés)
gitautoflow ac --debug
```

### 📺 Exemple de Sortie

```
🤖 Git Auto-Commit avec IA
==============================
🔄 Étape 1: Synchronisation avec develop...
✅ Branche déjà à jour avec develop

🔄 Étape 2: Scan sécurité...
🔍 Scan GitLeaks sur 3 fichier(s) modifié(s)...
✅ Aucun secret détecté

🔄 Étape 3: Staging des fichiers...
✅ Fichiers stagés avec succès

🔄 Étape 4: Initialisation IA...
✅ Gemini AI actif

🔄 Étape 5: Analyse des changements...
🔄 Étape 6: Génération du commit...

📝 Commit proposé:
   feat(auth): add JWT token validation middleware

✅ Confirmer ce commit? (y/N): y
✅ Commit effectué avec succès!
📤 Push vers origin/feature/auth...
✅ Push effectué avec succès!

🎉 Processus terminé avec succès!
```

### 📊 Options Disponibles

| Option | Description | Usage |
|--------|-------------|-------|
| `--force, -f` | Skip confirmations | Mode CI/automatisé |
| `--debug` | Affiche les commandes exécutées | Diagnostics/troubleshooting |

## 🚀 Pull Request Automatique avec IA

Créez des Pull Requests parfaites avec analyse IA automatique et workflow complet.

### ⚡ Syntaxe Ultra-Simple

```bash
# Alias ultra-court (recommandé)
gitautoflow pr

# Commande complète
gitautoflow auto-pr

# Avec options avancées
gitautoflow pr --base main --merge --delete-branch --force
```

### 🤖 Workflow IA Intelligent

1. **🔄 Rebase auto** : Sync avec branche de base (`develop`/`main`)
2. **📤 Push auto** : Push de la branche feature
3. **🤖 Analyse IA** : Diff → Titre + Description + Labels
4. **📋 Création PR** : Pull Request générée par IA
5. **🔄 Auto-merge** (optionnel) : Merge automatique
6. **🗑️ Cleanup** (optionnel) : Suppression branche après merge

### 🎯 IA Multi-Provider avec Fallback

- **🥇 Gemini AI** (Google) - Provider principal
- **🥈 Groq** - Fallback automatique si Gemini indisponible
- **📝 Format** : Titre optimisé + description détaillée + labels pertinents

### 🚀 Exemples d'Usage

```bash
# PR standard vers develop
gitautoflow pr

# PR vers main en mode force
gitautoflow pr --base main --force

# PR avec auto-merge et suppression branche
gitautoflow pr --merge --delete-branch

# PR draft pour review
gitautoflow pr --draft

# PR qui ferme une issue
gitautoflow pr --closes 123

# Mode debug pour voir les commandes
gitautoflow pr --debug
```

### 📊 Options Disponibles

| Option | Description | Défaut |
|--------|-------------|--------|
| `--base, -b` | Branche de base pour la PR | `develop` |
| `--draft, -d` | Créer en mode draft | `false` |
| `--merge, -m` | Auto-merge après création | `false` |
| `--delete-branch, -D` | Supprimer branche après merge | `false` |
| `--closes` | Ferme l'issue #N automatiquement | - |
| `--force, -f` | Pas de confirmation | `false` |
| `--debug` | Affiche les commandes exécutées | `false` |

### 📺 Exemple de Sortie

```
🚀 Git Auto-PR avec IA
==================================================
INFO     ✅ Branche à jour avec develop
INFO     📤 Push vérifié
INFO     🔄 Initialisation IA...
🤖 APIs: ✅ Gemini
INFO     🔍 Analyse des changements vs develop...
INFO     🤖 Génération de la PR avec Multi-IA...

📋 PR proposée:
   Titre: feat(auth): add JWT token validation middleware
   Base: develop
   Labels: feature, enhancement

## Summary
This PR adds JWT token validation middleware to enhance API security.

## Changes
- Add JWT validation middleware
- Update authentication flow
- Add comprehensive tests
- Update documentation

## Test Plan
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual JWT validation testing

✅ Créer cette PR? (y/N): y
✅ PR créée avec succès: https://github.com/user/repo/pull/42

🎉 Success! PR disponible: https://github.com/user/repo/pull/42
```

### 🔄 Workflow de Développement Recommandé

```bash
# 1. Créer feature
gitautoflow fs ma-nouvelle-feature

# 2. Développer
# ... votre code ...

# 3. Commit avec IA
gitautoflow ac

# 4. Créer PR avec IA
gitautoflow pr

# 5. PR prête pour review ! 🎉
```

## ⚙️ Configuration

### 🔑 GitHub CLI (Requis)

```bash
# Authentification GitHub
gh auth login

# Vérification
gh auth status
```

### 🤖 Git Auto-Config

Git Auto-Flow configure automatiquement votre identité Git depuis GitHub lors du premier commit.

### 🔧 Variables d'Environnement (Optionnel)

Créez un `.env` pour personnaliser :

```bash
# Clés API IA (optionnel - fallback auto)
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here

# Configuration workspace
WORKING_DIR=/home/user/workspace
GITHUB_ORG=your-default-org
```

## 🔄 Renommage du Binaire

### ⚡ Renommage 1-Ligne

Pour renommer `gitautoflow` → `gaf` :

```toml
# Éditez pyproject.toml
[project.scripts]
gaf = "gitautoflow.cli.main:main"  # ← Changez juste ça
```

```bash
# Appliquez
uv sync
gaf --help  # ✅ Nouveau nom !
```

### 🤖 Script Automatisé

```bash
# Renommage complet automatisé
python scripts/rename-binary.py gaf

# Avec alias personnalisé
python scripts/rename-binary.py devtools dt

# Application
uv sync
```

**Voir [RENAME.md](RENAME.md) pour plus de détails.**

## 🎯 Avantages Git Auto-Flow v2.0

- 🔒 **Sécurité Ultime** : Scan GitLeaks automatique - ZÉRO risque de fuite !
- 🤖 **Zéro Réflexion** : IA analyse et génère tout automatiquement
- ⚡ **Ultra-Rapide** : 1 commande = workflow complet
- 🏗️ **Setup Complet** : Repository → Release en 60 secondes
- 🌿 **GitFlow Intégré** : Feature branches pro en 1 commande
- 🎯 **Standards Pro** : Conventional Commits garantis
- 🚀 **PR Automatiques** : Pull Requests parfaites générées par IA
- 🔄 **Robuste** : Multi-IA avec fallback automatique
- 🛠️ **Architecture Moderne** : Typer + UV + Rich
- 🔄 **Renommage Facile** : 1 ligne pour changer le nom du binaire

## 🤝 Contribution

1. **Fork** le projet
2. **Créer** une branche (`git checkout -b feature/amazing`)
3. **Commit** avec Git Auto-Flow (`gitautoflow ac`)
4. **Push** (`git push origin feature/amazing`)
5. **Pull Request**

---

<div align="center">

**🚀 Git Auto-Flow v2.0 - Plus jamais de setup fastidieux ou de commits mal formatés ! 🔒✨**

[⭐ Star ce projet](https://github.com/votre-org/git-auto-flow) | [🐛 Issues](https://github.com/votre-org/git-auto-flow/issues) | [💡 Discussions](https://github.com/votre-org/git-auto-flow/discussions)

*Développé avec ❤️ par l'équipe Git Auto-Flow*

</div>