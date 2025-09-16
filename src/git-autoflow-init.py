#!/usr/bin/env python3
"""
Git Auto-Flow - Initialisation
Initialise un projet existant pour utiliser git-auto-flow.
Pour le moment, crée la branche 'develop' si elle n'existe pas.
"""

import sys
import subprocess
from pathlib import Path

# Assurez-vous que le chemin du projet est dans le sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.logger import info, success, error, warning

def run_command(command, check=True):
    """Exécute une commande shell et retourne le résultat."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=check,
            encoding='utf-8'
        )
        return result
    except subprocess.CalledProcessError as e:
        error(f"Erreur lors de l'exécution de `{' '.join(command)}`:")
        if e.stderr:
            error(e.stderr.strip())
        raise e

def get_default_branch():
    """Récupère la branche par défaut (main ou master)."""
    for branch in ["main", "master"]:
        # Vérifie l'existence de la branche sur le remote 'origin'
        result = run_command(['git', 'ls-remote', '--heads', 'origin', branch], check=False)
        if result.returncode == 0 and result.stdout:
             info(f"Branche par défaut trouvée sur origin: '{branch}'")
             return branch
    
    # Si non trouvée sur le remote, cherche en local
    for branch in ["main", "master"]:
        result = run_command(['git', 'rev-parse', '--verify', f'refs/heads/{branch}'], check=False)
        if result.returncode == 0:
            info(f"Branche par défaut trouvée en local: '{branch}'")
            return branch

    error("Impossible de trouver la branche 'main' ou 'master'.")
    sys.exit(1)

def main():
    """Point d'entrée principal."""
    info("Initialisation de Git Auto-Flow...")

    # 1. Vérifier si la branche 'develop' existe sur le remote 'origin'
    info("Vérification de la branche 'develop' sur le remote...")
    result_remote = run_command(['git', 'ls-remote', '--heads', 'origin', 'develop'], check=False)
    
    if result_remote.stdout.strip():
        warning("La branche 'develop' existe déjà sur le remote 'origin'.")
        # Vérifier si elle existe localement
        result_local = run_command(['git', 'branch', '--list', 'develop'], check=False)
        if not result_local.stdout.strip():
            info("La branche 'develop' n'existe pas localement. Création en cours...")
            run_command(['git', 'checkout', '--track', 'origin/develop'])
            success("Branche 'develop' créée localement et configurée pour suivre 'origin/develop'.")
        else:
            # S'assurer que la branche locale suit bien la branche remote
            info("Vérification du suivi de la branche locale 'develop'...")
            run_command(['git', 'branch', '--set-upstream-to=origin/develop', 'develop'])
            info("La branche locale 'develop' est bien configurée pour suivre 'origin/develop'.")
    else:
        # 2. Si elle n'existe pas sur le remote, la créer
        info("La branche 'develop' n'existe pas sur le remote.")
        default_branch = get_default_branch()
        
        info(f"Création de la branche 'develop' à partir de '{default_branch}'...")
        
        # D'abord, s'assurer que la branche par défaut est à jour
        info(f"Synchronisation de la branche '{default_branch}'...")
        run_command(['git', 'checkout', default_branch])
        run_command(['git', 'pull', 'origin', default_branch])

        # Créer et pusher la branche develop
        run_command(['git', 'checkout', '-b', 'develop'])
        info("Push de la nouvelle branche 'develop' vers 'origin'...")
        run_command(['git', 'push', '-u', 'origin', 'develop'])
        success("Branche 'develop' créée et poussée sur 'origin'.")

    success("Initialisation de Git Auto-Flow terminée !")

if __name__ == "__main__":
    main()
