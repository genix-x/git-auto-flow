#!/usr/bin/env python3
import sys
import os

# Configuration des paths pour Nuitka (normal et onefile)
base_dir = os.path.dirname(__file__)

# Détection du mode onefile de Nuitka
if hasattr(sys, 'frozen') or '/tmp/onefile_' in __file__:
    # Mode onefile : les modules sont dans le répertoire d'exécution
    src_path = base_dir
    lib_path = base_dir
else:
    # Mode normal : structure de développement
    src_path = os.path.join(base_dir, "src")
    lib_path = os.path.join(base_dir, "src", "lib")

# Insérer les paths en premier
if src_path not in sys.path:
    sys.path.insert(0, src_path)
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

# Patch pour forcer les imports absolus dans lib
import importlib.util
original_import = __builtins__.__import__

def patched_import(name, globals=None, locals=None, fromlist=(), level=0):
    # Convertir les imports relatifs de lib uniquement
    if level > 0 and globals and '__file__' in globals:
        file_path = globals['__file__']
        # Si on est dans le module lib, convertir en absolu
        if 'src/lib/' in file_path or '/lib/' in file_path:
            if name and name in ['prompt_templates', 'debug_logger', 'gemini_client', 'groq_client', 'git_utils', 'ai_provider']:
                try:
                    return original_import(name, globals, locals, fromlist, 0)
                except ImportError:
                    pass
    return original_import(name, globals, locals, fromlist, level)

__builtins__.__import__ = patched_import

# Import principal du projet
from gitautoflow.cli.main import main

if __name__ == "__main__":
    main()

