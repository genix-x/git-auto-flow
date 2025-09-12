# 🤖 Git Auto-Flow
**Automatisation Git intelligente avec Multi-IA (Gemini + Groq) et Gestion de Projets GitHub**

Simplifiez votre workflow Git avec des commits conventionnels, des PRs générés par IA, et la création de projets GitHub complets à partir de comptes-rendus de réunion.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-v0.15.0-blue.svg)](https://github.com/genix-x/git-auto-flow/releases/latest)

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
Le script v0.15.0 va :

✅ Installer Gitleaks (sécurité anti-secrets)
✅ Mode non-interactif pour automation
✅ Auto-merge PR configuré
✅ Configuration API simplifiée
✅ Workflow complet repo + tickets + releases

### 🔗 Obtenir les clés API (optionnel)
- **Gemini**: https://makersuite.google.com/app/apikey (gratuit)
- **Groq**: https://console.groq.com/keys (gratuit, non supporté actuellement)

##  Création Automatique de Tickets

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

- Analyse IA du compte-rendu de réunion
- Extraction automatique des tâches et priorités
- ️ Création des labels GitHub (priority-high, enhancement, etc.)
- Gestion des dépendances entre tickets
- ⏱️ Estimation automatique en jours
- Confirmation interactive avant création

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

## ⚡ Workflow Ultra-Automatisé v0.15.0

###  **Depuis Meeting → Code Déployé**
```bash
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
```
**Résultat : De la réunion au code en prod en quelques minutes ! ⚡**

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
# ~~git pc --debug~~ (déprécié)

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
-  Comprendre le workflow interne

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

 Scan sécurité des secrets...
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