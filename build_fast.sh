#!/bin/bash
set -e

echo "🔍 1️⃣ Vérification des imports..."
python3 -c "import sys; sys.path.insert(0, 'src'); sys.path.insert(0, 'src/lib'); import lib; import lib.prompt_templates; print('✅ Lib import OK')"

echo "🧹 2️⃣ Nettoyage..."
rm -rf dist && mkdir dist

echo "⚡ 3️⃣ Build rapide Nuitka..."
uv run python -m nuitka --assume-yes-for-downloads --jobs=4 \
    --include-package-data=gitautoflow --include-package=lib \
    --output-dir=dist launcher.py

chmod +x dist/launcher.bin
echo "✅ Build rapide terminé : ./dist/launcher.bin"