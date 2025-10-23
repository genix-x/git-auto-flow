# 🎯 PLAN DE CORRECTION COMPLET

## 📋 Priorité 1 : Corrections critiques

### 1. Ajouter le build Windows au workflow GitHub Actions
- Ajouter Windows x64 dans la matrice du workflow
- Configurer le runner Windows
- Tester le build Windows

### 2. Corriger les URLs du repository dans README.md
- Remplacer 'votre-org' par 'genix-x'
- Mettre à jour tous les liens

### 3. Mettre à jour les alias de commandes
- Corriger 'gitautoflow ra' → 'gitautoflow release auto'
- Vérifier tous les alias dans la documentation

## 📋 Priorité 2 : Corrections de documentation

### 4. Mettre à jour BUILD.md
- Indiquer clairement que Windows n'est pas encore supporté OU
- Implémenter le support Windows

### 5. Corriger le script d'installation
- Vérifier que les variables correspondent aux noms réels des binaires

### 6. Mettre à jour pyproject.toml
- Vérifier la cohérence des métadonnées

## 📋 Priorité 3 : Améliorations

### 7. Nettoyer les tags problématiques
- Renommer 'vvv1.8.0' → 'v1.8.0' (comme demandé précédemment)

### 8. Vérifier la cohérence globale
- S'assurer que toute la documentation correspond à l'implémentation

## 🚀 Plan d'exécution

1. **Étape 1** : Ajouter Windows au workflow GitHub Actions
2. **Étape 2** : Corriger README.md (URLs et commandes)
3. **Étape 3** : Mettre à jour BUILD.md
4. **Étape 4** : Vérifier pyproject.toml
5. **Étape 5** : Renommer le tag vvv1.8.0
6. **Étape 6** : Tester une nouvelle release complète

## ✅ Résultat attendu

- ✅ Binaires Windows générés automatiquement
- ✅ Documentation cohérente avec la réalité
- ✅ URLs correctes partout
- ✅ Tags propres sans 'v' en double
- ✅ Workflow complet multi-plateforme
