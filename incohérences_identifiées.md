## 📋 LISTE DES INCOHÉRENCES IDENTIFIÉES

### 1. Binaire Windows manquant ❌
- **Documenté dans README.md** : '📦 gitautoflow-windows-x64.exe'
- **Réalité** : Aucun binaire Windows dans les releases v1.6.7
- **GitHub Actions** : Pas de build Windows dans le workflow

### 2. URL du repository incorrecte ❌
- **README.md** : 'https://github.com/votre-org/git-auto-flow.git'
- **Réalité** : 'https://github.com/genix-x/git-auto-flow.git'

### 3. Alias de commandes obsolètes ❌
- **README.md** : 'gitautoflow ra' (release auto)
- **Réalité** : La commande est 'gitautoflow release auto'

### 4. Script d'installation avec variables incorrectes ❌
- **README.md** : 'OWNER=genix-x REPO=git-auto-flow BINARY_PREFIX=gitautoflow'
- **GitHub Actions** : Les binaires sont nommés 'gitautoflow-*' mais le script utilise 'BINARY_PREFIX=gitautoflow'

### 5. Documentation de build vs réalité ❌
- **BUILD.md** : Mentionne Windows mais pas implémenté
- **Scripts** : Le script build-binary.sh supporte Windows mais pas le workflow GitHub

### 6. Métadonnées de projet ❌
- **pyproject.toml** : À vérifier pour cohérence

### 7. Workflow GitHub Actions incomplet ❌
- **Actuel** : Linux x64/arm64, macOS x64/arm64
- **Manquant** : Windows x64
