#!/usr/bin/env python3
"""
Script pour automatiser le processus de release
Automatise: checkout develop -> pull -> créer PR vers main -> auto-merger
"""

import sys
import subprocess
import argparse
from pathlib import Path

# Ajout du dossier lib au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from ai_provider import AIProvider
from git_utils import GitUtils


def check_gh_cli():
    """Vérifie que GitHub CLI est installé et authentifié"""
    try:
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ GitHub CLI (gh) n'est pas installé")
        print("💡 Installation:")
        print("   macOS: brew install gh")
        print("   Ubuntu/Debian: sudo apt install gh")
        sys.exit(1)
    
    try:
        subprocess.run(['gh', 'auth', 'status'], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ GitHub CLI n'est pas authentifié")
        print("💡 Connectez-vous: gh auth login")
        sys.exit(1)


def auto_merge_pr(pr_url: str, merge_method: str = "merge") -> bool:
    """
    Auto-merge la PR créée
    
    Args:
        pr_url: URL de la PR
        merge_method: Méthode de merge (merge, squash, rebase)
        
    Returns:
        bool: True si le merge a réussi
    """
    try:
        # Extract PR number from URL
        pr_number = pr_url.split('/')[-1]
        
        print(f"🔄 Auto-merge de la PR #{pr_number}...")
        
        # Enable auto-merge
        cmd = [
            'gh', 'pr', 'merge', pr_number,
            f'--{merge_method}',
            '--auto'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Auto-merge activé! La PR sera mergée automatiquement.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Auto-merge échoué: {e.stderr}")
        print("💡 Vous pouvez merger manuellement depuis GitHub")
        return False


def run_gh_pr_create_release(pr_data: dict, auto_merge: bool = True) -> str:
    """
    Execute gh pr create pour une release avec auto-merge
    
    Args:
        pr_data: Dict contenant title, body, labels, etc.
        auto_merge: Si True, active l'auto-merge
        
    Returns:
        str: L'URL de la PR créée
    """
    # Affiche la PR de release proposée
    print("🚀 PR de Release proposée:")
    print(f"   Titre: {pr_data['title']}")
    print(f"   Base: main")
    if pr_data.get('labels'):
        print(f"   Labels: {', '.join(pr_data['labels'])}")
    print(f"\n{pr_data['body']}")
    
    if auto_merge:
        print("\n🔄 Auto-merge: ACTIVÉ (mergera automatiquement)")
    
    # Demande confirmation
    response = input("\n✅ Créer cette PR de release? (y/N): ").strip().lower()
    if response not in ['y', 'yes', 'o', 'oui']:
        print("❌ Release annulée")
        return ""
        
    # Construit la commande gh pr create
    cmd = [
        'gh', 'pr', 'create',
        '--base', 'main',
        '--head', 'develop',
        '--title', pr_data['title'],
        '--body', pr_data['body']
    ]
    
    # Ajoute les labels
    if pr_data.get('labels'):
        valid_labels = ['release', 'enhancement', 'feature']
        for label in pr_data['labels']:
            if label in valid_labels:
                cmd.extend(['--label', label])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        pr_url = result.stdout.strip()
        print(f"✅ PR de release créée: {pr_url}")
        
        # Auto-merge si demandé
        if auto_merge:
            auto_merge_pr(pr_url, "merge")
        
        return pr_url
        
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(f"❌ Erreur lors de la création de la PR: {e.stderr}")
        else:
            print(f"❌ Erreur lors de la création de la PR: {e}")
        sys.exit(1)


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Automatiser le processus de release develop -> main"
    )
    parser.add_argument(
        '--no-auto-merge',
        action='store_true',
        help="Ne pas auto-merger la PR (merge manuel)"
    )
    parser.add_argument(
        '--merge-method',
        choices=['merge', 'squash', 'rebase'],
        default='merge',
        help='Méthode de merge (défaut: merge)'
    )
    
    args = parser.parse_args()
    
    print("🚀 Git Release Auto - Processus de Release Automatisé")
    print("=" * 55)
    
    # Vérifie les prérequis
    if not GitUtils.is_git_repository():
        print("❌ Pas dans un repository Git")
        sys.exit(1)
    
    check_gh_cli()
    
    try:
        # Étape 1: Checkout develop et pull
        print("\n🔄 Étape 1: Synchronisation de develop...")
        current_branch = GitUtils.get_current_branch()
        print(f"📋 Branche courante: {current_branch}")
        
        # Checkout develop
        print("📂 Checkout develop...")
        result = subprocess.run(['git', 'checkout', 'develop'], 
                              capture_output=True, text=True, check=True)
        print("✅ Sur develop")
        
        # Pull origin develop
        print("📥 Pull origin develop...")
        result = subprocess.run(['git', 'pull', 'origin', 'develop'], 
                              capture_output=True, text=True, check=True)
        print("✅ Develop synchronisé")
        
        # Étape 2: Vérifier qu'il y a des changements vs main
        print("\n🔍 Étape 2: Analyse des changements develop -> main...")
        
        if not GitUtils.has_branch_changes('main'):
            print("❌ Aucun changement entre develop et main")
            print("💡 Rien à releaser!")
            sys.exit(1)
        
        # Récupère les informations pour la PR
        diff = GitUtils.get_branch_diff('main')
        files_list = GitUtils.get_branch_files('main')
        commits = GitUtils.get_commit_messages('main')
        
        print(f"📊 {len(commits)} commits à releaser")
        print(f"📁 {len(files_list)} fichiers modifiés")
        
        # Convertit la liste de fichiers en string pour l'IA
        files = '\n'.join(files_list)
        
        # Étape 3: Génération de la PR avec IA
        print("\n🤖 Étape 3: Génération de la PR de release avec IA...")
        
        ai = AIProvider()
        print(ai.get_status())
        
        # Génère une PR spécialement pour une release
        pr_data = ai.analyze_for_release(diff, files, commits)
        
        # Ajoute le label release
        if 'labels' not in pr_data:
            pr_data['labels'] = []
        if 'release' not in pr_data['labels']:
            pr_data['labels'].append('release')
        
        # Étape 4: Création de la PR avec auto-merge
        print("\n🚀 Étape 4: Création de la PR de release...")
        
        auto_merge = not args.no_auto_merge
        pr_url = run_gh_pr_create_release(pr_data, auto_merge)
        
        if pr_url:
            print(f"\n🎉 Release en cours! PR: {pr_url}")
            if auto_merge:
                print("⏳ La PR sera mergée automatiquement.")
                print("🏷️  Une nouvelle version sera créée après le merge!")
            else:
                print("💡 Mergez manuellement pour déclencher la release")
        
        # Retour à la branche d'origine si possible
        if current_branch and current_branch != 'develop':
            try:
                print(f"\n🔙 Retour à la branche {current_branch}...")
                subprocess.run(['git', 'checkout', current_branch], 
                             capture_output=True, check=True)
                print(f"✅ Retour sur {current_branch}")
            except subprocess.CalledProcessError:
                print(f"⚠️  Impossible de retourner sur {current_branch}")
        
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(f"❌ Erreur Git: {e.stderr}")
        else:
            print(f"❌ Erreur Git: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()