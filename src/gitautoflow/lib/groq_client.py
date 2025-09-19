#!/usr/bin/env python3
"""
Client Groq pour l'automation Git (fallback de Gemini)
"""

import os
import json
from typing import Dict, List, Optional
from groq import Groq
from prompt_templates import PromptTemplates


class GroqClient:
    """Client Groq comme fallback pour Gemini"""
    
    def __init__(self, api_key: str):
        """Initialise le client Groq"""
        self.client = Groq(api_key=api_key)
        # Modèles disponibles gratuitement sur Groq
        self.model = "mixtral-8x7b-32768"  # ou "llama3-8b-8192"
    
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
Analyse les changements Git suivants et génère UNIQUEMENT un JSON valide.

FICHIERS MODIFIÉS:
{files}

DIFFÉRENCES:
{diff[:2000]}...

IMPORTANT: Tu DOIS répondre EXCLUSIVEMENT avec ce format JSON exact, sans aucun texte avant ou après:

{{
    "type": "feat",
    "scope": "automation", 
    "description": "add gemini AI powered commit automation",
    "body": "Add intelligent commit message generation using AI.\\n- Auto-analyze git diff and staged files\\n- Generate conventional commit messages\\n- Support for scopes, breaking changes, and issue linking\\n- Interactive confirmation before commit",
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
{diff[:1500]}...

RÉPONSE OBLIGATOIRE: JSON STRICT - AUCUN TEXTE EXPLICATIF

Format JSON obligatoire (exemple):
{{
    "title": "feat(automation): add AI scripts for git automation",
    "body": "## Summary\n\nAdd intelligent automation scripts for Git commits and PR creation using AI.\n\n## Changes\n\n- Add automated commit message generation\n- Add automated PR creation\n- Add shared libraries for reusable functions\n- Add shell wrappers for easy execution\n\n## Test plan\n\n- [x] Scripts tested with real repositories\n- [x] Error handling validated\n- [x] API key configuration working",
    "labels": ["enhancement"],
    "draft": false
}}

RÈGLES CRITIQUES:
1. UNIQUEMENT JSON - PAS DE TEXTE AVANT/APRÈS
2. title: conventional commit format (type(scope): description)
3. body: markdown avec sections Summary, Changes, Test plan
4. labels: tableau de chaînes pertinentes (seulement: enhancement, bug, documentation)
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
        Effectue une requête à l'API Groq et parse le JSON
        
        Args:
            prompt: Le prompt à envoyer à Groq
            
        Returns:
            Dict parsé depuis la réponse JSON
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en Git et commits conventionnels. Tu génères UNIQUEMENT du JSON valide."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.1,  # Peu de créativité pour plus de consistance
                max_tokens=1000
            )
            
            content = chat_completion.choices[0].message.content.strip()
            
            # Nettoie la réponse pour extraire le JSON
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Erreur JSON Groq: {e}\\nContenu analysé: {content}")
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'analyse avec Groq: {e}")
    
    def analyze_for_release(self, diff: str, files: str, commits: Optional[List[str]] = None) -> Dict:
        """
        Analyse les changements pour générer une PR de release develop -> main
        
        Args:
            diff: Le git diff complet develop -> main
            files: La liste des fichiers modifiés
            commits: Liste des messages de commits
            
        Returns:
            Dict contenant les données de la PR de release
        """
        prompt = PromptTemplates.get_release_prompt(files, commits, diff)
        
        try:
            completion = self.client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": prompt,
                }],
                model="llama3-8b-8192",
                temperature=0.1,
            )
            
            content = PromptTemplates.clean_json_response(completion.choices[0].message.content)
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Erreur JSON Groq: {e}\\nContenu analysé: {content}")
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'analyse avec Groq: {e}")