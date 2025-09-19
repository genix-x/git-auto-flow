#!/bin/bash
set -e

# --- Configuration ---
PROJECT_NAME="gitautoflow"
SRC_LAUNCHER="launcher.py"
DIST_DIR="dist"
RAPID_BINARY="$DIST_DIR/${PROJECT_NAME}-dev"
FINAL_BINARY="$DIST_DIR/${PROJECT_NAME}-working"

# Nombre de jobs pour compilation C (ajuster selon le CPU)
JOBS=4

# --- Nettoyage ---
echo "🔹 Nettoyage du dossier dist/"
rm -rf "$DIST_DIR"
mkdir "$DIST_DIR"

# --- Build rapide pour tests locaux ---
echo "🔹 Build rapide pour tests locaux..."
uv run python -m nuitka \
    --assume-yes-for-downloads \
    --jobs=$JOBS \
    --include-package-data=gitautoflow \
    --include-package=lib \
    --output-dir="$DIST_DIR" \
    "$SRC_LAUNCHER" | tee "$DIST_DIR/rapid_build.log"

echo "✅ Build rapide terminé : $RAPID_BINARY"
echo "🔹 Tu peux tester avec : ./$RAPID_BINARY ac"

# --- Build final Onefile + anti-bloat ---
echo "🔹 Build final Onefile + anti-bloat..."
uv run python -m nuitka \
    --onefile \
    --assume-yes-for-downloads \
    --enable-plugin=anti-bloat \
    --jobs=$JOBS \
    --include-package-data=gitautoflow \
    --include-package=lib \
    --output-filename="$FINAL_BINARY" \
    --output-dir="$DIST_DIR" \
    "$SRC_LAUNCHER" | tee "$DIST_DIR/final_build.log"

echo "✅ Build final terminé : $FINAL_BINARY"
echo "🔹 Tu peux tester avec : ./$FINAL_BINARY ac"

# --- Fin ---
echo "🎉 Tous les builds sont terminés ! Logs disponibles dans $DIST_DIR/"
