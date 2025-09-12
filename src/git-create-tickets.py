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
        
        # Initialisation centralisée du token et des headers
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            result = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True)
            self.token = result.stdout.strip()
            
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }

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
            self.repo_full_name = f"{owner}/{repo}"
            return self.repo_full_name
        except RuntimeError as e:
            debug_command([], f"Error getting current repo: {e}")
            return None

    def _add_dependency_api(self, issue_number, dependency_number):
        """Ajoute une dépendance via l'API GitHub (même repo seulement)"""
        current_repo = self._get_current_repo()
        if not current_repo:
            print("    ❌ Impossible de déterminer le repo courant. Dépendance ignorée.")
            return False

        # D'abord récupérer l'ID de l'issue dépendante
        dep_url = f"https://api.github.com/repos/{current_repo}/issues/{dependency_number}"
        dep_response = requests.get(dep_url, headers=self.headers)
        
        if dep_response.status_code != 200:
            print(f"  ❌ Issue dépendante #{dependency_number} introuvable dans {current_repo} (Status: {dep_response.status_code})")
            return False
            
        dep_issue_id = dep_response.json()['id']
        
        # CORRECT: Utiliser /blocked_by avec issue_id
        url = f"https://api.github.com/repos/{current_repo}/issues/{issue_number}/dependencies/blocked_by"
        
        payload = {
            "issue_id": dep_issue_id  # ID global, pas le numéro de l'issue !
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        
        if response.status_code in [200, 201]:
            print(f"  ✅ Dépendance API: #{issue_number} ← #{dependency_number}")
            return True
        else:
            print(f"  ❌ Erreur API dépendance {issue_number} ← {dependency_number}: {response.status_code}")
            print(f"      {response.text}")
            return False

    def validate_requirements(self):
        """Vérifie que tous les outils nécessaires sont disponibles"""
        if not self._get_current_repo():
            print("❌ Erreur: Impossible de déterminer le repo. Utilisez --repo ou lancez depuis un repo Git.")
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

        # ÉTAPE 1: Créer TOUTES les issues d'abord
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

        # ÉTAPE 2: Attendre pour la propagation des issues
        print("\n⏳ Attente de 1 seconde pour la propagation des issues...")
        time.sleep(1)

        # ÉTAPE 3: Créer les dépendances et labels
        print("\n🔗 Création des dépendances et labels...")
        for issue in created:
            if issue.get('dependencies'):
                for dep_position in issue['dependencies']:
                    dep_github_number = position_to_github_number.get(dep_position)
                    if dep_github_number:
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
