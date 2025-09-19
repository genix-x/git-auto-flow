#!/bin/bash
set -e

echo "🔎 1️⃣ Vérification des doublons de prompt_templates..."
find src -name "prompt_templates*"

echo "💡 Rappel : doublon connu qu'on a déjà supprimé :"
echo "  src/lib/prompt_templates.py ✅ (à garder)"
echo "  src/gitautoflow/lib/prompt_templates.py ❌ (à supprimer)"

echo "🗑 Suppression des fichiers doublons et caches..."
rm -f src/gitautoflow/lib/prompt_templates.py
find src -name "prompt_templates*.pyc" -delete

echo "🧪 2️⃣ Test d'import Python pour lib et prompt_templates..."
cat > test_lib.py << 'EOF'
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import lib
from lib import prompt_templates

print("✅ lib and prompt_templates found")
EOF

python3 test_lib.py
rm test_lib.py

echo "✏️ 3️⃣ Fix des imports relatifs dans gemini_client.py..."
sed -i 's/from prompt_templates import/from .prompt_templates import/g' src/lib/gemini_client.py

echo "📝 4️⃣ Vérification du launcher..."
if ! grep -q "sys.path.insert.*src" launcher.py; then
    echo "⚠️  Launcher needs fixing"
else
    echo "✅ Launcher looks good"
fi

echo "⚙️ 5️⃣ Compilation Nuitka..."
uv run python -m nuitka --onefile --assume-yes-for-downloads \
    --enable-plugin=anti-bloat \
    --include-package-data=gitautoflow \
    --include-package=lib \
    --output-filename=gitautoflow-working \
    --output-dir=dist/ \
    launcher.py

echo "✅ Build terminé. Testez le binaire : ./dist/gitautoflow-working ac"