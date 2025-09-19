# 🏗️ Guide de Build - Binaires Multi-Architecture

Ce projet utilise **Nuitka** pour générer des binaires standalone pour plusieurs plateformes.

## 🚀 Build Automatique (GitHub Actions)

### À chaque release

Quand tu crées une release avec `gitautoflow release auto`, le système génère automatiquement :

```
gitautoflow-linux-x64          # Linux Intel/AMD
gitautoflow-linux-arm64        # Linux ARM (Raspberry Pi, etc.)
gitautoflow-macos-x64          # macOS Intel
gitautoflow-macos-arm64        # macOS M1/M2
gitautoflow-windows-x64.exe    # Windows
checksums.txt                  # Checksums SHA256
```

### Test sur chaque push/PR

Le workflow de test vérifie que le build fonctionne sur toutes les plateformes.

## 🔧 Build Local

### Prérequis

```bash
# Installer UV (si pas déjà fait)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Installer les dépendances de build
uv sync --extra build
```

### Build automatique

```bash
# Build pour la plateforme courante
./scripts/build-binary.sh

# Build pour une plateforme spécifique
./scripts/build-binary.sh linux
./scripts/build-binary.sh macos
./scripts/build-binary.sh windows
```

### Build manuel avec Nuitka

```bash
# Linux/macOS
uv run python -m nuitka \
    --onefile \
    --assume-yes-for-downloads \
    --enable-plugin=anti-bloat \
    --show-progress \
    --output-filename=gitautoflow \
    --output-dir=dist/ \
    src/gitautoflow/cli/main.py

# Test
chmod +x dist/gitautoflow
./dist/gitautoflow --help
```

## 📊 Tailles des Binaires (Estimées)

- **Linux x64** : ~15-25 MB
- **macOS x64/ARM** : ~20-30 MB
- **Windows x64** : ~20-30 MB

## 🎯 Avantages Nuitka vs PyInstaller

| Aspect | Nuitka | PyInstaller |
|--------|--------|-------------|
| **Performance** | ✅ Plus rapide (C++) | ❌ Plus lent (interprété) |
| **Taille** | ✅ Plus compact | ❌ Plus gros |
| **Compatibilité** | ⚠️ Parfois complexe | ✅ Très compatible |
| **Cross-platform** | ❌ Build sur chaque OS | ❌ Build sur chaque OS |

## 🔍 Debugging des Builds

### Logs détaillés

```bash
# Build avec logs complets
uv run python -m nuitka \
    --onefile \
    --show-progress \
    --show-memory \
    --verbose \
    src/gitautoflow/cli/main.py
```

### Test des dépendances manquantes

```bash
# Scanner les imports
uv run python -m nuitka \
    --module \
    --show-modules \
    src/gitautoflow/cli/main.py
```

## 🚨 Problèmes Connus

### Linux ARM64
- Peut nécessiter des dépendances système supplémentaires
- Build plus lent sur émulation

### macOS Notarisation
- Les binaires ne sont pas signés
- Utilisateurs doivent autoriser dans "Sécurité & Confidentialité"

### Windows Antivirus
- Certains antivirus peuvent flaguer les binaires Nuitka
- Faux positifs courants avec les compilateurs Python

## 📈 Roadmap

- [ ] **Code signing** pour macOS et Windows
- [ ] **Notarisation** macOS automatique
- [ ] **AppImage** pour Linux (optionnel)
- [ ] **Homebrew** formula (optionnel)
- [ ] **Chocolatey** package Windows (optionnel)

## 🆘 Support

Si tu rencontres des problèmes de build :

1. **Vérifier les logs** GitHub Actions
2. **Tester le build local** avec `./scripts/build-binary.sh`
3. **Vérifier les dépendances** avec `uv sync --extra build`