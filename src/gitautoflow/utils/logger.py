#!/usr/bin/env python3
"""
Git Auto-Flow - Système de logging centralisé
"""

import logging
from rich.console import Console
from rich.logging import RichHandler

# Console globale pour les messages
console = Console()

def setup_logger(name="gitautoflow", level=logging.INFO):
    """Configure le logger avec Rich"""
    
    # Création du logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Éviter les doublons de handlers
    if logger.handlers:
        return logger
    
    # Handler avec Rich pour les couleurs
    handler = RichHandler(
        console=console,
        show_time=False,
        show_path=False,
        markup=True
    )
    
    # Format des messages
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger

# Logger global
logger = setup_logger()

# Fonctions helper pour les messages avec emojis
def info(message):
    """Message d'information"""
    logger.info(f"[blue]{message}[/blue]")

def success(message):
    """Message de succès"""
    logger.info(f"[green]✅ {message}[/green]")

def error(message):
    """Message d'erreur"""
    logger.error(f"[red]❌ {message}[/red]")

def warning(message):
    """Message d'avertissement"""
    logger.warning(f"[yellow]⚠️ {message}[/yellow]")

def debug(message):
    """Message de debug"""
    logger.debug(f"[dim] {message}[/dim]")

def header(title, width=50):
    """Affiche un header stylé"""
    console.print(f"\n[bold blue] {title}[/bold blue]")
    console.print("=" * width)
