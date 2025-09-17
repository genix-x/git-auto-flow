#!/bin/bash
# Git Auto-Flow - Installation des alias et configuration

# Variables pour mode non-interactif
NON_INTERACTIVE=false

# Parse des arguments
for arg in "$@"; do
    case $arg in
        --non-interactive|-f)
        NON_INTERACTIVE=true
        shift
        ;;
        *)
        # Argument inconnu
        ;;
    esac
done

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
echo "Usage: $0 [--non-interactive|-f]"
echo "  --non-interactive, -f    Installation automatique sans interaction"
echo -e "${BLUE}=================================${NC}"
echo -e "📍 Répertoire d'installation: ${INSTALL_DIR}"
echo ""

# 1. Vérification des prérequis
echo -e "${BLUE}�� Vérification des prérequis...${NC}"

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
    if [ "$NON_INTERACTIVE" = true ]; then
        echo -e "${YELLOW}🤖 Mode non-interactif, continuation sans GitHub CLI.${NC}"
    else
        read -p "Continuer sans GitHub CLI? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
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
    echo -e "${YELLOW}⚠️  Continuez avec installation manuelle des dépendances Python si nécessaire${NC}"
fi

echo ""

# 3. Installation gitleaks pour sécurité
echo -e "${BLUE}📦 Installation gitleaks (sécurité)...${NC}"

install_gitleaks() {
    if command -v gitleaks &> /dev/null; then
        echo -e "${GREEN}✅ gitleaks déjà installé${NC}"
        return 0
    fi

    # Essayer brew d'abord (macOS/Linux)
    if command -v brew &> /dev/null; then
        if brew install gitleaks --quiet 2>/dev/null; then
            echo -e "${GREEN}✅ gitleaks installé via brew${NC}"
            return 0
        fi
    fi

    # Installation manuelle via GitHub releases
    if command -v curl &> /dev/null; then
        echo "�� Téléchargement gitleaks depuis GitHub..."
        
        GITLEAKS_VERSION="8.18.4"
        OS=$(uname -s | tr '[:upper:]' '[:lower:]')
        ARCH=$(uname -m)
        
        # Normalisation de l'architecture
        case "$ARCH" in
            x86_64) ARCH="amd64" ;;
            aarch64) ARCH="arm64" ;;
            arm64) ARCH="arm64" ;;
        esac
        
        # URL de téléchargement
        GITLEAKS_URL="https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_${OS}_${ARCH}.tar.gz"
        
        echo "🔗 URL: $GITLEAKS_URL"
        
        # Créer le répertoire bin local
        mkdir -p "${INSTALL_DIR}/bin"
        
        # Téléchargement avec timeout et retry
        if curl -L --connect-timeout 10 --max-time 60 --retry 2 --fail \
                -o "/tmp/gitleaks.tar.gz" "$GITLEAKS_URL" 2>/dev/null; then
            
            # Extraction
            if tar -xzf /tmp/gitleaks.tar.gz -C /tmp/ 2>/dev/null; then
                # Installation locale
                if mv /tmp/gitleaks "${INSTALL_DIR}/bin/" 2>/dev/null; then
                    chmod +x "${INSTALL_DIR}/bin/gitleaks"
                    rm -f /tmp/gitleaks.tar.gz 2>/dev/null
                    echo -e "${GREEN}✅ gitleaks installé dans ${INSTALL_DIR}/bin/${NC}"
                    return 0
                else
                    echo -e "${YELLOW}⚠️  Impossible de déplacer gitleaks${NC}"
                fi
            else
                echo -e "${YELLOW}⚠️  Extraction gitleaks échouée${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  Téléchargement gitleaks échoué (timeout ou URL invalide)${NC}"
        fi
        
        # Nettoyage en cas d'échec
        rm -f /tmp/gitleaks.tar.gz /tmp/gitleaks 2>/dev/null
    fi
    
    echo -e "${YELLOW}⚠️  Installation gitleaks échouée - continuons sans (optionnel)${NC}"
    return 1
}

# Appel de la fonction (non bloquant)
install_gitleaks || true

echo ""

# 4. Installation semantic-release (Node.js)
if [ -f "${INSTALL_DIR}/package.json" ]; then
    echo -e "${BLUE}📦 Installation semantic-release (Node.js)...${NC}"
    
    if command -v pnpm &> /dev/null; then
        echo -e "${GREEN}🔧 Utilisation de pnpm...${NC}"
        if cd "${INSTALL_DIR}" && pnpm install --quiet 2>/dev/null; then
            echo -e "${GREEN}✅ Dépendances Node.js installées${NC}"
        else
            echo -e "${YELLOW}⚠️  Installation des dépendances Node.js échouée${NC}"
        fi
    elif command -v npm &> /dev/null; then
        echo -e "${GREEN}🔧 Utilisation de npm...${NC}"
        if cd "${INSTALL_DIR}" && npm install --silent 2>/dev/null; then
            echo -e "${GREEN}✅ Dépendances Node.js installées${NC}"
        else
            echo -e "${YELLOW}⚠️  Installation des dépendances Node.js échouée${NC}"
        fi
    elif command -v yarn &> /dev/null; then
        echo -e "${GREEN}🔧 Utilisation de yarn...${NC}"
        if cd "${INSTALL_DIR}" && yarn install --silent 2>/dev/null; then
            echo -e "${GREEN}✅ Dépendances Node.js installées${NC}"
        else
            echo -e "${YELLOW}⚠️  Installation des dépendances Node.js échouée${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  package.json trouvé, mais ni npm, pnpm ou yarn. Installation semantic-release ignorée.${NC}"
    fi
fi

# 5. Configuration des clés API
echo -e "${BLUE}�� Configuration des clés API...${NC}"

GLOBAL_ENV_FILE="$HOME/.env.gitautoflow"

# Priorité 1: Variables d'environnement
if [ -n "${GEMINI_API_KEY:-}" ] || [ -n "${GROQ_API_KEY:-}" ]; then
    echo -e "${YELLOW}✨ Variables d'environnement GEMINI_API_KEY/GROQ_API_KEY détectées.${NC}"
    echo -e "${GREEN}   Utilisation de ces clés pour configurer $GLOBAL_ENV_FILE...${NC}"
    
    {
        echo "# Git Auto-Flow - Configuration des API"
        echo "# Généré automatiquement le $(date)"
        echo "# Priorité donnée aux variables d'environnement lors de l'installation."
        echo ""
        echo "GEMINI_API_KEY=${GEMINI_API_KEY:-}"
        echo "GROQ_API_KEY=${GROQ_API_KEY:-}"
    } > "$GLOBAL_ENV_FILE"

    if [ -n "${GEMINI_API_KEY:-}" ]; then
        echo -e "${GREEN}✅ Clé Gemini API configurée depuis l'environnement.${NC}"
    fi
    if [ -n "${GROQ_API_KEY:-}" ]; then
        echo -e "${GREEN}✅ Clé Groq API configurée depuis l'environnement.${NC}"
    fi
    echo ""

# Priorité 2: Fichier de configuration existant
elif [ -f "$GLOBAL_ENV_FILE" ]; then
    echo -e "${GREEN}✅ Fichier de configuration API déjà existant: $GLOBAL_ENV_FILE${NC}"
    echo -e "${YELLOW}   (Les variables d'environnement GEMINI_API_KEY/GROQ_API_KEY peuvent surcharger ce fichier à l'exécution)${NC}"
    echo ""

# Priorité 3: Configuration interactive ou non-interactive
else
    if [ "$NON_INTERACTIVE" = true ]; then
        echo -e "${RED}❌ Erreur: Aucune clé API trouvée en mode non-interactif et pas de fichier de config existant.${NC}"
        echo -e "${YELLOW}💡 Définissez les variables d'environnement avant l'installation :${NC}"
        echo -e "   export GEMINI_API_KEY=\"votre_clé_gemini\""
        echo -e "   export GROQ_API_KEY=\"votre_clé_groq\""
        exit 1
    else
        # Mode interactif
        echo -e "${YELLOW}💡 Configurons vos clés API (optionnel):${NC}"
        echo ""
        echo -e "${BLUE}🤖 Gemini API (Google AI Studio):${NC}"
        echo -e "   🔗 ${YELLOW}https://makersuite.google.com/app/apikey${NC}"
        read -p "Entrez votre clé Gemini API (ou ENTER pour ignorer): " USER_GEMINI_KEY
        echo ""
        echo -e "${BLUE}⚡ Groq API (Fallback gratuit):${NC}"
        echo -e "   🔗 ${YELLOW}https://console.groq.com/keys${NC}"
        read -p "Entrez votre clé Groq API (ou ENTER pour ignorer): " USER_GROQ_KEY

        {
            echo "# Git Auto-Flow - Configuration des API"
            echo "# Généré automatiquement le $(date)"
            echo ""
            echo "GEMINI_API_KEY=${USER_GEMINI_KEY}"
            echo "GROQ_API_KEY=${USER_GROQ_KEY}"
        } > "$GLOBAL_ENV_FILE"

        echo -e "${GREEN}✅ Clés API configurées dans $GLOBAL_ENV_FILE${NC}"
        echo ""
    fi
fi

# 6. Installation des alias Git
echo -e "${BLUE}📝 Installation des alias Git...${NC}"

# Fonction pour installer un alias Git de manière sûre
install_git_alias() {
    local alias_name="$1"
    local alias_command="$2"
    
    # Vérifier si l'alias existe déjà
    if git config --global --get-regexp "alias\.${alias_name}" >/dev/null 2>&1; then
        echo -e "${YELLOW}   ⚠️  Alias 'git ${alias_name}' existe déjà${NC}"
        return 1
    else
        git config --global alias."${alias_name}" "${alias_command}"
        echo -e "${GREEN}   ✅ git ${alias_name}${NC}"
        return 0
    fi
}

# Installation des alias principaux
echo "Installation des alias Git Auto-Flow..."

install_git_alias "ca" "!python3 '${INSTALL_DIR}/scripts/commit_ai.py'"
install_git_alias "pr" "!python3 '${INSTALL_DIR}/scripts/create_pr.py'"
install_git_alias "pc" "!python3 '${INSTALL_DIR}/scripts/project_config.py'"
install_git_alias "feature-start" "!python3 '${INSTALL_DIR}/scripts/feature_start.py'"
install_git_alias "repo-create" "!python3 '${INSTALL_DIR}/scripts/repo_create.py'"

# Alias utilitaires
install_git_alias "acp" "!git add . && git ca && git push"
install_git_alias "sync" "!git fetch origin && git rebase origin/\$(git branch --show-current)"
install_git_alias "cleanup" "!git branch --merged | grep -v '\\*\\|main\\|master\\|develop' | xargs -n 1 git branch -d"

echo ""

# 7. Ajout du répertoire bin au PATH
echo -e "${BLUE}🔧 Configuration du PATH...${NC}"

# Détecter le shell et le fichier de configuration
SHELL_RC=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
fi

# Ajout au PATH si nécessaire
if [ -n "$SHELL_RC" ] && [ -f "$SHELL_RC" ]; then
    if ! grep -q "${INSTALL_DIR}/bin" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# Git Auto-Flow" >> "$SHELL_RC"
        echo "export PATH=\"${INSTALL_DIR}/bin:\$PATH\"" >> "$SHELL_RC"
        echo -e "${GREEN}✅ PATH configuré dans $SHELL_RC${NC}"
    else
        echo -e "${GREEN}✅ PATH déjà configuré${NC}"
    fi
    
    # Export temporaire pour la session actuelle
    export PATH="${INSTALL_DIR}/bin:$PATH"
else
    echo -e "${YELLOW}⚠️  Ajoutez manuellement au PATH: export PATH=\"${INSTALL_DIR}/bin:\$PATH\"${NC}"
fi

echo ""

# 8. Instructions finales
echo ""
echo -e "${GREEN}🎉 Installation globale terminée!${NC}"

echo ""
echo -e "${YELLOW}📋 Commandes disponibles:${NC}"
echo -e "${BLUE}Création de projets:${NC}"
echo -e "   ${GREEN}git repo-create mon-projet${NC}        # Projet privé avec workflow complet"
echo -e "   ${GREEN}git repo-create api --public${NC}      # Projet public"
echo -e "   ${GREEN}git pc${NC}                           # (Re)configurer le projet actuel"

echo ""
echo -e "${BLUE}Workflow quotidien:${NC}"
echo -e "   ${GREEN}git feature-start ma-feature${NC}     # Nouvelle feature"
echo -e "   ${GREEN}git ca${NC}                          # Commit avec message IA"
echo -e "   ${GREEN}git pr${NC}                          # Pull Request automatique"
echo -e "   ${GREEN}git acp${NC}                         # Add + Commit IA + Push"

echo ""
echo -e "${BLUE}Utilitaires:${NC}"
echo -e "   ${GREEN}git sync${NC}                        # Synchroniser avec origin"
echo -e "   ${GREEN}git cleanup${NC}                     # Nettoyer les branches mergées"

echo ""
echo -e "${BLUE}📚 Documentation complète:${NC}"
echo -e "   ${YELLOW}${INSTALL_DIR}/README.md${NC}"

echo ""
echo -e "${BLUE}🔄 Pour activer dans le shell actuel:${NC}"
echo -e "   ${GREEN}source ~/.zshrc${NC}     # ou source ~/.bashrc"

echo ""
echo -e "${GREEN}✨ Git Auto-Flow est prêt à l'emploi!${NC}"
