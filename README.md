# 🤖 Git Auto-Flow
**Automatisation Git intelligente avec Multi-IA (Gemini + Groq) et Gestion de Projets GitHub**

Simplifiez votre workflow Git avec des commits conventionnels, des PRs générés par IA, et la création de projets GitHub complets à partir de comptes-rendus de réunion.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-v0.15.0-blue.svg)](https://github.com/genix-x/git-auto-flow/releases/latest)

## Sommaire
- [Challenge 3 Minutes : Meeting → Production](#challenge-3-minutes--meeting--production)
- [Fonctionnalités Core](#fonctionnalités-core)
  - [Sécurité & Qualité Built-in](#sécurité--qualité-built-in)
- [Installation & Setup](#-installation--setup)
- [Guide Détaillé](#guide-détaillé)
  - [Project Management Avancé (`git create-tickets`)](#project-management-avancé-git-create-tickets)
  - [Exemples de Workflow](#exemples-de-workflow)
- [Configuration (.env.gitautoflow)](#️-configuration-envgitautoflow)
- [Roadmap](#-roadmap)

## Challenge 3 Minutes : Meeting → Production

```bash
#  Setup + Planification (60s)
git repo-create mon-projet --force
git create-tickets meeting-notes.md

# ⚡ Développement (90s/feature)  
git feature-start auth-system
git ca --force && git pr --force --auto-merge --closes 42

#  Production (30s)
git deploy --force  # v1.1.0 → main
```
**ROI : 95% temps gagné | Sécurité : 100% commits scannés**

## Fonctionnalités Core

| Feature | Commande | Description |
|---|---|---|
| **️Setup** | `git repo-create` | Repo + GitFlow + Release |
| **Planning** | `git create-tickets` | Meeting → Issues IA |
| **Dev** | `git ca --force` | Commit IA + Gitleaks |
| **Integration** | `git pr --force --auto-merge` | PR automation |
| **Deploy** | `git deploy --force` | Release sémantique |

### Sécurité & Qualité Built-in
- **Gitleaks** : Scan automatique des secrets à chaque commit
- **Standards** : Commits conventionnels (Angular) générés par IA
- **Multi-IA** : Fallback automatique de Gemini vers Groq pour une robustesse maximale

## 🚀 Installation & Setup

**Installation interactive (recommandée) :**
```bash
git clone https://github.com/genix-x/git-auto-flow.git && cd git-auto-flow && ./install.sh
```
**Installation automatisée (CI/serveurs) :**
```bash
git clone https://github.com/genix-x/git-auto-flow.git && cd git-auto-flow && ./install.sh --non-interactive
```
Le script configure Gitleaks, les dépendances Python et les alias Git automatiquement.

## Guide Détaillé

### Project Management Avancé (`git create-tickets`)

Transformez un compte-rendu de réunion en issues GitHub structurées en une seule commande.

```bash
# Analyser un fichier et créer les issues dans le repo courant
git create-tickets meeting-notes.md

# Spécifier un autre repo
git create-tickets notes.md --repo my-org/another-repo
```

L'IA se charge de :
- **Extraire** les tâches, priorités et dépendances.
- **Créer** les labels (`priority-high`, `bug`, `enhancement`).
- **Lier** les issues entre elles avec les dépendances GitHub.
- **Estimer** le temps de développement en jours.

### Exemples de Workflow

**Créer une simple PR pour l'issue #55:**
```bash
git feature-start fix-login-bug
git ca --force
git pr --closes 55
```

**Lancer un cycle complet de développement et merger automatiquement:**
```bash
git feature-start new-dashboard-feature
# ... coder la fonctionnalité ...
git ca --force
git pr --force --auto-merge --delete-branch --closes 56
```

## ⚙️ Configuration (.env.gitautoflow)

Le fichier `~/.env.gitautoflow` centralise votre configuration :
```bash
# Clés API (Gemini est prioritaire)
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key

# Configuration GitHub
GITHUB_ORG=your-github-org
WORKING_DIR=/path/to/your/projects
GITHUB_BASE_URL=https://github.com/
```

## 🎯 Roadmap
- ✅ v0.15.0 : Auto-merge PR + installation non-interactive
- ✅ v0.14.0 : Corrections deploy PR
- ✅ v0.13.0 : Options `--no-auto-delete` et `--force` pour PR
- ✅ v0.10.0 : Création tickets avec dépendances GitHub API
- ✅ v0.7.0 : Commande `git repo-create`

### À Venir
-  v0.16.0 : Support complet Groq API (fallback multi-IA)
-  v0.17.0 : Templates de projets avancés
-  v0.18.0 : Dashboard web de gestion projets

---

**🚀 Git Auto-Flow - Plus jamais de commits mal formatés, de secrets exposés, ou de setup projet fastidieux ! 🔒✨**

*Développé avec ❤️ par Genix Team*