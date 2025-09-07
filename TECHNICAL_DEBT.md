##  **DETTE TECHNIQUE - Système de Logging**

### **❌ Problème actuel :**
- Utilisation de `print()` dans certains anciens fichiers
- Pas de niveaux de log uniformes partout

### **✅ Solution EN COURS :**
- **✅ Logger centralisé** dans `utils/logger.py` - CRÉÉ
- **✅ `git-repo-create.py`** - MIGRÉ vers logging
- **⚠️ `git-project-config.py`** - 15+ prints à convertir
- **⚠️ `git-new-project.py`** - 20+ prints à convertir

### **Priorité :**
**MOYENNE** - Migration progressive en cours

### **⏱️ Estimation restante :**
**30min** - 2 fichiers à migrer

### **Prochaine étape :**
Migrer `git-project-config.py`
