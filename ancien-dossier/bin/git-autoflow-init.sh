#!/bin/bash
# Exécute le script Python pour git-autoflow-init

# Détermine le répertoire du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Exécute le script Python
"$SCRIPT_DIR/../src/git-autoflow-init.py" "$@"
