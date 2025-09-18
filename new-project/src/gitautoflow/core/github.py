#!/usr/bin/env python3
"""
GitAutoFlow - Module de gestion GitHub
"""

import subprocess
import sys
from pathlib import Path
from ..utils.logger import info, success, error, warning, header

def check_gh_cli():
    """Vérifier que gh CLI est installé et configuré"""
    try:
        result = subprocess.run(['gh', 'auth', 'status'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            error("GitHub CLI n'est pas authentifié")
            info("Lancez: gh auth login")
            return False
        return True
    except FileNotFoundError:
        error("GitHub CLI (gh) n'est pas installé")
        info("Installation: https://cli.github.com/")
        return False

def create_github_repo(project_name, org=None, force=False, private=True):
    """Créer un repository GitHub via gh CLI"""
    
    header(f"Création du repository GitHub: {project_name}")
    
    # Vérification préalable
    if not check_gh_cli():
        return False
    
    # Construction de la commande
    cmd = ['gh', 'repo', 'create']
    
    if org:
        cmd.append(f"{org}/{project_name}")
    else:
        cmd.append(project_name)
    
    # Options
    cmd.extend(['--description', f'Repository {project_name}'])
    
    if private:
        cmd.append('--private')
    else:
        cmd.append('--public')
    
    if force:
        cmd.append('--confirm')
    
    # Exécution
    try:
        info(f"Commande: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        success(f"Repository {project_name} créé avec succès!")
        if result.stdout:
            info(result.stdout.strip())
        
        return True
        
    except subprocess.CalledProcessError as e:
        error(f"Erreur lors de la création: {e}")
        if e.stderr:
            error(f"Détails: {e.stderr.strip()}")
        return False
