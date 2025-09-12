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
from debug_logger import debug_command, set_global_debug_mode


def run_gh_pr_create(pr_data: dict, base_branch: str = "develop", force: bool = False, auto_merge: bool = False, delete_branch: bool = False) -> str:
    """
    Execute gh pr create avec les données automatiques
    
    Args:
        pr_data: Dict contenant title, body, labels, etc.
        base_branch: La branche cible pour la PR
        force: Si True, sauter la confirmation de création
        auto_merge: Si True, merger la PR automatiquement
        delete_branch: Si True et si auto_merge est activé, supprime la branche après le merge
        
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
    if not force:
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
    
    # Ajoute les labels si présents
    if pr_data.get('labels'):
        valid_labels = ['enhancement', 'bug', 'documentation', 'feature']
        for label in pr_data['labels']:
            if label in valid_labels:
                cmd.extend(['--label', label])
    
    # Ajoute le flag draft si nécessaire
    if pr_data.get('draft', False):
        cmd.append('--draft')
    
    try:
        debug_command(cmd, "create PR")
            
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        pr_url = result.stdout.strip()
        print(f"✅ PR créée avec succès: {pr_url}")

        # Auto-merge si demandé
        if auto_merge:
            print("🔄 Merge automatique de la PR...")
            current_branch = GitUtils.get_current_branch()
            try:
                import time
                time.sleep(2)
                
                merge_cmd = ['gh', 'pr', 'merge', pr_url, '--squash']
                debug_command(merge_cmd, "merge PR")
                
                subprocess.run(merge_cmd, capture_output=True, text=True, check=True)
                print("✅ PR mergée avec succès")

                # Retourner sur la branche de base et pull
                print(f"🔄 Retour sur la branche '{base_branch}'...")
                subprocess.run(['git', 'checkout', base_branch], check=True)
                subprocess.run(['git', 'pull'], check=True)
                
                # Supprimer la branche si demandé
                if delete_branch:
                    print(f"🗑️ Suppression de la branche '{current_branch}'...")
                    subprocess.run(['git', 'branch', '-D', current_branch], check=True)
                    subprocess.run(['git', 'push', 'origin', '--delete', current_branch], check=True)
                    print(f"✅ Branche '{current_branch}' supprimée (local et remote)")
                else:
                    print(f"✅ Branche '{base_branch}' mise à jour. La branche '{current_branch}' est conservée.")

            except subprocess.CalledProcessError as e:
                print(f"⚠️  Erreur lors du merge ou de la suppression de branche: {e.stderr if e.stderr else e}")
                print(f"💡 PR créée mais non mergée: {pr_url}")
        
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
        version_cmd = ['gh', '--version']
        debug_command(version_cmd, "check gh version")
        subprocess.run(version_cmd, capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ GitHub CLI (gh) n'est pas installé")
        print("💡 Installation: brew install gh")
        sys.exit(1)
    
    try:
        auth_cmd = ['gh', 'auth', 'status']
        debug_command(auth_cmd, "check gh auth")
        subprocess.run(auth_cmd, capture_output=True, check=True)
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
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Activer le mode debug pour voir les commandes exécutées'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Forcer la création de la PR sans confirmation'
    )
    parser.add_argument(
        '--merge', '-m',
        action='store_true',
        help='Merger automatiquement la PR après création'
    )
    parser.add_argument(
        '--delete-branch', '-D',
        action='store_true',
        help='Supprimer la branche locale et remote après un merge réussi (nécessite --merge)'
    )
    
    args = parser.parse_args()
    
    set_global_debug_mode(args.debug)
    
    if not GitUtils.is_git_repository():
        print("❌ Pas dans un repository Git")
        sys.exit(1)
    
    check_gh_cli()
    
    current_branch = GitUtils.get_current_branch()
    if current_branch == args.base:
        print(f"❌ Vous êtes sur la branche cible '{args.base}'")
        sys.exit(1)
    
    if not GitUtils.has_branch_changes(args.base):
        print(f"❌ Aucun changement dans la branche courante vs {args.base}")
        sys.exit(1)
    
    print(f"🔄 Vérification si la branche est à jour avec {args.base}...")
    if not GitUtils.is_branch_up_to_date(args.base):
        print(f"⚠️  Branche en retard sur {args.base}, rebase automatique...")
        try:
            GitUtils.rebase_on_target(args.base)
            print("✅ Rebase terminé avec succès")
            print("📤 Push de la branche rebasée...")
            GitUtils.push_current_branch(force_with_lease=True)
            print("✅ Push terminé")
        except RuntimeError as e:
            print(f"❌ {e}")
            sys.exit(1)
    else:
        print(f"✅ Branche à jour avec {args.base}")
        try:
            print("📤 Vérification du push...")
            GitUtils.push_current_branch()
            print("✅ Push vérifié")
        except RuntimeError:
            pass
    
    try:
        ai = AIProvider()
        print(ai.get_status())
        
        print(f"🔍 Analyse des changements vs {args.base}...")
        diff = GitUtils.get_branch_diff(args.base)
        files = '\n'.join(GitUtils.get_branch_files(args.base))
        
        print("🤖 Génération de la PR avec Multi-IA...")
        pr_data = ai.analyze_for_pr(diff, files, args.base)
        
        if args.draft:
            pr_data['draft'] = True
        
        if args.merge and not args.force:
            print("⚠️  Auto-merge activé - la PR sera mergée automatiquement")
            if args.delete_branch:
                print("🗑️  L'option de suppression de branche est également activée.")
            response = input("✅ Continuer? (y/N): ").strip().lower()
            if response not in ['y', 'yes', 'o', 'oui']:
                print("❌ Opération annulée")
                sys.exit(1)

        pr_url = run_gh_pr_create(
            pr_data, 
            args.base, 
            force=args.force, 
            auto_merge=args.merge,
            delete_branch=args.delete_branch
        )
        
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