#!/usr/bin/env python3
"""
Script de renommage du binaire Git Auto-Flow
Usage: python scripts/rename-binary.py <nouveau-nom>
"""

import sys
import re
from pathlib import Path

def rename_binary(new_name: str, new_short: str = None):
    """Renomme le binaire dans tous les fichiers de configuration"""

    if not new_short:
        new_short = new_name[:3] if len(new_name) >= 3 else new_name

    # Fichiers à modifier
    files_to_update = [
        {
            'path': Path('pyproject.toml'),
            'changes': [
                (r'^gitautoflow = .*', f'{new_name} = "gitautoflow.cli.main:main"'),
                (r'^gaf = .*', f'{new_short} = "gitautoflow.cli.main:main"'),
            ]
        },
        {
            'path': Path('src/gitautoflow/__meta__.py'),
            'changes': [
                (r'CLI_NAME = ".*"', f'CLI_NAME = "{new_name}"'),
                (r'CLI_SHORT = ".*"', f'CLI_SHORT = "{new_short}"'),
            ]
        }
    ]

    print(f"🔄 Renommage du binaire vers: {new_name} (alias: {new_short})")

    for file_config in files_to_update:
        file_path = file_config['path']
        if not file_path.exists():
            print(f"❌ Fichier non trouvé: {file_path}")
            continue

        print(f"📝 Mise à jour: {file_path}")

        # Lire le contenu
        content = file_path.read_text()

        # Appliquer les changements
        for pattern, replacement in file_config['changes']:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        # Écrire le contenu modifié
        file_path.write_text(content)

    print(f"✅ Renommage terminé !")
    print(f"💡 Pour appliquer les changements:")
    print(f"   uv sync")
    print(f"   {new_name} --help")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/rename-binary.py <nouveau-nom> [alias-court]")
        print("Exemple: python scripts/rename-binary.py gaf")
        print("Exemple: python scripts/rename-binary.py myapp ma")
        sys.exit(1)

    new_name = sys.argv[1]
    new_short = sys.argv[2] if len(sys.argv) > 2 else None

    # Validation basique
    if not new_name.replace('-', '').replace('_', '').isalnum():
        print("❌ Le nom doit contenir uniquement des lettres, chiffres, '-' et '_'")
        sys.exit(1)

    rename_binary(new_name, new_short)

if __name__ == "__main__":
    main()