#!/usr/bin/env python3
"""
Git Auto-Flow - CLI Principal
Point d'entr�e pour toutes les commandes
"""

import typer
from .repos import app as repos_app
from .features import app as features_app
from gitautoflow.utils.logger import header
from gitautoflow.__meta__ import CLI_HELP, CLI_VERSION_MSG

# Application principale
app = typer.Typer(help=CLI_HELP)

# Ajouter les sous-commandes
app.add_typer(repos_app, name="repo", help="Gestion des repositories GitHub")

# Aliases directs pour les commandes fréquentes
from .commits import auto_commit as _auto_commit
from .features import start as _feature_start

@app.command(name="auto-commit")
def auto_commit_alias(
    force: bool = typer.Option(False, "--force", "-f", help="Force le commit sans demander confirmation"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes Git exécutées")
):
    """Commit automatique avec rebase + IA (alias: ac)"""
    _auto_commit(force=force, debug=debug)

@app.command(name="ac", hidden=True)
def ac_alias(
    force: bool = typer.Option(False, "--force", "-f", help="Force le commit sans demander confirmation"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes Git exécutées")
):
    """Alias ultra-court pour auto-commit"""
    _auto_commit(force=force, debug=debug)

@app.command(name="feature-start")
def feature_start_alias(
    feature_name: str = typer.Argument(..., help="Nom de la feature à créer"),
    base: str = typer.Option("develop", "--base", "-b", help="Branche de base (défaut: develop)"),
    force: bool = typer.Option(False, "--force", "-f", help="Forcer la création même si la branche existe"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes Git exécutées")
):
    """Démarre une nouvelle feature branch GitFlow (alias: fs)"""
    _feature_start(feature_name=feature_name, base=base, force=force, debug=debug)

@app.command(name="fs", hidden=True)
def fs_alias(
    feature_name: str = typer.Argument(..., help="Nom de la feature à créer"),
    base: str = typer.Option("develop", "--base", "-b", help="Branche de base (défaut: develop)"),
    force: bool = typer.Option(False, "--force", "-f", help="Forcer la création même si la branche existe"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes Git exécutées")
):
    """Alias ultra-court pour feature start"""
    _feature_start(feature_name=feature_name, base=base, force=force, debug=debug)


@app.command()
def version():
    """Affiche la version du projet"""
    header(CLI_VERSION_MSG)


def main():
    """Point d'entrée principal pour le binaire"""
    app()


if __name__ == "__main__":
    main()