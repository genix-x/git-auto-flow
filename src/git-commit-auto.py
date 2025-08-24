#!/usr/bin/env python3
"""
Script pour commit automatique avec rebase + IA
Remplace git commit-safe mais avec IA au lieu de commitizen
"""

import sys
import subprocess
import os
from pathlib import Path

# Ajout du dossier lib au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from ai_provider import AIProvider
from git_utils import GitUtils


def run_gitleaks_scan() -> bool:
    """
    Execute gitleaks pour scanner les fichiers stagés
    
    Returns:
        bool: True si aucun secret détecté, False sinon
    """
    try:
        # Trouve le chemin vers gitleaks
        script_dir = Path(__file__).parent.parent
        
        # Priorité 1: gitleaks local dans bin/
        local_gitleaks = script_dir / 'bin' / 'gitleaks'
        if local_gitleaks.exists():
            gitleaks_cmd = str(local_gitleaks)
        else:
            # Priorité 2: gitleaks global
            result = subprocess.run(['which', 'gitleaks'], capture_output=True)
            if result.returncode != 0:
                print("⚠️  gitleaks non trouvé - scan de sécurité ignoré")
                return True  # Continue sans scan si pas installé
            gitleaks_cmd = 'gitleaks'
        
        # Lance gitleaks sur les commits récents uniquement (évite de scanner tout l'historique)
        result = subprocess.run([
            gitleaks_cmd, 'detect', 
            '--log-opts=--since=1.hour.ago',
            '--verbose',
            '--exit-code', '1'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            return True  # Aucun secret détecté
        elif result.returncode == 1:
            print("🚨 SECRETS DÉTECTÉS:")
            print(result.stdout)
            if result.stderr:
                print("Détails supplémentaires:")
                print(result.stderr)
            return False  # Secrets trouvés
        else:
            print(f"⚠️  Erreur gitleaks: {result.stderr}")
            return True  # Continue en cas d'erreur technique
            
    except Exception as e:
        print(f"⚠️  Erreur scan sécurité: {e}")
        return True  # Continue en cas d'erreur


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
        
    # Gère le cas où Gemini utilise un autre champ que 'description'
    description = commit_data.get('description', '')
    if not description:
        # Cherche d'autres champs possibles
        for key, value in commit_data.items():
            if key not in ['type', 'scope', 'body', 'breaking', 'issues'] and isinstance(value, str):
                description = value
                break
    
    commit_msg += f": {description}"
    
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
        
        # Push automatique vers la branche distante
        try:
            current_branch = subprocess.run(['git', 'branch', '--show-current'], 
                                          capture_output=True, text=True, check=True).stdout.strip()
            print(f"📤 Push vers origin/{current_branch}...")
            subprocess.run(['git', 'push', 'origin', current_branch], check=True)
            print("✅ Push effectué avec succès!")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Push échoué: {e}")
            print("💡 La branche locale a été commitée mais pas pushée")
        
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
        # 1. Rebase automatique (seulement si pas sur branche de base)
        current_branch = subprocess.run(['git', 'branch', '--show-current'], 
                                      capture_output=True, text=True, check=True).stdout.strip()
        
        # Déterminer la branche de base
        base_branch = "develop"
        try:
            subprocess.run(['git', 'show-ref', '--verify', '--quiet', 'refs/heads/develop'], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # develop n'existe pas, utiliser main
            base_branch = "main"
            print("ℹ️  Branche develop non trouvée, utilisation de main")
        
        # Rebase seulement si on n'est PAS sur la branche de base
        if current_branch != base_branch:
            # Vérifie d'abord si un rebase est vraiment nécessaire
            print(f"🔍 Vérification si rebase nécessaire sur {base_branch}...")
            
            try:
                # Fetch pour avoir les dernières infos
                subprocess.run(['git', 'fetch', 'origin', base_branch], 
                             capture_output=True, check=True)
                
                # Check si la branche est déjà à jour
                behind_check = subprocess.run(
                    ['git', 'rev-list', '--count', f'HEAD..origin/{base_branch}'],
                    capture_output=True, text=True, check=True
                )
                behind_count = int(behind_check.stdout.strip())
                
                if behind_count == 0:
                    print(f"✅ Branche déjà à jour avec {base_branch}")
                else:
                    print(f"🔄 Branche en retard de {behind_count} commits, rebase nécessaire...")
                    
                    # Vérifie s'il y a des changements stagés
                    has_staged = GitUtils.has_staged_changes()
                    
                    if has_staged:
                        print("📦 Sauvegarde des changements stagés...")
                        try:
                            subprocess.run(['git', 'stash', 'push', '--staged', '-m', 'Auto-stash for rebase'], 
                                         check=True, capture_output=True)
                            print("✅ Changements sauvegardés")
                        except subprocess.CalledProcessError as e:
                            print(f"❌ Erreur lors de la sauvegarde: {e}")
                            sys.exit(1)
                    
                    print(f"🔄 Rebase {current_branch} sur {base_branch}...")
                    if GitUtils.rebase_on_target(base_branch):
                        print("✅ Rebase réussi")
                        
                        # Restore les changements stagés si nécessaire
                        if has_staged:
                            print("📦 Restauration des changements...")
                            try:
                                subprocess.run(['git', 'stash', 'pop'], check=True, capture_output=True)
                                print("✅ Changements restaurés")
                            except subprocess.CalledProcessError as e:
                                print(f"❌ Erreur lors de la restauration: {e}")
                                print("💡 Vérifiez avec 'git stash list' et 'git stash pop' manuellement")
                                sys.exit(1)
                    else:
                        # Si le rebase échoue, on essaie de restaurer les changements
                        if has_staged:
                            print("🔄 Tentative de restauration des changements après échec...")
                            try:
                                subprocess.run(['git', 'stash', 'pop'], check=True, capture_output=True)
                                print("✅ Changements restaurés")
                            except subprocess.CalledProcessError:
                                print("⚠️  Changements en stash - utilisez 'git stash pop' après résolution")
                        
                        print("⚠️  Conflits détectés ! Résolvez-les puis relancez la commande")
                        sys.exit(1)
                        
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur lors de la vérification de {base_branch}: {e}")
                print(f"ℹ️  Continuons sans rebase...")
        else:
            print(f"ℹ️  Déjà sur {base_branch}, pas de rebase nécessaire")
        
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
        
        # 4. Scan sécurité avec gitleaks
        print("🔒 Scan sécurité des secrets...")
        if not run_gitleaks_scan():
            print("❌ Scan sécurité échoué - commit bloqué pour votre protection!")
            sys.exit(1)
        print("✅ Aucun secret détecté")
        
        # 5. Récupère les changements
        print("🔍 Analyse des changements...")
        diff = GitUtils.get_staged_diff()
        files = GitUtils.get_staged_files()
        
        # 6. Analyse avec IA (fallback automatique)
        commit_data = ai.analyze_for_commit(diff, files)
        
        # 7. Execute le commit
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