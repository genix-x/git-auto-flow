#!/usr/bin/env python3
"""
Utilitaires Git réutilisables pour l'automation
"""

import subprocess
import sys
from typing import Tuple


class GitUtils:
    """Utilitaires Git communs pour les scripts d'automation"""
    
    @staticmethod
    def get_staged_diff() -> str:
        """
        Récupère le git diff des fichiers stagés
        
        Returns:
            str: Le contenu du git diff --cached
        """
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de la récupération du diff stagé: {e}")
    
    @staticmethod
    def get_staged_files() -> str:
        """
        Récupère la liste des fichiers stagés
        
        Returns:
            str: La liste des noms de fichiers stagés (un par ligne)
        """
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de la récupération des fichiers stagés: {e}")
    
    @staticmethod
    def get_branch_diff(base_branch: str = "develop") -> str:
        """
        Récupère le git diff de la branche courante vs base_branch
        
        Args:
            base_branch: La branche de référence (par défaut: develop)
            
        Returns:
            str: Le contenu du git diff base_branch...HEAD
        """
        try:
            result = subprocess.run(
                ['git', 'diff', f'{base_branch}...HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de la récupération du diff de branche: {e}")
    
    @staticmethod
    def get_branch_files(base_branch: str = "develop") -> str:
        """
        Récupère la liste des fichiers modifiés dans la branche courante vs base_branch
        
        Args:
            base_branch: La branche de référence (par défaut: develop)
            
        Returns:
            str: La liste des noms de fichiers modifiés (un par ligne)
        """
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', f'{base_branch}...HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de la récupération des fichiers de branche: {e}")
    
    @staticmethod
    def get_current_branch() -> str:
        """
        Récupère le nom de la branche courante
        
        Returns:
            str: Le nom de la branche courante
        """
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de la récupération de la branche courante: {e}")
    
    @staticmethod
    def get_commit_messages(base_branch: str = "develop", limit: int = 10) -> list:
        """
        Récupère les messages de commit de la branche courante vs base_branch
        
        Args:
            base_branch: La branche de référence (par défaut: develop)
            limit: Nombre maximum de commits à récupérer
            
        Returns:
            list: Liste des messages de commit
        """
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', f'-{limit}', f'{base_branch}..HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            # Retourner une liste de commits, pas une string
            commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
            return [commit for commit in commits if commit.strip()]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de la récupération des commits: {e}")
    
    @staticmethod
    def has_staged_changes() -> bool:
        """
        Vérifie s'il y a des changements stagés
        
        Returns:
            bool: True s'il y a des changements stagés
        """
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def has_branch_changes(base_branch: str = "develop") -> bool:
        """
        Vérifie s'il y a des changements dans la branche courante vs base_branch
        
        Args:
            base_branch: La branche de référence (par défaut: develop)
            
        Returns:
            bool: True s'il y a des changements dans la branche
        """
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', f'{base_branch}...HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def is_git_repository() -> bool:
        """
        Vérifie si on est dans un repository Git
        
        Returns:
            bool: True si on est dans un repo Git
        """
        try:
            subprocess.run(['git', 'status'], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def rebase_on_target(target_branch: str = "develop") -> bool:
        """
        Effectue un rebase sur la branche cible
        
        Args:
            target_branch: La branche sur laquelle rebaser (par défaut: develop)
            
        Returns:
            bool: True si le rebase s'est bien passé
        """
        try:
            # Fetch les derniers changements
            subprocess.run(['git', 'fetch', 'origin', target_branch], 
                         capture_output=True, check=True)
            
            # Effectue le rebase
            subprocess.run(['git', 'rebase', f'origin/{target_branch}'], 
                         capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            # En cas de conflit, on arrête le rebase
            try:
                subprocess.run(['git', 'rebase', '--abort'], 
                             capture_output=True, check=False)
            except:
                pass
            raise RuntimeError(f"Conflit lors du rebase sur {target_branch}. Résolvez manuellement avec 'git rebase origin/{target_branch}'")
    
    @staticmethod
    def is_branch_up_to_date(base_branch: str = "develop") -> bool:
        """
        Vérifie si la branche courante est à jour avec base_branch
        
        Args:
            base_branch: La branche de référence (par défaut: develop)
            
        Returns:
            bool: True si la branche est à jour
        """
        try:
            # Fetch pour avoir les dernières infos
            subprocess.run(['git', 'fetch', 'origin', base_branch], 
                         capture_output=True, check=True)
            
            # Compare les refs
            result = subprocess.run(
                ['git', 'rev-list', '--count', f'HEAD..origin/{base_branch}'],
                capture_output=True, text=True, check=True
            )
            
            behind_count = int(result.stdout.strip())
            return behind_count == 0
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def push_current_branch(force_with_lease: bool = False) -> None:
        """
        Pousse la branche courante vers l'origine
        
        Args:
            force_with_lease: Utilise --force-with-lease pour un push sécurisé
        """
        try:
            current_branch = GitUtils.get_current_branch()
            cmd = ['git', 'push', 'origin', current_branch]
            
            if force_with_lease:
                cmd.append('--force-with-lease')
                
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors du push: {e}")