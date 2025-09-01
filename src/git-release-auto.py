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
from debug_logger import debug_command, set_global_debug_mode


def get_repo_name() -> str:
    """Récupère le nom du repository GitHub"""
    try:
        cmd = ['git', 'remote', 'get-url', 'origin']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        url = result.stdout.strip()
        
        # Parse GitHub URL (https://github.com/user/repo.git ou git@github.com:user/repo.git)
        if 'github.com/' in url:
            repo_part = url.split('github.com/')[-1]
            if repo_part.endswith('.git'):
                repo_part = repo_part[:-4]
            return repo_part
        return "unknown/unknown"
    except:
        return "unknown/unknown"


def get_latest_tag() -> str:
    """Récupère le dernier tag pour calculer la prochaine version"""
    try:
        cmd = ['git', 'describe', '--tags', '--abbrev=0']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except:
        return "v0.0.0"  # Première version si aucun tag


def create_github_release(release_data: dict) -> bool:
    """
    Crée une GitHub Release avec tag
    
    Args:
        release_data: Dict contenant version, changes, etc.
        
    Returns:
        bool: True si succès
    """
    try:
        version = f"v{release_data['version']}"
        
        # 1. Checkout main pour créer le tag
        print("📂 Checkout main pour la release...")
        subprocess.run(['git', 'checkout', 'main'], capture_output=True, check=True)
        
        # 2. Pull latest main
        print("📥 Pull main...")
        subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, check=True)
        
        # 3. Créer le tag local
        print(f"🏷️  Création du tag {version}...")
        tag_cmd = ['git', 'tag', '-a', version, '-m', f'Release {version}']
        debug_command(tag_cmd, f"create tag {version}")
        subprocess.run(tag_cmd, check=True)
        
        # 4. Push le tag
        print(f"📤 Push du tag {version}...")
        push_tag_cmd = ['git', 'push', 'origin', version]
        debug_command(push_tag_cmd, f"push tag {version}")
        subprocess.run(push_tag_cmd, check=True)
        
        # 5. Générer les release notes depuis les données IA
        release_notes = generate_release_notes(release_data)
        
        # 6. Créer la GitHub Release
        print(f"🚀 Création de la GitHub Release {version}...")
        gh_cmd = [
            'gh', 'release', 'create', version,
            '--title', f'{version}',
            '--notes', release_notes
        ]
        
        debug_command(gh_cmd, f"create GitHub release {version}")
        subprocess.run(gh_cmd, check=True)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la création de la release: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue lors de la release: {e}")
        return False


def generate_release_notes(release_data: dict) -> str:
    """Génère les release notes formatées pour GitHub"""
    notes = f"## 🚀 Release v{release_data['version']}\n\n"
    
    if release_data.get('breaking_changes'):
        notes += "### ⚠️ BREAKING CHANGES\n"
        for change in release_data.get('major_changes', []):
            notes += f"- {change}\n"
        notes += "\n"
    
    if release_data.get('minor_changes'):
        notes += "### ✨ New Features\n"
        for change in release_data['minor_changes']:
            notes += f"- {change}\n"
        notes += "\n"
    
    if release_data.get('patch_changes'):
        notes += "### 🐛 Bug Fixes & Improvements\n"
        for change in release_data['patch_changes']:
            notes += f"- {change}\n"
        notes += "\n"
    
    notes += f"**Full Changelog**: https://github.com/{get_repo_name()}/compare/{get_latest_tag()}...v{release_data['version']}\n"
    
    return notes


def check_gh_cli():
    """Vérifie que GitHub CLI est installé et authentifié"""
    try:
        version_cmd = ['gh', '--version']
        debug_command(version_cmd, "check gh version")
            
        subprocess.run(version_cmd, capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ GitHub CLI (gh) n'est pas installé")
        print("💡 Installation:")
        print("   macOS: brew install gh")
        print("   Ubuntu/Debian: sudo apt install gh")
        sys.exit(1)
    
    try:
        auth_cmd = ['gh', 'auth', 'status']
        debug_command(auth_cmd, "check gh auth")
            
        subprocess.run(auth_cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ GitHub CLI n'est pas authentifié")
        print("💡 Connectez-vous: gh auth login")
        sys.exit(1)


def merge_pr_immediately(pr_url: str, merge_method: str = "merge") -> bool:
    """
    Merge immédiatement la PR créée
    
    Args:
        pr_url: URL de la PR
        merge_method: Méthode de merge (merge, squash, rebase)
        debug_mode: Si True, affiche les commandes exécutées
        
    Returns:
        bool: True si le merge a réussi
    """
    try:
        # Extract PR number from URL
        pr_number = pr_url.split('/')[-1]
        
        print(f"🔄 Merge immédiat de la PR #{pr_number}...")
        
        # Merge immediately (no --auto flag)
        cmd = [
            'gh', 'pr', 'merge', pr_number,
            f'--{merge_method}'
        ]
        
        debug_command(cmd, "merge PR immediately")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ PR mergée avec succès!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Merge échoué: {e.stderr}")
        print("💡 Vous pouvez merger manuellement depuis GitHub")
        return False


def run_gh_pr_create_release(pr_data: dict, immediate_merge: bool = True) -> str:
    """
    Execute gh pr create pour une release avec merge immédiat
    
    Args:
        pr_data: Dict contenant title, body, labels, etc.
        immediate_merge: Si True, merge immédiatement la PR
        debug_mode: Si True, affiche les commandes exécutées
        
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
    
    if immediate_merge:
        print("\n🔄 Merge immédiat: ACTIVÉ (mergera automatiquement après création)")
    
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
    
    # Labels supprimés pour éviter les erreurs
    
    try:
        debug_command(cmd, "create release PR")
            
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        pr_url = result.stdout.strip()
        print(f"✅ PR de release créée: {pr_url}")
        
        # Merge immédiat si demandé
        if immediate_merge:
            merge_pr_immediately(pr_url, "merge")
        
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
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Activer le mode debug pour voir les commandes exécutées'
    )
    
    args = parser.parse_args()
    
    # Configuration du logger global
    set_global_debug_mode(args.debug)
    
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
        
        # Génère une PR spécialement pour une release + calcul version
        release_data = ai.analyze_for_release(diff, files, commits)
        
        print(f"🏷️  Version calculée: v{release_data['release']['version']} ({release_data['release']['version_type']})")
        
        # Étape 4: Création de la PR avec auto-merge
        print("\n🚀 Étape 4: Création de la PR de release...")
        
        immediate_merge = not args.no_auto_merge  
        pr_url = run_gh_pr_create_release(release_data['pr'], immediate_merge)
        
        if pr_url and immediate_merge:
            print(f"\n🎉 PR mergée! Création de la release v{release_data['release']['version']}...")
            
            # Étape 5: Création automatique de la release
            if create_github_release(release_data['release']):
                print(f"🏷️  Release v{release_data['release']['version']} créée avec succès!")
                print(f"🔗 Voir: https://github.com/{get_repo_name()}/releases/tag/v{release_data['release']['version']}")
            else:
                print("⚠️  Erreur lors de la création de la release GitHub")
        elif pr_url:
            print(f"\n🎉 PR créée: {pr_url}")
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