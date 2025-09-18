#!/usr/bin/env python3
"""
Git Auto-Flow - CLI Principal
Point d'entr�e pour toutes les commandes
"""

import typer
from .repos import app as repos_app
from gitautoflow.utils.logger import header
from gitautoflow.__meta__ import CLI_HELP, CLI_VERSION_MSG

# Application principale
app = typer.Typer(help=CLI_HELP)

# Ajouter les sous-commandes
app.add_typer(repos_app, name="repo", help="Gestion des repositories GitHub")


@app.command()
def version():
    """Affiche la version du projet"""
    header(CLI_VERSION_MSG)


def main():
    """Point d'entrée principal pour le binaire"""
    app()


if __name__ == "__main__":
    main()