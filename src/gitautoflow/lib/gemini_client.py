#!/usr/bin/env python3
"""
Bibliothèque commune pour les appels à l'API Gemini
"""

import os
import json
import google.generativeai as genai
from typing import Dict, List, Optional
from dotenv import load_dotenv
from .prompt_templates import PromptTemplates
from .debug_logger import debug_command


class GeminiClient:
    """Client réutilisable pour les appels à l'API Gemini"""
    
    def __init__(self):
        """Initialise le client Gemini avec la clé API"""
        # Charge le fichier .env depuis le système global
        self._load_env_from_git_root()
        
        # Vérifie la clé API
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            env_path = os.path.expanduser('~/.env.gitautoflow')
            raise ValueError(
                "❌ GEMINI_API_KEY non définie\n"
                "💡 Solutions:\n"
                f"   1. Ajouter GEMINI_API_KEY=ta_cle dans le fichier {env_path}\n"
                "   2. Export GEMINI_API_KEY='ta_cle_ici'"
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def _load_env_from_git_root(self):
        """Charge le fichier .env depuis le home directory"""
        env_file = os.path.expanduser('~/.env.gitautoflow')
        if os.path.exists(env_file):
            load_dotenv(env_file)
            return
        
        # Fallback sur le fichier local si le global n'existe pas
        local_env = os.path.join(os.path.dirname(__file__), '../../.env')
        if os.path.exists(local_env):
            load_dotenv(local_env)
    
    def analyze_for_commit(self, diff: str, files: str) -> Dict:
        """
        Analyse les changements Git pour générer un commit conventionnel
        
        Args:
            diff: Le git diff des fichiers stagés
            files: La liste des fichiers modifiés
            
        Returns:
            Dict contenant les données du commit (type, scope, description, body, etc.)
        """
        prompt = f"""
Tu es un générateur de commit conventionnel. Tu DOIS répondre avec UNIQUEMENT le JSON demandé.

FICHIERS MODIFIÉS:
{files}

DIFFÉRENCES:
{diff}

RÉPONSE OBLIGATOIRE - FORMAT EXACT:
{{
    "type": "fix",
    "scope": "commit",
    "description": "correct newline characters in commit messages",
    "body": "Replace escaped newlines with actual newlines\n- Fix \\\\n display issue in GitHub\n- Improve commit readability",
    "breaking": false,
    "issues": []
}}

TYPES AUTORISÉS: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert

RÈGLES CRITIQUES:
- UNIQUEMENT JSON - AUCUN TEXTE EXPLICATIF
- OBLIGATOIRE: type, description
- description: anglais, sans majuscule début
- body: optionnel, avec vrais \\n pour retours ligne

GÉNÈRE TON JSON:"""
        return self._make_request(prompt)
    
    def analyze_for_pr(self, diff: str, files: str, target_branch: str = "develop") -> Dict:
        """
        Analyse les changements Git pour générer une PR
        
        Args:
            diff: Le git diff complet de la branche
            files: La liste des fichiers modifiés
            target_branch: La branche cible (develop, main, etc.)
            
        Returns:
            Dict contenant les données de la PR (title, body, labels, etc.)
        """
        prompt = f"""
Analyse les changements Git pour créer une Pull Request vers {target_branch}.

FICHIERS MODIFIÉS:
{files}

DIFFÉRENCES (première partie):
{diff[:2000]}...

RÉPONSE OBLIGATOIRE: JSON STRICT - AUCUN TEXTE EXPLICATIF

Format JSON obligatoire (exemple):
{{
    "title": "feat(automation): add gemini AI scripts for git automation",
    "body": "## Summary\n\nAdd intelligent automation scripts for Git commits and PR creation using Gemini AI.\n\n## Changes\n\n- Add git-cz-auto-v2.py for automatic commit message generation\n- Add git-pr-auto.py for automatic PR creation\n- Add shared lib with GeminiClient and GitUtils\n- Add shell wrappers for easy execution\n\n## Test plan\n\n- [x] Scripts tested with real repositories\n- [x] Error handling validated\n- [x] API key configuration working\n\n🤖 Generated with [Claude Code](https://claude.ai/code)",
    "labels": ["enhancement"],
    "draft": false
}}

RÈGLES CRITIQUES:
1. UNIQUEMENT JSON - PAS DE TEXTE AVANT/APRÈS
2. title: conventional commit format (type(scope): description)
3. body: markdown avec sections Summary, Changes, Test plan
4. labels: tableau de chaînes pertinentes
5. draft: booléen

RÉPONSE = JSON SEULEMENT:
"""
        return self._make_request(prompt)
    
    def generate_json_response(self, prompt: str) -> Dict:
        """
        Génère une réponse JSON générique depuis un prompt
        """
        return self._make_request(prompt)
    
    def _make_request(self, prompt: str) -> Dict:
        """
        Effectue une requête à l'API Gemini et parse le JSON
        
        Args:
            prompt: Le prompt à envoyer à Gemini
            
        Returns:
            Dict parsé depuis la réponse JSON
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
            raise ValueError(f"Erreur JSON: {e}\\nContenu analysé: {content}")
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'analyse avec Gemini: {e}")
    
    def analyze_for_release(self, diff: str, files: str, commits: Optional[List[str]] = None, latest_tag: str = "v0.0.0") -> Dict:
        """
        Analyse les changements pour générer une PR de release + calcul de version
        
        Args:
            diff: Le git diff complet develop -> main
            files: La liste des fichiers modifiés
            commits: Liste des messages de commits
            latest_tag: Le dernier tag git pour le calcul de version
            
        Returns:
            Dict contenant les données de la PR + version calculée
        """
        prompt = self._get_enhanced_release_prompt(files, commits, diff, latest_tag)
        
        try:
            response = self.model.generate_content(prompt)
            content = PromptTemplates.clean_json_response(response.text)
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Erreur JSON: {e}\\nContenu analysé: {content}")
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'analyse avec Gemini: {e}")
    
    def _get_enhanced_release_prompt(self, files: str, commits: Optional[List[str]] = None, diff: str = "", latest_tag: str = "v0.0.0") -> str:
        """
        Nouveau prompt qui génère PR + calcul de version automatique
        """
        commits_text = ""
        if commits:
            commits_text = f"""
COMMITS INCLUS:
{chr(10).join(f'• {commit}' for commit in commits)}
"""

        # Tronquer le diff s'il est trop long
        diff_text = diff[:4000] if diff else ""

        return f"""
Analyze the changes for a RELEASE (develop -> main) and generate COMPLETE JSON for PR + VERSION.

CURRENT VERSION: {latest_tag}

MODIFIED FILES:
{files}
{commits_text}
DIFF:
{diff_text}

Generate JSON with this EXACT structure:
{{
    "pr": {{
        "title": "Release: Short description of changes",
        "body": "## 🚀 Release Notes\n\n### ✨ New Features\n- Feature 1\n\n### 🐛 Bug Fixes\n- Fix 1\n\n### 📝 Documentation\n- Doc update\n\n### 🔧 Other Changes\n- Other changes",
        "labels": []
    }},
    "release": {{
        "version": "1.2.0",
        "version_type": "minor",
        "breaking_changes": false,
        "major_changes": [],
        "minor_changes": [],
        "patch_changes": []
    }}
}}

VERSION CALCULATION RULES (Semantic Versioning):
- MAJOR (x.0.0): Breaking changes, major refactors, API changes
- MINOR (0.x.0): New features (feat:), enhancements, new capabilities  
- PATCH (0.0.x): Bug fixes (fix:), docs, style, test, chore, refactor

ANALYZE COMMITS and determine:
1. Highest impact change type (major > minor > patch)
2. List changes by category in release object
3. Calculate next version based on commit types and CURRENT VERSION ({latest_tag})

IMPORTANT:
- PR title: "Release: Short description" (NO version number)
- PR body: Professional English release notes with emoji sections
- Version: Calculate based on commit analysis and CURRENT VERSION ({latest_tag})
- Breaking changes: Look for "BREAKING CHANGE:" or major refactors
- Group changes by type in the release object

RETURN ONLY THE JSON, NO EXPLANATION:
"""