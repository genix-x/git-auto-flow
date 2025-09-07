#!/usr/bin/env python3
"""
Script pour commit automatique avec rebase + IA
Remplace git commit-safe mais avec IA au lieu de commitizen
"""

import sys
import subprocess
import os
import argparse
from pathlib import Path

# Ajout du dossier lib au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from ai_provider import AIProvider
from git_utils import GitUtils
from debug_logger import debug_command, set_global_debug_mode

def run_gitleaks_scan_all_modified() -> bool:
    """
    Scan sécurité de TOUS les fichiers modifiés (stagés, non-stagés, untracked)

    Returns:
        bool: True si aucun secret détecté, False sinon
    """
    try:
        # Trouve le chemin vers gitleaks
        script_dir = Path(__file__).parent.parent
        local_gitleaks = script_dir / 'bin' / 'gitleaks'
        if local_gitleaks.exists():
            gitleaks_cmd = str(local_gitleaks)
        else:
            result = subprocess.run(['which', 'gitleaks'], capture_output=True)
            if result.returncode != 0:
                print("⚠️  gitleaks non trouvé - scan de sécurité ignoré")
                return True
            gitleaks_cmd = 'gitleaks'

        # Récupère TOUS les fichiers modifiés
        all_files = []

        # 1. Fichiers stagés
        staged_cmd = ['git', 'diff', '--cached', '--name-only']
        debug_command(staged_cmd, "get staged files")
        staged_result = subprocess.run(staged_cmd, capture_output=True, text=True, check=False)
        if staged_result.returncode == 0:
            all_files.extend([f.strip() for f in staged_result.stdout.strip().split('\n') if f.strip()])

        # 2. Fichiers modifiés non-stagés
        unstaged_cmd = ['git', 'diff', '--name-only']
        debug_command(unstaged_cmd, "get unstaged files") 
        unstaged_result = subprocess.run(unstaged_cmd, capture_output=True, text=True, check=False)
        if unstaged_result.returncode == 0:
            all_files.extend([f.strip() for f in unstaged_result.stdout.strip().split('\n') if f.strip()])

        # 3. Fichiers untracked
        untracked_cmd = ['git', 'ls-files', '--others', '--exclude-standard']
        debug_command(untracked_cmd, "get untracked files")
        untracked_result = subprocess.run(untracked_cmd, capture_output=True, text=True, check=False)
        if untracked_result.returncode == 0:
            all_files.extend([f.strip() for f in untracked_result.stdout.strip().split('\n') if f.strip()])

        # Supprime les doublons
        unique_files = list(set(all_files))

        if not unique_files:
            print("ℹ️  Aucun fichier modifié à scanner")
            return True

        print(f"🔍 Scan GitLeaks sur {len(unique_files)} fichier(s) modifié(s)...")

        # Scanner chaque fichier
        for file_path in unique_files:
            if not os.path.exists(file_path):
                continue  # Fichier supprimé, ignoré

            gitleaks_command = [
                gitleaks_cmd, 'detect', 
                '--no-git',
                '--source', file_path,
                '--verbose',
                '--exit-code', '1'
            ]

            debug_command(gitleaks_command, f"scan {file_path}")
            result = subprocess.run(gitleaks_command, capture_output=True, text=True)

            if result.returncode == 1:
                print(f"🚨 SECRETS DÉTECTÉS dans {file_path}:")
                print(result.stdout)
                if result.stderr:
                    print("Détails supplémentaires:")
                    print(result.stderr)
                return False  # Arrêt immédiat si secret détecté
            elif result.returncode != 0:
                print(f"⚠️  Erreur gitleaks sur {file_path}: {result.stderr}")
                # Continue le scan des autres fichiers

        return True  # Aucun secret détecté

    except Exception as e:
        print(f"⚠️  Erreur scan sécurité: {e}")
        return True

def run_git_commit(commit_data: dict, force: bool = False) -> None:
    """
    Execute git commit avec les données automatiques

    Args:
        commit_data: Dict contenant type, scope, description, body, etc.
        force: Si True, effectue le commit sans demander confirmation
    """
    # Construit le message de commit
    if 'type' not in commit_data:
        print(f"❌ Erreur: Réponse IA invalide - champ 'type' manquant")
        print(f"📋 Réponse reçue: {commit_data}")
        return

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

    body = '\n\n'.join(body_parts) if body_parts else ''

    # Affiche le commit proposé
    print("📝 Commit proposé:")
    print(f"   {commit_msg}")
    if body:
        print(f"\n{body}")

    # Demande confirmation uniquement si pas en mode force
    if not force:
        response = input("\n✅ Confirmer ce commit? (y/N): ").strip().lower()
        if response not in ['y', 'yes', 'o', 'oui']:
            print("❌ Commit annulé")
            return
    else:
        print("\n⚡ Mode force activé - commit automatique")

    # Execute le commit
    try:
        full_msg = commit_msg
        if body:
            full_msg += f"\n\n{body}"

        commit_command = ['git', 'commit', '-m', full_msg]
        debug_command(['git', 'commit', '-m', repr(full_msg)], "commit")

        subprocess.run(commit_command, check=True)
        print("✅ Commit effectué avec succès!")

        # Push automatique vers la branche distante
        try:
            current_branch_cmd = ['git', 'branch', '--show-current']
            debug_command(current_branch_cmd, "get current branch")

            current_branch = subprocess.run(current_branch_cmd, 
                                          capture_output=True, text=True, check=True).stdout.strip()
            print(f"📤 Push vers origin/{current_branch}...")

            push_command = ['git', 'push', 'origin', current_branch]
            debug_command(push_command, "push branch")

            subprocess.run(push_command, check=True)
            print("✅ Push effectué avec succès!")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Push échoué: {e}")
            print("💡 La branche locale a été commitée mais pas pushée")

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du commit: {e}")
        sys.exit(1)

def main():
    """Fonction principale - Rebase + Commit avec IA"""
    
    # Parse des arguments en premier
    parser = argparse.ArgumentParser(
        description='Commit automatique avec rebase + IA',
        usage='%(prog)s [options]'
    )
    parser.add_argument('-f', '--force', 
                       action='store_true',
                       help='Force le commit sans demander confirmation')
    parser.add_argument('--debug', 
                       action='store_true',
                       help='Affiche les commandes Git exécutées')
    
    args = parser.parse_args()

    # Configuration du logger global
    set_global_debug_mode(args.debug)

    # Vérifie qu'on est dans un repo git
    if not GitUtils.is_git_repository():
        print("❌ Pas dans un repository Git")
        sys.exit(1)

    try:
        print("🤖 Git Auto-Commit avec IA")
        print("==============================")
        
        if args.force:
            print("⚡ MODE FORCE ACTIVÉ")
        
        print()

        # 1. Rebase automatique (seulement si pas sur branche de base)
        print("🔄 Étape 1: Synchronisation avec develop...")
        current_branch_cmd = ['git', 'branch', '--show-current']
        debug_command(current_branch_cmd, "get current branch")

        current_branch = subprocess.run(current_branch_cmd, 
                                      capture_output=True, text=True, check=True).stdout.strip()

        # Déterminer la branche de base
        base_branch = "develop"
        try:
            show_ref_cmd = ['git', 'show-ref', '--verify', '--quiet', 'refs/heads/develop']
            if args.debug:
                print(f"🐛 DEBUG: Exécution de: {' '.join(show_ref_cmd)}")

            subprocess.run(show_ref_cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # develop n'existe pas, utiliser main
            base_branch = "main"
            print("ℹ️  Branche develop non trouvée, utilisation de main")

        # Rebase seulement si on n'est PAS sur la branche de base
        if current_branch != base_branch:
            # Vérifie d'abord si un rebase est vraiment nécessaire
            print(f"📥 Synchronisation avec {base_branch}...")

            try:
                # Fetch pour avoir les dernières infos
                fetch_cmd = ['git', 'fetch', 'origin', base_branch]
                if args.debug:
                    print(f"🐛 DEBUG: Exécution de: {' '.join(fetch_cmd)}")

                subprocess.run(fetch_cmd, capture_output=True, check=True)

                # Check si la branche est déjà à jour
                rev_list_cmd = ['git', 'rev-list', '--count', f'HEAD..origin/{base_branch}']
                if args.debug:
                    print(f"🐛 DEBUG: Exécution de: {' '.join(rev_list_cmd)}")

                behind_check = subprocess.run(rev_list_cmd, capture_output=True, text=True, check=True)
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
                            stash_cmd = ['git', 'stash', 'push', '--staged', '-m', 'Auto-stash for rebase']
                            if args.debug:
                                print(f"🐛 DEBUG: Exécution de: {' '.join(stash_cmd)}")

                            subprocess.run(stash_cmd, check=True, capture_output=True)
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
                                stash_pop_cmd = ['git', 'stash', 'pop']
                                debug_command(stash_pop_cmd, "restore staged changes after rebase")

                                subprocess.run(stash_pop_cmd, check=True, capture_output=True)
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
                                stash_pop_cmd = ['git', 'stash', 'pop']
                                debug_command(stash_pop_cmd, "restore changes after rebase failure")

                                subprocess.run(stash_pop_cmd, check=True, capture_output=True)
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

        # 2. Scan sécurité UNIQUE de tous les fichiers modifiés
        print("\n🔄 Étape 2: Scan sécurité...")
        print("🔒 Scan sécurité des fichiers modifiés...")
        if not run_gitleaks_scan_all_modified():
            print("❌ Secrets détectés - commit bloqué pour votre protection!")
            sys.exit(1)
        print("✅ Aucun secret détecté")

        # 3. Stage automatique (maintenant sécurisé car pré-scanné)
        print("\n🔄 Étape 3: Staging des fichiers...")
        print("📁 git add . automatique...")

        try:
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            print("✅ Fichiers stagés avec succès")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur git add: {e}")
            sys.exit(1)

        # Vérifie qu'il y a maintenant des changements à commiter
        if not GitUtils.has_staged_changes():
            print("❌ Aucun changement à commiter")
            sys.exit(1)


        # 4. Initialise le gestionnaire multi-IA
        print("\n🔄 Étape 4: Initialisation IA...")
        ai = AIProvider()
        print(ai.get_status())

        # 5. Récupère les changements
        print("\n🔄 Étape 5: Analyse des changements...")
        print("🔍 Analyse des changements...")
        diff = GitUtils.get_staged_diff()
        files = GitUtils.get_staged_files()

        # 6. Analyse avec IA (fallback automatique)
        print("\n🔄 Étape 6: Génération du commit...")
        commit_data = ai.analyze_for_commit(diff, files)

        # 7. Execute le commit
        print("\n🔄 Étape 7: Commit et push...")
        run_git_commit(commit_data, force=args.force)

        print("\n🎉 Processus terminé avec succès!")

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
