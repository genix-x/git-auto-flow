# 🤖 Git Auto-Flow
**Automation Git intelligente avec Multi-IA (Gemini + Groq) + Gestion de Projets GitHub**

Simplifiez votre workflow Git avec des commits conventionnels, des PRs générés automatiquement par IA, et créez vos projets GitHub complets depuis une réunion. Compatible avec toute équipe et projet.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Multi-IA](https://img.shields.io/badge/AI-Gemini%20%2B%20Groq-green.svg)](https://github.com/genix-x/git-auto-flow)

## 🎯 Fonctionnalités

### ✅ Multi-IA avec Fallback Intelligent
- **Gemini** (priorité 1) - Gratuit et performant
- **Groq** (fallback) - API gratuite de secours
- Basculement automatique en cas de quota dépassé

### ✅ Commit Automation + Sécurité
- 🔒 **Scan automatique des secrets** avec Gitleaks avant chaque commit
- Analyse automatique du git diff avec IA
- Messages conventionnels (Angular standard)
- Support scopes, breaking changes, issues
- Confirmation interactive
- **Protection totale** : Bloque automatiquement les commits contenant des clés API, mots de passe, tokens

### ✅ PR Automation
- Titre et description générés par IA
- Rebase automatique avant création
- Push sécurisé `--force-with-lease`
- Support mode draft et labels

### ✅ 🆕 **Project Management**
- 🎯 **Création complète de projets GitHub depuis une réunion**
- 📋 Génération automatique de tickets/issues
- 🏗️ Configuration de repositories avec branches protégées
- 📁 Organisation automatique des projets dans votre workspace

### ✅ Workflow Complet
- Une seule commande: rebase + commit + PR
- Gestion intelligente des conflits
- Intégration GitHub CLI

## 🚀 Installation Ultra-Simple

**1 commande = Installation complète**
```bash
# Cloner + installer en 1 fois
git clone https://github.com/genix-x/git-auto-flow.git && cd git-auto-flow && ./install.sh
```

**C'est tout ! 🎉**

Le script va :
- ✅ Installer Gitleaks (sécurité anti-secrets) via brew ou téléchargement
- ✅ Demander vos clés API (Gemini + Groq) - optionnel
- ✅ Installer les dépendances Python automatiquement
- ✅ Configurer tous les alias Git avec nettoyage automatique
- ✅ 🆕 Configurer la gestion de projets GitHub
- ✅ Créer la branche develop si nécessaire
- ✅ Activer l'auto-suppression des branches après merge

### 🔗 Obtenir les clés API (optionnel)
- **Gemini**: https://makersuite.google.com/app/apikey (gratuit)
- **Groq**: https://console.groq.com/keys (gratuit, 1000 calls/mois)

## 🆕 Gestion de Projets - Workflow Réunion
```bash
# 🏗️ 1. Configuration initiale (une seule fois)
git pc                        # Configuration interactive

# 🎯 2. Créer repository GitHub uniquement  
git repo-create mon-api       # ✅ Disponible maintenant

# 🚧 3. Ou projet complet (bientôt)
git project-create mon-app    # (À implémenter - Ticket #2)

# 🚀 4. L'équipe commence immédiatement
git feature-start login-page
git ca
git pr
```

## ✨ Workflow ultra-court
```bash
git feature-start ma-feature  # Nouvelle feature
git ca                        # Commit auto
git pr                        # PR auto
git pc                        # 🆕 Configuration projet
```

## 📖 Guide d'utilisation

### 🔥 Workflow Ultra-Rapide
```bash
# 1. Démarrer une nouvelle feature
git feature-start ma-super-feature

# 2. Développement...
# ... coding ...

# 3. Commit avec rebase automatique + IA
git ca                 # (git commit-auto en long)

# 4. Continuer le développement...
git ca                 # Rebase + IA à chaque fois

# 5. Finaliser et créer PR
git pr                 # (git pr-create-auto en long)

# ✨ Le nettoyage est automatique ! 
# git feature-start nettoie déjà tout (local + remote)

# ✅ Résultat: Workflow complet automatisé !
```

###  Création de Repository GitHub
```bash
# 1. Configurer une fois
git pc                      # Organisation + workspace

# 2. Créer repository GitHub uniquement
git repo-create mon-backend

# 3. Ou avec confirmation forcée
git repo-create mon-frontend --force

# ✅ Résultat : Repository créé sur votre organisation
#  Lien GitHub affiché + prochaines étapes suggérées
```

### 🆕 Workflow Réunion → Développement
```bash
# 🎯 En réunion
git pc                        # Config organisation/workspace
git project-create dashboard  # Création complète (bientôt)

# 🚀 Post-réunion - L'équipe développe
cd ~/projects/genix/dashboard  # Auto-navigué
git feature-start auth-system
git ca                        # Commit IA
git pr                        # PR automatique
```

## 🛠️ Commandes Disponibles

| Commande | Alias | Description | Usage |
|----------|-------|-------------|-------|
| **🆕 Gestion de Projets** | | | |
| `git project-config` | `git pc` |  Configuration interactive projets | `git pc` |
| `git repo-create <nom>` | - |  Créer repository GitHub seul | `git repo-create mon-api` |
| `git project-create <nom>` | - |  Créer projet complet (bientôt) | `git project-create mon-app` |
| **Workflow Git** | | | |
| `git feature-start <nom>` | - | Créer nouvelle feature + nettoyage auto | `git feature-start auth-system` |
| `git commit-auto` | `git ca` | Commit + rebase + IA | `git ca` (recommandé) |
| `git pr-create-auto` | `git pr` | Créer PR auto | `git pr` (recommandé) |
| `git feature-finish` | - | Finaliser feature | `git feature-finish` |

### 🆕 Gestion de Configuration
```bash
# Voir la configuration actuelle
git pc --show

# Configuration interactive
git pc

# Configuration silencieuse (pour scripts)
git pc --org genix-x --workdir ~/projects/genix --template web-app
```

### 🧹 Nettoyage Automatique
`git feature-start` fait automatiquement :
- ✅ Fetch + prune : Synchronise avec origin
- ✅ Supprime branches locales mergées dans main ou develop
- ✅ Supprime branches remote mergées sur GitHub
- ✅ Créé nouvelle feature depuis develop propre

**Résultat : Workspace 100% clean à chaque nouvelle feature ! 🎯**

### ⚙️ Options Avancées
```bash
# Mode draft
git pr-auto --draft

# Branche cible différente  
git pr-auto --base main

# Workflow complet avec options
git pr-create-auto --base main --draft

# 🆕 Configuration avec debug
git pc --debug
```

## 🐛 Mode Debug
Pour diagnostiquer les problèmes ou voir les commandes exécutées en temps réel :

```bash
# Commit avec debug (voir toutes les commandes git/gitleaks)
git ca --debug
git commit-auto --debug

# PR avec debug (voir commandes gh, git)
git pr --debug
git pr-auto --debug

# 🆕 Configuration avec debug
git pc --debug

# Release avec debug (voir tout le processus)
python3 src/git-release-auto.py --debug
```

**Exemples de sortie debug :**
```
🐛 Mode DEBUG activé
🐛 DEBUG (gitleaks scan): gitleaks detect --log-opts=--since=1.hour.ago --verbose --exit-code 1
🐛 DEBUG (get current branch): git branch --show-current
🐛 DEBUG (commit): git commit -m 'feat(api): add user authentication'
🐛 DEBUG (push branch): git push origin feature/auth
🐛 DEBUG (create PR): gh pr create --base develop --title "..." --body "..."
```

**Quand utiliser le debug :**
- ❌ Erreurs de gitleaks ou permissions
- ❌ Problèmes de rebase ou conflits
- ❌ Échecs de création PR
- �� Comprendre le workflow interne

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
git add config.js

# Git Auto-Flow vous protège automatiquement !
git ca

�� Scan sécurité des secrets...
🚨 SECRETS DÉTECTÉS:
Finding:     sk-1234567890abcdef
Secret:      sk-1234567890abcdef
RuleID:      generic-api-key
Entropy:     3.5
File:        config.js
Line:        1
Fingerprint: config.js:generic-api-key:1

❌ Scan sécurité échoué - commit bloqué pour votre protection!
```

**✅ Résultat : Votre secret ne sera JAMAIS commité !**

### 💡 Comment Corriger
1. Supprimez le secret du fichier
2. Utilisez les variables d'environnement à la place
3. Recommitez - le scan passera ✅

```bash
# Correction sécurisée
echo "API_KEY=process.env.MY_API_KEY" > config.js
git ca  # ✅ Scan réussi, commit autorisé !
```

## 🤖 Intelligence Artificielle

### Multi-IA avec Fallback
```bash
# Ordre de priorité automatique:
1. 🚀 Gemini (google-generativeai) - Priorité 1
2. ⚡ Groq (groq) - Fallback automatique
3. ❌ Erreur si aucune API disponible
```

**Gestion Intelligente :**
- ✅ Détection automatique des quotas dépassés
- ✅ Basculement transparent vers l'IA de secours
- ✅ Messages informatifs sur l'IA utilisée
- ✅ Optimisation des prompts par IA

## 🚨 Troubleshooting

### "Aucune IA disponible"
```bash
# Vérifier les clés API
cat ~/.env.gitautoflow | grep -E "(GEMINI|GROQ)"

# Tester la connectivité
python3 -c "import google.generativeai as genai; print('Gemini OK')"
python3 -c "import groq; print('Groq OK')"
```

### "Erreur de rebase"
```bash
# Résoudre manuellement
git status
git add .                # Après résolution des conflits
git rebase --continue
```

### "GitHub CLI non trouvé"
```bash
# Installation
brew install gh          # macOS
sudo apt install gh      # Ubuntu

# Authentification
gh auth login
```

## 🎯 Workflow Complet

### 📊 Schéma du Git Flow
```
feature/auth-system ─────┐
feature/user-profile ────┤
feature/dashboard ───────┤
feature/api-integration ─┴──► develop ──┐                (PR #1)
                                        │
                                        ├──► main ──► 🚀 v0.2.0
                                        │
feature/notifications ───┐              │
feature/search-filters ──┤              │
feature/dark-mode ───────┤              │
feature/mobile-ui ───────┴──► develop ──┤                (PR #2)
                                        │
                                        ├──► main ──► 🚀 v0.3.0
                                        │
feature/performance ─────┐              │
feature/analytics ───────┤              │
feature/admin-panel ─────┴──► develop ──┤                (PR #3)
                                        │
                                        ├──► main ──► 🚀 v0.4.0
```

**🔄 Cycle de Release :**
```
   1️⃣ Features (5) ──► develop ──► main ──► 🚀 v0.2.0
   2️⃣ Features (4) ──► develop ──► main ──► 🚀 v0.3.0  
   3️⃣ Features (3) ──► develop ──► main ──► 🚀 v0.4.0
```

### ⚡ Workflow en Action
```bash
# Développeur A 
git feature-start auth-system    # 🧹 Nettoie + crée branche
git ca                          # 📝 Commit IA 
git pr                          # 🔄 PR vers develop

# Développeur B (en parallèle)
git feature-start user-profile  # 🧹 Nettoie + crée branche  
git ca                          # 📝 Commit IA
git pr                          # 🔄 PR vers develop

# Release Manager
git checkout develop
git pr --base main              # 🚀 Release PR develop → main
# Merge = auto-release v0.2.0 !
```

## 🏗️ Architecture
```
git-auto-flow/
├── install.sh                # Installation automatique
├── README.md                 # Cette documentation
├── requirements.txt          # Dépendances Python
├── src/                      # Code source
│   ├── lib/                  # Bibliothèques communes
│   │   ├── ai_provider.py    # 🤖 Gestionnaire Multi-IA
│   │   ├── gemini_client.py  # Client Gemini
│   │   ├── groq_client.py    # Client Groq (fallback)
│   │   └── git_utils.py      # Utilitaires Git
│   ├── git-commit-auto.py    # Commit automation
│   ├── git-pr-auto.py        # PR automation
│   ├── git-pr-create-auto.py # Workflow complet
│   ├── git-release-auto.py   # Release automation
│   ├──  git-project-config.py # Configuration projets
│   └──  git-repo-create.py    # Création repository GitHub
├── bin/                      # Scripts shell (optionnels)
└── config/
    └── git-aliases           # Aliases Git traditionnels
```

## 🆕 Configuration Projet (.env.gitautoflow étendu)
```bash
# APIs existantes
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key

# 🆕 Nouvelle section projets  
GITHUB_ORG=genix-x
WORKING_DIR=/Users/vous/projects/genix
GITHUB_BASE_URL=https://github.com/genix-x/
DEFAULT_PROJECT_TEMPLATE=web-app
```

## 🎯 Roadmap
- ✅ v0.5.0 : Configuration de projets (git pc)
- ✅ v0.5.1 : Création repository GitHub (git repo-create)
- 🔄 v0.6.0 : Création automatique de projets complets (git project-create)
- 📋 v0.7.0 : Génération de tickets/issues
- 🏗️ v0.8.0 : Templates de projets avancés

## 🎉 Avantages
- 🔒 **Sécurité Ultime** : Scan automatique des secrets - ZÉRO risque de fuite !
- 🤖 **Zéro réflexion** : L'IA analyse et génère tout
- ⚡ **Ultra-rapide** : 1 commande = workflow complet
- 🛡️ **Protection Totale** : Rebase + push intelligent + détection secrets
- 🎯 **Standards** : Commits/PRs conventionnels garantis
- 🔄 **Robuste** : Fallback multi-IA automatique
- 👥 **Équipe** : Package réutilisable sur tous projets
- 🆕 **🎯 Gestion Complète** : De la réunion au code déployé !

---

**🚀 Git Auto-Flow - Plus jamais de commits mal formatés, de secrets exposés, ou de setup projet fastidieux ! 🔒✨**

*Développé avec ❤️ par Genix Team*