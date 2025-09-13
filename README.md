License: MIT Python 3.8+ Version

 Usine Numérique AIOps - De l'Idée à la Production en 3 Minutes
AIOps = Intelligence Artificielle + Automatisation DevOps. Git Auto-Flow transforme votre pipeline en un cerveau autonome qui code, teste et déploie.

⚡ Workflow AIOps Ultra-Rapide (Challenge 3 min)

# 1. Setup (30s)
git clone https://github.com/genix-x/git-auto-flow.git && cd git-auto-flow && ./install.sh
git repo-create mon-projet --force

# 2. Développement (60s)
git feature-start ma-feature
# ... Votre code ici ...

# 3. Déploiement (90s)
git ca --force                     # Commit IA + Scan Sécurité
git pr --force --auto-merge        # PR auto-mergée vers develop
git deploy --force                 # Release de develop vers main (auto-tag)
Architecture GitFlow AIOps : main ← develop ← feature/*

✅ ROI Immédiat : 95% de Temps Gagné.

Création Automatique de Tickets
✅ Génération d'Issues depuis Compte-Rendu
# Analyser un CR de réunion et créer les tickets GitHub
git create-tickets meeting-notes.md

# Pour un autre repository
git create-tickets notes.md --repo genix-x/mon-projet

# Mode debug
git create-tickets notes.md --debug
Fonctionnalités :

Analyse IA du compte-rendu de réunion
Extraction automatique des tâches et priorités
️ Création des labels GitHub (priority-high, enhancement, etc.)
Gestion des dépendances entre tickets
⏱️ Estimation automatique en jours
Confirmation interactive avant création
Exemple de fichier meeting-notes.md :

# Réunion Planning Sprint

## Fonctionnalités à développer
- Système d'authentification avec OAuth
- Dashboard utilisateur avec stats
- API REST pour mobile
- Tests unitaires complets

## Points bloquants
- L'API dépend de l'auth
- Tests dépendent de l'API
Résultat : 4 issues GitHub créées avec labels, priorités et dépendances !

⚡ Workflow Ultra-Automatisé v0.15.0
Depuis Meeting → Code Déployé
#  1. Créer projet complet depuis 0
git repo-create mon-super-projet    # Repo + GitFlow + README + v0.1.0

#  2. Générer tickets depuis CR réunion  
git create-tickets meeting-notes.md # IA → Issues GitHub avec dépendances

#  3. Dev cycle ultra-rapide
git feature-start auth-system       # Feature branch
git ca                              # Commit IA + Gitleaks scan
git pr --auto-merge                 # PR auto-merged après CI ✅

# ♻️ 4. Répéter pour chaque ticket
git feature-start dashboard && git ca && git pr --force

#  5. Release automatique
git checkout develop  
git pr --base main --auto-merge     # → Auto-release v0.2.0 
Résultat : De la réunion au code en prod en quelques minutes ! ⚡

# 🤖 Git Auto-Flow
**Automatisation Git intelligente avec Multi-IA (Gemini + Groq) et Gestion de Projets GitHub**

Simplifiez votre workflow Git avec des commits conventionnels, des PRs générés par IA, et la création de projets GitHub complets à partir de comptes-rendus de réunion.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-v0.15.0-blue.svg)](https://github.com/genix-x/git-auto-flow/releases/latest)

## Sommaire
- [Fonctionnalités Core](#fonctionnalités-core)
  - [Sécurité & Qualité Built-in](#sécurité--qualité-built-in)
- [Installation & Setup](#-installation--setup)
- [Guide Détaillé](#guide-détaillé)
  - [Exemples de Workflow](#exemples-de-workflow)
- [Configuration (.env.gitautoflow)](#️-configuration-envgitautoflow)
- [Roadmap](#-roadmap)

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