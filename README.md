# 🤖 Git Auto-Flow

**Automation Git intelligente avec Multi-IA (Gemini + Groq)**

Simplifiez votre workflow Git avec des commits conventionnels et des PRs générés automatiquement par IA. Compatible avec toute équipe et projet.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Multi-IA](https://img.shields.io/badge/AI-Gemini%20%2B%20Groq-green.svg)](https://github.com/genix-x/git-auto-flow)

## 🎯 Fonctionnalités

✅ **Multi-IA avec Fallback Intelligent**
- **Gemini** (priorité 1) - Gratuit et performant
- **Groq** (fallback) - API gratuite de secours
- Basculement automatique en cas de quota dépassé

✅ **Commit Automation**
- Analyse automatique du `git diff` avec IA
- Messages conventionnels (Angular standard)
- Support scopes, breaking changes, issues
- Confirmation interactive

✅ **PR Automation**
- Titre et description générés par IA
- Rebase automatique avant création
- Push sécurisé `--force-with-lease`
- Support mode draft et labels

✅ **Workflow Complet**
- Une seule commande: rebase + commit + PR
- Gestion intelligente des conflits
- Intégration GitHub CLI

## 🚀 Installation Rapide

### **1. Dans votre projet**
```bash
# Ajouter en submodule
git submodule add https://github.com/genix-x/git-auto-flow.git .git-auto-flow

# Installer (une seule fois)
./.git-auto-flow/install-alias.sh
```

### **2. Configuration des APIs**
```bash
# Créer .git-auto-flow/.env
GEMINI_API_KEY=votre_cle_gemini
GROQ_API_KEY=votre_cle_groq
```

**🔗 Obtenir les clés:**
- **Gemini**: https://makersuite.google.com/app/apikey (gratuit)
- **Groq**: https://console.groq.com/keys (gratuit, 1000 calls/mois)

### **3. Utilisation immédiate**
```bash
git add .
git cz-auto              # ✨ Commit automatique
git pr-create-auto       # ✨ PR automatique
```

## 📖 Guide d'utilisation

### **🔥 Workflow Ultra-Rapide**
```bash
# 1. Démarrer une nouvelle feature
git feature-start ma-super-feature

# 2. Développement...
# ... coding ...

# 3. Commit avec rebase automatique + IA
git commit-auto        # ou: git ca (alias court)

# 4. Continuer le développement...
git commit-auto        # Rebase + IA à chaque fois

# 5. Finaliser et créer PR
git pr-create-auto

# ✅ Résultat: Workflow complet automatisé !
```

### **🛠️ Commandes Disponibles**

| Commande | Description | Usage |
|----------|-------------|--------|
| `git feature-start <nom>` | Créer nouvelle feature | `git feature-start auth-system` |
| `git commit-auto` | Commit + rebase + IA | `git commit-auto` (auto-stage) |
| `git ca` | Alias court | `git ca` (même chose) |
| `git feature-finish` | Finaliser feature | `git feature-finish` |
| `git pr-create-auto` | **Créer PR auto** | `git pr-create-auto` |

### **⚙️ Options Avancées**

```bash
# Mode draft
git pr-auto --draft

# Branche cible différente  
git pr-auto --base main

# Workflow complet avec options
git pr-create-auto --base main --draft
```

## 🏗️ Architecture

```
git-auto-flow/
├── install-alias.sh          # Installation automatique
├── README.md                 # Cette documentation
├── requirements.txt          # Dépendances Python
├── src/                      # Code source
│   ├── lib/                  # Bibliothèques communes
│   │   ├── ai_provider.py    # 🤖 Gestionnaire Multi-IA
│   │   ├── gemini_client.py  # Client Gemini
│   │   ├── groq_client.py    # Client Groq (fallback)
│   │   └── git_utils.py      # Utilitaires Git
│   ├── git-cz-auto-v2.py     # Commit automation
│   ├── git-pr-auto.py        # PR automation
│   └── git-pr-create-auto.py # Workflow complet
├── bin/                      # Scripts shell (optionnels)
│   ├── git-cz-auto.sh
│   ├── git-pr-auto.sh
│   └── git-pr-create-auto.sh
└── config/
    └── git-aliases           # Aliases Git traditionnels
```

## 🤖 Intelligence Artificielle

### **Multi-IA avec Fallback**
```python
# Ordre de priorité automatique:
1. 🚀 Gemini (google-generativeai) - Priorité 1
2. ⚡ Groq (groq) - Fallback automatique
3. ❌ Erreur si aucune API disponible
```

### **Gestion Intelligente**
- ✅ Détection automatique des quotas dépassés
- ✅ Basculement transparent vers l'IA de secours
- ✅ Messages informatifs sur l'IA utilisée
- ✅ Optimisation des prompts par IA

## 🚨 Troubleshooting

### **"Aucune IA disponible"**
```bash
# Vérifier les clés API
cat .git-auto-flow/.env

# Tester la connectivité
python3 -c "import google.generativeai as genai; print('Gemini OK')"
python3 -c "import groq; print('Groq OK')"
```

### **"Erreur de rebase"**
```bash
# Résoudre manuellement
git status
git add .                # Après résolution des conflits
git rebase --continue
```

### **"GitHub CLI non trouvé"**
```bash
# Installation
brew install gh          # macOS
sudo apt install gh      # Ubuntu

# Authentification
gh auth login
```

## 🎉 Avantages

- **🤖 Zéro réflexion** : L'IA analyse et génère tout
- **⚡ Ultra-rapide** : 1 commande = workflow complet  
- **🔒 Sécurisé** : Rebase + push intelligent
- **🎯 Standards** : Commits/PRs conventionnels garantis
- **🔄 Robuste** : Fallback multi-IA automatique
- **👥 Équipe** : Package réutilisable sur tous projets

---

**🚀 Git Auto-Flow - Plus jamais de commits mal formatés !** ✨

*Développé avec ❤️ par [Genix Team](https://github.com/genix-x)*