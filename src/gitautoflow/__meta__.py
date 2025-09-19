#!/usr/bin/env python3
"""
Métadonnées du projet Git Auto-Flow
Centralisé pour faciliter les changements de nom/version
"""

# Configuration du projet
PROJECT_NAME = "Git Auto-Flow"
PROJECT_SLUG = "gitautoflow"
VERSION = "1.0.0"
DESCRIPTION = "Outils de développement Git/GitHub"

# Configuration binaire
CLI_NAME = "gitautoflow"  # Changez juste cette ligne pour renommer le binaire
CLI_SHORT = "gaf"         # Alias court optionnel

# Pour l'affichage
CLI_HELP = f"{PROJECT_NAME} - {DESCRIPTION}"
CLI_VERSION_MSG = f"{PROJECT_NAME} v{VERSION}"