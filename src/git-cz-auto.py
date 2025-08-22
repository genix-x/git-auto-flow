#!/usr/bin/env python3
"""
Script pour automatiser git cz avec l'API Gemini
"""

import subprocess
import json
import os
import sys
import google.generativeai as genai
from typing import Dict, Tuple
from dotenv import load_dotenv

class GitCzAutomator:
    def __init__(self, api_key: str):
        """Initialise le client Gemini"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Mapping des types de commits
        self.commit_types = {
            'feat': 'A new feature',
            'fix': 'A bug fix',
            'docs': 'Documentation only changes',
            'style': 'Changes that do not affect the meaning of the code',
            'refactor': 'A code change that neither fixes a bug nor adds a feature',
            'perf': 'A code change that improves performance',
            'test': 'Adding missing tests or correcting existing tests',
            'chore': 'Changes to the build process or auxiliary tools',
            'ci': 'Changes to CI configuration files and scripts',
            'build': 'Changes that affect the build system or external dependencies',
            'revert': 'Reverts a previous commit'
        }

    def get_git_diff(self) -> str:
        """Récupère le git diff des fichiers stagés"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la récupération du diff: {e}")
            sys.exit(1)

    def get_staged_files(self) -> str:
        """Récupère la liste des fichiers stagés"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la récupération des fichiers: {e}")
            sys.exit(1)

    def analyze_changes_with_gemini(self, diff: str, files: str) -> Dict:
        """Utilise Gemini pour analyser les changements"""
        
        prompt = f"""
Analyse les changements Git suivants et génère UNIQUEMENT un JSON valide.

FICHIERS MODIFIÉS:
{files}

DIFFÉRENCES:
{diff}

IMPORTANT: Tu DOIS répondre EXCLUSIVEMENT avec ce format JSON exact, sans aucun texte avant ou après:

{{
    "type": "feat",
    "scope": "automation",
    "description": "add gemini AI powered commit automation",
    "body": "Add intelligent commit message generation using Google Gemini API\\n- Auto-analyze git diff and staged files\\n- Generate conventional commit messages\\n- Support for scopes, breaking changes, and issue linking\\n- Interactive confirmation before commit",
    "breaking": false,
    "issues": []
}}

Types possibles: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert

Règles strictes:
1. Réponse = JSON SEULEMENT
2. Pas de markdown, pas de texte explicatif
3. description en anglais, sans majuscule au début
4. scope optionnel mais pertinent
5. body avec détails si nécessaire (avec \\n pour newlines)

JSON SEULEMENT:
"""

        try:
            response = self.model.generate_content(prompt)
            
            
            # Nettoie la réponse pour extraire le JSON
            content = response.text.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            print(f"Erreur JSON: {e}")
            print(f"Contenu analysé: {content}")
            sys.exit(1)
        except Exception as e:
            print(f"Erreur lors de l'analyse avec Gemini: {e}")
            sys.exit(1)

    def run_git_cz(self, commit_data: Dict) -> None:
        """Execute git cz avec les données automatiques"""
        
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
        
        body = '\n\n'.join(body_parts) if body_parts else ''
        
        # Affiche le commit proposé
        print("📝 Commit proposé:")
        print(f"   {commit_msg}")
        if body:
            print(f"\n{body}")
        
        # Demande confirmation
        response = input("\n✅ Confirmer ce commit? (y/N): ").strip().lower()
        if response not in ['y', 'yes', 'o', 'oui']:
            print("❌ Commit annulé")
            return
            
        # Execute le commit
        try:
            full_msg = commit_msg
            if body:
                full_msg += f"\n\n{body}"
                
            subprocess.run(['git', 'commit', '-m', full_msg], check=True)
            print("✅ Commit effectué avec succès!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors du commit: {e}")
            sys.exit(1)

def main():
    """Fonction principale"""
    
    # Charge le fichier .env
    load_dotenv()
    
    # Vérifie la clé API
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY non définie")
        print("💡 Solutions:")
        print("   1. Ajouter GEMINI_API_KEY=ta_cle dans le fichier .env")
        print("   2. Export GEMINI_API_KEY='ta_cle_ici'")
        sys.exit(1)
    
    # Vérifie qu'on est dans un repo git
    try:
        subprocess.run(['git', 'status'], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ Pas dans un repository Git")
        sys.exit(1)
    
    automator = GitCzAutomator(api_key)
    
    # Récupère les changements
    print("🔍 Analyse des changements...")
    diff = automator.get_git_diff()
    files = automator.get_staged_files()
    
    if not diff:
        print("❌ Aucun changement stagé trouvé")
        print("Utilise 'git add' pour stager tes fichiers")
        sys.exit(1)
    
    print("🤖 Analyse avec Gemini...")
    commit_data = automator.analyze_changes_with_gemini(diff, files)
    
    # Execute le commit
    automator.run_git_cz(commit_data)

if __name__ == "__main__":
    main()