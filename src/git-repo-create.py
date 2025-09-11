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
    if not force:
        if not confirm("✅ Lancer la création du repository GitHub ?"):
            warning("Création annulée par l'utilisateur.")
            sys.exit(0)
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
        
        run_command(cmd, check=True)
        success(f"Repository GitHub {'privé' if private else 'public'} {github_org}/{project_name} créé avec succès!")

        # Délai pour laisser GitHub propager le repository
        info("Attente de la propagation du repository GitHub...")
        import time
        time.sleep(3)  # Attendre 3 secondes
        
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
    if not force:
        if not confirm("🚀 Lancer le workflow de setup complet (clone, branches, README, PR, release) ?"):
            warning("Workflow de setup annulé.")
            info(f"Vous pouvez cloner manuellement le repo: git clone {repo_url}.git")
            sys.exit(0)
    else:
        info("🚀 Mode force activé - Setup automatique complet")

    try:
        header("🚀 Démarrage du workflow de setup")
        
        working_dir = config.get('WORKING_DIR')
        if not working_dir:
            error("La variable WORKING_DIR n'est pas configurée.")
            info("Lancez `git pc` pour la configurer.")
            sys.exit(1)

        project_path = setup_local_repo(project_name, f"{repo_url}.git", working_dir, force=force)
        
        if not create_readme_workflow(project_path, project_name):
            error("❌ Le workflow de setup a échoué")
            return
        
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
    print(f"Executing command: {' '.join(command)} in directory: {cwd or '.'}") # Added for debugging
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

def setup_local_repo(project_name, repo_url, working_dir, force=False):
    """Clone le repo dans le working_dir. Si le dossier existe et n'est pas un repo git,
    demande avant de le remplacer."""
    try:
        info(f"Setup local repository dans {working_dir}")
        
        Path(working_dir).mkdir(parents=True, exist_ok=True)
        project_path = Path(working_dir) / project_name
        
        if not (project_path / ".git").is_dir():
            if project_path.exists():
                warning(f"Le dossier {project_path} existe mais n'est pas un repo git valide.")
                if not force and not confirm("Voulez-vous le supprimer et re-cloner le projet ?"):
                    error("Opération annulée. Le setup ne peut pas continuer.")
                    raise Exception("Setup local annulé par l'utilisateur.")
                
                import shutil
                info(f"Suppression du dossier existant: {project_path}")
                shutil.rmtree(str(project_path))

            info(f"Clonage du repository {repo_url}...")
            run_command(['git', 'clone', repo_url, str(project_path)])
        else:
            warning(f"Le repo git {project_path} existe déjà. On continue dedans.")
        
        success(f"✅ Repository cloné dans {project_path}")
        return str(project_path)
        
    except Exception as e:
        if "annulé par l'utilisateur" in str(e):
            raise
        error(f"Erreur lors du clone: {e}")
        raise

def create_readme_workflow(project_path, project_name):
    """Workflow complet README avec Git natif - séquence testée et validée"""
    try:
        info("🚀 Workflow README avec Git natif")
        
        # 1. GÉRER LE REPO VIDE (obligatoire pour les repos GitHub vides)
        info("Initialisation du repository vide")
        gitkeep_path = Path(project_path) / ".gitkeep"
        gitkeep_path.write_text("# Initial commit\n")
        
        run_command(['git', 'add', '.gitkeep'], cwd=project_path)
        run_command(['git', 'commit', '-m', 'Initial commit'], cwd=project_path)
        run_command(['git', 'branch', '-M', 'main'], cwd=project_path)
        run_command(['git', 'push', '-u', 'origin', 'main'], cwd=project_path)
        
        # 2. Créer develop depuis main
        info("Création de la branche develop")
        run_command(['git', 'checkout', '-b', 'develop'], cwd=project_path)
        run_command(['git', 'push', '-u', 'origin', 'develop'], cwd=project_path)
        
        # 3. Créer feature branch depuis develop
        info("Création de feature/readme")
        run_command(['git', 'checkout', '-b', 'feature/readme'], cwd=project_path)
        
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
        
        # 5. Commit et push feature (Git natif - pas d'IA !)
        run_command(['git', 'add', 'README.md'], cwd=project_path)
        run_command(['git', 'commit', '-m', 'feat: Add README.md'], cwd=project_path)
        run_command(['git', 'push', '-u', 'origin', 'feature/readme'], cwd=project_path)
        
        # 6. PR feature → develop + merge automatique
        info("Création PR feature/readme → develop")
        run_command(['gh', 'pr', 'create', '--base', 'develop', '--head', 'feature/readme', 
                    '--title', 'feat: Add README', '--body', 'Initial README', '--fill'], cwd=project_path)
        run_command(['gh', 'pr', 'merge', '--squash'], cwd=project_path)
        
        # 7. Retour sur develop et pull des changements
        run_command(['git', 'checkout', 'develop'], cwd=project_path)
        run_command(['git', 'pull'], cwd=project_path)
        
        # 8. PR develop → main + merge automatique
        info("Création PR develop → main (Release)")
        run_command(['gh', 'pr', 'create', '--base', 'main', '--head', 'develop',
                    '--title', 'Release v0.1.0', '--body', 'First release', '--fill'], cwd=project_path)
        run_command(['gh', 'pr', 'merge', '--squash'], cwd=project_path)
        
        # 9. Tag de release
        info("Création du tag v0.1.0")
        run_command(['git', 'checkout', 'main'], cwd=project_path)
        run_command(['git', 'pull'], cwd=project_path)
        run_command(['git', 'tag', 'v0.1.0'], cwd=project_path)
        run_command(['git', 'push', '--tags'], cwd=project_path)
        
        # 10. NETTOYAGE : Supprimer la branche feature/readme
        info("Nettoyage des branches temporaires")
        run_command(['git', 'push', 'origin', '--delete', 'feature/readme'], cwd=project_path)
        run_command(['git', 'branch', '-D', 'feature/readme'], cwd=project_path)
        
        success("✅ Workflow complet terminé !")
        success("✅ Repository prêt avec README, branches GitFlow et release v0.1.0")
        return True
        
    except Exception as e:
        error(f"Erreur workflow: {e}")
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
        info("Utilise uniquement des lettres, chiffres, '-', et '_'.")
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