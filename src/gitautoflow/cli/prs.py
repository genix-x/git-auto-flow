#!/usr/bin/env python3
"""
Git Auto-Flow - Création automatique de PR avec IA
Migration vers architecture Typer
"""

import sys
import subprocess
import os
from pathlib import Path
from typing import Optional

import typer

# Import des utilitaires logger
from gitautoflow.utils.logger import info, success, error, warning, header, console

app = typer.Typer(help="Commandes de gestion des Pull Requests avec IA")

# Import des modules lib (chemin relatif au projet parent)
def import_lib_modules():
    """Import dynamique des modules lib du projet parent"""
    try:
        # Chemin vers le projet parent
        parent_lib = Path(__file__).parent.parent.parent.parent.parent / "src" / "lib"
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


def confirm(message: str) -> bool:
    """Demande confirmation à l'utilisateur"""
    response = console.input(f"[yellow]{message} (y/N):[/yellow] ").lower()
    return response in ['y', 'yes', 'o', 'oui']


def run_git_command(command: list, debug: bool = False, **kwargs):
    """Exécute une commande Git et log si debug activé"""
    if debug:
        info(f"[DEBUG] Commande: {' '.join(command)}")

    return subprocess.run(command, **kwargs)


def check_gh_cli():
    """Vérifie que GitHub CLI est installé et authentifié"""
    try:
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        error("GitHub CLI (gh) n'est pas installé")
        info("💡 Installation: brew install gh")
        raise typer.Exit(1)

    try:
        subprocess.run(['gh', 'auth', 'status'], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        error("GitHub CLI n'est pas authentifié")
        info("💡 Connectez-vous: gh auth login")
        raise typer.Exit(1)


def run_gh_pr_create(pr_data: dict, base_branch: str = "develop", force: bool = False,
                     auto_merge: bool = False, delete_branch: bool = False, debug: bool = False) -> str:
    """Execute gh pr create avec les données automatiques"""

    # Affiche la PR proposée
    info("📋 PR proposée:")
    info(f"   Titre: {pr_data['title']}")
    info(f"   Base: {base_branch}")
    if pr_data.get('labels'):
        info(f"   Labels: {', '.join(pr_data['labels'])}")
    console.print(f"\n{pr_data['body']}")

    # Demande confirmation
    if not force:
        if not confirm("✅ Créer cette PR?"):
            error("PR annulée")
            return ""

    # Construit la commande gh pr create
    cmd = [
        'gh', 'pr', 'create',
        '--base', base_branch,
        '--title', pr_data['title'],
        '--body', pr_data['body']
    ]

    # Ajoute les labels si présents
    if pr_data.get('labels'):
        valid_labels = ['enhancement', 'bug', 'documentation', 'feature']
        for label in pr_data['labels']:
            if label in valid_labels:
                cmd.extend(['--label', label])

    # Ajoute le flag draft si nécessaire
    if pr_data.get('draft', False):
        cmd.append('--draft')

    try:
        if debug:
            info(f"[DEBUG] Commande: {' '.join(cmd)}")

        result = run_git_command(cmd, debug=debug, capture_output=True, text=True, check=True)
        pr_url = result.stdout.strip()
        success(f"PR créée avec succès: {pr_url}")

        # Auto-merge si demandé
        if auto_merge:
            info("🔄 Merge automatique de la PR...")
            current_branch = subprocess.run(['git', 'branch', '--show-current'],
                                          capture_output=True, text=True, check=True).stdout.strip()
            try:
                import time
                time.sleep(2)

                merge_cmd = ['gh', 'pr', 'merge', pr_url, '--squash']
                run_git_command(merge_cmd, debug=debug, capture_output=True, text=True, check=True)
                success("PR mergée avec succès")

                # Retourner sur la branche de base et pull
                info(f"🔄 Retour sur la branche '{base_branch}'...")
                run_git_command(['git', 'checkout', base_branch], debug=debug, check=True)
                run_git_command(['git', 'pull'], debug=debug, check=True)

                # Supprimer la branche si demandé
                if delete_branch:
                    info(f"🗑️ Suppression de la branche '{current_branch}'...")
                    run_git_command(['git', 'branch', '-D', current_branch], debug=debug, check=True)
                    run_git_command(['git', 'push', 'origin', '--delete', current_branch], debug=debug, check=True)
                    success(f"Branche '{current_branch}' supprimée (local et remote)")
                else:
                    success(f"Branche '{base_branch}' mise à jour. La branche '{current_branch}' est conservée.")

            except subprocess.CalledProcessError as e:
                warning(f"Erreur lors du merge ou de la suppression de branche: {e.stderr if e.stderr else e}")
                info(f"💡 PR créée mais non mergée: {pr_url}")

        return pr_url

    except subprocess.CalledProcessError as e:
        if e.stderr:
            error(f"Erreur lors de la création de la PR: {e.stderr}")
        else:
            error(f"Erreur lors de la création de la PR: {e}")
        raise typer.Exit(1)


@app.command()
def auto_pr(
    base: str = typer.Option("develop", "--base", "-b", help="Branche de base pour la PR (défaut: develop)"),
    draft: bool = typer.Option(False, "--draft", "-d", help="Créer la PR en mode draft"),
    merge: bool = typer.Option(False, "--merge", "-m", help="Merger automatiquement la PR après création"),
    delete_branch: bool = typer.Option(False, "--delete-branch", "-D", help="Supprimer la branche locale et remote après un merge réussi (nécessite --merge)"),
    closes: Optional[int] = typer.Option(None, "--closes", help="Numéro de l'issue à fermer automatiquement avec la PR"),
    force: bool = typer.Option(False, "--force", "-f", help="Forcer la création de la PR sans confirmation"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes exécutées")
):
    """Créer automatiquement une PR avec analyse IA"""

    # Import des modules lib
    AIProvider, GitUtils, debug_command, set_global_debug_mode = import_lib_modules()

    # Active le mode debug global
    set_global_debug_mode(debug)

    # Vérifications prérequis
    if not GitUtils.is_git_repository():
        error("Pas dans un repository Git")
        raise typer.Exit(1)

    check_gh_cli()

    current_branch = GitUtils.get_current_branch()
    if current_branch == base:
        error(f"Vous êtes sur la branche cible '{base}'")
        raise typer.Exit(1)

    if not GitUtils.has_branch_changes(base):
        error(f"Aucun changement dans la branche courante vs {base}")
        raise typer.Exit(1)

    try:
        header("🚀 Git Auto-PR avec IA")

        if force:
            info("⚡ MODE FORCE ACTIVÉ")

        info(f"🔄 Vérification si la branche est à jour avec {base}...")
        if not GitUtils.is_branch_up_to_date(base):
            warning(f"Branche en retard sur {base}, rebase automatique...")
            try:
                GitUtils.rebase_on_target(base)
                success("Rebase terminé avec succès")
                info("📤 Push de la branche rebasée...")
                GitUtils.push_current_branch(force_with_lease=True)
                success("Push terminé")
            except RuntimeError as e:
                error(f"{e}")
                raise typer.Exit(1)
        else:
            success(f"Branche à jour avec {base}")
            try:
                info("📤 Vérification du push...")
                GitUtils.push_current_branch()
                success("Push vérifié")
            except RuntimeError:
                pass

        # Initialise le gestionnaire multi-IA
        info("🔄 Initialisation IA...")
        ai = AIProvider()
        console.print(ai.get_status())

        info(f"🔍 Analyse des changements vs {base}...")
        diff = GitUtils.get_branch_diff(base)
        files = '\n'.join(GitUtils.get_branch_files(base))

        info("🤖 Génération de la PR avec Multi-IA...")
        pr_data = ai.analyze_for_pr(diff, files, base)

        if draft:
            pr_data['draft'] = True

        # Ajouter le closes si spécifié
        if closes:
            pr_data['body'] += f"\n\nCloses #{closes}"

        if merge and not force:
            warning("Auto-merge activé - la PR sera mergée automatiquement")
            if delete_branch:
                warning("L'option de suppression de branche est également activée.")
            if not confirm("✅ Continuer?"):
                error("Opération annulée")
                raise typer.Exit(1)

        pr_url = run_gh_pr_create(
            pr_data,
            base,
            force=force,
            auto_merge=merge,
            delete_branch=delete_branch,
            debug=debug
        )

        if pr_url:
            success(f"🎉 Success! PR disponible: {pr_url}")

    except ValueError as e:
        error(f"Configuration: {e}")
        raise typer.Exit(1)
    except RuntimeError as e:
        error(f"Erreur Git: {e}")
        raise typer.Exit(1)
    except Exception as e:
        error(f"Erreur inattendue: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()