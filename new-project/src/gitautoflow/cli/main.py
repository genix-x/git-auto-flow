#!/usr/bin/env python3
"""
Git Auto-Flow - CLI Principal
Point d'entr�e pour toutes les commandes
"""

import typer
from .repos import app as repos_app
from .commits import app as commits_app
from gitautoflow.utils.logger import header
from gitautoflow.__meta__ import CLI_HELP, CLI_VERSION_MSG

# Application principale
app = typer.Typer(help=CLI_HELP)

# Ajouter les sous-commandes
app.add_typer(repos_app, name="repo", help="Gestion des repositories GitHub")
app.add_typer(commits_app, name="commit", help="Commit automatique avec IA")

# Aliases directs pour les commandes fréquentes
from .commits import auto_commit as _auto_commit

@app.command(name="auto-commit")
def auto_commit_alias(
    force: bool = typer.Option(False, "--force", "-f", help="Force le commit sans demander confirmation"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes Git exécutées")
):
    """Commit automatique avec rebase + IA (alias direct)"""
    _auto_commit(force=force, debug=debug)

@app.command(name="ac")
def ac_alias(
    force: bool = typer.Option(False, "--force", "-f", help="Force le commit sans demander confirmation"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes Git exécutées")
):
    """Alias ultra-court pour auto-commit"""
    _auto_commit(force=force, debug=debug)


@app.command()
def version():
    """Affiche la version du projet"""
    header(CLI_VERSION_MSG)


def main():
    """Point d'entrée principal pour le binaire"""
    app()


if __name__ == "__main__":
    main()