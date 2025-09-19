#!/bin/bash
set -e

echo "🔍 1️⃣ Vérification des imports..."
python3 -c "import sys; sys.path.insert(0, 'src'); sys.path.insert(0, 'src/lib'); import lib; import lib.prompt_templates; print('✅ Lib import OK')"

echo "🧹 2️⃣ Nettoyage..."
rm -rf dist && mkdir dist

echo "🔧 3️⃣ Correction des imports relatifs (au cas où)..."
find src/lib -name "*.py" -exec sed -i 's/^from gemini_client import/from .gemini_client import/g' {} \;
find src/lib -name "*.py" -exec sed -i 's/^from groq_client import/from .groq_client import/g' {} \;
find src/lib -name "*.py" -exec sed -i 's/^from git_utils import/from .git_utils import/g' {} \;
find src/lib -name "*.py" -exec sed -i 's/^from ai_provider import/from .ai_provider import/g' {} \;

echo "🏗️ 4️⃣ Build complet Nuitka (onefile + anti-bloat)..."
uv run python -m nuitka --onefile --assume-yes-for-downloads --enable-plugin=anti-bloat --jobs=4 \
    --include-package-data=gitautoflow --include-package=lib \
    --output-filename=gitautoflow-production \
    --output-dir=dist launcher.py

chmod +x dist/gitautoflow-production
echo "✅ Build complet terminé : ./dist/gitautoflow-production"