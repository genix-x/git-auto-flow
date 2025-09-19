#!/bin/bash
# Activation rapide de l'environnement Git Auto-Flow v2.0

echo "🚀 Activation de Git Auto-Flow v2.0..."

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Erreur: Lancez ce script depuis le répertoire new-project/"
    exit 1
fi

# Activer l'environnement UV
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Environnement UV activé"
    echo "💡 Vous pouvez maintenant utiliser:"
    echo "   gitautoflow --help"
    echo "   gitautoflow ac"
    echo "   gitautoflow repo create-repo"
else
    echo "❌ Environnement .venv non trouvé"
    echo "💡 Lancez d'abord: uv sync"
    exit 1
fi

# Lancer un nouveau shell avec l'environnement activé
exec $SHELL