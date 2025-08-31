"""
Module de logging centralisé pour les scripts git-auto-flow
Permet d'avoir un système de debug unifié et configurable
"""

import logging
import sys
from typing import List, Optional


class DebugLogger:
    """Logger centralisé avec support du mode debug pour les commandes shell"""
    
    def __init__(self, name: str = "git-auto-flow", debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.logger = logging.getLogger(name)
        
        if not self.logger.handlers:
            # Configuration du logger
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
        if debug_mode:
            self.logger.setLevel(logging.DEBUG)
            self.info("🐛 Mode DEBUG activé")
    
    def debug_command(self, command: List[str], description: str = ""):
        """Affiche une commande en mode debug"""
        if self.debug_mode:
            cmd_str = ' '.join(command)
            if description:
                self.logger.info(f"🐛 DEBUG ({description}): {cmd_str}")
            else:
                self.logger.info(f"🐛 DEBUG: Exécution de: {cmd_str}")
    
    def info(self, message: str):
        """Log d'information standard"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log d'avertissement"""
        self.logger.warning(f"⚠️  {message}")
    
    def error(self, message: str):
        """Log d'erreur"""
        self.logger.error(f"❌ {message}")
    
    def success(self, message: str):
        """Log de succès"""
        self.logger.info(f"✅ {message}")


# Instance globale partagée
_debug_logger: Optional[DebugLogger] = None


def get_debug_logger(name: str = "git-auto-flow", debug_mode: bool = False) -> DebugLogger:
    """Récupère ou crée l'instance du logger global"""
    global _debug_logger
    
    if _debug_logger is None:
        _debug_logger = DebugLogger(name, debug_mode)
    
    # Met à jour le mode debug si nécessaire
    if debug_mode != _debug_logger.debug_mode:
        _debug_logger.set_debug_mode(debug_mode)
    
    return _debug_logger


def debug_command(command: List[str], description: str = ""):
    """Fonction helper pour débugger une commande (utilise le logger global)"""
    global _debug_logger
    if _debug_logger is not None:
        _debug_logger.debug_command(command, description)


def set_global_debug_mode(debug_mode: bool):
    """Active le mode debug globalement"""
    logger = get_debug_logger(debug_mode=debug_mode)
    return logger