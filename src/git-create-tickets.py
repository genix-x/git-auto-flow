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
        existing_labels = self._get_github_labels()
        
        if label_name in existing_labels:
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
            else:
                print(f"  ⚠️  Impossible de créer le label '{label_name}': {result.stderr.strip()}")
                return False
        except Exception as e:
            print(f"  ❌ Erreur lors de la création du label '{label_name}': {e}")
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

    def create_github_issues(self, tickets):
        """Crée les issues sur GitHub"""
        created_issues = []
        
        for i, ticket in enumerate(tickets, 1):
            try:
                print(f"\n🎫 [{i}/{len(tickets)}] {ticket['title']}")
                
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
                    '--title', ticket['title'],
                    '--body', description,
                ]
                for label in valid_labels:
                    cmd.extend(['--label', label])
                
                debug_command(cmd, f"create issue: {ticket['title']}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    issue_url = result.stdout.strip()
                    created_issues.append({
                        'title': ticket['title'],
                        'url': issue_url,
                        'priority': ticket['priority']
                    })
                    print(f"  ✅ {issue_url}")
                else:
                    print(f"  ❌ Erreur: {result.stderr.strip()}")
                    
            except Exception as e:
                print(f"  ❌ Erreur création: {e}")
        
        return created_issues

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
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(ticket.get('priority', 'medium'), '⚪')
            print(f"  {i}. {priority_icon} {ticket['title']} ({ticket.get('estimate', '?')}j)")
        
        confirm = input(f"\n✅ Créer ces {len(tickets)} issues GitHub? (y/N): ")
        if confirm.lower() not in ['y', 'yes', 'o', 'oui']:
            print("❌ Création annulée")
            return
        
        print("\n🚀 Création en cours...")
        created = self.create_github_issues(tickets)
        
        if created:
            print(f"\n🎉 {len(created)} issues créées !")
            for issue in created:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue.get('priority', 'medium'), '⚪')
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