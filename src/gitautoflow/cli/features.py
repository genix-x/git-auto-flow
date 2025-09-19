#!/usr/bin/env python3
"""
Git Auto-Flow - Gestion des feature branches
Migration vers architecture Typer
"""

import sys
import subprocess
from pathlib import Path

import typer

# Import des utilitaires logger
from gitautoflow.utils.logger import info, success, error, warning, header

app = typer.Typer(help="Gestion des feature branches GitFlow")

# Import des modules lib (chemin relatif au projet parent)
def import_lib_modules():
    """Import dynamique des modules lib du projet parent"""
    try:
        # Chemin vers le projet parent
        parent_lib = Path(__file__).parent.parent.parent / "lib"
        if parent_lib.exists():
            sys.path.insert(0, str(parent_lib))

            from ai_provider import AIProvider
            from git_utils import GitUtils
            from debug_logger import debug_command, set_global_debug_mode

            return AIProvider, GitUtils, debug_command, set_global_debug_mode
        else:
            error(f"Module lib non trouvé dans: {parent_lib}")
            raise typer.Exit(1)
    except ImportError as e:
        error(f"Impossible d'importer les modules lib: {e}")
        raise typer.Exit(1)


def run_command(command: list, description: str = "", debug: bool = False):
    """Exécute une commande Git et gère les erreurs"""
    try:
        if debug:
            info(f"[DEBUG] Commande: {' '.join(command)}")

        if description:
            info(description)

        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # Log la sortie si elle existe et n'est pas vide
        if result.stdout and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            for line in lines[-3:]:  # Affiche les 3 dernières lignes max
                if line.strip():
                    info(f"  {line.strip()}")

        return result

    except subprocess.CalledProcessError as e:
        error(f"Commande échouée: {' '.join(command)}")
        if e.stderr:
            error(f"  {e.stderr.strip()}")
        elif e.stdout:
            error(f"  {e.stdout.strip()}")
        raise typer.Exit(1)


def check_git_repository():
    """Vérifie qu'on est dans un repository Git"""
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'],
                      capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        error("Pas dans un repository Git")
        raise typer.Exit(1)


def get_current_branch():
    """Récupère la branche courante"""
    try:
        result = subprocess.run(['git', 'branch', '--show-current'],
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        error("Impossible de déterminer la branche courante")
        raise typer.Exit(1)


def branch_exists(branch_name: str, remote: bool = False) -> bool:
    """Vérifie si une branche existe"""
    try:
        if remote:
            cmd = ['git', 'show-ref', '--verify', '--quiet', f'refs/remotes/origin/{branch_name}']
        else:
            cmd = ['git', 'show-ref', '--verify', '--quiet', f'refs/heads/{branch_name}']

        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0
    except:
        return False


@app.command()
def start(
    feature_name: str = typer.Argument(..., help="Nom de la feature à créer"),
    base: str = typer.Option("develop", "--base", "-b", help="Branche de base (défaut: develop)"),
    force: bool = typer.Option(False, "--force", "-f", help="Forcer la création même si la branche existe"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes Git exécutées")
):
    """Démarre une nouvelle feature branch selon GitFlow"""

    # Vérification prérequis
    check_git_repository()

    # Validation du nom de feature
    if not feature_name.replace('-', '').replace('_', '').isalnum():
        error("Nom de feature invalide.")
        info("Utilisez uniquement des lettres, chiffres, '-' et '_'.")
        raise typer.Exit(1)

    feature_branch = f"feature/{feature_name}"

    header(f"🚀 Démarrage feature: {feature_name}")
    info(f"Branche cible: {feature_branch}")
    info(f"Branche de base: {base}")

    # Vérifier si la branche de base existe
    if not branch_exists(base):
        error(f"La branche de base '{base}' n'existe pas localement")
        info(f"Branches disponibles: git branch -a")
        raise typer.Exit(1)

    # Vérifier si la feature branch existe déjà
    if branch_exists(feature_branch):
        if not force:
            error(f"La branche '{feature_branch}' existe déjà")
            info("Utilisez --force pour forcer la recréation ou choisissez un autre nom")
            raise typer.Exit(1)
        else:
            warning(f"La branche '{feature_branch}' existe déjà - Suppression forcée")
            try:
                # Supprimer la branche locale si elle existe
                run_command(['git', 'branch', '-D', feature_branch],
                           f"Suppression de la branche locale {feature_branch}", debug=debug)
            except:
                pass  # La branche n'existe peut-être pas localement

    # Workflow de création de feature
    try:
        # 1. Basculer sur la branche de base et la mettre à jour
        current_branch = get_current_branch()
        if current_branch != base:
            run_command(['git', 'checkout', base],
                       f"Basculement sur {base}", debug=debug)

        run_command(['git', 'pull', 'origin', base],
                   f"Mise à jour de {base} depuis origin", debug=debug)

        # 2. Créer la feature branch
        run_command(['git', 'checkout', '-b', feature_branch],
                   f"Création de la branche {feature_branch}", debug=debug)

        # 3. Pousser la branche vers origin
        run_command(['git', 'push', '-u', 'origin', feature_branch],
                   f"Push initial de {feature_branch}", debug=debug)

        success(f"Feature branch créée: {feature_branch}")
        success(f"Branche trackée sur origin")
        info("💡 Vous pouvez maintenant commencer à développer !")
        info(f"💡 Pour committer: gitautoflow ac")

    except Exception as e:
        error(f"Erreur lors de la création de la feature: {e}")
        raise typer.Exit(1)




if __name__ == "__main__":
    app()