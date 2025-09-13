# 🤖 Git Auto-Flow
**Automatisation Git intelligente avec Multi-IA (Gemini + Groq) et Gestion de Projets GitHub**

Simplifiez votre workflow Git avec des commits conventionnels, des PRs générés par IA, et la création de projets GitHub complets à partir de comptes-rendus de réunion.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-v0.15.0-blue.svg)](https://github.com/genix-x/git-auto-flow/releases/latest)

## 📑 Sommaire
- [🏭 Usine Numérique AIOps](#-usine-numérique-aiops---de-lidée-à-la-production-en-3-minutes)
- [📋 Création Automatique de Tickets](#-création-automatique-de-tickets)  
- [🚀 Installation](#-installation-ultra-simple)
- [🎯 Fonctionnalités Complètes](#-fonctionnalités-actuelles)
- [🐛 Debug & Troubleshooting](#-mode-debug)
- [🔒 Sécurité](#-sécurité-intégrée)  
- [⚙️ Configuration](#️-configuration)
- [🗺️ Roadmap](#-roadmap)

## 🏭 Usine Numérique AIOps - De l'Idée à la Production en 3 Minutes

**AIOps = Intelligence Artificielle + Automatisation DevOps.** Git Auto-Flow transforme votre pipeline en un cerveau autonome qui code, teste et déploie.

### ⚡ Workflow AIOps Ultra-Rapide (Challenge 3 min)

```bash
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
```

**Architecture GitFlow AIOps :** `main` ← `develop` ← `feature/*`

**✅ ROI Immédiat : 95% de Temps Gagné.**

## 📋 Création Automatique de Tickets

### ✅ Génération d'Issues depuis Compte-Rendu

```bash
# Analyser un CR de réunion et créer les tickets GitHub
git create-tickets meeting-notes.md

# Pour un autre repository
git create-tickets notes.md --repo genix-x/mon-projet

# Mode debug
git create-tickets notes.md --debug
```

**Fonctionnalités :**
- 🧠 Analyse IA du compte-rendu de réunion
- 📊 Extraction automatique des tâches et priorités
- 🏷️ Création des labels GitHub (priority-high, enhancement, etc.)
- 🔗 Gestion des dépendances entre tickets
- ⏱️ Estimation automatique en jours
- ✅ Confirmation interactive avant création

**Exemple de fichier `meeting-notes.md` :**
```markdown
# Réunion Planning Sprint

## Fonctionnalités à développer
- Système d'authentification avec OAuth
- Dashboard utilisateur avec stats
- API REST pour mobile
- Tests unitaires complets

## Points bloquants
- L'API dépend de l'auth
- Tests dépendent de l'API
```

**Résultat : 4 issues GitHub créées avec labels, priorités et dépendances !**

### ⚡ Workflow Ultra-Automatisé v0.15.0

#### 🏭 Depuis Meeting → Code Déployé

```bash
# 🎯 1. Créer projet complet depuis 0
git repo-create mon-super-projet    # Repo + GitFlow + README + v0.1.0

# 📋 2. Générer tickets depuis CR réunion  
git create-tickets meeting-notes.md # IA → Issues GitHub avec dépendances

# ⚡ 3. Dev cycle ultra-rapide (pour l'issue #42)
git feature-start auth-system       # Feature branch
git ca                              # Commit IA + Gitleaks scan
git pr --auto-merge --closes 42     # PR qui ferme l'issue #42 en mergant ✅

# ♻️ 4. Répéter pour chaque ticket
git feature-start dashboard && git ca && git pr --force

# 🚀 5. Release automatique
git checkout develop  
git pr --base main --auto-merge     # → Auto-release v0.2.0 
```

**Résultat : De la réunion au code en prod en quelques minutes ! ⚡**

## 🚀 Installation Ultra-Simple

**Installation interactive (recommandée) :**
```bash
git clone https://github.com/genix-x/git-auto-flow.git && cd git-auto-flow && ./install.sh
```

**Installation automatisée (CI/serveurs) :**
```bash
git clone https://github.com/genix-x/git-auto-flow.git && cd git-auto-flow && ./install.sh --non-interactive
```

Le script v0.15.0 configure automatiquement :
- ✅ Gitleaks (protection anti-secrets)
- ✅ Dépendances Python et alias Git
- ✅ Mode auto-merge pour les PRs
- ✅ API keys et workflow complet

### 🔗 Obtenir les clés API (optionnel)
- **Gemini**: https://makersuite.google.com/app/apikey (gratuit)
- **Groq**: https://console.groq.com/keys (gratuit, prévu v0.16.0)

## 🎯 Fonctionnalités Actuelles

### ✅ Multi-IA avec Fallback Planifié
- **Gemini** (principal) - Gratuit et performant ✅
- **Groq** (fallback) - 🔄 En développement (prévu v0.16.0)
- Basculement automatique planifié pour robustesse maximale

### ✅ 🏗️ **Project & Ticket Management**
- 🎯 **Création complète de projets GitHub** (`git repo-create`)
- 📋 **Génération automatique de tickets** depuis meetings (`git create-tickets`) 
- ⚙️ **Setup automatisé** : repo + branches + README + première release
- 🔗 **Gestion des dépendances** entre tickets via GitHub API
- 📊 **Estimation automatique** et labels priorité

### ✅ 🔄 **PR Automation Avancée**
- 🤖 Auto-merge optionnel avec `--auto-merge`
- ⚡ Mode force avec `--force` (skip confirmation)
- 🌿 Contrôle suppression branches avec `--no-auto-delete`
- 🎯 **Fermeture auto des issues avec `--closes <issue_number>`**
- 📝 Titre et description générés par IA
- 📋 Support mode draft et labels

### ✅ 💻 **Commit Automation + Sécurité**
- 🔒 **Scan automatique des secrets** avec Gitleaks avant chaque commit
- 🧠 Analyse automatique du git diff avec IA
- 📏 Messages conventionnels (Angular standard)
- 🛡️ **Protection totale** : Bloque les commits contenant des clés API, mots de passe, etc.

## 🐛 Mode Debug

Pour diagnostiquer les problèmes ou voir les commandes exécutées en temps réel :

```bash
# Commit avec debug (voir toutes les commandes git/gitleaks)
git ca --debug

# PR avec debug (voir commandes gh, git)
git pr --debug

# Release avec debug (voir tout le processus)
python3 src/git-release-auto.py --debug
```

**Quand utiliser le debug :**
- ❌ Erreurs de gitleaks ou permissions
- ❌ Problèmes de rebase ou conflits
- ❌ Échecs de création PR
- 🔍 Comprendre le workflow interne

### 🚨 Troubleshooting

**"Aucune IA disponible"**
```bash
# Vérifier les clés API
cat ~/.env.gitautoflow | grep -E "(GEMINI|GROQ)"
```

**"GitHub CLI non trouvé"**  
```bash
# Installation + Authentification
brew install gh && gh auth login        # macOS
sudo apt install gh && gh auth login    # Ubuntu
```

## 🔒 Sécurité Intégrée

### Protection Anti-Secrets avec Gitleaks
Chaque commit est automatiquement scanné pour détecter :
- 🔑 Clés API (AWS, Google, GitHub, etc.)
- 🔐 Mots de passe en dur dans le code
- 🎫 Tokens d'authentification
- 📧 Adresses email privées
- 🛡️ Certificats SSL et clés privées

### 🚨 Exemple de Protection en Action
```bash
# Vous ajoutez accidentellement une clé API
echo "API_KEY=sk-1234567890abcdef" > config.js
git ca

# 🛡️ Git Auto-Flow vous protège automatiquement !
🚨 SECRETS DÉTECTÉS:
❌ Scan sécurité échoué - commit bloqué pour votre protection!
```

**✅ Correction sécurisée :**
```bash
echo "API_KEY=process.env.MY_API_KEY" > config.js
git ca  # ✅ Scan réussi, commit autorisé !
```

## ⚙️ Configuration

**Fichier `~/.env.gitautoflow` :**
```bash
# APIs 
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key  # 🔄 Non supporté actuellement

# Organisation GitHub  
GITHUB_ORG=genix-x
WORKING_DIR=/Users/vous/projects/genix
GITHUB_BASE_URL=https://github.com/genix-x/
```

## 🗺️ Roadmap

### ✅ **Versions Disponibles**
- v0.15.0 : Auto-merge PR + installation non-interactive
- v0.14.0 : Corrections deploy PR + suppression auto-branches
- v0.13.0 : Options --no-auto-delete et --force pour PR
- v0.11.0 : Workflow git-repo-create complet
- v0.10.0 : Création tickets avec dépendances GitHub API
- v0.6.0 : Création automatique tickets depuis meetings

### 🔮 **À Venir**
- 🚀 v0.16.0 : Support complet Groq API (fallback multi-IA)
- 📋 v0.17.0 : Templates de projets avancés
- 🖥️ v0.18.0 : Dashboard web de gestion projets

---

## 🎉 Avantages

- 🔒 **Sécurité Ultime** : Scan automatique des secrets - ZÉRO risque de fuite !
- 🤖 **Zéro réflexion** : L'IA analyse et génère tout
- ⚡ **Ultra-rapide** : 1 commande = workflow complet
- 🛡️ **Protection Totale** : Rebase + push intelligent + détection secrets
- 🎯 **Standards** : Commits/PRs conventionnels garantis
- 🔄 **Robuste** : Fallback multi-IA automatique
- 👥 **Équipe** : Package réutilisable sur tous projets
- 🎯 **Gestion Complète** : De la réunion au code déployé !

---

**🚀 Git Auto-Flow - Plus jamais de commits mal formatés, de secrets exposés, ou de setup projet fastidieux ! 🔒✨**

*Développé avec ❤️ par Genix Team*