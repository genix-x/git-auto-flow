# 🔄 Guide de Renommage du Binaire

## Renommage Rapide (1 seul changement)

Pour renommer le binaire de `gitautoflow` vers `gaf`, modifiez **uniquement** cette ligne dans `pyproject.toml` :

```toml
[project.scripts]
# Changez juste cette ligne ⬇️
gaf = "gitautoflow.cli.main:main"
# ✂️ Supprimez ou commentez cette ligne
# gitautoflow = "gitautoflow.cli.main:main"
```

Puis synchronisez :
```bash
uv sync
gaf --help  # ✅ Fonctionne !
```

## Renommage Complet (Script automatisé)

Pour un renommage complet avec mise à jour des métadonnées :

```bash
# Renommer vers "gaf"
python scripts/rename-binary.py gaf

# Renommer vers "myapp" avec alias "ma"
python scripts/rename-binary.py myapp ma

# Synchroniser pour appliquer
uv sync
```

## Architecture Flexible

L'architecture a été conçue pour être facilement renommable :

```
src/gitautoflow/
├── __meta__.py          # ← Métadonnées centralisées
├── cli/
│   ├── main.py         # ← Point d'entrée unique
│   └── repos.py        # ← Commandes métier (inchangé)
└── utils/logger.py     # ← Utilitaires (inchangé)
```

### Fichiers concernés par le renommage :

1. **`pyproject.toml`** → Scripts binaires
2. **`src/gitautoflow/__meta__.py`** → Métadonnées (optionnel)

### Fichiers NON touchés :
- Structure des packages (`src/gitautoflow/`)
- Logique métier (`repos.py`, `logger.py`)
- Imports Python (restent identiques)

## Exemples de renommage

| Avant | Après | Commande |
|--------|--------|-----------|
| `gitautoflow` | `gaf` | `python scripts/rename-binary.py gaf` |
| `gitautoflow` | `devtools` | `python scripts/rename-binary.py devtools dt` |
| `gitautoflow` | `gh-flow` | `python scripts/rename-binary.py gh-flow ghf` |

## Avantages de cette architecture

✅ **Un seul changement** → `pyproject.toml`
✅ **Pas de refactoring** → Logique préservée
✅ **Script automatisé** → Renommage complet
✅ **Métadonnées centralisées** → Cohérence garantie