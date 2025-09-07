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

# Réutilise les libs existantes ! 🎯
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from ai_provider import AIProvider
from git_utils import GitUtils  
from debug_logger import debug_command, set_global_debug_mode

class GitCreateTickets:
    def __init__(self, debug_mode=False):
        set_global_debug_mode(debug_mode)
        self.ai = AIProvider()  # ✨ Réutilise le provider existant !
        self.validate_requirements()

    def validate_requirements(self):
        """Vérifie les prérequis"""
        # Git repo
        if not GitUtils.is_git_repository():
            print("❌ Pas dans un repository Git")
            sys.exit(1)

        # GitHub CLI
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
            
            # Utilise l'AIProvider qui gère tout !
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
                
                # Description enrichie
                description = f"{ticket['description']}\n\n"
                description += f"**🎛️ Priorité:** {ticket['priority']}\n"
                description += f"**⏱️ Estimation:** {ticket['estimate']} jours\n"
                description += f"\n---\n*🤖 Généré automatiquement par git-auto-flow*"
                
                # Labels
                labels = ','.join(ticket.get('labels', ['enhancement']))
                
                # Commande GitHub CLI
                cmd = [
                    'gh', 'issue', 'create',
                    '--title', ticket['title'],
                    '--body', description,
                    '--label', labels
                ]
                
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
        
        # Lecture fichier
        try:
            content = Path(file_path).read_text(encoding='utf-8')
            print(f"📄 Fichier: {file_path} ({len(content)} chars)")
        except Exception as e:
            print(f"❌ Erreur lecture: {e}")
            return
        
        # Parse IA
        print("\n🤖 Analyse IA en cours...")
        tickets = self.parse_meeting_notes(content)
        
        if not tickets:
            print("❌ Aucun ticket généré")
            return
            
        # Aperçu
        print(f"\n📋 {len(tickets)} tickets détectés:")
        for i, ticket in enumerate(tickets, 1):
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(ticket.get('priority', 'medium'), '⚪')
            print(f"  {i}. {priority_icon} {ticket['title']} ({ticket.get('estimate', '?')}j)")
        
        # Confirmation
        confirm = input(f"\n✅ Créer ces {len(tickets)} issues GitHub? (y/N): ")
        if confirm.lower() not in ['y', 'yes', 'o', 'oui']:
            print("❌ Création annulée")
            return
        
        # Création
        print("\n🚀 Création en cours...")
        created = self.create_github_issues(tickets)
        
        # Résumé final
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
