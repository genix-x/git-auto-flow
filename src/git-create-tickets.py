#!/usr/bin/env python3
"""
Git Auto-Flow - Création automatique de tickets/issues
Génère des issues GitHub depuis un compte-rendu avec IA
"""

import os
import sys
import json
import argparse
import subprocess
import time
import requests
from pathlib import Path
from typing import List, Optional

# Réutilise les libs existantes ! 🎯
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from ai_provider import AIProvider
from git_utils import GitUtils  
from debug_logger import debug_command, set_global_debug_mode

class GitCreateTickets:
    PRIORITY_COLORS = {
        'priority-high': 'd73a4a',    # Rouge
        'priority-medium': 'fbca04',  # Jaune  
        'priority-low': '0e8a16',     # Vert
        'enhancement': '0969da',      # Bleu
        'bug': 'd73a4a',             # Rouge
        'documentation': '0969da',    # Bleu
        'testing': '0969da'          # Bleu
    }

    def __init__(self, repo_full_name: Optional[str] = None, debug_mode: bool = False):
        set_global_debug_mode(debug_mode)
        self.ai = AIProvider()
        self.repo_full_name = repo_full_name
        self._github_labels_cache = None
        self.validate_requirements()

    def _get_github_labels(self) -> List[str]:
        """Récupère et cache la liste des labels GitHub existants pour le repo cible."""
        if self._github_labels_cache is None:
            try:
                repo_arg = ['--repo', self._get_current_repo()] if self._get_current_repo() else []
                cmd = ['gh', 'label', 'list', *repo_arg, '--json', 'name', '--jq', '.[].name']
                debug_command(cmd, "get github labels")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                self._github_labels_cache = result.stdout.strip().split('\n') if result.stdout else []
            except (subprocess.CalledProcessError, FileNotFoundError):
                self._github_labels_cache = []
        return self._github_labels_cache

    def _ensure_label_exists(self, label_name: str, color: str = "0969da") -> bool:
        """Crée le label s'il n'existe pas dans le repo cible. Retourne True si succès."""
        if self._github_labels_cache is None:
            self._get_github_labels()

        if label_name in self._github_labels_cache:
            return True

        print(f"️️ℹ️  Label '{label_name}' non trouvé, tentative de création...")
        try:
            repo_arg = ['--repo', self._get_current_repo()] if self._get_current_repo() else []
            cmd = ['gh', 'label', 'create', label_name, '--color', color, *repo_arg]
            debug_command(cmd, f"create label {label_name}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"  ✅ Label '{label_name}' créé.")
                self._github_labels_cache.append(label_name)
                return True

            if "already exists" in result.stderr:
                print(f"  ✅ Label '{label_name}' existe déjà.")
                self._github_labels_cache.append(label_name)
                return True

            print(f"  ⚠️  Impossible de créer le label '{label_name}': {result.stderr.strip()}")
            return False
        except Exception as e:
            print(f"  ❌ Erreur lors de la création du label '{label_name}': {e}")
            return False

    def _get_current_repo(self) -> Optional[str]:
        """Récupère le propriétaire/nom du repo, en priorité l'argument --repo."""
        if self.repo_full_name:
            return self.repo_full_name
        try:
            owner, repo = GitUtils.get_repo_info()
            return f"{owner}/{repo}"
        except RuntimeError as e:
            debug_command([], f"Error getting current repo: {e}")
            return None

    def _add_dependency_api(self, issue_number, blocked_by_number):
        """Crée une vraie dépendance GitHub entre deux issues, en vérifiant le repo."""
        current_repo_full_name = self._get_current_repo()
        if not current_repo_full_name:
            print("    ❌ Impossible de vérifier le repo courant. Dépendance ignorée.")
            return False
        
        owner, repo = current_repo_full_name.split('/')
        debug_command([], f"Creating dependency in repo: {current_repo_full_name}")

        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by"

        try:
            token = os.getenv("GITHUB_TOKEN")
            if not token:
                result = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True)
                token = result.stdout.strip()
        except:
            print("⚠️ Impossible de récupérer le token GitHub")
            return False

        headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"}
        data = {"issue_id": int(blocked_by_number)}

        max_retries = 4
        retry_delay = 5  # Augmentation du délai à 5 secondes

        for attempt in range(max_retries):
            try:
                debug_command(['curl', '-X', 'POST', url, '-d', json.dumps(data)], f"add dependency {issue_number} <- {blocked_by_number}")
                resp = requests.post(url, json=data, headers=headers)
                
                if resp.status_code == 201:
                    print(f"    ✅ Dépendance API créée: #{issue_number} bloqué par #{blocked_by_number}")
                    return True
                
                if resp.status_code == 404 and attempt < max_retries - 1:
                    print(f"    ⏳ Tentative {attempt+1}/{max_retries-1}: Issue #{blocked_by_number} pas encore disponible, retry dans {retry_delay}s...")
                    time.sleep(retry_delay)
                    continue
                
                print(f"    ❌ Erreur API dépendance {issue_number} <- {blocked_by_number}: {resp.status_code} {resp.text}")
                return False
            except Exception as e:
                print(f"    ❌ Exception lors de la création de dépendance: {e}")
                return False
        return False

    def validate_requirements(self):
        """Vérifie que tous les outils nécessaires sont disponibles"""
        if not self.repo_full_name and not GitUtils.is_git_repository():
            print("❌ Erreur: Vous devez être dans un repository Git ou spécifier --repo")
            sys.exit(1)

        try:
            cmd = ['gh', 'auth', 'status']
            debug_command(cmd, "check GitHub CLI auth")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Erreur: GitHub CLI non authentifié. Lancez: gh auth login")
                sys.exit(1)
        except FileNotFoundError:
            print("❌ Erreur: GitHub CLI non installé. https://cli.github.com/")
            sys.exit(1)

        print("✅ Prérequis validés")

    def parse_meeting_notes(self, content):
        """Parse le compte-rendu avec IA pour extraire les tickets"""
        try:
            tickets_data = self.ai.generate_tickets(content)
            if not isinstance(tickets_data, dict) or 'tickets' not in tickets_data:
                print("❌ Erreur: Format JSON invalide de l'IA (pas de champ 'tickets')")
                return []
            return tickets_data.get('tickets', [])
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse IA: {e}")
            return []

    def create_github_issues(self, tickets, file_path):
        """Crée les issues sur GitHub avec leurs dépendances"""
        created = []
        position_to_github_number = {}
        repo_arg = ['--repo', self._get_current_repo()] if self._get_current_repo() else []

        print("\n🚀 Création des issues sur GitHub...")
        
        for i, ticket in enumerate(tickets, 1):
            try:
                issue_title = ticket['title']
                print(f"\n🎫 [{i}/{len(tickets)}] {issue_title}")

                labels = ticket.get('labels', ['enhancement'])
                for label in labels:
                    color = self.PRIORITY_COLORS.get(label, '0969da')
                    self._ensure_label_exists(label, color)

                description = f"{ticket['description']}\n\n**🎛️ Priorité:** {ticket['priority']}\n**⏱️ Estimation:** {ticket['estimate']} jours\n"
                if ticket.get('dependencies'):
                    deps_str = ', '.join([f"#{dep}" for dep in ticket['dependencies']])
                    description += f"**🔗 Dépendances:** {deps_str}\n"
                description += f"\n---\n*🤖 Généré automatiquement par git-auto-flow*"

                cmd = ['gh', 'issue', 'create', *repo_arg, '--title', issue_title, '--body', description]
                for label in labels:
                    cmd.extend(['--label', label])

                debug_command(cmd, f"create issue: {ticket['title']}")
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    issue_url = result.stdout.strip()
                    issue_number = issue_url.split('/')[-1]
                    if ticket.get('position'):
                        position_to_github_number[ticket.get('position')] = issue_number
                    created.append({'title': issue_title, 'url': issue_url, 'priority': ticket['priority'], 'github_number': issue_number, 'dependencies': ticket.get('dependencies', []), 'position': ticket.get('position')})
                    print(f"  ✅ {issue_url}")
                else:
                    print(f"  ❌ Erreur: {result.stderr.strip()}")
            except Exception as e:
                print(f"  ❌ Erreur création: {e}")

        print("\n🔗 Création des dépendances et labels...")
        for issue in created:
            if issue.get('dependencies'):
                for dep_position in issue['dependencies']:
                    dep_github_number = position_to_github_number.get(dep_position)
                    if dep_github_number:
                        # Ajout du label "blocked_by_#..."
                        label_name = f"blocked_by_#{dep_github_number}"
                        print(f"  - Ajout du label '{label_name}' à l'issue #{issue['github_number']}")
                        self._ensure_label_exists(label_name, color='d73a4a')
                        edit_cmd = ['gh', 'issue', 'edit', issue['github_number'], *repo_arg, '--add-label', label_name]
                        debug_command(edit_cmd, f"add dependency label to #{issue['github_number']}")
                        subprocess.run(edit_cmd, capture_output=True, text=True)

                        # Création de la dépendance
                        self._add_dependency_api(issue['github_number'], dep_github_number)
                    else:
                        print(f"    ⚠️  Dépendance non trouvée pour la position: {dep_position}")
        return created

    def run(self, file_path):
        """Processus principal"""
        print("🎫 Git Auto-Flow - Création de tickets")
        print("=" * 45)
        
        try:
            content = Path(file_path).read_text(encoding='utf-8')
            print(f"📄 Fichier: {file_path} ({len(content)} chars)")
        except Exception as e:
            print(f"❌ Erreur lecture: {e}")
            return
        
        print("\n🤖 Analyse IA en cours...")
        tickets = self.parse_meeting_notes(content)
        
        if not tickets:
            print("❌ Aucun ticket généré")
            return
            
        print(f"\n📋 {len(tickets)} tickets détectés:")
        for i, ticket in enumerate(tickets, 1):
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(ticket.get('priority', 'medium'), '⚪️')
            print(f"  {i}. {priority_icon} {ticket['title']} ({ticket.get('estimate', '?')}j)")
        
        confirm = input(f"\n✅ Créer ces {len(tickets)} issues GitHub? (y/N): ")
        if confirm.lower() not in ['y', 'yes', 'o', 'oui']:
            print("❌ Création annulée")
            return
        
        created = self.create_github_issues(tickets, file_path)
        
        if created:
            print(f"\n🎉 {len(created)} issues créées !")
            for issue in created:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue.get('priority', 'medium'), '⚪️')
                print(f"  {priority_icon} {issue['title']}")
                print(f"    └── {issue['url']}")
        else:
            print("\n❌ Aucune issue créée")

def main():
    parser = argparse.ArgumentParser(description='Crée des tickets GitHub depuis un compte-rendu')
    parser.add_argument('file', help='Fichier de compte-rendu à analyser')
    parser.add_argument('--repo', help='Repo cible au format owner/repo (ex: genix-x/git-auto-flow)')
    parser.add_argument('--debug', action='store_true', help='Mode debug détaillé')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"❌ Fichier non trouvé: {args.file}")
        sys.exit(1)
    
    creator = GitCreateTickets(repo_full_name=args.repo, debug_mode=args.debug)
    creator.run(args.file)

if __name__ == '__main__':
    main()