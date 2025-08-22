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
    # 🚀 WORKFLOW PRINCIPAL avec IA
    feature-start = "!f() { \
        echo '🚀 Démarrage feature: '\$1; \
        git checkout develop && \
        git pull origin develop && \
        git checkout -b feature/\$1 && \
        git push -u origin feature/\$1 && \
        echo '✅ Feature branch créée: feature/'\$1; \
    }; f"
    
    # Commit avec rebase + IA (remplace commit-safe)
    commit-auto = "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-commit-auto.py"
    
    # Alias courts 
    ca = "!git commit-auto"
    
    # Finaliser feature (avant PR)  
    feature-finish = "!f() { \
        echo '🔄 Finalisation de la feature...'; \
        git fetch origin develop && \
        git rebase origin/develop && \
        git push --force-with-lease origin \$(git branch --show-current) && \
        echo '✅ Feature prête pour PR vers develop'; \
    }; f"
    
    # PR automation
    pr-create-auto = "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-pr-create-auto.py"

EOF

echo -e "${GREEN}✅ Alias Git Auto-Flow ajoutés à ~/.gitconfig${NC}"

# 4. Configuration du repository Git Flow
echo ""
echo -e "${BLUE}🌿 Configuration Git Flow (develop/main)...${NC}"

# Vérifier qu'on est dans un repo Git
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo -e "${RED}❌ Pas dans un repository Git${NC}"
    echo -e "${YELLOW}💡 Lancez cette commande depuis un repo Git${NC}"
    exit 1
fi

# Créer branche develop si elle n'existe pas
if ! git show-ref --verify --quiet refs/heads/develop; then
    echo -e "${YELLOW}📝 Création de la branche develop...${NC}"
    
    # S'assurer qu'on est sur main
    if git show-ref --verify --quiet refs/heads/main; then
        git checkout main >/dev/null 2>&1 || true
        git pull origin main >/dev/null 2>&1 || echo -e "${YELLOW}⚠️  Pull main ignoré (pas de remote ou conflit)${NC}"
    fi
    
    # Créer develop depuis main (ou HEAD si main n'existe pas)
    git checkout -b develop >/dev/null 2>&1
    echo -e "${GREEN}✅ Branche develop créée localement${NC}"
    
    # Push develop vers origin si possible
    if git remote get-url origin >/dev/null 2>&1; then
        if git push -u origin develop >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Branche develop pushée vers origin${NC}"
        else
            echo -e "${YELLOW}⚠️  Push develop échoué (configurez origin d'abord)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Pas de remote origin configuré${NC}"
    fi
else
    echo -e "${GREEN}✅ Branche develop existe déjà${NC}"
fi

# Configurer branch protection via GitHub CLI si disponible
if command -v gh &> /dev/null; then
    echo -e "${BLUE}🛡️  Configuration protection develop...${NC}"
    
    # Vérifier qu'on est connecté à GitHub
    if gh auth status >/dev/null 2>&1; then
        # Protection develop (require PR + up-to-date)
        gh api repos/:owner/:repo/branches/develop/protection \
          --method PUT \
          --field required_status_checks='{"strict":true,"contexts":[]}' \
          --field enforce_admins=true \
          --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
          --field restrictions=null \
          >/dev/null 2>&1 && echo -e "${GREEN}✅ Protection develop activée${NC}" || echo -e "${YELLOW}⚠️  Protection develop échouée (permissions?)${NC}"
        
        # Protection main (require PR + up-to-date)  
        if git show-ref --verify --quiet refs/heads/main; then
            gh api repos/:owner/:repo/branches/main/protection \
              --method PUT \
              --field required_status_checks='{"strict":true,"contexts":[]}' \
              --field enforce_admins=true \
              --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
              --field restrictions=null \
              >/dev/null 2>&1 && echo -e "${GREEN}✅ Protection main activée${NC}" || echo -e "${YELLOW}⚠️  Protection main échouée${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  GitHub CLI non connecté - lancez: gh auth login${NC}"
        echo -e "${YELLOW}💡 Protection manuelle requise sur GitHub.com${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  GitHub CLI non trouvé - protection manuelle requise${NC}"
fi

# Revenir sur develop pour setup
git checkout develop >/dev/null 2>&1 || true

# 5. Installation semantic-release (si Node.js disponible)
if command -v npm &> /dev/null || command -v pnpm &> /dev/null || command -v yarn &> /dev/null; then
    echo ""
    echo -e "${BLUE}📦 Installation semantic-release...${NC}"
    
    # Utiliser pnpm si disponible, sinon npm
    if command -v pnpm &> /dev/null; then
        PACKAGE_MANAGER="pnpm"
    elif command -v yarn &> /dev/null; then
        PACKAGE_MANAGER="yarn"
    else
        PACKAGE_MANAGER="npm"
    fi
    
    echo -e "${YELLOW}📦 Utilisation de ${PACKAGE_MANAGER}...${NC}"
    
    # Installation des dépendances semantic-release
    if $PACKAGE_MANAGER install >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Semantic-release installé${NC}"
        echo -e "${YELLOW}💡 Releases automatiques activées sur push vers main${NC}"
    else
        echo -e "${YELLOW}⚠️  Installation semantic-release échouée${NC}"
        echo -e "${YELLOW}💡 Les releases devront être créées manuellement${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Node.js non trouvé - semantic-release désactivé${NC}"
    echo -e "${YELLOW}💡 Installez Node.js pour les releases automatiques${NC}"
fi

# 6. Configuration interactive des clés API  
echo ""
echo -e "${BLUE}🔑 Configuration des clés API...${NC}"

# Création du fichier .env s'il n'existe pas
if [ ! -f "${INSTALL_DIR}/.env" ]; then
    touch "${INSTALL_DIR}/.env"
    echo "# Git Auto-Flow - Configuration des API" > "${INSTALL_DIR}/.env"
fi

# Configuration interactive
echo -e "${YELLOW}💡 Configurons vos clés API (optionnel):${NC}"
echo ""

# Gemini API
echo -e "${BLUE}🤖 Gemini API (Google AI Studio):${NC}"
echo -e "   🔗 ${YELLOW}https://makersuite.google.com/app/apikey${NC}"
read -p "Entrez votre clé Gemini API (ou ENTER pour ignorer): " GEMINI_KEY

# Groq API  
echo ""
echo -e "${BLUE}⚡ Groq API (Fallback gratuit):${NC}"
echo -e "   🔗 ${YELLOW}https://console.groq.com/keys${NC}"
read -p "Entrez votre clé Groq API (ou ENTER pour ignorer): " GROQ_KEY

# Écriture dans .env
{
    echo "# Git Auto-Flow - Configuration des API"
    echo "# Généré automatiquement le $(date)"
    echo ""
    if [ ! -z "$GEMINI_KEY" ]; then
        echo "GEMINI_API_KEY=${GEMINI_KEY}"
    else
        echo "# GEMINI_API_KEY=votre_cle_gemini"
        echo "# Obtenez votre clé: https://makersuite.google.com/app/apikey"
    fi
    echo ""
    if [ ! -z "$GROQ_KEY" ]; then
        echo "GROQ_API_KEY=${GROQ_KEY}"  
    else
        echo "# GROQ_API_KEY=votre_cle_groq"
        echo "# Obtenez votre clé: https://console.groq.com/keys"
    fi
} > "${INSTALL_DIR}/.env"

if [ ! -z "$GEMINI_KEY" ] || [ ! -z "$GROQ_KEY" ]; then
    echo -e "${GREEN}✅ Clés API configurées${NC}"
else
    echo -e "${YELLOW}⚠️  Aucune clé API configurée${NC}"
    echo -e "${YELLOW}💡 Les scripts afficheront des messages d'erreur appropriés${NC}"
fi

# 7. Test de l'installation
echo ""
echo -e "${BLUE}🧪 Test de l'installation...${NC}"

if git cz-auto --help >/dev/null 2>&1 || python3 "${INSTALL_DIR}/src/git-cz-auto-v2.py" --help >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Installation réussie!${NC}"
else
    echo -e "${YELLOW}⚠️  Test partiel - configurez les clés API${NC}"
fi

# 8. Instructions finales
echo ""
echo -e "${GREEN}🎉 Installation terminée!${NC}"
echo ""
echo -e "${BLUE}📋 Git Flow complet configuré:${NC}"
echo -e "   ${GREEN}🌿 develop${NC} (intégration) ← ${GREEN}🚀 feature/*${NC}"
echo -e "   ${GREEN}🎯 main${NC} (production) ← ${GREEN}🌿 develop${NC} (release)"
echo ""
echo -e "${BLUE}📋 Workflow disponible:${NC}"
echo -e "   1️⃣  ${GREEN}git feature-start <nom>${NC}     # Nouvelle feature depuis develop"
echo -e "   2️⃣  ${GREEN}git commit-auto${NC} (ou ${GREEN}git ca${NC})   # Commit + rebase automatique"  
echo -e "   3️⃣  ${GREEN}git feature-finish${NC}           # Finaliser feature"
echo -e "   4️⃣  ${GREEN}git pr-create-auto${NC}           # PR feature→develop"
echo -e "   5️⃣  Merge PR → ${GREEN}develop${NC}"
echo -e "   6️⃣  ${GREEN}gh pr create --base main --head develop${NC} # Release vers main"
echo -e "   7️⃣  Merge → ${GREEN}main${NC} = 🚀 Tag + Release automatique !"
echo ""
echo -e "${BLUE}🔧 Configuration:${NC}"
echo -e "   1. Éditez: ${YELLOW}${INSTALL_DIR}/.env${NC}"
echo -e "   2. Ajoutez vos clés API (Gemini + Groq)"
echo -e "   3. Testez: ${GREEN}git commit-auto${NC} dans un repo Git"
echo ""
echo -e "${BLUE}📚 Documentation complète:${NC}"
echo -e "   ${YELLOW}${INSTALL_DIR}/README.md${NC}"
echo ""
echo -e "${GREEN}✨ Git Auto-Flow est prêt à l'emploi!${NC}"