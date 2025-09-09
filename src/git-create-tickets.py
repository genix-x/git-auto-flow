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
from typing import List

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
        'documentation': '0969da'     # Bleu
    }

    def __init__(self, debug_mode=False):
        set_global_debug_mode(debug_mode)
        self.ai = AIProvider()
        self._github_labels_cache = None
        self.validate_requirements()

    def _get_github_labels(self) -> List[str]:
        """Récupère et cache la liste des labels GitHub existants"""
        if self._github_labels_cache is None:
            try:
                cmd = ['gh', 'label', 'list', '--json', 'name', '--jq', '.[].name']
                debug_command(cmd, "get github labels")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                self._github_labels_cache = result.stdout.strip().split('\n') if result.stdout else []
            except (subprocess.CalledProcessError, FileNotFoundError):
                self._github_labels_cache = []
        return self._github_labels_cache

    def _ensure_label_exists(self, label_name: str, color: str = "0969da") -> bool:
        """Crée le label s'il n'existe pas. Retourne True si succès"""
        # Utilise le cache de labels pour éviter les appels répétés
        if self._github_labels_cache is None:
            self._get_github_labels()

        if label_name in self._github_labels_cache:
            return True

        print(f"️️ℹ️  Label '{label_name}' non trouvé, tentative de création...")
        try:
            cmd = ['gh', 'label', 'create', label_name, '--color', color]
            debug_command(cmd, f"create label {label_name}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ Label '{label_name}' créé.")
                self._github_labels_cache.append(label_name)
                return True
            
            # Si le label existe déjà, on l'ajoute au cache et on continue
            if "already exists" in result.stderr:
                print(f"  ✅ Label '{label_name}' existe déjà, ajout au cache.")
                self._github_labels_cache.append(label_name)
                return True
            
            print(f"  ⚠️  Impossible de créer le label '{label_name}': {result.stderr.strip()}")
            return False
        except Exception as e:
            print(f"  ❌ Erreur lors de la création du label '{label_name}': {e}")
            return False

    def _add_dependency_api(self, issue_number, blocked_by_number):
        """Crée une vraie dépendance GitHub entre deux issues, avec une logique de réessai."""
        owner, repo = GitUtils.get_repo_info()
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by"
        
        try:
            token = os.getenv("GITHUB_TOKEN")
            if not token:
                result = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True)
                token = result.stdout.strip()
        except:
            print("⚠️ Impossible de récupérer le token GitHub")
            return False
        
        headers = {
            "Accept": "application/vnd.github+json", 
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        data = {"issue_id": int(blocked_by_number)}
        
        max_retries = 3
        retry_delay = 2  # secondes

        for attempt in range(max_retries):
            try:
                resp = requests.post(url, json=data, headers=headers)
                if resp.status_code == 201:
                    print(f"    ✅ Dépendance API créée: #{issue_number} bloqué par #{blocked_by_number}")
                    return True
                
                # Si l'issue n'est pas trouvée (404), on réessaie après un délai
                if resp.status_code == 404 and attempt < max_retries - 1:
                    print(f"    ⚠️  Dépendance non trouvée (404) pour #{issue_number} <- #{blocked_by_number}. Nouvelle tentative dans {retry_delay}s...")
                    time.sleep(retry_delay)
                    continue
                
                # Pour les autres erreurs ou à la dernière tentative, on signale l'échec
                print(f"    ❌ Erreur API dépendance {issue_number} <- {blocked_by_number}: {resp.status_code} {resp.text}")
                return False
            except Exception as e:
                print(f"    ❌ Exception lors de la création de la dépendance: {e}")
                return False
        return False

    def validate_requirements(self):
        """Vérifie les prérequis"""
        if not GitUtils.is_git_repository():
            print("❌ Pas dans un repository Git")
            sys.exit(1)

        try:
            cmd = ['gh', 'auth', 'status']
            debug_command(cmd, "check GitHub CLI auth")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ GitHub CLI non authentifié. Lancez: gh auth login")
                sys.exit(1)
        except FileNotFoundError:
            print("❌ GitHub CLI non installé")
            sys.exit(1)

        print("✅ Prérequis validés")

    def parse_meeting_notes(self, content):
        """Parse le compte-rendu avec IA pour extraire les tickets"""
        try:
            print(f" {self.ai.get_status()}")
            tickets_data = self.ai.generate_tickets(content)
            if 'tickets' not in tickets_data:
                print("❌ Format JSON invalide (pas de champ 'tickets')")
                return []
            return tickets_data.get('tickets', [])
        except Exception as e:
            print(f"❌ Erreur IA: {e}")
            return []

    def create_github_issues(self, tickets, file_path):
        """Crée les issues sur GitHub et leurs dépendances"""
        created = []
        position_to_github_number = {}
        file_name = os.path.basename(file_path)
        
        # Étape 1: Création de toutes les issues
        print("\n🚀 Création des issues sur GitHub...")
        for i, ticket in enumerate(tickets, 1):
            try:
                issue_title = f"[{file_name}] {ticket['title']}"
                print(f"\n🎫 [{i}/{len(tickets)}] {issue_title}")
                
                # Labels
                labels = ticket.get('labels', ['enhancement'])
                valid_labels = []
                for label in labels:
                    color = self.PRIORITY_COLORS.get(label, '0969da')
                    if self._ensure_label_exists(label, color):
                        valid_labels.append(label)
                    else:
                        print(f"  ⚠️  Label '{label}' ignoré car il n'a pas pu être créé.")

                if not valid_labels:
                    print("  ⚠️  Aucun label valide pour ce ticket, il sera créé sans label.")

                # Description enrichie
                description = f"{ticket['description']}\n\n"
                description += f"**🎛️ Priorité:** {ticket['priority']}\n"
                description += f"**⏱️ Estimation:** {ticket['estimate']} jours\n"
                description += f"\n---\n*🤖 Généré automatiquement par git-auto-flow*"
                
                # Commande GitHub CLI
                cmd = [
                    'gh', 'issue', 'create',
                    '--title', issue_title,
                    '--body', description,
                ]
                for label in valid_labels:
                    cmd.extend(['--label', label])
                
                debug_command(cmd, f"create issue: {ticket['title']}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    issue_url = result.stdout.strip()
                    issue_number = issue_url.split('/')[-1]
                    
                    position = ticket.get('position')
                    if position:
                        position_to_github_number[position] = issue_number

                    created.append({
                        'title': issue_title,
                        'url': issue_url,
                        'priority': ticket['priority'],
                        'github_number': issue_number,
                        'dependencies': ticket.get('dependencies', []),
                        'position': position
                    })
                    print(f"  ✅ {issue_url}")
                else:
                    print(f"  ❌ Erreur: {result.stderr.strip()}")
                    
            except Exception as e:
                print(f"  ❌ Erreur création: {e}")
        
        # Étape 2: Création des dépendances via l'API
        print("\n Création des dépendances GitHub...")
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
    parser.add_argument('--debug', action='store_true', help='Mode debug détaillé')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"❌ Fichier non trouvé: {args.file}")
        sys.exit(1)
    
    creator = GitCreateTickets(debug_mode=args.debug)
    creator.run(args.file)

if __name__ == '__main__':
    main()