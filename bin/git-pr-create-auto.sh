#!/bin/bash
# git-pr-create-auto.sh - Workflow complet: feature-finish + PR auto avec Gemini

set -e

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}🚀 Git PR Create Auto - Workflow Complet${NC}"
echo -e "${BLUE}==============================================${NC}"

# Charge le fichier .env si il existe
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo -e "${GREEN}✅ Configuration chargée depuis .env${NC}"
fi

# Charge la clé API si elle existe dans un fichier
if [ -f ~/.gemini_api_key ]; then
    export GEMINI_API_KEY=$(cat ~/.gemini_api_key)
    echo -e "${GREEN}✅ Clé API Gemini chargée depuis ~/.gemini_api_key${NC}"
fi

# Vérifie que la clé API est disponible
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}❌ GEMINI_API_KEY non trouvée${NC}"
    echo -e "${YELLOW}💡 Solutions:${NC}"
    echo -e "   1. ${YELLOW}Ajouter GEMINI_API_KEY=ta_cle dans .env${NC}"
    echo -e "   2. ${YELLOW}export GEMINI_API_KEY='ta_cle_ici'${NC}"
    echo -e "   3. ${YELLOW}echo 'ta_cle_ici' > ~/.gemini_api_key${NC}"
    echo ""
    echo -e "${BLUE}🔗 Obtenir une clé API: https://makersuite.google.com/app/apikey${NC}"
    exit 1
fi

# Vérifie les dépendances Python
echo -e "${BLUE}🔍 Vérification des dépendances...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 non trouvé${NC}"
    exit 1
fi

# Vérifie que GitHub CLI est installé
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) non trouvé${NC}"
    echo -e "${YELLOW}💡 Installation:${NC}"
    echo -e "   macOS: ${YELLOW}brew install gh${NC}"
    echo -e "   Ubuntu: ${YELLOW}sudo apt install gh${NC}"
    exit 1
fi

# Trouve le script Python
SCRIPT_DIR="$(dirname "$0")"
PYTHON_SCRIPT="$SCRIPT_DIR/git-pr-create-auto.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}❌ Script Python non trouvé: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# Execute le script Python
echo -e "${GREEN}🚀 Lancement du workflow complet...${NC}"
echo ""
python3 "$PYTHON_SCRIPT" "$@"