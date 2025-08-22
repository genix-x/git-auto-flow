#!/bin/bash
# Git Auto-Flow - Installation des alias et configuration

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_USER=$(whoami)

echo -e "${BLUE}🚀 Git Auto-Flow - Installation${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "📍 Répertoire d'installation: ${INSTALL_DIR}"
echo ""

# 1. Vérification des prérequis
echo -e "${BLUE}🔍 Vérification des prérequis...${NC}"

# Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 non trouvé${NC}"
    echo -e "${YELLOW}💡 Installez Python3 d'abord:${NC}"
    echo -e "   macOS: brew install python3"
    echo -e "   Ubuntu: sudo apt install python3 python3-pip"
    exit 1
fi
echo -e "${GREEN}✅ Python3 trouvé: $(python3 --version)${NC}"

# pip3
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 non trouvé${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip3 trouvé${NC}"

# Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git non trouvé${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Git trouvé: $(git --version)${NC}"

# GitHub CLI
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLI (gh) non trouvé${NC}"
    echo -e "${YELLOW}💡 Installation recommandée:${NC}"
    echo -e "   macOS: brew install gh"
    echo -e "   Ubuntu: sudo apt install gh"
    echo -e "   Ou: https://github.com/cli/cli/releases"
    echo ""
    read -p "Continuer sans GitHub CLI? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✅ GitHub CLI trouvé: $(gh --version | head -n1)${NC}"
fi

echo ""

# 2. Installation des dépendances Python
echo -e "${BLUE}📦 Installation des dépendances Python...${NC}"

if [ -f "${INSTALL_DIR}/requirements.txt" ]; then
    pip3 install -r "${INSTALL_DIR}/requirements.txt" --break-system-packages 2>/dev/null || pip3 install -r "${INSTALL_DIR}/requirements.txt"
    echo -e "${GREEN}✅ Dépendances Python installées${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt non trouvé, installation manuelle...${NC}"
    pip3 install google-generativeai python-dotenv groq --break-system-packages 2>/dev/null || pip3 install google-generativeai python-dotenv groq
fi

echo ""

# 3. Configuration des alias Git
echo -e "${BLUE}⚙️  Configuration des alias Git...${NC}"

# Sauvegarde de la configuration actuelle
if [ -f ~/.gitconfig ]; then
    cp ~/.gitconfig ~/.gitconfig.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅ Sauvegarde de ~/.gitconfig créée${NC}"
fi

# Ajout des alias Git Auto-Flow
cat >> ~/.gitconfig << EOF

# Git Auto-Flow - Aliases ajoutés automatiquement
[alias]
    # Automation avec IA
    cz-auto = "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-cz-auto-v2.py"
    pr-auto = "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-pr-auto.py"
    pr-create-auto = "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-pr-create-auto.py"
    
    # Aliases shell (si disponibles)
    cz-auto-sh = "!cd \$(git rev-parse --show-toplevel) && ${INSTALL_DIR}/bin/git-cz-auto.sh"
    pr-auto-sh = "!cd \$(git rev-parse --show-toplevel) && ${INSTALL_DIR}/bin/git-pr-auto.sh"
    pr-create-auto-sh = "!cd \$(git rev-parse --show-toplevel) && ${INSTALL_DIR}/bin/git-pr-create-auto.sh"

EOF

echo -e "${GREEN}✅ Alias Git Auto-Flow ajoutés à ~/.gitconfig${NC}"

# 4. Configuration des clés API
echo ""
echo -e "${BLUE}🔑 Configuration des clés API...${NC}"

# Création du fichier .env s'il n'existe pas
if [ ! -f "${INSTALL_DIR}/.env" ]; then
    touch "${INSTALL_DIR}/.env"
    echo "# Git Auto-Flow - Configuration des API" > "${INSTALL_DIR}/.env"
fi

echo -e "${YELLOW}💡 Configuration des clés API requises:${NC}"
echo ""
echo -e "${BLUE}1. Gemini API (Google AI Studio):${NC}"
echo -e "   🔗 https://makersuite.google.com/app/apikey"
echo -e "   Ajoutez: ${GREEN}GEMINI_API_KEY=votre_cle_gemini${NC}"
echo ""
echo -e "${BLUE}2. Groq API (Fallback gratuit):${NC}"
echo -e "   🔗 https://console.groq.com/keys"
echo -e "   Ajoutez: ${GREEN}GROQ_API_KEY=votre_cle_groq${NC}"
echo ""
echo -e "${BLUE}📝 Éditez le fichier de configuration:${NC}"
echo -e "   ${YELLOW}${INSTALL_DIR}/.env${NC}"

# 5. Test de l'installation
echo ""
echo -e "${BLUE}🧪 Test de l'installation...${NC}"

if git cz-auto --help >/dev/null 2>&1 || python3 "${INSTALL_DIR}/src/git-cz-auto-v2.py" --help >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Installation réussie!${NC}"
else
    echo -e "${YELLOW}⚠️  Test partiel - configurez les clés API${NC}"
fi

# 6. Instructions finales
echo ""
echo -e "${GREEN}🎉 Installation terminée!${NC}"
echo ""
echo -e "${BLUE}📋 Alias disponibles:${NC}"
echo -e "   ${GREEN}git cz-auto${NC}          # Commit automatique avec IA"
echo -e "   ${GREEN}git pr-auto${NC}          # PR automatique avec IA"
echo -e "   ${GREEN}git pr-create-auto${NC}   # Workflow complet: rebase + PR"
echo ""
echo -e "${BLUE}🔧 Configuration:${NC}"
echo -e "   1. Éditez: ${YELLOW}${INSTALL_DIR}/.env${NC}"
echo -e "   2. Ajoutez vos clés API (Gemini + Groq)"
echo -e "   3. Testez: ${GREEN}git cz-auto${NC} dans un repo Git"
echo ""
echo -e "${BLUE}📚 Documentation complète:${NC}"
echo -e "   ${YELLOW}${INSTALL_DIR}/README.md${NC}"
echo ""
echo -e "${GREEN}✨ Git Auto-Flow est prêt à l'emploi!${NC}"