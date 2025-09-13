# 🤖 Git Auto-Flow
**Automatisation Git intelligente avec Multi-IA (Gemini + Groq) et Gestion de Projets GitHub**

Simplifiez votre workflow Git avec des commits conventionnels, des PRs générés par IA, et la création de projets GitHub complets à partir de comptes-rendus de réunion.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-v0.15.0-blue.svg)](https://github.com/genix-x/git-auto-flow/releases/latest)

## Usine Numérique AIOps - De l'Idée à la Production en 3 Minutes

### Phase 1 : Planification Automatisée IA
**Création Automatique de Tickets**
- ✅ `git create-tickets meeting-notes.md` - Génération d'Issues depuis Compte-Rendu  
- ✅ Extraction automatique tâches + priorités + dépendances
- ✅ Estimation IA en jours + labels GitHub
- ✅ Gestion dependencies entre tickets via GitHub API

### Phase 2 : Développement Accéléré  
**Workflow Git Intelligent**
- ✅ `git feature-start ma-feature` - Branch + link automatique issue
- ✅ `git ca --force` - Commit IA + Scan Sécurité Gitleaks
- ✅ `git pr --force --auto-merge --closes 42` - PR auto-mergée + ferme issue

### Phase 3 : Production Continue
**Pipeline Autonome** 
- ✅ `git deploy --force` - Release develop → main auto-taggée
- ✅ Tests + Sécurité + Documentation automatiques
- ✅ Monitoring intégré des métriques de développement

---

### ⚡ **Challenge 3 Minutes : Meeting → Production**

```bash
#  1. PLANIFICATION (45s) - De la réunion aux tickets
git create-tickets meeting-notes.md
# ↳ Analyse IA → 5 issues GitHub créées avec dépendances

# ⚡ 2. DÉVELOPPEMENT (90s) - Code prêt pour prod  
git feature-start auth-system --issue 42
echo "// Votre code ici" > auth.py
git ca --force                           # Commit IA + scan secrets
git pr --force --auto-merge --closes 42  # PR mergée + issue fermée

#  3. PRODUCTION (45s) - En ligne automatiquement
git checkout develop
git deploy --force                       # Release v1.2.0 auto-taggée sur main
# ↳ Pipeline CI/CD → Application en production ✅
```
**Résultat : ROI 95% - De la réunion au code déployé sans intervention manuelle !**

## Gestion Complète de Projets - Meeting to Production

### Création Automatique de Tickets IA
**Transformez vos réunions en roadmap structurée :**

```bash
#  Depuis un compte-rendu → Issues GitHub complètes
git create-tickets meeting-notes.md

#  Multi-repo support  
git create-tickets notes.md --repo genix-x/mon-projet

#  Mode diagnostic complet
git create-tickets notes.md --debug
```
**Intelligence Artificielle Intégrée :**

- **Analyse sémantique** : Extraction automatique tâches, priorités, blocages
- **️Labellisation smart** : priority-high, enhancement, bug selon contexte  
- **Dépendances automatiques** : Détection "l'API dépend de l'auth"
- **⏱️ Estimation IA** : Story points basés sur complexité détectée
- **✅ Validation interactive** : Confirmation avant création GitHub

### Format Meeting Notes Optimisé
```markdown
# Réunion Sprint Planning - 2025-01-15

##  Fonctionnalités Prioritaires  
- Système d'authentification OAuth2 (critique)
- Dashboard utilisateur temps réel  
- API REST mobile avec rate limiting
- Suite tests unitaires complète

## ⚠️ Dépendances Techniques
- API mobile dépend de l'auth OAuth  
- Tests E2E dépendent de l'API finalisée
- Dashboard nécessite API metrics

##  Objectifs Sprint
- Auth system → delivery semaine 1
- API REST → delivery semaine 2  
- Tests coverage → minimum 80%
```

### Output Automatique :
✅ 4 issues GitHub créées automatiquement:
   - `#123 [PRIORITY-HIGH] Système Auth OAuth2 (est: 5j)` 
   - `#124 [ENHANCEMENT] Dashboard utilisateur (est: 3j, depends: #123)`
   - `#125 [FEATURE] API REST mobile (est: 4j, depends: #123)` 
   - `#126 [TESTING] Suite tests unitaires (est: 2j, depends: #124,#125)`

- **Dépendances détectées et configurées dans GitHub**
- **⏱️ Estimations totales : 14 jours développement**
- **Sprint planifié automatiquement !**

## Workflow AIOps Complet - Version Ultime

```bash
#  ÉTAPE 1 : Setup Projet (30s)
git repo-create mon-super-projet --force    # Repo + GitFlow + README + v0.1.0

#  ÉTAPE 2 : Planification IA (60s)  
git create-tickets meeting-notes.md         # Meeting → Issues avec dépendances

# ⚡ ÉTAPE 3 : Développement Ultra-Rapide (90s/feature)
git feature-start auth-system               # Auto-link avec issue #123
git ca --force                              # Commit IA + Gitleaks protection  
git pr --force --auto-merge --closes 123    # PR mergée + issue fermée ✅

#  ÉTAPE 4 : Production Automatique (60s)
git checkout develop && git deploy --force  # Release v1.1.0 sur main

# ♻️ ÉTAPE 5 : Répéter pour chaque issue
git feature-start dashboard && git ca --force && git pr --force --closes 124
git feature-start api-mobile && git ca --force && git pr --force --closes 125
```

### Métriques Real-Time :
- **⏱️ Time to Market** : Meeting → Production = < 4 min/feature
- **️Sécurité** : 100% commits scannés (Gitleaks intégré)  
- **Qualité** : Standards conventionnels garantis IA
- **Automatisation** : 95% tâches manuelles éliminées

## Position dans l'Architecture

Cette structure présente un **pipeline logique et fluide** :
`Meeting Notes → IA Analysis → GitHub Issues → Feature Branches → IA Commits → Auto PR → Production`
      `↓             ↓            ↓              ↓               ↓          ↓           ↓`
   `Phase 1       Phase 1      Phase 1        Phase 2         Phase 2    Phase 2    Phase 3`

**Avantages de cette approche :**
✅ **Flow naturel** : Suit le processus de développement réel  
✅ **Intégration parfaite** : Chaque tool nourrit le suivant  
✅ **Démonstration concrete** : Exemple end-to-end avec timing  
✅ **ROI mesurable** : Métriques claires de gain de temps  
✅ **Adoption facile** : Workflow familier mais automatisé

## 🎯 Fonctionnalités Actuelles

### ✅ Multi-IA avec Fallback Planifié
- **Gemini** (principal) - Gratuit et performant ✅
- **Groq** (fallback) -  En développement (prévu v0.16.0)
- Basculement automatique planifié pour robustesse

### ✅  **Project & Ticket Management (v0.6.0+)**
-  **Création complète de projets GitHub** (git repo-create)
-  **Génération automatique de tickets** depuis meetings (git create-tickets) 
- ️ **Setup automatisé** : repo + branches + README + première release
-  **Gestion des dépendances** entre tickets via GitHub API
-  **Estimation automatique** et labels priorité

### ✅ **PR Automation Avancée (v0.13.0+)**
- Auto-merge optionnel avec `--auto-merge`
- Mode force avec `--force` (skip confirmation)
- Contrôle suppression branches avec `--no-auto-delete`
- **Fermeture auto des issues avec `--closes <issue_number>`**
- Titre et description générés par IA
- Support mode draft et labels

### ✅ Commit Automation + Sécurité
- 🔒 **Scan automatique des secrets** avec Gitleaks avant chaque commit
- Analyse automatique du git diff avec IA
- Messages conventionnels (Angular standard)
- **Protection totale** : Bloque les commits contenant des clés API, mots de passe, etc.

## 🚀 Installation Ultra-Simple v0.15.0

**Installation interactive (recommandée) :**
```bash
git clone https://github.com/genix-x/git-auto-flow.git && cd git-auto-flow && ./install.sh
```
**Installation automatisée (CI/serveurs) :**
```bash
git clone https://github.com/genix-x/git-auto-flow.git && cd git-auto-flow && ./install.sh --non-interactive
```

## 🐛 Mode Debug
Pour diagnostiquer les problèmes ou voir les commandes exécutées en temps réel :

```bash
# PR avec debug (voir commandes gh, git)
git pr --debug
git pr-auto --debug
```

## 🔒 Sécurité Intégrée

### Protection Anti-Secrets avec Gitleaks
Chaque commit est automatiquement scanné pour détecter :
- 🔑 Clés API (AWS, Google, GitHub, etc.)
- 🔐 Mots de passe en dur dans le code
- 🎫 Tokens d'authentification

## 🚨 Troubleshooting

### "GitHub CLI non trouvé"
```bash
# Installation
brew install gh          # macOS
sudo apt install gh      # Ubuntu

# Authentification
gh auth login
```

## 🏗️ Architecture

```
git-auto-flow/                    # v0.15.0
├── install.sh                    # Installation + mode --non-interactive
├── src/
│   ├── git-commit-auto.py        # Commit IA + Gitleaks 
│   ├── git-pr-auto.py            # PR IA + auto-merge
│   ├── git-repo-create.py        # Création repo complet ⭐
│   ├── git-create-tickets.py     # Tickets depuis meetings ⭐
│   ├── git-release-auto.py       # Releases avec --force
│   └── git-project-config.py     # Config (gardé mais déprécié)
├── utils/
│   └── logger.py                 # Logger centralisé v0.7.0+
└── config/
```

## ⚙️ Configuration (.env.gitautoflow)

```bash
# APIs 
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key  #  Non supporté actuellement

# Organisation GitHub  
GITHUB_ORG=genix-x
WORKING_DIR=/Users/vous/projects/genix
GITHUB_BASE_URL=https://github.com/genix-x/
```

## 🎯 Roadmap
- ✅ v0.15.0 : Auto-merge PR + installation non-interactive
- ✅ v0.14.0 : Corrections deploy PR + suppression auto-branches
- ✅ v0.13.0 : Options --no-auto-delete et --force pour PR
- ✅ v0.11.0 : Workflow git-repo-create complet
- ✅ v0.10.0 : Création tickets avec dépendances GitHub API
- ✅ v0.9.0 : Mode force pour releases
- ✅ v0.8.0 : Workflow automatisé complet repo-create
- ✅ v0.7.0 : Commande git repo-create + docs
- ✅ v0.6.0 : Création automatique tickets depuis meetings
- ✅ v0.5.2 : Corrections commit messages

###  À Venir
-  v0.16.0 : Support complet Groq API (fallback multi-IA)
-  v0.17.0 : Templates de projets avancés
-  v0.18.0 : Dashboard web de gestion projets

---

**🚀 Git Auto-Flow - Plus jamais de commits mal formatés, de secrets exposés, ou de setup projet fastidieux ! 🔒✨**

*Développé avec ❤️ par Genix Team*