#!/usr/bin/env python3
"""
Git Auto-Flow - Commit automatique avec IA
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

app = typer.Typer(help="Commandes de commit automatique avec IA")

# Import des modules lib (chemin relatif au projet parent)
def import_lib_modules():
    """Import dynamique des modules lib du projet parent"""
    try:
        # Chemin vers le répertoire lib du projet
        parent_lib = Path(__file__).parent.parent.parent.parent / "src" / "lib"
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


def run_gitleaks_scan_all_modified(debug: bool = False) -> bool:
    """Scan sécurité de TOUS les fichiers modifiés (stagés, non-stagés, untracked)"""
    try:
        # Trouve le chemin vers gitleaks
        parent_project = Path(__file__).parent.parent.parent.parent.parent
        local_gitleaks = parent_project / 'bin' / 'gitleaks'
        if local_gitleaks.exists():
            gitleaks_cmd = str(local_gitleaks)
        else:
            result = subprocess.run(['which', 'gitleaks'], capture_output=True)
            if result.returncode != 0:
                warning("gitleaks non trouvé - scan de sécurité ignoré")
                return True
            gitleaks_cmd = 'gitleaks'

        # Récupère TOUS les fichiers modifiés
        all_files = []

        # 1. Fichiers stagés
        staged_result = run_git_command(['git', 'diff', '--cached', '--name-only'],
                                        debug=debug, capture_output=True, text=True, check=False)
        if staged_result.returncode == 0:
            all_files.extend([f.strip() for f in staged_result.stdout.strip().split('\n') if f.strip()])

        # 2. Fichiers modifiés non-stagés
        unstaged_result = run_git_command(['git', 'diff', '--name-only'],
                                          debug=debug, capture_output=True, text=True, check=False)
        if unstaged_result.returncode == 0:
            all_files.extend([f.strip() for f in unstaged_result.stdout.strip().split('\n') if f.strip()])

        # 3. Fichiers untracked
        untracked_result = run_git_command(['git', 'ls-files', '--others', '--exclude-standard'],
                                           debug=debug, capture_output=True, text=True, check=False)
        if untracked_result.returncode == 0:
            all_files.extend([f.strip() for f in untracked_result.stdout.strip().split('\n') if f.strip()])

        # Supprime les doublons
        unique_files = list(set(all_files))

        if not unique_files:
            info("Aucun fichier modifié à scanner")
            return True

        info(f"🔍 Scan GitLeaks sur {len(unique_files)} fichier(s) modifié(s)...")

        # Scanner chaque fichier
        for file_path in unique_files:
            if not os.path.exists(file_path):
                continue  # Fichier supprimé, ignoré

            gitleaks_command = [
                gitleaks_cmd, 'detect',
                '--no-git',
                '--source', file_path,
                '--verbose',
                '--exit-code', '1'
            ]

            result = subprocess.run(gitleaks_command, capture_output=True, text=True)

            if result.returncode == 1:
                error(f"🚨 SECRETS DÉTECTÉS dans {file_path}:")
                console.print(result.stdout)
                if result.stderr:
                    console.print("Détails supplémentaires:")
                    console.print(result.stderr)
                return False  # Arrêt immédiat si secret détecté
            elif result.returncode != 0:
                warning(f"Erreur gitleaks sur {file_path}: {result.stderr}")

        return True  # Aucun secret détecté

    except Exception as e:
        warning(f"Erreur scan sécurité: {e}")
        return True


def run_git_commit(commit_data: dict, force: bool = False, debug: bool = False) -> None:
    """Execute git commit avec les données automatiques"""
    # Construit le message de commit
    if 'type' not in commit_data:
        error(f"Erreur: Réponse IA invalide - champ 'type' manquant")
        console.print(f"📋 Réponse reçue: {commit_data}")
        return

    commit_msg = commit_data['type']

    if commit_data.get('scope'):
        commit_msg += f"({commit_data['scope']})"

    if commit_data.get('breaking', False):
        commit_msg += "!"

    # Gère le cas où l'IA utilise un autre champ que 'description'
    description = commit_data.get('description', '')
    if not description:
        # Cherche d'autres champs possibles
        for key, value in commit_data.items():
            if key not in ['type', 'scope', 'body', 'breaking', 'issues'] and isinstance(value, str):
                description = value
                break

    commit_msg += f": {description}"

    # Prépare le body complet
    body_parts = []
    if commit_data.get('body'):
        body_parts.append(commit_data['body'])

    if commit_data.get('breaking', False):
        body_parts.append("BREAKING CHANGE: " + commit_data.get('body', 'See changes above'))

    if commit_data.get('issues'):
        for issue in commit_data['issues']:
            body_parts.append(f"Closes #{issue}")

    body = '\n\n'.join(body_parts) if body_parts else ''

    # Affiche le commit proposé
    console.print("📝 Commit proposé:")
    console.print(f"   {commit_msg}")
    if body:
        console.print(f"\n{body}")

    # Demande confirmation uniquement si pas en mode force
    if not force:
        if not confirm("✅ Confirmer ce commit?"):
            error("Commit annulé")
            return
    else:
        info("⚡ Mode force activé - commit automatique")

    # Execute le commit
    try:
        full_msg = commit_msg
        if body:
            full_msg += f"\n\n{body}"

        run_git_command(['git', 'commit', '-m', full_msg], debug=debug, check=True)
        success("Commit effectué avec succès!")

        # Push automatique vers la branche distante
        try:
            current_branch = run_git_command(['git', 'branch', '--show-current'],
                                             debug=debug, capture_output=True, text=True, check=True).stdout.strip()
            info(f"📤 Push vers origin/{current_branch}...")

            run_git_command(['git', 'push', 'origin', current_branch], debug=debug, check=True)
            success("Push effectué avec succès!")
        except subprocess.CalledProcessError as e:
            warning(f"Push échoué: {e}")
            info("💡 La branche locale a été commitée mais pas pushée")

    except subprocess.CalledProcessError as e:
        error(f"Erreur lors du commit: {e}")
        raise typer.Exit(1)


@app.command()
def auto_commit(
    force: bool = typer.Option(False, "--force", "-f", help="Force le commit sans demander confirmation"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes Git exécutées")
):
    """Commit automatique avec rebase + IA"""

    # Import des modules lib
    AIProvider, GitUtils, debug_command, set_global_debug_mode = import_lib_modules()

    # Configuration du debug
    set_global_debug_mode(debug)

    # Vérifie qu'on est dans un repo git
    if not GitUtils.is_git_repository():
        error("Pas dans un repository Git")
        raise typer.Exit(1)

    try:
        header("🤖 Git Auto-Commit avec IA")

        if force:
            info("⚡ MODE FORCE ACTIVÉ")

        # 1. Rebase automatique (seulement si pas sur branche de base)
        info("🔄 Étape 1: Synchronisation avec develop...")
        current_branch = run_git_command(['git', 'branch', '--show-current'],
                                         debug=debug, capture_output=True, text=True, check=True).stdout.strip()

        # Déterminer la branche de base
        base_branch = "develop"
        try:
            run_git_command(['git', 'show-ref', '--verify', '--quiet', 'refs/heads/develop'],
                            debug=debug, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # develop n'existe pas, utiliser main
            base_branch = "main"
            info("ℹ️  Branche develop non trouvée, utilisation de main")

        # Rebase seulement si on n'est PAS sur la branche de base
        if current_branch != base_branch:
            info(f"📥 Synchronisation avec {base_branch}...")

            try:
                # Fetch pour avoir les dernières infos
                run_git_command(['git', 'fetch', 'origin', base_branch], debug=debug, capture_output=True, check=True)

                # Check si la branche est déjà à jour
                behind_check = run_git_command(['git', 'rev-list', '--count', f'HEAD..origin/{base_branch}'],
                                               debug=debug, capture_output=True, text=True, check=True)
                behind_count = int(behind_check.stdout.strip())

                if behind_count == 0:
                    success(f"Branche déjà à jour avec {base_branch}")
                else:
                    info(f"🔄 Branche en retard de {behind_count} commits, rebase nécessaire...")

                    # Vérifie s'il y a des changements stagés
                    has_staged = GitUtils.has_staged_changes()

                    if has_staged:
                        info("📦 Sauvegarde des changements stagés...")
                        try:
                            run_git_command(['git', 'stash', 'push', '--staged', '-m', 'Auto-stash for rebase'],
                                            debug=debug, check=True, capture_output=True)
                            success("Changements sauvegardés")
                        except subprocess.CalledProcessError as e:
                            error(f"Erreur lors de la sauvegarde: {e}")
                            raise typer.Exit(1)

                    info(f"🔄 Rebase {current_branch} sur {base_branch}...")
                    if GitUtils.rebase_on_target(base_branch):
                        success("Rebase réussi")

                        # Restore les changements stagés si nécessaire
                        if has_staged:
                            info("📦 Restauration des changements...")
                            try:
                                run_git_command(['git', 'stash', 'pop'], debug=debug, check=True, capture_output=True)
                                success("Changements restaurés")
                            except subprocess.CalledProcessError as e:
                                error(f"Erreur lors de la restauration: {e}")
                                info("💡 Vérifiez avec 'git stash list' et 'git stash pop' manuellement")
                                raise typer.Exit(1)
                    else:
                        # Si le rebase échoue, on essaie de restaurer les changements
                        if has_staged:
                            info("🔄 Tentative de restauration des changements après échec...")
                            try:
                                run_git_command(['git', 'stash', 'pop'], debug=debug, check=True, capture_output=True)
                                success("Changements restaurés")
                            except subprocess.CalledProcessError:
                                warning("Changements en stash - utilisez 'git stash pop' après résolution")

                        warning("Conflits détectés ! Résolvez-les puis relancez la commande")
                        raise typer.Exit(1)

            except subprocess.CalledProcessError as e:
                error(f"Erreur lors de la vérification de {base_branch}: {e}")
                info("ℹ️  Continuons sans rebase...")
        else:
            info(f"ℹ️  Déjà sur {base_branch}, pas de rebase nécessaire")

        # 2. Scan sécurité UNIQUE de tous les fichiers modifiés
        info("🔄 Étape 2: Scan sécurité...")
        info("🔒 Scan sécurité des fichiers modifiés...")
        if not run_gitleaks_scan_all_modified(debug=debug):
            error("Secrets détectés - commit bloqué pour votre protection!")
            raise typer.Exit(1)
        success("Aucun secret détecté")

        # 3. Stage automatique (maintenant sécurisé car pré-scanné)
        info("🔄 Étape 3: Staging des fichiers...")
        info("📁 git add . automatique...")

        try:
            run_git_command(['git', 'add', '.'], debug=debug, check=True, capture_output=True)
            success("Fichiers stagés avec succès")
        except subprocess.CalledProcessError as e:
            error(f"Erreur git add: {e}")
            raise typer.Exit(1)

        # Vérifie qu'il y a maintenant des changements à commiter
        if not GitUtils.has_staged_changes():
            error("Aucun changement à commiter")
            raise typer.Exit(1)

        # 4. Initialise le gestionnaire multi-IA
        info("🔄 Étape 4: Initialisation IA...")
        ai = AIProvider()
        console.print(ai.get_status())

        # 5. Récupère les changements
        info("🔄 Étape 5: Analyse des changements...")
        info("🔍 Analyse des changements...")
        diff = GitUtils.get_staged_diff()
        files = GitUtils.get_staged_files()

        # 6. Analyse avec IA (fallback automatique)
        info("🔄 Étape 6: Génération du commit...")
        commit_data = ai.analyze_for_commit(diff, files)

        # 7. Execute le commit
        info("🔄 Étape 7: Commit et push...")
        run_git_commit(commit_data, force=force, debug=debug)

        success("🎉 Processus terminé avec succès!")

    except ValueError as e:
        error(f"Configuration: {e}")
        raise typer.Exit(1)
    except RuntimeError as e:
        error(f"Erreur Git: {e}")
        raise typer.Exit(1)
    except Exception as e:
        error(f"Erreur inattendue: {e}")
        raise typer.Exit(1)


# Alias pour la commande courte
@app.command(name="ac")
def auto_commit_short(
    force: bool = typer.Option(False, "--force", "-f", help="Force le commit sans demander confirmation"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes Git exécutées")
):
    """Alias court pour auto-commit"""
    auto_commit(force=force, debug=debug)


if __name__ == "__main__":
    app()