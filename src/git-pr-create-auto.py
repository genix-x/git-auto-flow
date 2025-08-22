#!/usr/bin/env python3
"""
Script pour automatiser complètement: rebase + push + création de PR avec Gemini
Équivaut à git feature-finish + git-pr-auto
"""

import sys
import argparse
from pathlib import Path

# Ajout du dossier lib au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from git_utils import GitUtils


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Finaliser une feature et créer automatiquement une PR avec Gemini"
    )
    parser.add_argument(
        '--base', '-b',
        default='develop',
        help='Branche de base pour la PR (défaut: develop)'
    )
    parser.add_argument(
        '--draft', '-d',
        action='store_true',
        help='Créer la PR en mode draft'
    )
    
    args = parser.parse_args()
    
    print("🚀 Git PR Create Auto - Workflow complet")
    print("=" * 50)
    
    # Vérifie les prérequis
    if not GitUtils.is_git_repository():
        print("❌ Pas dans un repository Git")
        sys.exit(1)
    
    current_branch = GitUtils.get_current_branch()
    if current_branch == args.base:
        print(f"❌ Vous êtes sur la branche cible '{args.base}'")
        print("💡 Créez une feature branch d'abord")
        sys.exit(1)
    
    print(f"📋 Branche courante: {current_branch}")
    print(f"📋 Branche cible: {args.base}")
    
    # Étape 1: Finalisation style git feature-finish
    print("\n🔄 Étape 1: Finalisation de la feature...")
    try:
        if not GitUtils.is_branch_up_to_date(args.base):
            print(f"⚠️  Branche en retard sur {args.base}, rebase...")
            GitUtils.rebase_on_target(args.base)
            print("✅ Rebase terminé")
        
        print("📤 Push de la branche...")
        GitUtils.push_current_branch(force_with_lease=True)
        print("✅ Branche prête pour PR")
        
    except RuntimeError as e:
        print(f"❌ Erreur lors de la finalisation: {e}")
        sys.exit(1)
    
    # Étape 2: Création de PR avec git-pr-auto
    print("\n📋 Étape 2: Création de la PR...")
    
    # Import et exécution du script PR auto
    try:
        import subprocess
        cmd = [sys.executable, str(Path(__file__).parent / 'git-pr-auto.py')]
        cmd.extend(['--base', args.base])
        if args.draft:
            cmd.append('--draft')
        
        # Execute le script de création de PR
        result = subprocess.run(cmd, check=True)
        print("✅ Workflow complet terminé!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la création de PR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()