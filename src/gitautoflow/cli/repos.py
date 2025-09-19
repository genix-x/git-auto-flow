#!/usr/bin/env python3
"""
Git Auto-Flow - Gestion des repositories GitHub
Migration vers architecture Typer
"""

import sys
import subprocess
import time
import os
import json
from pathlib import Path
from subprocess import CalledProcessError
import shutil

import typer
from typing import Optional

# Import des utilitaires logger
from gitautoflow.utils.logger import info, success, error, warning, header, console

app = typer.Typer(help="Commandes de gestion des repositories GitHub")


def confirm(message: str) -> bool:
    """Demande confirmation à l'utilisateur"""
    response = console.input(f"[yellow]{message} (y/N):[/yellow] ").lower()
    return response in ['y', 'yes', 'o', 'oui']


def check_prerequisites() -> bool:
    """Vérifie que gh CLI est installé et configuré"""
    try:
        # Vérifier que gh est installé
        subprocess.run(['gh', '--version'], capture_output=True, check=True)

        # Vérifier que gh est authentifié
        result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            error("GitHub CLI n'est pas authentifié")
            info(" Lance: gh auth login")
            return False

        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        error("GitHub CLI (gh) n'est pas installé")
        info(" Installation: https://cli.github.com/")
        return False


def check_git_config() -> bool:
    """Vérifie et configure l'identité Git si nécessaire"""
    try:
        # Vérifier l'email
        result_email = subprocess.run(['git', 'config', '--global', 'user.email'],
                                    capture_output=True, text=True)
        # Vérifier le nom
        result_name = subprocess.run(['git', 'config', '--global', 'user.name'],
                                   capture_output=True, text=True)

        if result_email.returncode != 0 or not result_email.stdout.strip():
            warning("Email Git non configuré")
            return False

        if result_name.returncode != 0 or not result_name.stdout.strip():
            warning("Nom Git non configuré")
            return False

        info(f"Configuration Git: {result_name.stdout.strip()} <{result_email.stdout.strip()}>")
        return True

    except (subprocess.CalledProcessError, FileNotFoundError):
        error("Git n'est pas installé")
        return False


def configure_git_from_github():
    """Configure Git automatiquement depuis les infos GitHub"""
    try:
        info("Configuration automatique de Git depuis GitHub...")

        # Récupérer les infos utilisateur GitHub
        result = subprocess.run(['gh', 'api', 'user'], capture_output=True, text=True, check=True)

        import json
        user_info = json.loads(result.stdout)

        github_name = user_info.get('name') or user_info.get('login')
        github_email = user_info.get('email')

        # Si pas d'email public, essayer les emails privés
        if not github_email:
            try:
                email_result = subprocess.run(['gh', 'api', 'user/emails'],
                                            capture_output=True, text=True, check=True)
                emails = json.loads(email_result.stdout)
                primary_email = next((e['email'] for e in emails if e.get('primary')), None)
                github_email = primary_email or f"{user_info['login']}@users.noreply.github.com"
            except:
                github_email = f"{user_info['login']}@users.noreply.github.com"

        # Configurer Git
        subprocess.run(['git', 'config', '--global', 'user.name', github_name], check=True)
        subprocess.run(['git', 'config', '--global', 'user.email', github_email], check=True)

        success(f"Git configuré: {github_name} <{github_email}>")
        return True

    except Exception as e:
        error(f"Impossible de configurer Git automatiquement: {e}")
        error("Configure manuellement:")
        info('  git config --global user.name "Ton Nom"')
        info('  git config --global user.email "ton@email.com"')
        return False


def load_config():
    """Charge la configuration depuis le projet parent"""
    try:
        # Import dynamique du module de config
        import importlib.util
        config_path = Path(__file__).parent.parent.parent / "git-project-config.py"
        if not config_path.exists():
            return None

        spec = importlib.util.spec_from_file_location("git_project_config", config_path)
        git_project_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(git_project_config)
        return git_project_config.load_current_config()
    except Exception:
        return None


def run_command(command: list, cwd: Optional[str] = None, check: bool = True, debug: bool = False):
    """Helper pour exécuter une commande et logger le résultat"""
    if debug:
        info(f"[DEBUG] Commande: {' '.join(command)} in directory: {cwd or '.'}")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=check,
            cwd=cwd,
            env=os.environ
        )
        # Log stdout seulement si non vide
        if result.stdout and result.stdout.strip():
            console.print(f"[grey50]... {result.stdout.strip().splitlines()[-1]}[/grey50]")
        # Log stderr comme warning, sauf pour les messages de progression git
        if result.stderr and result.stderr.strip() and "cloning into" not in result.stderr.lower():
            warning(result.stderr.strip())
        return result
    except CalledProcessError as e:
        error(f"Command `{' '.join(command)}` failed in `{cwd or '.'}`:")
        if e.stderr:
            error(e.stderr.strip())
        elif e.stdout:
            error(e.stdout.strip())
        raise


def set_github_actions_permissions(repo_full_name: str, force: bool = False, debug: bool = False):
    """Configure le repo pour autoriser les GitHub Actions à créer et approuver des PRs"""
    info("Configuration des permissions pour les GitHub Actions...")

    # Confirmation
    if not force:
        if not confirm("✅ Autoriser les GitHub Actions à créer et approuver des pull requests ?"):
            warning("Configuration des permissions annulée.")
            return

    try:
        cmd = [
            'gh', 'api',
            '--method', 'PUT',
            f'/repos/{repo_full_name}/actions/permissions/workflow',
            '-f', 'default_workflow_permissions=write'
        ]
        run_command(cmd, check=True, debug=debug)
        success("Permissions pour les GitHub Actions configurées avec succès!")
    except CalledProcessError:
        error("Erreur lors de la configuration des permissions pour les GitHub Actions.")


def setup_local_repo(project_name: str, repo_url: str, working_dir: str, force: bool = False, debug: bool = False) -> str:
    """Clone le repo dans le working_dir"""
    try:
        info(f"Setup local repository dans {working_dir}")

        Path(working_dir).mkdir(parents=True, exist_ok=True)
        project_path = Path(working_dir) / project_name

        if not (project_path / ".git").is_dir():
            if project_path.exists():
                warning(f"Le dossier {project_path} existe mais n'est pas un repo git valide.")
                if not force and not confirm("Voulez-vous le supprimer et re-cloner le projet ?"):
                    error("Opération annulée. Le setup ne peut pas continuer.")
                    raise typer.Exit(1)

                info(f"Suppression du dossier existant: {project_path}")
                shutil.rmtree(str(project_path))

            info(f"Clonage du repository {repo_url}...")
            run_command(['git', 'clone', repo_url, str(project_path)], debug=debug)
        else:
            warning(f"Le repo git {project_path} existe déjà. On continue dedans.")

        success(f"✅ Repository cloné dans {project_path}")
        return str(project_path)

    except Exception as e:
        if "Opération annulée" in str(e):
            raise typer.Exit(1)
        error(f"Erreur lors du clone: {e}")
        raise typer.Exit(1)


def create_readme_workflow(project_path: str, project_name: str, debug: bool = False) -> bool:
    """Workflow complet README avec Git natif"""
    try:
        info("🚀 Workflow README avec Git natif")

        # 1. GÉRER LE REPO VIDE
        info("Initialisation du repository vide")
        gitkeep_path = Path(project_path) / ".gitkeep"
        gitkeep_path.write_text("# Initial commit\n")

        run_command(['git', 'add', '.gitkeep'], cwd=project_path, debug=debug)
        run_command(['git', 'commit', '-m', 'Initial commit'], cwd=project_path, debug=debug)
        run_command(['git', 'branch', '-M', 'main'], cwd=project_path, debug=debug)
        run_command(['git', 'push', '-u', 'origin', 'main'], cwd=project_path, debug=debug)

        # 2. Créer develop depuis main
        info("Création de la branche develop")
        run_command(['git', 'checkout', '-b', 'develop'], cwd=project_path, debug=debug)
        run_command(['git', 'push', '-u', 'origin', 'develop'], cwd=project_path, debug=debug)

        # 3. Créer feature branch depuis develop
        info("Création de feature/readme")
        run_command(['git', 'checkout', '-b', 'feature/readme'], cwd=project_path, debug=debug)

        # 4. Créer README avec contenu dynamique
        info("Génération du README.md")
        readme_path = Path(project_path) / "README.md"
        readme_content = f"""# {project_name}

Projet {project_name} créé avec Git Auto-Flow.

## Installation

```bash
git clone https://github.com/[ORG]/{project_name}.git
cd {project_name}
```
## Utilisation
À documenter...
"""
        readme_path.write_text(readme_content)

        # 5. Commit et push feature
        run_command(['git', 'add', 'README.md'], cwd=project_path, debug=debug)
        run_command(['git', 'commit', '-m', 'feat: Add README.md'], cwd=project_path, debug=debug)
        run_command(['git', 'push', '-u', 'origin', 'feature/readme'], cwd=project_path, debug=debug)

        # 6. PR feature → develop + merge automatique
        info("Création PR feature/readme → develop")
        run_command(['gh', 'pr', 'create', '--base', 'develop', '--head', 'feature/readme',
                    '--title', 'feat: Add README', '--body', 'Initial README', '--fill'], cwd=project_path, debug=debug)
        run_command(['gh', 'pr', 'merge', '--squash'], cwd=project_path, debug=debug)

        # 7. Retour sur develop et pull des changements
        run_command(['git', 'checkout', 'develop'], cwd=project_path, debug=debug)
        run_command(['git', 'pull'], cwd=project_path, debug=debug)

        # 8. PR develop → main + merge automatique
        info("Création PR develop → main (Release)")
        run_command(['gh', 'pr', 'create', '--base', 'main', '--head', 'develop',
                    '--title', 'Release v0.1.0', '--body', 'First release', '--fill'], cwd=project_path, debug=debug)
        run_command(['gh', 'pr', 'merge', '--squash'], cwd=project_path, debug=debug)

        # 9. Tag de release
        info("Création du tag v0.1.0")
        run_command(['git', 'checkout', 'main'], cwd=project_path, debug=debug)
        run_command(['git', 'pull'], cwd=project_path, debug=debug)
        run_command(['git', 'tag', 'v0.1.0'], cwd=project_path, debug=debug)
        run_command(['git', 'push', '--tags'], cwd=project_path, debug=debug)

        # 10. NETTOYAGE : Supprimer la branche feature/readme
        info("Nettoyage des branches temporaires")
        run_command(['git', 'push', 'origin', '--delete', 'feature/readme'], cwd=project_path, debug=debug)
        run_command(['git', 'branch', '-D', 'feature/readme'], cwd=project_path, debug=debug)

        success("✅ Workflow complet terminé !")
        success("✅ Repository prêt avec README, branches GitFlow et release v0.1.0")
        return True

    except Exception as e:
        error(f"Erreur workflow: {e}")
        return False


@app.command(name="create")
def create_repo(
    repo_spec: str = typer.Argument(..., help="Repository à créer (format: owner/repo-name ou repo-name)"),
    private: bool = typer.Option(True, "--private/--public", help="Repository privé ou public"),
    force: bool = typer.Option(False, "--force", "-f", help="Mode non-interactif (aucune confirmation)"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes exécutées")
):
    """Crée un nouveau repository GitHub et setup l'environnement complet"""

    # Parser le format owner/repo-name ou repo-name
    if '/' in repo_spec:
        github_org, project_name = repo_spec.split('/', 1)
        info(f"Format détecté: {github_org}/{project_name}")
    else:
        project_name = repo_spec
        # Fallback vers config ou défaut
        config = load_config()
        github_org = config.get('GITHUB_ORG', 'ousamabenyounes') if config else 'ousamabenyounes'
        warning(f"Aucun owner spécifié, utilisation de: {github_org}")

    # Validation du nom de projet et owner
    if not project_name.replace('-', '').replace('_', '').isalnum():
        error("Nom de repository invalide.")
        info("Utilise uniquement des lettres, chiffres, '-', et '_'.")
        raise typer.Exit(1)

    if not github_org.replace('-', '').replace('_', '').isalnum():
        error("Nom d'organisation invalide.")
        info("Utilise uniquement des lettres, chiffres, '-', et '_'.")
        raise typer.Exit(1)

    # Vérification des prérequis
    if not check_prerequisites():
        raise typer.Exit(1)

    # Vérifier et configurer Git si nécessaire
    if not check_git_config():
        if not force:
            if not confirm("🔧 Configurer Git automatiquement depuis GitHub ?"):
                error("Configuration Git requise pour continuer")
                raise typer.Exit(1)
        else:
            info("🔧 Configuration automatique de Git (mode force)")

        if not configure_git_from_github():
            raise typer.Exit(1)

    header(f"Création du projet: {project_name}")
    info(f"Organisation: {github_org}")
    info(f"Visibilité: {'Privé' if private else 'Public'}")

    repo_url = f"https://github.com/{github_org}/{project_name}"
    info(f"URL du repo: {repo_url}")
    console.print()

    # Confirmation
    if not force:
        if not confirm("✅ Lancer la création du repository GitHub ?"):
            warning("Création annulée par l'utilisateur.")
            raise typer.Exit(0)
    else:
        info("🚀 Mode force activé - Création automatique du repository")

    try:
        # Création du repo via gh CLI
        info("Création du repository GitHub en cours...")

        visibility_flag = '--private' if private else '--public'

        cmd = [
            'gh', 'repo', 'create',
            f'{github_org}/{project_name}',
            visibility_flag,
            '--description', f'Projet {project_name} créé avec Git Auto-Flow'
        ]

        run_command(cmd, check=True, debug=debug)
        success(f"Repository GitHub {'privé' if private else 'public'} {github_org}/{project_name} créé avec succès!")

        # Configuration des permissions
        set_github_actions_permissions(f"{github_org}/{project_name}", force=force, debug=debug)

        # Délai pour laisser GitHub propager le repository
        info("Attente de la propagation du repository GitHub...")
        time.sleep(3)

    except CalledProcessError as e:
        if "already exists" in str(e.stderr):
            warning(f"Le repository {repo_url} existe déjà.")
            if not force and not confirm("Voulez-vous continuer le setup local avec ce repo existant ?"):
                warning("Opération annulée.")
                raise typer.Exit(0)
        else:
            error("Erreur critique lors de la création du repository GitHub.")
            raise typer.Exit(1)

    # WORKFLOW DE SETUP
    if not force:
        if not confirm("🚀 Lancer le workflow de setup complet (clone, branches, README, PR, release) ?"):
            warning("Workflow de setup annulé.")
            info(f"Vous pouvez cloner manuellement le repo: git clone {repo_url}.git")
            raise typer.Exit(0)
    else:
        info("🚀 Mode force activé - Setup automatique complet")

    try:
        header("🚀 Démarrage du workflow de setup")

        # Chargement de la config pour WORKING_DIR
        config = load_config()
        if not config:
            error("Aucune configuration trouvée pour WORKING_DIR")
            info(" Lance d'abord: git pc")
            raise typer.Exit(1)

        working_dir = config.get('WORKING_DIR')
        if not working_dir:
            error("La variable WORKING_DIR n'est pas configurée.")
            info("Lancez `git pc` pour la configurer.")
            raise typer.Exit(1)

        project_path = setup_local_repo(project_name, f"{repo_url}.git", working_dir, force=force, debug=debug)

        if not create_readme_workflow(project_path, project_name, debug=debug):
            error("❌ Le workflow de setup a échoué")
            raise typer.Exit(1)

        header("🎉 WORKFLOW TERMINÉ AVEC SUCCÈS 🎉")
        release_url = f"{repo_url}/releases/tag/v0.1.0"
        console.print(f"  [bold]Projet local:[/] [cyan]{project_path}[/]")
        console.print(f"  [bold]Repo GitHub:[/] [link={repo_url}]{repo_url}[/link]")
        console.print(f"  [bold]Release v0.1.0:[/] [link={release_url}]{release_url}[/link]")
        console.print(f"\n[green]Vous pouvez maintenant faire `cd {project_path}` pour commencer.[/green]")

    except Exception as e:
        error(f"Le workflow de setup a échoué: {e}")
        error("Le repository GitHub a été créé, mais le setup local a rencontré un problème.")
        raise typer.Exit(1)


@app.command()
def delete(
    repo_spec: str = typer.Argument(..., help="Repository à supprimer (format: owner/repo-name ou repo-name)"),
    force: bool = typer.Option(False, "--force", "-f", help="Mode non-interactif (aucune confirmation)"),
    debug: bool = typer.Option(False, "--debug", help="Affiche les commandes exécutées")
):
    """Supprime un repository GitHub (ATTENTION: action irréversible!)"""

    if not check_prerequisites():
        raise typer.Exit(1)

    # Parse du repo spec
    if '/' in repo_spec:
        owner, repo_name = repo_spec.split('/', 1)
    else:
        # Utiliser l'utilisateur GitHub courant
        try:
            result = subprocess.run(['gh', 'api', 'user'], capture_output=True, text=True, check=True)
            user_data = json.loads(result.stdout)
            owner = user_data.get('login', 'unknown')
            repo_name = repo_spec
            repo_spec = f"{owner}/{repo_name}"
        except:
            error("Impossible de déterminer l'utilisateur GitHub. Utilisez le format owner/repo-name")
            raise typer.Exit(1)

    header(f"🗑️ Suppression du repository GitHub: {repo_spec}")

    # Vérifier que le repository existe
    try:
        if debug:
            info(f"[DEBUG] Vérification de l'existence: gh repo view {repo_spec}")
        result = subprocess.run(['gh', 'repo', 'view', repo_spec], capture_output=True, text=True, check=True)
        info(f"✅ Repository trouvé: {repo_spec}")
    except subprocess.CalledProcessError:
        error(f"❌ Repository '{repo_spec}' introuvable ou inaccessible")
        raise typer.Exit(1)

    # Avertissement de sécurité
    warning("⚠️  ATTENTION: Cette action est IRREVERSIBLE!")
    warning("⚠️  Toutes les données (code, issues, PRs, releases) seront PERDUES!")
    console.print(f"[red bold]Repository à supprimer: {repo_spec}[/red bold]")

    # Demande de confirmation
    if not force:
        if not confirm(f"❌ Êtes-vous ABSOLUMENT SÛR de vouloir supprimer '{repo_spec}' ?"):
            info("✅ Suppression annulée - aucune action effectuée")
            return

        # Double confirmation pour plus de sécurité
        console.print(f"\n[red]Tapez exactement '[bold]{repo_name}[/bold]' pour confirmer:[/red]")
        confirmation = console.input("[yellow]> [/yellow]").strip()
        if confirmation != repo_name:
            error(f"❌ Confirmation incorrecte (attendu: '{repo_name}', reçu: '{confirmation}')")
            info("✅ Suppression annulée - aucune action effectuée")
            return
    else:
        warning("🔥 MODE FORCE - Suppression automatique sans confirmation")

    try:
        # Commande de suppression
        cmd = ['gh', 'repo', 'delete', repo_spec, '--yes']

        if debug:
            info(f"[DEBUG] Commande: {' '.join(cmd)}")

        info(f"🗑️ Suppression en cours de {repo_spec}...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        success(f"✅ Repository '{repo_spec}' supprimé avec succès!")
        info("💡 Le repository n'est plus accessible et toutes ses données sont perdues")

    except subprocess.CalledProcessError as e:
        error(f"❌ Erreur lors de la suppression: {e.stderr if e.stderr else str(e)}")
        if "403" in str(e.stderr):
            error("💡 Vérifiez que vous avez les permissions d'administration sur ce repository")
        elif "404" in str(e.stderr):
            error("💡 Le repository n'existe pas ou n'est pas accessible")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()