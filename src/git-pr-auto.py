#!/usr/bin/env python3
"""
Script pour automatiser la création de PR avec l'API Gemini
"""

import sys
import subprocess
import argparse
from pathlib import Path

# Ajout du dossier lib au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from ai_provider import AIProvider
from git_utils import GitUtils


def run_gh_pr_create(pr_data: dict, base_branch: str = "develop") -> str:
    """
    Execute gh pr create avec les données automatiques
    
    Args:
        pr_data: Dict contenant title, body, labels, etc.
        base_branch: La branche cible pour la PR
        
    Returns:
        str: L'URL de la PR créée
    """
    # Affiche la PR proposée
    print("📋 PR proposée:")
    print(f"   Titre: {pr_data['title']}")
    print(f"   Base: {base_branch}")
    if pr_data.get('labels'):
        print(f"   Labels: {', '.join(pr_data['labels'])}")
    print(f"\n{pr_data['body']}")
    
    # Demande confirmation
    response = input("\n✅ Créer cette PR? (y/N): ").strip().lower()
    if response not in ['y', 'yes', 'o', 'oui']:
        print("❌ PR annulée")
        return ""
        
    # Construit la commande gh pr create
    cmd = [
        'gh', 'pr', 'create',
        '--base', base_branch,
        '--title', pr_data['title'],
        '--body', pr_data['body']
    ]
    
    # Ajoute les labels si présents (ignore les erreurs de labels inexistants)
    if pr_data.get('labels'):
        # Liste des labels connus qui existent sur le repo
        valid_labels = ['enhancement', 'bug', 'documentation', 'feature']
        for label in pr_data['labels']:
            if label in valid_labels:
                cmd.extend(['--label', label])
    
    # Ajoute le flag draft si nécessaire
    if pr_data.get('draft', False):
        cmd.append('--draft')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        pr_url = result.stdout.strip()
        print(f"✅ PR créée avec succès: {pr_url}")
        return pr_url
        
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(f"❌ Erreur lors de la création de la PR: {e.stderr}")
        else:
            print(f"❌ Erreur lors de la création de la PR: {e}")
        sys.exit(1)


def check_gh_cli():
    """Vérifie que GitHub CLI est installé et authentifié"""
    try:
        # Vérifie que gh est installé
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ GitHub CLI (gh) n'est pas installé")
        print("💡 Installation:")
        print("   macOS: brew install gh")
        print("   Ubuntu/Debian: sudo apt install gh")
        print("   Ou: https://github.com/cli/cli/releases")
        sys.exit(1)
    
    try:
        # Vérifie l'authentification
        subprocess.run(['gh', 'auth', 'status'], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ GitHub CLI n'est pas authentifié")
        print("💡 Connectez-vous: gh auth login")
        sys.exit(1)


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Créer automatiquement une PR avec analyse Gemini"
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
    
    # Vérifie les prérequis
    if not GitUtils.is_git_repository():
        print("❌ Pas dans un repository Git")
        sys.exit(1)
    
    check_gh_cli()
    
    # Vérifie qu'il y a des changements dans la branche
    current_branch = GitUtils.get_current_branch()
    if current_branch == args.base:
        print(f"❌ Vous êtes sur la branche cible '{args.base}'")
        print("💡 Créez une feature branch d'abord")
        sys.exit(1)
    
    if not GitUtils.has_branch_changes(args.base):
        print(f"❌ Aucun changement dans la branche courante vs {args.base}")
        print("💡 Effectuez des commits d'abord")
        sys.exit(1)
    
    # Vérifie si la branche est à jour et rebase si nécessaire
    print(f"🔄 Vérification si la branche est à jour avec {args.base}...")
    if not GitUtils.is_branch_up_to_date(args.base):
        print(f"⚠️  Branche en retard sur {args.base}, rebase automatique...")
        try:
            GitUtils.rebase_on_target(args.base)
            print("✅ Rebase terminé avec succès")
            
            # Push après rebase
            print("📤 Push de la branche rebasée...")
            GitUtils.push_current_branch(force_with_lease=True)
            print("✅ Push terminé")
        except RuntimeError as e:
            print(f"❌ {e}")
            sys.exit(1)
    else:
        print(f"✅ Branche à jour avec {args.base}")
        
        # S'assurer que la branche est pushée
        try:
            print("📤 Vérification du push...")
            GitUtils.push_current_branch()
            print("✅ Push vérifié")
        except RuntimeError:
            # Si le push échoue, c'est probablement que la branche est déjà pushée
            pass
    
    try:
        # Initialise le gestionnaire multi-IA
        ai = AIProvider()
        print(ai.get_status())
        
        # Récupère les changements de la branche
        print(f"🔍 Analyse des changements vs {args.base}...")
        diff = GitUtils.get_branch_diff(args.base)
        files = GitUtils.get_branch_files(args.base)
        commits = GitUtils.get_commit_messages(args.base)
        
        print("🤖 Génération de la PR avec Multi-IA...")
        pr_data = ai.analyze_for_pr(diff, files, args.base)
        
        # Force le mode draft si demandé
        if args.draft:
            pr_data['draft'] = True
        
        # Crée la PR
        pr_url = run_gh_pr_create(pr_data, args.base)
        
        if pr_url:
            print(f"\n🎉 Success! PR disponible: {pr_url}")
        
    except ValueError as e:
        print(f"❌ Configuration: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"❌ Erreur Git: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()