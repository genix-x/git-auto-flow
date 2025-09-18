#!/usr/bin/env python3
"""
Git Auto-Flow - CLI Principal
Point d'entr�e pour toutes les commandes
"""

import typer
from typing import Optional
from .repos import app as repos_app
from .features import app as features_app
from .issues import app as issues_app
from gitautoflow.utils.logger import header
from gitautoflow.__meta__ import CLI_HELP, CLI_VERSION_MSG

# Application principale
app = typer.Typer(help=CLI_HELP)

# Aliases directs pour les commandes fréquentes
from .commits import auto_commit as _auto_commit
from .features import start as _feature_start
from .prs import auto_pr as _auto_pr

# Commandes directes dans l'ordre alphabétique (Typer impose cet ordre)
@app.command(name="auto-commit")
def auto_commit_alias(
    force: bool = typer.Option(False, "--force", "-f", help="Force le commit sans demander confirmation"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes Git exécutées")
):
    """Commit automatique avec rebase + IA (alias: ac)"""
    _auto_commit(force=force, debug=debug)

@app.command(name="auto-pr")
def auto_pr_alias(
    base: str = typer.Option("develop", "--base", "-b", help="Branche de base pour la PR (défaut: develop)"),
    draft: bool = typer.Option(False, "--draft", "-d", help="Créer la PR en mode draft"),
    merge: bool = typer.Option(False, "--merge", "-m", help="Merger automatiquement la PR après création"),
    delete_branch: bool = typer.Option(False, "--delete-branch", "-D", help="Supprimer la branche locale et remote après un merge réussi (nécessite --merge)"),
    closes: Optional[int] = typer.Option(None, "--closes", help="Numéro de l'issue à fermer automatiquement avec la PR"),
    force: bool = typer.Option(False, "--force", "-f", help="Forcer la création de la PR sans confirmation"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes exécutées")
):
    """Créer automatiquement une PR avec IA (alias: pr)"""
    _auto_pr(base=base, draft=draft, merge=merge, delete_branch=delete_branch, closes=closes, force=force, debug=debug)

@app.command(name="feature-start")
def feature_start_alias(
    feature_name: str = typer.Argument(..., help="Nom de la feature à créer"),
    base: str = typer.Option("develop", "--base", "-b", help="Branche de base (défaut: develop)"),
    force: bool = typer.Option(False, "--force", "-f", help="Forcer la création même si la branche existe"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes Git exécutées")
):
    """Démarre une nouvelle feature branch GitFlow (alias: fs)"""
    _feature_start(feature_name=feature_name, base=base, force=force, debug=debug)

@app.command()
def version():
    """Affiche la version du projet"""
    header(CLI_VERSION_MSG)

# Aliases cachés
@app.command(name="ac", hidden=True)
def ac_alias(
    force: bool = typer.Option(False, "--force", "-f", help="Force le commit sans demander confirmation"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes Git exécutées")
):
    """Alias ultra-court pour auto-commit"""
    _auto_commit(force=force, debug=debug)

@app.command(name="fs", hidden=True)
def fs_alias(
    feature_name: str = typer.Argument(..., help="Nom de la feature à créer"),
    base: str = typer.Option("develop", "--base", "-b", help="Branche de base (défaut: develop)"),
    force: bool = typer.Option(False, "--force", "-f", help="Forcer la création même si la branche existe"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes Git exécutées")
):
    """Alias ultra-court pour feature start"""
    _feature_start(feature_name=feature_name, base=base, force=force, debug=debug)

@app.command(name="pr", hidden=True)
def pr_alias(
    base: str = typer.Option("develop", "--base", "-b", help="Branche de base pour la PR (défaut: develop)"),
    draft: bool = typer.Option(False, "--draft", "-d", help="Créer la PR en mode draft"),
    merge: bool = typer.Option(False, "--merge", "-m", help="Merger automatiquement la PR après création"),
    delete_branch: bool = typer.Option(False, "--delete-branch", "-D", help="Supprimer la branche locale et remote après un merge réussi (nécessite --merge)"),
    closes: Optional[int] = typer.Option(None, "--closes", help="Numéro de l'issue à fermer automatiquement avec la PR"),
    force: bool = typer.Option(False, "--force", "-f", help="Forcer la création de la PR sans confirmation"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes exécutées")
):
    """Alias ultra-court pour auto-pr"""
    _auto_pr(base=base, draft=draft, merge=merge, delete_branch=delete_branch, closes=closes, force=force, debug=debug)

# Sous-commandes (apparaîtront après les commandes directes)
app.add_typer(issues_app, name="issue", help="Commandes de gestion des issues GitHub")
app.add_typer(repos_app, name="repo", help="Commandes de gestion des repositories GitHub")


def main():
    """Point d'entrée principal pour le binaire"""
    app()


if __name__ == "__main__":
    main()