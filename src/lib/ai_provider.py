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
        # Charge le fichier .env
        load_dotenv()
        
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
            env_path = os.path.join(os.path.dirname(__file__), '../../.env')
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
                "⚡ Ou relancez: ./install-alias.sh pour configuration interactive"
            )
    
    def _get_gemini_client(self):
        """Initialise le client Gemini si pas encore fait"""
        if not self.gemini_client and self.gemini_available:
            try:
                from .gemini_client import GeminiClient
                # On initialise avec une clé factice pour tester la structure
                # Le vrai GeminiClient gère sa propre clé API
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
                from .groq_client import GroqClient
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