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
Analyze the changes for a RELEASE (develop -> main) and generate ONLY valid JSON.

MODIFIED FILES:
{files}
{commits_text}
DIFF:
{diff_text}

Generate JSON with this exact structure:
{{
    "title": "Release: Short description of changes",
    "body": "## 🚀 Release Notes\\n\\n### ✨ New Features\\n- Feature 1\\n\\n### 🐛 Bug Fixes\\n- Fix 1\\n\\n### 📝 Documentation\\n- Doc update\\n\\n### 🔧 Other Changes\\n- Other changes",
    "labels": []
}}

Instructions:
- Title: Format "Release: Short description" (NO version number)
- Body: Professional English release notes with emoji sections
- Summarize ALL important features/fixes in this release
- Be factual and professional in ENGLISH
- Group by change type (Features, Bug Fixes, Documentation, Other Changes)
- Labels: empty array
- WRITE EVERYTHING IN ENGLISH

RETURN ONLY THE JSON, NO EXPLANATION:
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