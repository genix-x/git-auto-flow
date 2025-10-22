#!/usr/bin/env python3
"""
Git Auto-Flow - Automatisation des releases
Migration de git-release-auto.py vers architecture Typer
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import Optional

import typer

# Import des utilitaires logger
from gitautoflow.utils.logger import info, success, error, warning, header, console

app = typer.Typer(help="Commandes d'automatisation des releases")

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


def confirm(message: str) -> bool:
    """Demande confirmation à l'utilisateur"""
    response = console.input(f"[yellow]{message} (y/N):[/yellow] ").lower()
    return response in ['y', 'yes', 'o', 'oui']


def get_repo_name() -> str:
    """Récupère le nom du repository GitHub"""
    try:
        cmd = ['git', 'remote', 'get-url', 'origin']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        url = result.stdout.strip()

        # Parse GitHub URL (https://github.com/user/repo.git ou git@github.com:user/repo.git)
        if 'github.com/' in url:
            repo_part = url.split('github.com/')[-1]
            if repo_part.endswith('.git'):
                repo_part = repo_part[:-4]
            return repo_part
        return "unknown/unknown"
    except:
        return "unknown/unknown"


def get_latest_tag() -> str:
    """Récupère le dernier tag pour calculer la prochaine version"""
    try:
        # On s'assure d'avoir les derniers tags de l'origin
        subprocess.run(['git', 'fetch', 'origin', '--tags'], capture_output=True, text=True)

        # Liste les tags par version et prend le dernier
        cmd = ['git', 'tag', '-l', '--sort=-v:refname']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        tags = result.stdout.strip().split('\n')

        if tags and tags[0]:
            # Nettoie le tag pour retirer les "v" en trop
            # Exemple: "vvv1.8.0" devient "v1.8.0"
            latest_tag = tags[0]
            # Garde seulement le premier "v" et les chiffres
            import re
            cleaned_tag = re.sub(r'^v+', 'v', latest_tag)
            return cleaned_tag
        else:
            return "v0.0.0"
    except Exception:
        return "v0.0.0"  # Première version si aucun tag


def create_github_release(release_data: dict, debug_command) -> bool:
    """
    Crée une GitHub Release avec tag

    Args:
        release_data: Dict contenant version, changes, etc.
        debug_command: Fonction de debug

    Returns:
        bool: True si succès
    """
    try:
        version = f"v{release_data['version']}"

        # 1. Checkout main pour créer le tag
        info("📂 Checkout main pour la release...")
        subprocess.run(['git', 'checkout', 'main'], capture_output=True, check=True)

        # 2. Pull latest main
        info("📥 Pull main...")
        subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, check=True)

        # 3. Créer le tag local
        info(f"🏷️  Création du tag {version}...")
        tag_cmd = ['git', 'tag', '-a', version, '-m', f'Release {version}']
        debug_command(tag_cmd, f"create tag {version}")
        subprocess.run(tag_cmd, check=True)

        # 4. Push le tag
        info(f"📤 Push du tag {version}...")
        push_tag_cmd = ['git', 'push', 'origin', version]
        debug_command(push_tag_cmd, f"push tag {version}")
        subprocess.run(push_tag_cmd, check=True)

        # 5. Générer les release notes depuis les données IA
        release_notes = generate_release_notes(release_data)

        # 6. Créer la GitHub Release
        info(f"🚀 Création de la GitHub Release {version}...")
        gh_cmd = [
            'gh', 'release', 'create', version,
            '--title', f'{version}',
            '--notes', release_notes
        ]

        debug_command(gh_cmd, f"create GitHub release {version}")
        subprocess.run(gh_cmd, check=True)

        return True

    except subprocess.CalledProcessError as e:
        error(f"Erreur lors de la création de la release: {e}")
        return False
    except Exception as e:
        error(f"Erreur inattendue lors de la release: {e}")
        return False


def generate_release_notes(release_data: dict) -> str:
    """Génère les release notes formatées pour GitHub"""
    notes = f"## 🚀 Release v{release_data['version']}\n\n"

    if release_data.get('breaking_changes'):
        notes += "### ⚠️ BREAKING CHANGES\n"
        for change in release_data.get('major_changes', []):
            notes += f"- {change}\n"
        notes += "\n"

    if release_data.get('minor_changes'):
        notes += "### ✨ New Features\n"
        for change in release_data['minor_changes']:
            notes += f"- {change}\n"
        notes += "\n"

    if release_data.get('patch_changes'):
        notes += "### 🐛 Bug Fixes & Improvements\n"
        for change in release_data['patch_changes']:
            notes += f"- {change}\n"
        notes += "\n"

    notes += f"**Full Changelog**: https://github.com/{get_repo_name()}/compare/{get_latest_tag()}...v{release_data['version']}\n"

    return notes


def check_gh_cli(debug_command):
    """Vérifie que GitHub CLI est installé et authentifié"""
    try:
        version_cmd = ['gh', '--version']
        debug_command(version_cmd, "check gh version")
        subprocess.run(version_cmd, capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        error("GitHub CLI (gh) n'est pas installé")
        info("💡 Installation:")
        info("   macOS: brew install gh")
        info("   Ubuntu/Debian: sudo apt install gh")
        raise typer.Exit(1)

    try:
        auth_cmd = ['gh', 'auth', 'status']
        debug_command(auth_cmd, "check gh auth")
        subprocess.run(auth_cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError:
        error("GitHub CLI n'est pas authentifié")
        info("💡 Connectez-vous: gh auth login")
        raise typer.Exit(1)


def merge_pr_immediately(pr_url: str, merge_method: str, debug_command) -> bool:
    """
    Merge immédiatement la PR créée

    Args:
        pr_url: URL de la PR
        merge_method: Méthode de merge (merge, squash, rebase)
        debug_command: Fonction de debug

    Returns:
        bool: True si le merge a réussi
    """
    try:
        # Extract PR number from URL
        pr_number = pr_url.split('/')[-1]

        info(f"🔄 Merge immédiat de la PR #{pr_number}...")

        # Merge immediately (no --auto flag)
        cmd = [
            'gh', 'pr', 'merge', pr_number,
            f'--{merge_method}'
        ]

        debug_command(cmd, "merge PR immediately")

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        success("PR mergée avec succès!")
        return True

    except subprocess.CalledProcessError as e:
        error(f"Merge échoué: {e.stderr}")
        info("💡 Vous pouvez merger manuellement depuis GitHub")
        return False


def run_gh_pr_create_release(pr_data: dict, immediate_merge: bool, merge_method: str, force_mode: bool, debug_command) -> str:
    """
    Execute gh pr create pour une release avec merge immédiat

    Args:
        pr_data: Dict contenant title, body, labels, etc.
        immediate_merge: Si True, merge immédiatement la PR
        merge_method: Méthode de merge
        force_mode: Si True, bypass la confirmation
        debug_command: Fonction de debug

    Returns:
        str: L'URL de la PR créée
    """
    # Affiche la PR de release proposée
    info("🚀 PR de Release proposée:")
    info(f"   Titre: {pr_data['title']}")
    info(f"   Base: main")
    if pr_data.get('labels'):
        info(f"   Labels: {', '.join(pr_data['labels'])}")
    console.print(f"\n{pr_data['body']}")

    if immediate_merge:
        info("\n🔄 Merge immédiat: ACTIVÉ (mergera automatiquement après création)")

    # Demande confirmation
    if not force_mode:
        if not confirm("✅ Créer cette PR de release?"):
            error("Release annulée")
            return ""
    else:
        success("Confirmation automatique (mode force)")

    # Construit la commande gh pr create
    cmd = [
        'gh', 'pr', 'create',
        '--base', 'main',
        '--head', 'develop',
        '--title', pr_data['title'],
        '--body', pr_data['body']
    ]

    try:
        debug_command(cmd, "create release PR")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        pr_url = result.stdout.strip()
        success(f"PR de release créée: {pr_url}")

        # Merge immédiat si demandé
        if immediate_merge:
            merge_pr_immediately(pr_url, merge_method, debug_command)

        return pr_url

    except subprocess.CalledProcessError as e:
        if e.stderr:
            error(f"Erreur lors de la création de la PR: {e.stderr}")
        else:
            error(f"Erreur lors de la création de la PR: {e}")
        raise typer.Exit(1)


@app.command()
def auto(
    version: Optional[str] = typer.Option(None, "--version", help="Forcer un numéro de version spécifique (ex: 1.0.0, 2.1.3)"),
    no_auto_merge: bool = typer.Option(False, "--no-auto-merge", help="Ne pas auto-merger la PR (merge manuel)"),
    merge_method: str = typer.Option("merge", "--merge-method", help="Méthode de merge (merge, squash, rebase)"),
    force: bool = typer.Option(False, "--force", "-f", help="Mode non-interactif (aucune confirmation)"),
    debug: bool = typer.Option(False, "--debug", help="Activer le mode debug pour voir les commandes exécutées")
):
    """Processus de release automatisé complet : develop → main → tag → release GitHub"""

    # Import des modules lib
    AIProvider, GitUtils, debug_command, set_global_debug_mode = import_lib_modules()

    # Configuration du logger global
    set_global_debug_mode(debug)

    header("🚀 Git Release Auto - Processus de Release Automatisé")

    # Vérifie les prérequis
    if not GitUtils.is_git_repository():
        error("Pas dans un repository Git")
        raise typer.Exit(1)

    check_gh_cli(debug_command)

    try:
        # Étape 1: Checkout develop et pull
        info("\n🔄 Étape 1: Synchronisation de develop...")
        current_branch = GitUtils.get_current_branch()
        info(f"📋 Branche courante: {current_branch}")

        # Checkout develop
        info("📂 Checkout develop...")
        result = subprocess.run(['git', 'checkout', 'develop'],
                              capture_output=True, text=True, check=True)
        success("Sur develop")

        # Pull origin develop
        info("📥 Pull origin develop...")
        result = subprocess.run(['git', 'pull', 'origin', 'develop'],
                              capture_output=True, text=True, check=True)
        success("Develop synchronisé")

        # Étape 2: Vérifier qu'il y a des changements vs main
        info("\n🔍 Étape 2: Analyse des changements develop -> main...")

        if not GitUtils.has_branch_changes('main'):
            error("Aucun changement entre develop et main")
            info("💡 Rien à releaser!")
            raise typer.Exit(1)

        # Récupère les informations pour la PR
        diff = GitUtils.get_branch_diff('main')
        files_list = GitUtils.get_branch_files('main')
        commits = GitUtils.get_commit_messages('main')

        info(f"📊 {len(commits)} commits à releaser")
        info(f"📁 {len(files_list)} fichiers modifiés")

        # Convertit la liste de fichiers en string pour l'IA
        files = '\n'.join(files_list)

        # Étape 3: Génération de la PR avec IA
        info("\n🤖 Étape 3: Génération de la PR de release avec IA...")

        ai = AIProvider()
        console.print(ai.get_status())

        # Récupère le dernier tag pour le calcul de la version
        latest_tag = get_latest_tag()

        # Toujours utiliser l'IA pour analyser les changements
        info(f"Le dernier tag trouvé est '{latest_tag}'. Il sera utilisé comme base pour l'analyse des changements.")
        # Génère une PR spécialement pour une release + calcul version
        release_data = ai.analyze_for_release(diff, files, commits, latest_tag=latest_tag)

        if version:
            # Version forcée par l'utilisateur - on garde l'analyse IA mais on override la version
            info(f"🎯 Version forcée: v{version} (utilisateur)")
            info(f"📋 Changements analysés par IA: {len(release_data['release'].get('minor_changes', []) + release_data['release'].get('patch_changes', []) + release_data['release'].get('major_changes', []))} modifications détectées")

            # Override seulement la version dans les données
            release_data['release']['version'] = version
            release_data['release']['version_type'] = 'forced'
            release_data['pr']['title'] = f'Release v{version}'
        else:
            # Version calculée par l'IA
            info(f"🏷️  Version calculée: v{release_data['release']['version']} ({release_data['release']['version_type']})")

        # Affichage final de la version utilisée
        final_version = version if version else release_data['release']['version']
        version_type = 'forcée par utilisateur' if version else release_data['release']['version_type']
        info(f"🏷️  Version finale: v{final_version} ({version_type})")

        # Étape 4: Création de la PR avec auto-merge
        info("\n🚀 Étape 4: Création de la PR de release...")

        immediate_merge = not no_auto_merge
        pr_url = run_gh_pr_create_release(release_data['pr'], immediate_merge, merge_method, force, debug_command)

        if pr_url and immediate_merge:
            success(f"\n🎉 PR mergée! Création de la release v{release_data['release']['version']}...")

            # Étape 5: Création automatique de la release
            if create_github_release(release_data['release'], debug_command):
                success(f"🏷️  Release v{release_data['release']['version']} créée avec succès!")
                success(f"🔗 Voir: https://github.com/{get_repo_name()}/releases/tag/v{release_data['release']['version']}")
            else:
                warning("Erreur lors de la création de la release GitHub")
        elif pr_url:
            success(f"\n🎉 PR créée: {pr_url}")
            info("💡 Mergez manuellement pour déclencher la release")

        # Retour à la branche d'origine si possible
        if current_branch and current_branch != 'develop':
            try:
                info(f"\n🔙 Retour à la branche {current_branch}...")
                subprocess.run(['git', 'checkout', current_branch],
                             capture_output=True, check=True)
                success(f"Retour sur {current_branch}")
            except subprocess.CalledProcessError:
                warning(f"Impossible de retourner sur {current_branch}")

    except subprocess.CalledProcessError as e:
        if e.stderr:
            error(f"Erreur Git: {e.stderr}")
        else:
            error(f"Erreur Git: {e}")
        raise typer.Exit(1)
    except ValueError as e:
        error(f"Configuration: {e}")
        raise typer.Exit(1)
    except Exception as e:
        error(f"Erreur inattendue: {e}")
        raise typer.Exit(1)


@app.command()
def next_version(
    debug: bool = typer.Option(False, "--debug", help="Mode debug pour voir le détail du calcul")
):
    """Affiche la prochaine version qui sera créée (sans rien faire)"""

    # Import des modules lib
    AIProvider, GitUtils, debug_command, set_global_debug_mode = import_lib_modules()

    # Configuration du logger global
    set_global_debug_mode(debug)

    # Vérifie les prérequis
    if not GitUtils.is_git_repository():
        error("Pas dans un repository Git")
        raise typer.Exit(1)

    try:
        # Vérifier qu'il y a des changements vs main
        if not GitUtils.has_branch_changes('main'):
            info("Aucun changement entre develop et main")
            console.print("v0.0.0")
            return

        # Récupère les informations pour l'analyse
        diff = GitUtils.get_branch_diff('main')
        files_list = GitUtils.get_branch_files('main')
        commits = GitUtils.get_commit_messages('main')
        files = '\n'.join(files_list)

        if debug:
            info(f"📊 {len(commits)} commits à analyser")
            info(f"📁 {len(files_list)} fichiers modifiés")

        # Initialise l'IA
        ai = AIProvider()
        if debug:
            console.print(ai.get_status())

        # Récupère le dernier tag
        latest_tag = get_latest_tag()
        if debug:
            info(f"Dernier tag: {latest_tag}")

        # Génère l'analyse pour calculer la version
        release_data = ai.analyze_for_release(diff, files, commits, latest_tag=latest_tag)

        # Affiche juste la version
        console.print(f"v{release_data['release']['version']}")

        if debug:
            info(f"Type de version: {release_data['release']['version_type']}")

    except ValueError as e:
        error(f"Configuration: {e}")
        raise typer.Exit(1)
    except Exception as e:
        error(f"Erreur: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
