#!/usr/bin/env python3
"""
Script pour commit automatique avec rebase + IA
Remplace git commit-safe mais avec IA au lieu de commitizen
"""

import sys
import subprocess
from pathlib import Path

# Ajout du dossier lib au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from ai_provider import AIProvider
from git_utils import GitUtils


def run_git_commit(commit_data: dict) -> None:
    """
    Execute git commit avec les données automatiques
    
    Args:
        commit_data: Dict contenant type, scope, description, body, etc.
    """
    # Construit le message de commit
    commit_msg = commit_data['type']
    
    if commit_data.get('scope'):
        commit_msg += f"({commit_data['scope']})"
        
    if commit_data.get('breaking', False):
        commit_msg += "!"
        
    commit_msg += f": {commit_data['description']}"
    
    # Prépare le body complet
    body_parts = []
    if commit_data.get('body'):
        body_parts.append(commit_data['body'])
        
    if commit_data.get('breaking', False):
        body_parts.append("BREAKING CHANGE: " + commit_data.get('body', 'See changes above'))
        
    if commit_data.get('issues'):
        for issue in commit_data['issues']:
            body_parts.append(f"Closes #{issue}")
    
    body = '\\n\\n'.join(body_parts) if body_parts else ''
    
    # Affiche le commit proposé
    print("📝 Commit proposé:")
    print(f"   {commit_msg}")
    if body:
        print(f"\\n{body}")
    
    # Demande confirmation
    response = input("\\n✅ Confirmer ce commit? (y/N): ").strip().lower()
    if response not in ['y', 'yes', 'o', 'oui']:
        print("❌ Commit annulé")
        return
        
    # Execute le commit
    try:
        full_msg = commit_msg
        if body:
            full_msg += f"\\n\\n{body}"
            
        subprocess.run(['git', 'commit', '-m', full_msg], check=True)
        print("✅ Commit effectué avec succès!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du commit: {e}")
        sys.exit(1)


def main():
    """Fonction principale - Rebase + Commit avec IA"""
    
    # Vérifie qu'on est dans un repo git
    if not GitUtils.is_git_repository():
        print("❌ Pas dans un repository Git")
        sys.exit(1)
    
    try:
        # 1. Rebase automatique sur develop (ou main si pas de develop)
        base_branch = "develop"
        
        # Vérifier si develop existe
        try:
            subprocess.run(['git', 'show-ref', '--verify', '--quiet', 'refs/heads/develop'], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # develop n'existe pas, utiliser main
            base_branch = "main"
            print("ℹ️  Branche develop non trouvée, utilisation de main")
        
        print(f"🔄 Rebase sur {base_branch}...")
        if GitUtils.rebase_on_target(base_branch):
            print("✅ Rebase réussi")
        else:
            print("⚠️  Conflits détectés ! Résolvez-les puis relancez la commande")
            sys.exit(1)
        
        # 2. Vérifie qu'il y a des changements stagés OU auto-stage tout
        if not GitUtils.has_staged_changes():
            print("📁 Aucun changement stagé - staging automatique...")
            try:
                subprocess.run(['git', 'add', '.'], check=True)
                print("✅ Fichiers stagés automatiquement")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur lors du staging: {e}")
                sys.exit(1)
        
        # Vérifie à nouveau
        if not GitUtils.has_staged_changes():
            print("❌ Aucun changement à commiter")
            sys.exit(1)
        
        # 3. Initialise le gestionnaire multi-IA
        ai = AIProvider()
        print(ai.get_status())
        
        # 4. Récupère les changements
        print("🔍 Analyse des changements...")
        diff = GitUtils.get_staged_diff()
        files = GitUtils.get_staged_files()
        
        # 5. Analyse avec IA (fallback automatique)
        commit_data = ai.analyze_for_commit(diff, files)
        
        # 6. Execute le commit
        run_git_commit(commit_data)
        
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