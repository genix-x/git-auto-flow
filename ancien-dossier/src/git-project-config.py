#!/usr/bin/env python3
"""
Configuration interactive pour la gestion de projets GitHub
Étend ~/.env.gitautoflow avec les paramètres projet
"""

import sys
import os
import subprocess
from pathlib import Path

# Ajout du dossier lib au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from debug_logger import debug_command, set_global_debug_mode


def get_env_file_path() -> Path:
    """Retourne le chemin vers le fichier de configuration"""
    return Path.home() / '.env.gitautoflow'


def load_current_config() -> dict:
    """Charge la configuration actuelle depuis ~/.env.gitautoflow"""
    env_file = get_env_file_path()
    config = {}
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()

    # Ajout du répertoire de travail par défaut
    if 'WORKING_DIR' not in config:
        config['WORKING_DIR'] = os.environ.get('GIT_WORKING_DIR', os.path.expanduser('~/workspace'))
    
    return config


def save_config(config: dict) -> None:
    """Sauvegarde la configuration dans ~/.env.gitautoflow"""
    env_file = get_env_file_path()
    
    # Garde l'en-tête existant si présent
    header_lines = []
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('#') or line.strip() == '':
                    header_lines.append(line)
                else:
                    break  # Arrête dès qu'on trouve une vraie config
    
    # Écrit la nouvelle configuration
    with open(env_file, 'w') as f:
        # Garde l'en-tête existant
        for line in header_lines:
            f.write(line)
        
        # Ajoute séparateur si pas déjà présent
        if header_lines and not any('PROJET' in line for line in header_lines):
            f.write('\n# Configuration projets GitHub\n')
        
        # Écrit toutes les variables
        for key, value in config.items():
            f.write(f'{key}={value}\n')
    
    print(f"✅ Configuration sauvegardée dans {env_file}")


def get_default_working_dir() -> str:
    """Détermine le répertoire de travail par défaut"""
    # Essaie de deviner depuis l'environnement
    possible_dirs = [
        os.path.expanduser("~/projects"),
        os.path.expanduser("~/project"), 
        os.path.expanduser("~/dev"),
        os.path.expanduser("~/Development"),
        os.getcwd()
    ]
    
    for dir_path in possible_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            return dir_path
    
    return os.path.expanduser("~/projects")


def get_github_username() -> str:
    """Essaie de deviner le nom d'utilisateur GitHub"""
    try:
        # Via git config
        result = subprocess.run(['git', 'config', '--global', 'user.name'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    # Via gh CLI
    try:
        result = subprocess.run(['gh', 'api', 'user', '--jq', '.login'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return "your-username"


def interactive_config() -> dict:
    """Configuration interactive"""
    print("🔧 Configuration Git Auto-Flow - Gestion de Projets")
    print("=" * 50)
    
    current_config = load_current_config()
    
    # GitHub Organization/Username
    default_org = current_config.get('GITHUB_ORG', get_github_username())
    github_org = input(f"📂 GitHub Organisation/Username [{default_org}]: ").strip() or default_org
    
    # Working Directory  
    default_workdir = current_config.get('WORKING_DIR', get_default_working_dir())
    working_dir = input(f"💾 Répertoire de travail [{default_workdir}]: ").strip() or default_workdir
    working_dir = os.path.expanduser(working_dir)
    
    # Validation du répertoire
    if not os.path.exists(working_dir):
        create = input(f"📁 Le répertoire {working_dir} n'existe pas. Le créer ? (y/N): ").strip().lower()
        if create in ['y', 'yes', 'o', 'oui']:
            os.makedirs(working_dir, exist_ok=True)
            print(f"✅ Répertoire créé: {working_dir}")
        else:
            print("⚠️  Répertoire non créé - peut causer des erreurs")
    
    # GitHub Base URL
    default_base_url = current_config.get('GITHUB_BASE_URL', f'https://github.com/{github_org}/')
    github_base_url = input(f"🔗 GitHub Base URL [{default_base_url}]: ").strip() or default_base_url
    
    # S'assure que l'URL finit par /
    if not github_base_url.endswith('/'):
        github_base_url += '/'
    
    # Template par défaut  
    default_template = current_config.get('DEFAULT_PROJECT_TEMPLATE', 'web-app')
    project_template = input(f"🎨 Template projet par défaut [{default_template}]: ").strip() or default_template
    
    # Prépare la configuration finale
    config = current_config.copy()  # Garde les clés API existantes
    config.update({
        'GITHUB_ORG': github_org,
        'WORKING_DIR': working_dir,
        'GITHUB_BASE_URL': github_base_url,
        'DEFAULT_PROJECT_TEMPLATE': project_template
    })
    
    return config


def show_current_config() -> None:
    """Affiche la configuration actuelle"""
    config = load_current_config()
    
    print("📋 Configuration actuelle:")
    print("-" * 30)
    
    project_keys = ['GITHUB_ORG', 'WORKING_DIR', 'GITHUB_BASE_URL', 'DEFAULT_PROJECT_TEMPLATE']
    api_keys = ['GEMINI_API_KEY', 'GROQ_API_KEY']
    
    print("🎯 Projets:")
    for key in project_keys:
        value = config.get(key, '❌ Non configuré')
        if key == 'WORKING_DIR' and value != '❌ Non configuré':
            exists = "✅" if os.path.exists(value) else "❌"
            print(f"  {key}: {value} {exists}")
        else:
            print(f"  {key}: {value}")
    
    print("\n🤖 APIs:")
    for key in api_keys:
        value = config.get(key)
        if value:
            masked = value[:8] + '...' if len(value) > 8 else value
            print(f"  {key}: {masked} ✅")
        else:
            print(f"  {key}: ❌ Non configuré")


def check_prerequisites() -> bool:
    """Vérifie les prérequis système"""
    print("🔍 Vérification des prérequis...")
    
    required_commands = ['git', 'gh']
    missing = []
    
    for cmd in required_commands:
        try:
            result = subprocess.run(['which', cmd], capture_output=True, check=False)
            if result.returncode == 0:
                print(f"  ✅ {cmd}")
            else:
                print(f"  ❌ {cmd} manquant")
                missing.append(cmd)
        except:
            print(f"  ❌ {cmd} manquant") 
            missing.append(cmd)
    
    if missing:
        print(f"\n❌ Commandes manquantes: {', '.join(missing)}")
        print("💡 Installez-les avec:")
        if 'gh' in missing:
            print("   brew install gh  # ou apt install gh")
        return False
    
    # Vérifie l'authentification GitHub CLI
    try:
        result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, check=False)
        if result.returncode == 0:
            print("  ✅ GitHub CLI authentifié")
        else:
            print("  ⚠️  GitHub CLI non authentifié")
            print("💡 Lancez: gh auth login")
            return False
    except:
        print("  ❌ Erreur vérification GitHub CLI")
        return False
    
    return True


def main():
    """Fonction principale"""
    debug_mode = '--debug' in sys.argv
    if debug_mode:
        sys.argv.remove('--debug')
    
    set_global_debug_mode(debug_mode)
    
    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Usage: git project-config [--show] [--debug]")
            print("\nOptions:")
            print("  --show    Affiche la configuration actuelle")
            print("  --debug   Mode debug")
            return
        elif sys.argv[1] == '--show':
            show_current_config()
            return
    
    # Vérification des prérequis
    if not check_prerequisites():
        print("\n❌ Prérequis non satisfaits")
        sys.exit(1)
    
    # Configuration interactive
    try:
        config = interactive_config()
        
        # Affiche résumé
        print("\n📋 Résumé de la configuration:")
        print(f"  📂 Organisation: {config['GITHUB_ORG']}")
        print(f"  💾 Répertoire: {config['WORKING_DIR']}")
        print(f"  🔗 Base URL: {config['GITHUB_BASE_URL']}")
        print(f"  🎨 Template: {config['DEFAULT_PROJECT_TEMPLATE']}")
        
        # Confirmation
        confirm = input("\n✅ Sauvegarder cette configuration ? (y/N): ").strip().lower()
        if confirm in ['y', 'yes', 'o', 'oui']:
            save_config(config)
            print("\n🎉 Configuration terminée !")
            print("💡 Vous pouvez maintenant utiliser:")
            print("   git repo-create <nom-projet>")
            print("   git project-create <nom-projet>")
        else:
            print("❌ Configuration annulée")
            
    except KeyboardInterrupt:
        print("\n❌ Configuration annulée")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        if debug_mode:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
