#!/usr/bin/env python3
"""
Gestionnaire multi-IA intelligent avec fallback automatique
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv


class AIProvider:
    """Gestionnaire intelligent multi-IA avec fallback automatique"""
    
    def __init__(self):
        """Initialise le gestionnaire multi-IA"""
        # Charge le fichier .env depuis le système global
        self._load_env_from_git_root()
        
        # Stockage des clients
        self.gemini_client = None
        self.groq_client = None
        
        # Configuration des APIs
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.groq_key = os.getenv('GROQ_API_KEY')
        
        # État des APIs (pour éviter de retester une API qui a échoué)
        self.gemini_available = bool(self.gemini_key)
        self.groq_available = bool(self.groq_key)
        
        if not (self.gemini_available or self.groq_available):
            env_path = os.path.expanduser('~/.env.gitautoflow')
            raise ValueError(
                "❌ Aucune clé API configurée!\n\n"
                "💡 Configurez vos clés API en éditant le fichier .env:\n"
                f"   📄 {env_path}\n\n"
                "🔑 Clés disponibles:\n"
                "   GEMINI_API_KEY=votre_cle_gemini\n"
                "   GROQ_API_KEY=votre_cle_groq\n\n"
                "🔗 Obtenir les clés:\n"
                "   • Gemini: https://makersuite.google.com/app/apikey\n"
                "   • Groq: https://console.groq.com/keys\n\n"
                "⚡ Ou relancez: ./install.sh pour configuration interactive"
            )
    
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
    
    def _get_gemini_client(self):
        """Initialise le client Gemini si pas encore fait"""
        if not self.gemini_client and self.gemini_available:
            try:
                # Import dynamique pour éviter les erreurs de chemin
                import sys
                from pathlib import Path
                lib_path = Path(__file__).parent
                if str(lib_path) not in sys.path:
                    sys.path.insert(0, str(lib_path))
                
                from gemini_client import GeminiClient
                self.gemini_client = GeminiClient()
                return self.gemini_client
            except Exception as e:
                print(f"⚠️  Gemini indisponible: {e}")
                self.gemini_available = False
                return None
        return self.gemini_client
    
    def _get_groq_client(self):
        """Initialise le client Groq si pas encore fait"""
        if not self.groq_client and self.groq_available:
            try:
                # Import dynamique pour éviter les erreurs de chemin
                import sys
                from pathlib import Path
                lib_path = Path(__file__).parent
                if str(lib_path) not in sys.path:
                    sys.path.insert(0, str(lib_path))
                
                from groq_client import GroqClient
                self.groq_client = GroqClient(self.groq_key)
                return self.groq_client
            except Exception as e:
                print(f"⚠️  Groq indisponible: {e}")
                self.groq_available = False
                return None
        return self.groq_client
    
    def analyze_for_commit(self, diff: str, files: str) -> Dict:
        """
        Analyse intelligente avec fallback automatique
        
        Args:
            diff: Le git diff des fichiers stagés
            files: La liste des fichiers modifiés
            
        Returns:
            Dict contenant les données du commit
        """
        # Tentative 1: Gemini (priorité 1)
        if self.gemini_available:
            try:
                print("🤖 Analyse avec Gemini...")
                client = self._get_gemini_client()
                if client:
                    return client.analyze_for_commit(diff, files)
            except Exception as e:
                print(f"❌ Gemini: {e}")
                print("🔄 Fallback vers Groq...")
                self.gemini_available = False
        
        # Tentative 2: Groq (fallback)
        if self.groq_available:
            try:
                print("🚀 Analyse avec Groq (fallback)...")
                client = self._get_groq_client()
                if client:
                    return client.analyze_for_commit(diff, files)
            except Exception as e:
                print(f"❌ Groq: {e}")
                self.groq_available = False
        
        # Aucune IA disponible
        raise RuntimeError(
            "❌ Aucune IA disponible!\n"
            "💡 Vérifiez vos clés API et votre connexion internet"
        )
    
    def analyze_for_pr(self, diff: str, files: str, target_branch: str = "develop") -> Dict:
        """
        Analyse intelligente pour PR avec fallback automatique
        
        Args:
            diff: Le git diff complet de la branche
            files: La liste des fichiers modifiés
            target_branch: La branche cible
            
        Returns:
            Dict contenant les données de la PR
        """
        # Tentative 1: Gemini (priorité 1)
        if self.gemini_available:
            try:
                print("🤖 Génération PR avec Gemini...")
                client = self._get_gemini_client()
                if client:
                    return client.analyze_for_pr(diff, files, target_branch)
            except Exception as e:
                print(f"❌ Gemini: {e}")
                print("🔄 Fallback vers Groq...")
                self.gemini_available = False
        
        # Tentative 2: Groq (fallback)
        if self.groq_available:
            try:
                print("🚀 Génération PR avec Groq (fallback)...")
                client = self._get_groq_client()
                if client:
                    return client.analyze_for_pr(diff, files, target_branch)
            except Exception as e:
                print(f"❌ Groq: {e}")
                self.groq_available = False
        
        # Aucune IA disponible
        raise RuntimeError(
            "❌ Aucune IA disponible!\n"
            "💡 Vérifiez vos clés API et votre connexion internet"
        )
    
    def analyze_for_release(self, diff: str, files: str, commits: list = None, latest_tag: str = "v0.0.0") -> Dict:
        """
        Analyse intelligente pour release PR avec fallback automatique
        
        Args:
            diff: Le git diff complet develop -> main
            files: La liste des fichiers modifiés
            commits: Liste des messages de commits
            latest_tag: Le dernier tag git pour le calcul de version
            
        Returns:
            Dict contenant les données de la PR de release
        """
        # Tentative 1: Gemini (priorité 1)
        if self.gemini_available:
            try:
                print("🤖 Génération Release PR avec Gemini...")
                client = self._get_gemini_client()
                if client:
                    return client.analyze_for_release(diff, files, commits, latest_tag)
            except Exception as e:
                print(f"❌ Gemini: {e}")
                print("🔄 Fallback vers Groq...")
                self.gemini_available = False
        
        # Tentative 2: Groq (fallback)
        if self.groq_available:
            try:
                print("🚀 Génération Release PR avec Groq (fallback)...")
                client = self._get_groq_client()
                if client:
                    return client.analyze_for_release(diff, files, commits, latest_tag)
            except Exception as e:
                print(f"❌ Groq: {e}")
                self.groq_available = False
        
        # Aucune IA disponible
        raise RuntimeError(
            "❌ Aucune IA disponible!\n"
            "💡 Vérifiez vos clés API et votre connexion internet"
        )

    def generate_response(self, prompt: str) -> Dict:
        """
        Génère une réponse JSON générique avec fallback automatique
        """
        # Tentative 1: Gemini (priorité 1)
        if self.gemini_available:
            try:
                print("🤖 Analyse avec Gemini...")
                client = self._get_gemini_client()
                if client:
                    return client.generate_json_response(prompt)
            except Exception as e:
                print(f"❌ Gemini: {e}")
                print("🔄 Fallback vers Groq...")
                self.gemini_available = False
        
        # Tentative 2: Groq (fallback)
        if self.groq_available:
            try:
                print("🚀 Analyse avec Groq (fallback)...")
                client = self._get_groq_client()
                if client:
                    return client.generate_json_response(prompt)
            except Exception as e:
                print(f"❌ Groq: {e}")
                self.groq_available = False
        
        # Aucune IA disponible
        raise RuntimeError(
            "❌ Aucune IA disponible!\n"
            "💡 Vérifiez vos clés API et votre connexion internet"
        )
    
    def generate_tickets(self, content: str, context: str = "") -> dict:
        """
        Génère des tickets/issues depuis un compte-rendu avec IA
        """
        prompt = f'''
Analyse ce compte-rendu de projet et extrait les tickets/tâches à créer comme issues GitHub.

COMPTE-RENDU:
{content}

CONTEXTE ADDITIONNEL:
{context}

Tu dois répondre UNIQUEMENT avec un JSON valide dans ce format exact:
{{
  "tickets": [
    {{
      "title": "Titre concis et actionnable",
      "description": "Description détaillée avec critères d'acceptance",
      "labels": ["enhancement", "priority-high"],
      "priority": "high",
      "estimate": "3"
    }}
  ]
}}

RÈGLES STRICTES:
- Maximum 5 tickets les plus prioritaires
- Titres courts et clairs (50 chars max)
- Descriptions avec bullet points et critères d'acceptance
- Labels GitHub standards: bug, enhancement, documentation, good first issue, etc.
- Priority: high, medium, low
- Estimate: nombre de jours (1-5)
- Format JSON strict, pas de markdown autour
'''
        try:
            return self.generate_response(prompt)
        except Exception as e:
            raise RuntimeError(f"Erreur génération tickets: {e}")

    def get_status(self) -> str:
        """Retourne le statut des APIs disponibles"""
        status = []
        if self.gemini_available:
            status.append("✅ Gemini")
        if self.groq_available:
            status.append("✅ Groq")
        
        if not status:
            return "❌ Aucune IA disponible"
        
        return f"🤖 APIs: {', '.join(status)}"
