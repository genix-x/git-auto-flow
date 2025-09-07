#!/usr/bin/env python3
"""
Git Auto-Flow - Création de repository GitHub
Crée un nouveau repo GitHub via gh CLI
"""

import sys
import subprocess
from pathlib import Path

# Import du logger centralisé
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import logger, info, success, error, warning, header, console
import importlib.util
spec = importlib.util.spec_from_file_location("git_project_config", Path(__file__).parent / "git-project-config.py")
git_project_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(git_project_config)
load_config = git_project_config.load_current_config

def confirm(message):
    """Demande confirmation à l'utilisateur"""
    response = console.input(f"[yellow]{message} (y/N):[/yellow] ").lower()
    return response in ['y', 'yes', 'o', 'oui']

def check_prerequisites():
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

def create_github_repo(project_name, org=None, force=False, private=True):
    """Crée un nouveau repository GitHub et setup l'environnement complet"""
    
    # Vérification des prérequis
    if not check_prerequisites():
        sys.exit(1)
    
    # Chargement de la config
    config = load_config()
    if not config:
        error("Aucune configuration trouvée")
        info(" Lance d'abord: git pc")
        sys.exit(1)
    
    # Récupération des paramètres
    github_org = org or config.get('GITHUB_ORG', 'ousamabenyounes')
    
    header(f"Création du projet: {project_name}")
    info(f"Organisation: {github_org}")
    info(f"Visibilité: {'Privé' if private else 'Public'}")
    
    repo_url = f"https://github.com/{github_org}/{project_name}"
    info(f"URL du repo: {repo_url}")
    console.print()

    # Confirmation
    if not force and not confirm("✅ Lancer la création du repository GitHub ?"):
        warning("Création annulée par l'utilisateur.")
        sys.exit(0)
    
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
        
        run_command(cmd, check=True)
        success(f"Repository GitHub {'privé' if private else 'public'} {github_org}/{project_name} créé avec succès!")
        
    except CalledProcessError as e:
        if "already exists" in e.stderr:
            warning(f"Le repository {repo_url} existe déjà.")
            if not force and not confirm("Voulez-vous continuer le setup local avec ce repo existant ?"):
                warning("Opération annulée.")
                sys.exit(0)
        else:
            error("Erreur critique lors de la création du repository GitHub.")
            sys.exit(1)

    # --- WORKFLOW DE SETUP ---
    if not force and not confirm("🚀 Lancer le workflow de setup complet (clone, branches, README, PR, release) ?"):
        warning("Workflow de setup annulé.")
        info(f"Vous pouvez cloner manuellement le repo: git clone {repo_url}.git")
        sys.exit(0)

    try:
        header("🚀 Démarrage du workflow de setup")
        
        working_dir = config.get('WORKING_DIR')
        if not working_dir:
            error("La variable WORKING_DIR n'est pas configurée.")
            info("Lancez `git pc` pour la configurer.")
            sys.exit(1)

        project_path = setup_local_repo(project_name, f"{repo_url}.git", working_dir)
        
        if not setup_develop_branch(project_path):
            raise Exception("Échec de la création de la branche develop.")

        if not create_readme_feature(project_path, project_name):
            raise Exception("Échec de la création de la feature README.")

        if not auto_commit_and_pr(project_path, force_mode=True):
            raise Exception("Échec du commit automatique et de la création de la PR.")

        if not auto_deploy_release(project_path, force_mode=True):
            raise Exception("Échec du déploiement de la release initiale.")
        
        header("🎉 WORKFLOW TERMINÉ AVEC SUCCÈS 🎉")
        release_url = f"{repo_url}/releases/tag/v0.1.0"
        console.print(f"  [bold]Projet local:[/] [cyan]{project_path}[/]")
        console.print(f"  [bold]Repo GitHub:[/] [link={repo_url}]{repo_url}[/link]")
        console.print(f"  [bold]Release v0.1.0:[/] [link={release_url}]{release_url}[/link]")
        console.print(f"\n[green]Vous pouvez maintenant faire `cd {project_path}` pour commencer.[/green]")

    except Exception as e:
        error(f"Le workflow de setup a échoué: {e}")
        error("Le repository GitHub a été créé, mais le setup local a rencontré un problème.")
        sys.exit(1)

from subprocess import CalledProcessError
import os

# =============================================
# NEW WORKFLOW FUNCTIONS
# =============================================

def run_command(command, cwd=None, check=True):
    """Helper to run a command and log output/errors."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=check,
            cwd=cwd,
            env=os.environ
        )
        # Log stdout only if it's not empty to avoid clutter
        if result.stdout and result.stdout.strip():
            console.print(f"[grey50]... {result.stdout.strip().splitlines()[-1]}[/grey50]")
        # Log stderr as a warning, unless it's a git progress message
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

def setup_local_repo(project_name, repo_url, working_dir):
    """Clone le repo dans le working_dir et se positionne dedans"""
    try:
        info(f"Setup local repository dans {working_dir}")
        
        Path(working_dir).mkdir(parents=True, exist_ok=True)
        
        project_path = Path(working_dir) / project_name
        
        if not project_path.exists():
            run_command(['git', 'clone', repo_url, str(project_path)])
        else:
            warning(f"Le dossier {project_path} existe déjà. On continue dedans.")
        
        success(f"✅ Repository cloné dans {project_path}")
        return str(project_path)
        
    except Exception as e:
        error(f"Erreur lors du clone: {e}")
        raise

def setup_develop_branch(project_path):
    """Crée et push la branche develop"""
    try:
        info("Création branche develop")
        
        try:
            run_command(['git', 'checkout', '-b', 'develop'], cwd=project_path)
        except CalledProcessError as e:
            if "already exists" in e.stderr or "existe déjà" in e.stderr:
                warning("La branche 'develop' existe déjà. On se positionne dessus.")
                run_command(['git', 'checkout', 'develop'], cwd=project_path)
            else:
                raise

        run_command(['git', 'push', '-u', 'origin', 'develop'], cwd=project_path)
        
        success("✅ Branche develop créée et pushée")
        return True
        
    except Exception as e:
        error(f"Erreur création develop: {e}")
        return False

def create_readme_feature(project_path, project_name):
    """Crée une feature branch readme avec fichier README.md"""
    try:
        info("Création feature readme")
        
        run_command(['git', 'flow', 'feature', 'start', 'readme'], cwd=project_path)
        
        readme_path = Path(project_path) / "README.md"
        readme_path.write_text(f"# {project_name}\n")

        if not readme_path.exists():
            raise FileNotFoundError("Le fichier README.md n'a pas été créé.")
        
        success("✅ README.md créé dans feature/readme")
        return True
        
    except Exception as e:
        error(f"Erreur feature readme: {e}")
        return False

def auto_commit_and_pr(project_path, force_mode=True):
    """Commit automatique et création PR vers develop"""
    try:
        info("Commit automatique et PR")
        
        run_command(['git', 'add', 'README.md'], cwd=project_path)
        
        cmd = ['git', 'ca']
        if force_mode:
            cmd.append('--force')
        
        run_command(cmd, cwd=project_path)
        
        success("✅ Commit effectué et PR créée vers develop")
        return True
        
    except Exception as e:
        error(f"Erreur commit/PR: {e}")
        return False

def auto_deploy_release(project_path, force_mode=True):
    """Lance git deploy pour créer le premier tag"""
    try:
        info("Déploiement automatique v0.1.0")
        
        cmd = ['git', 'deploy']
        if force_mode:
            cmd.append('--force')
        
        run_command(cmd, cwd=project_path)
        
        tags_result = run_command(['git', 'tag'], cwd=project_path, check=False)
        if 'v0.1.0' in tags_result.stdout:
            success("Vérification: Tag v0.1.0 trouvé.")
        else:
            warning("Vérification: Tag v0.1.0 non trouvé.")
        
        success("✅ Release v0.1.0 créée avec succès")
        return True
        
    except Exception as e:
        error(f"Erreur déploiement: {e}")
        return False

def main():
    """Point d'entrée principal"""
    
    args = sys.argv[1:]
    project_name = None
    force = False
    org = None
    private = True  # Par défaut privé

    if not args or '-h' in args or '--help' in args:
        header("Git Auto-Flow - Création de Repository GitHub")
        console.print()
        info(" Usage:")
        info("   git repo-create <nom-projet> [options]")
        console.print()
        info("️  Options:")
        info("   --org <orga>   Organisation GitHub (défaut: config)")
        info("   --public       Créer un repository public (défaut: privé)")
        info("   -f, --force    Mode non-interactif (aucune confirmation)")
        info("   -h, --help     Afficher cette aide")
        console.print()
        info(" Exemples:")
        info("   git repo-create mon-super-projet")
        info("   git repo-create api-backend --force --org my-company --public")
        sys.exit(0)

    # Simple parsing
    if args and not args[0].startswith('-'):
        project_name = args[0]

    if not project_name:
        error("Le nom du projet est manquant.")
        info("Usage: git repo-create <nom-projet> [options]")
        sys.exit(1)

    force = '--force' in args or '-f' in args
    
    if '--org' in args:
        try:
            org_index = args.index('--org') + 1
            if org_index < len(args) and not args[org_index].startswith('-'):
                org = args[org_index]
            else:
                raise ValueError()
        except (ValueError, IndexError):
            error("L'argument --org doit être suivi d'un nom d'organisation.")
            sys.exit(1)

    if '--public' in args:
        private = False

    # Validation du nom de projet
    if not project_name.replace('-', '').replace('_', '').isalnum():
        error("Nom de projet invalide.")
        info("Utilise uniquement des lettres, chiffres, '-' et '_'.")
        sys.exit(1)
    
    # Demander à l'utilisateur si pas en mode force
    if not force:
        # Si --public est passé, on ne demande pas
        if '--public' not in args:
            user_input = console.input("[yellow]Voulez-vous que ce repository soit privé ? (O/n):[/yellow] ").strip().lower()
            if user_input in ['n', 'non', 'no']:
                private = False

    # Lancement du processus
    create_github_repo(project_name, org=org, force=force, private=private)

if __name__ == "__main__":
    main()
