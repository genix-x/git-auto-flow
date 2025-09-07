# 🔧 Dette technique - Git Auto-Flow

## 🏛️ Architecture & Configuration

### .ENV trop générique
**Problème :** Le fichier `.env` global pose problème avec plusieurs projets
**Solutions à explorer :**
- [ ] `.env` per-project (`.git-auto-flow.env`)
- [ ] Config hiérarchique : global → projet → local
- [ ] Detection automatique du contexte projet
**Priorité :** P1 (bloquant multi-projets)

---

## 🌿 Git Operations & Workflows

### Gestion des rebases automatiques
**Problème :** Conflits et échecs de rebase non gérés proprement
**Workflow à implémenter :**
- [ ] 1. Stash automatique des modifications non commitées
- [ ] 2. Checkout develop + pull origin/develop
- [ ] 3. Checkout feature-branch + rebase develop
- [ ] 4. Gestion des conflits avec prompt utilisateur
- [ ] 5. Auto-unstash si rebase success
**Priorité :** P1 (workflows cassés = adoption ❌)

### Auto-staging des fichiers
**Problème :** `git add .` n'est pas fait automatiquement
**Solutions :**
- [ ] Auto-detect fichiers modifiés non-stagés
- [ ] Prompt avant staging : "Fichiers à ajouter : [liste] - Confirmer ?"
- [ ] Option `--auto-stage` pour skip prompt
**Priorité :** P2

### Gestion intelligente des secrets & GitLeaks
**Problème :** Quand l'IA génère de la documentation avec des exemples de configuration, elle peut créer du contenu fictif (mots de passe d'exemple, clés API fictives, etc.) qui trigger GitLeaks
**Comportement attendu :** L'IA doit être consciente qu'elle génère du contenu fictif/éducatif
**Solutions intelligentes :**
- [ ] L'IA détecte automatiquement qu'elle crée du contenu fictif/exemple
- [ ] Auto-ajout dans `.gitleaksignore` avec commentaire explicatif
- [ ] Format : `# Exemple fictif généré par IA pour documentation - [date]`
- [ ] Warning à l'utilisateur : "🛡️ Contenu fictif détecté et ajouté à .gitleaksignore"
- [ ] Validation que c'est bien fictif (pas de vrais secrets)
**Priorité :** P1 (sécurité + UX critique)

---

## 🎫 Amélioration création de tickets

### Problèmes identifiés :
- [ ] Doublons exacts (même fichier → même tickets)
- [ ] Similarité sémantique (différents mots, même intention)
- [ ] Pas de vérification avec tickets existants GitHub

### Solutions à explorer :
- [ ] Cache local avec hash de fichier
- [ ] API GitHub pour détecter doublons
- [ ] IA pour détecter similarité sémantique
- [ ] Workflow interactif "Voulez-vous créer/fusionner/ignorer ?"
**Priorité :** P2 (après stabilisation core features)

---

## 🐛 **DETTE TECHNIQUE - Système de Logging**

### **❌ Problème actuel :**
- Utilisation de `print()` dans certains anciens fichiers
- Pas de niveaux de log uniformes partout

### **✅ Solution EN COURS :**
- **✅ Logger centralisé** dans `utils/logger.py` - CRÉÉ
- **✅ `git-repo-create.py`** - MIGRÉ vers logging
- **⚠️ `git-project-config.py`** - 15+ prints à convertir
- **⚠️ `git-new-project.py`** - 20+ prints à convertir

### **📈 Priorité :**
**MOYENNE** - Migration progressive en cours

### **⏱️ Estimation restante :**
**30min** - 2 fichiers à migrer

### **🎯 Prochaine étape :**
Migrer `git-project-config.py`

---

## 🎯 Priorités générales

**P0 - Bloquant :** Aucun pour l'instant
**P1 - Critique :** .ENV multi-projets, Rebases, GitLeaks intelligents
**P2 - Important :** Auto-staging, Tickets doublons, Migration logging
**P3 - Nice-to-have :** À définir

---


## 📦 Release Management & Documentation

### Synchronisation automatique du CHANGELOG.md
**Problème :** Le fichier CHANGELOG.md se duplique et n'est pas mis à jour avec les vraies releases GitHub
**Situation actuelle :** 
- ✅ `git release` génère parfaitement les GitHub Releases 
- ❌ CHANGELOG.md contient des doublons et versions incohérentes
- ❌ Pas de synchro entre le beau contenu des releases GitHub et le CHANGELOG.md

**Solutions à implémenter :**
- [ ] **Réutiliser l'API release existante** pour générer le CHANGELOG.md
- [ ] Nettoyer et reformater le CHANGELOG.md actuel (supprimer doublons)
- [ ] Après chaque `git release`, auto-update du CHANGELOG.md avec le contenu de la release GitHub
- [ ] Format cohérent : reprendre exactement le même contenu que les releases GitHub
- [ ] Validation : une seule source de vérité = GitHub Releases → CHANGELOG.md
**Priorité :** P1 (le CHANGELOG.md actuel est cassé/dupliqué)

**Note :** Ne pas refaire d'API, juste réutiliser ce qui marche déjà ! 🎯

---


*Dernière mise à jour : 2024-12-28*
