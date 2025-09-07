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

def create_github_repo(project_name, force=False):
    """Crée un repository GitHub"""
    
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
    org = config.get('GITHUB_ORG', 'ousamabenyounes')
    
    info(" Création du repository GitHub...")
    info(f" Organisation: {org}")
    info(f" Nom du projet: {project_name}")
    info(f" URL finale: https://github.com/{org}/{project_name}")
    console.print()
    
    # Confirmation
    if not force and not confirm("✅ Créer le repository"):
        warning("Création annulée")
        sys.exit(0)
    
    try:
        # Création du repo via gh CLI
        info(" Création en cours...")
        
        cmd = [
            'gh', 'repo', 'create',
            f'{org}/{project_name}',
            '--public',
            '--description', f'Projet {project_name} créé avec Git Auto-Flow'
        ]
        
        subprocess.run(cmd, check=True)
        
        success(f"Repository {org}/{project_name} créé avec succès!")
        info(f" https://github.com/{org}/{project_name}")
        console.print()
        info(" Prochaines étapes suggérées:")
        info(f"   git repo-init {project_name}    # Initialiser la structure")
        info(f"   git project-create {project_name} # Créer projet complet")
        
    except subprocess.CalledProcessError as e:
        error("Erreur lors de la création du repository:")
        error(f"   {e}")
        console.print()
        warning(" Causes possibles:")
        info("   - Le repository existe déjà")
        info("   - Permissions insuffisantes")
        info("   - Problème de connexion")
        sys.exit(1)

def main():
    """Point d'entrée principal"""
    
    # Vérification des arguments
    if len(sys.argv) < 2:
        header("Git Auto-Flow - Création de Repository GitHub")
        console.print()
        info(" Usage:")
        info("   git repo-create <nom-projet> [options]")
        console.print()
        info("️  Options:")
        info("   -f, --force    Créer sans confirmation")
        info("   -h, --help     Afficher cette aide")
        console.print()
        info(" Exemples:")
        info("   git repo-create mon-super-projet")
        info("   git repo-create api-backend --force")
        sys.exit(1)
    
    # Parsing des arguments
    project_name = sys.argv[1]
    force = '--force' in sys.argv or '-f' in sys.argv
    
    # Validation du nom de projet
    if not project_name.replace('-', '').replace('_', '').isalnum():
        error("Nom de projet invalide")
        info(" Utilise uniquement des lettres, chiffres, - et _")
        sys.exit(1)
    
    # Création du repo
    create_github_repo(project_name, force)

if __name__ == "__main__":
    main()
