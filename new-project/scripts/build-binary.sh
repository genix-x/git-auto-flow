#!/bin/bash
# Script de build local des binaires Nuitka
# Usage: ./scripts/build-binary.sh [platform]

set -e

echo "🚀 Git Auto-Flow - Build binaire Nuitka"
echo "========================================"

# Détecter la plateforme
if [[ "$1" ]]; then
    PLATFORM="$1"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    PLATFORM="windows"
else
    PLATFORM="unknown"
fi

# Déterminer l'architecture
ARCH=$(uname -m)
case $ARCH in
    x86_64) ARCH="x64" ;;
    arm64|aarch64) ARCH="arm64" ;;
    *) ARCH="unknown" ;;
esac

echo "📊 Plateforme détectée: $PLATFORM-$ARCH"

# Nom du binaire
if [[ "$PLATFORM" == "windows" ]]; then
    BINARY_NAME="gitautoflow-${PLATFORM}-${ARCH}.exe"
else
    BINARY_NAME="gitautoflow-${PLATFORM}-${ARCH}"
fi

echo "📦 Nom du binaire: $BINARY_NAME"

# Vérifier que UV est installé
if ! command -v uv &> /dev/null; then
    echo "❌ UV n'est pas installé. Installez-le d'abord:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Installer les dépendances de build
echo "🔧 Installation des dépendances de build..."
uv sync --extra build

# Créer le répertoire dist
mkdir -p dist

# Build avec Nuitka
echo "🏗️ Build en cours avec Nuitka..."
uv run python -m nuitka \
    --onefile \
    --assume-yes-for-downloads \
    --enable-plugin=anti-bloat \
    --show-progress \
    --show-memory \
    --output-filename="$BINARY_NAME" \
    --output-dir=dist/ \
    src/gitautoflow/cli/main.py

# Rendre exécutable (Unix)
if [[ "$PLATFORM" != "windows" ]]; then
    chmod +x "dist/$BINARY_NAME"
fi

# Test du binaire
echo ""
echo "✅ Test du binaire..."
if [[ "$PLATFORM" == "windows" ]]; then
    "dist/$BINARY_NAME" --help
else
    "./dist/$BINARY_NAME" --help
fi

echo ""
echo "🎉 Build terminé avec succès!"
echo "📁 Binaire généré: dist/$BINARY_NAME"
echo "📊 Taille du fichier:"
ls -lh "dist/$BINARY_NAME"

# Affichage des informations du binaire
echo ""
echo "📋 Informations du binaire:"
file "dist/$BINARY_NAME" 2>/dev/null || echo "Commande 'file' non disponible"