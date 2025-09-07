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

echo -e "${BLUE}🚀 Git Auto-Flow - Installation Globale${NC}"
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

# Fonction d'installation intelligente
install_python_deps() {
    local packages="google-generativeai python-dotenv groq"
    
    # Méthode 1: pipx (recommandée pour les outils)
    if command -v pipx &> /dev/null; then
        echo -e "${GREEN}🔧 Utilisation de pipx (méthode recommandée)...${NC}"
        for package in $packages; do
            pipx install $package --quiet 2>/dev/null || true
        done
        return 0
    fi
    
    # Méthode 2: pip --user (sûre)
    if pip3 install --user $packages --quiet 2>/dev/null; then
        echo -e "${GREEN}✅ Installation --user réussie${NC}"
        return 0
    fi
    
    # Méthode 3: break-system-packages (derniers recours)
    if pip3 install --break-system-packages $packages --quiet 2>/dev/null; then
        echo -e "${YELLOW}⚡ Installation avec --break-system-packages${NC}"
        return 0
    fi
    
    # Méthode 4: requirements.txt si présent
    if [ -f "${INSTALL_DIR}/requirements.txt" ]; then
        if pip3 install --user -r "${INSTALL_DIR}/requirements.txt" --quiet 2>/dev/null; then
            echo -e "${GREEN}✅ Installation via requirements.txt réussie${NC}"
            return 0
        fi
    fi
    
    echo -e "${RED}❌ Impossible d'installer les dépendances Python${NC}"
    echo -e "${YELLOW}💡 Installation manuelle:${NC}"
    echo -e "   brew install pipx && pipx install google-generativeai python-dotenv groq"
    return 1
}

# Appel de la fonction
if install_python_deps; then
    echo -e "${GREEN}✅ Dépendances Python configurées${NC}"
else
    echo -e "${YELLOW}⚠️  Continuez avec installation manuelle si nécessaire${NC}"
fi

echo ""

# 3. Installation gitleaks pour sécurité
echo -e "${BLUE}📦 Installation gitleaks (sécurité)...${NC}"
if command -v brew &> /dev/null; then
    if ! command -v gitleaks &> /dev/null; then
        brew install gitleaks --quiet 2>/dev/null && echo -e "${GREEN}✅ gitleaks installé via brew${NC}" || echo -e "${YELLOW}⚠️  Installation gitleaks via brew échouée${NC}"
    else
        echo -e "${GREEN}✅ gitleaks déjà installé${NC}"
    fi
elif command -v curl &> /dev/null; then
    if [[ ! -f "${INSTALL_DIR}/bin/gitleaks" ]]; then
        echo "📥 Téléchargement gitleaks depuis GitHub..."
        GITLEAKS_VERSION="8.18.4"
        OS=$(uname -s | tr '[:upper:]' '[:lower:]')
        ARCH=$(uname -m)
        if [[ "$ARCH" == "x86_64" ]]; then ARCH="amd64"; fi
        if [[ "$ARCH" == "arm64" ]] && [[ "$OS" == "darwin" ]]; then ARCH="arm64"; fi
        
        curl -L "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_${OS}_${ARCH}.tar.gz" -o /tmp/gitleaks.tar.gz 2>/dev/null && {
            tar -xzf /tmp/gitleaks.tar.gz -C /tmp/ 2>/dev/null && {
                mkdir -p "${INSTALL_DIR}/bin"
                mv /tmp/gitleaks "${INSTALL_DIR}/bin/"
                chmod +x "${INSTALL_DIR}/bin/gitleaks"
                rm /tmp/gitleaks.tar.gz
                echo -e "${GREEN}✅ gitleaks installé dans ${INSTALL_DIR}/bin/${NC}"
            } || echo -e "${YELLOW}⚠️  Extraction gitleaks échouée${NC}"
        } || echo -e "${YELLOW}⚠️  Téléchargement gitleaks échoué${NC}"
    else
        echo -e "${GREEN}✅ gitleaks déjà installé dans ${INSTALL_DIR}/bin/${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  curl et brew non trouvés - gitleaks non installé${NC}"
fi
echo ""

# 4. Configuration des alias Git
echo -e "${BLUE}⚙️  Configuration des alias Git...${NC}"

# Sauvegarde de la configuration actuelle
if [ -f ~/.gitconfig ]; then
    cp ~/.gitconfig ~/.gitconfig.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅ Sauvegarde de ~/.gitconfig créée${NC}"
fi

# Configuration sécurisée des alias via git config
echo -e "${BLUE}🔧 Configuration des alias Git Auto-Flow...${NC}"

# WORKFLOW
git config --global alias.feature-start "!f() { echo '🚀 Feature: '\$1; echo '🧹 Nettoyage des branches mergées...'; git fetch --prune origin 2>/dev/null || true; git branch --merged main 2>/dev/null | grep 'feature/' | xargs -n 1 git branch -d 2>/dev/null || true; git branch --merged develop 2>/dev/null | grep 'feature/' | xargs -n 1 git branch -d 2>/dev/null || true; git branch -r --merged main 2>/dev/null | grep 'origin/feature/' | sed 's/origin\\///' | xargs -n 1 git push origin --delete 2>/dev/null || true; git branch -r --merged develop 2>/dev/null | grep 'origin/feature/' | sed 's/origin\\///' | xargs -n 1 git push origin --delete 2>/dev/null || true; git checkout develop 2>/dev/null || git checkout -b develop; git pull origin develop 2>/dev/null || true; git checkout -b feature/\$1 && git push -u origin feature/\$1 2>/dev/null || true; echo '✅ Feature créée: feature/'\$1; }; f"
git config --global alias.commit-auto "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-commit-auto.py"
git config --global alias.ca "!git commit-auto"
git config --global alias.pr "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-pr-auto.py"
git config --global alias.feature-finish "!f() { echo '🔄 Finalisation de la feature...'; git fetch origin develop && git rebase origin/develop && git push --force-with-lease origin \$(git branch --show-current) && echo '✅ Feature prête pour PR vers develop'; }; f"
git config --global alias.pr-create-auto "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-pr-create-auto.py"
git config --global alias.deploy "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-release-auto.py"
git config --global alias.cleanup-branches "!f() { echo '🧹 Nettoyage des branches locales...'; git fetch --prune origin; git branch --merged develop | grep -v 'develop\\|main\\|master' | xargs -n 1 git branch -d 2>/dev/null || true; git branch --merged main | grep -v 'develop\\|main\\|master' | xargs -n 1 git branch -d 2>/dev/null || true; echo '✅ Branches mergées supprimées'; }; f"

# PROJECT MANAGEMENT
git config --global alias.project-config "!cd \$(git rev-parse --show-toplevel 2>/dev/null || pwd) && python3 ${INSTALL_DIR}/src/git-project-config.py"
git config --global alias.pc "!git project-config"
git config --global alias.repo-create "!cd \$(git rev-parse --show-toplevel 2>/dev/null || pwd) && python3 ${INSTALL_DIR}/src/git-repo-create.py"
git config --global alias.create-tickets "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-create-tickets.py"

echo -e "${GREEN}✅ Alias Git Auto-Flow configurés proprement${NC}"

# 5. Installation semantic-release (conditionnelle)
if [ -f "package.json" ]; then
    if command -v npm &> /dev/null || command -v pnpm &> /dev/null || command -v yarn &> /dev/null; then
        echo ""
        echo -e "${BLUE}📦 Installation semantic-release (détecté package.json)...${NC}"
        
        if command -v pnpm &> /dev/null; then
            PACKAGE_MANAGER="pnpm"
        elif command -v yarn &> /dev/null; then
            PACKAGE_MANAGER="yarn"
        else
            PACKAGE_MANAGER="npm"
        fi
        
        echo -e "${YELLOW}📦 Utilisation de ${PACKAGE_MANAGER}...${NC}"
        
        if $PACKAGE_MANAGER install >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Dépendances Node.js installées${NC}"
        else
            echo -e "${YELLOW}⚠️  Installation des dépendances Node.js échouée${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  package.json trouvé, mais ni npm, pnpm ou yarn. Installation semantic-release ignorée.${NC}"
    fi
fi

# 6. Configuration interactive des clés API  
echo ""
echo -e "${BLUE}🔑 Configuration des clés API...${NC}"

GLOBAL_ENV_FILE="$HOME/.env.gitautoflow"
if [ -f "$GLOBAL_ENV_FILE" ]; then
    echo -e "${GREEN}✅ Configuration API trouvée: $GLOBAL_ENV_FILE${NC}"
else
    echo -e "${YELLOW}💡 Configurons vos clés API (optionnel):${NC}"
    echo ""
    echo -e "${BLUE}🤖 Gemini API (Google AI Studio):${NC}"
    echo -e "   🔗 ${YELLOW}https://makersuite.google.com/app/apikey${NC}"
    read -p "Entrez votre clé Gemini API (ou ENTER pour ignorer): " GEMINI_KEY
    echo ""
    echo -e "${BLUE}⚡ Groq API (Fallback gratuit):${NC}"
    echo -e "   🔗 ${YELLOW}https://console.groq.com/keys${NC}"
    read -p "Entrez votre clé Groq API (ou ENTER pour ignorer): " GROQ_KEY

    {
        echo "# Git Auto-Flow - Configuration des API"
        echo "# Généré automatiquement le $(date)"
        echo ""
        echo "GEMINI_API_KEY=${GEMINI_KEY}"
        echo "GROQ_API_KEY=${GROQ_KEY}"
    } > "$GLOBAL_ENV_FILE"

    echo -e "${GREEN}✅ Clés API configurées dans $GLOBAL_ENV_FILE${NC}"
    echo ""
fi

# 7. Instructions finales
echo ""
echo -e "${GREEN}🎉 Installation globale terminée!${NC}"

echo ""
echo -e "${YELLOW}Pour créer un nouveau projet GitHub complet :${NC}"
echo -e "   ${GREEN}git repo-create mon-projet${NC}     # Projet privé avec workflow complet"
echo -e "   ${GREEN}git repo-create api --public${NC}   # Projet public"
echo -e "   ${GREEN}git pc${NC}                        # (Re)lancer la configuration"

echo ""
echo -e "${YELLOW}Dans un repo existant :${NC}"
echo -e "   ${GREEN}git feature-start ma-feature${NC}  # Nouvelle feature"
echo -e "   ${GREEN}git ca${NC}                       # Commit IA"
echo -e "   ${GREEN}git pr${NC}                       # PR automatique"

echo ""
echo -e "${BLUE}📚 Documentation complète:${NC}"
echo -e "   ${YELLOW}${INSTALL_DIR}/README.md${NC}"

echo ""
echo -e "${GREEN}✨ Git Auto-Flow est prêt à l'emploi!${NC}"