#!/usr/bin/env python3
"""
Templates de prompts communs pour éviter la duplication de code
"""

from typing import List, Optional


class PromptTemplates:
    """Classe contenant tous les templates de prompts pour les différentes IA"""
    
    @staticmethod
    def get_release_prompt(files: str, commits: Optional[List[str]] = None, diff: str = "") -> str:
        """
        Génère le prompt pour analyze_for_release
        
        Args:
            files: Liste des fichiers modifiés
            commits: Liste optionnelle des messages de commits
            diff: Le git diff (tronqué si nécessaire)
            
        Returns:
            str: Le prompt formaté pour l'analyse de release
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
Analyse les changements pour une RELEASE (develop -> main) et génère UNIQUEMENT un JSON valide.

FICHIERS MODIFIÉS:
{files}
{commits_text}
DIFF:
{diff_text}

Génère un JSON avec cette structure exacte:
{{
    "title": "Release: v0.x.x - Description courte",
    "body": "## 🚀 Release Notes\\n\\n### ✨ New Features\\n- Feature 1\\n\\n### 🐛 Bug Fixes\\n- Fix 1\\n\\n### 📝 Documentation\\n- Doc update\\n\\n### 🔧 Other Changes\\n- Other changes",
    "labels": ["release"]
}}

Instructions:
- Titre: Format "Release: v0.x.x - Description" (incrementer automatiquement)
- Body: Release notes structure avec emojis et sections
- Résumer TOUTES les features/fixes importants de cette release
- Être factuel et professionnel
- Grouper par type de changement
- Labels: toujours inclure "release"

RETOURNER UNIQUEMENT LE JSON, PAS D'EXPLICATION:
"""

    @staticmethod
    def clean_json_response(content: str) -> str:
        """
        Nettoie la réponse de l'IA pour extraire le JSON
        
        Args:
            content: Le contenu brut de la réponse IA
            
        Returns:
            str: Le JSON nettoyé
        """
        content = content.strip()
        
        # Supprime les balises markdown si présentes
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
            
        return content.strip()