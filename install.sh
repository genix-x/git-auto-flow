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

# Vérifier et supprimer les anciens alias Git Auto-Flow s'ils existent
if grep -q "# Git Auto-Flow" ~/.gitconfig 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Suppression des anciens alias Git Auto-Flow...${NC}"
    # Créer une copie temporaire sans les alias Git Auto-Flow
    grep -v "# Git Auto-Flow" ~/.gitconfig > ~/.gitconfig.tmp 2>/dev/null || touch ~/.gitconfig.tmp
    # Supprimer aussi les lignes entre "# Git Auto-Flow" et la prochaine section
    sed '/# Git Auto-Flow/,/^$/d' ~/.gitconfig > ~/.gitconfig.tmp 2>/dev/null || touch ~/.gitconfig.tmp
    mv ~/.gitconfig.tmp ~/.gitconfig
    echo -e "${GREEN}✅ Anciens alias supprimés${NC}"
fi

# Configuration sécurisée des alias via git config
echo -e "${BLUE}🔧 Configuration des alias Git Auto-Flow...${NC}"

# 🚀 WORKFLOW PRINCIPAL avec IA
git config --global alias.feature-start "!f() { 
    echo '🚀 Feature: '\$1; 
    echo '🧹 Nettoyage des branches mergées...'; 
    git fetch --prune origin 2>/dev/null || true; 
    git branch --merged main 2>/dev/null | grep 'feature/' | xargs -n 1 git branch -d 2>/dev/null || true; 
    git branch --merged develop 2>/dev/null | grep 'feature/' | xargs -n 1 git branch -d 2>/dev/null || true; 
    git branch -r --merged main 2>/dev/null | grep 'origin/feature/' | sed 's/origin\\///' | xargs -n 1 git push origin --delete 2>/dev/null || true; 
    git branch -r --merged develop 2>/dev/null | grep 'origin/feature/' | sed 's/origin\\///' | xargs -n 1 git push origin --delete 2>/dev/null || true; 
    git checkout develop 2>/dev/null || git checkout -b develop; 
    git pull origin develop 2>/dev/null || true; 
    git checkout -b feature/\$1 && 
    git push -u origin feature/\$1 2>/dev/null || true; 
    echo '✅ Feature créée: feature/'\$1; 
}; f"

# Commit avec rebase + IA
git config --global alias.commit-auto "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-commit-auto.py"

# Alias courts
git config --global alias.ca "!git commit-auto"
git config --global alias.pr "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-pr-auto.py"

# Finaliser feature (avant PR)
git config --global alias.feature-finish "!f() { echo '🔄 Finalisation de la feature...'; git fetch origin develop && git rebase origin/develop && git push --force-with-lease origin \$(git branch --show-current) && echo '✅ Feature prête pour PR vers develop'; }; f"

# PR automation
git config --global alias.pr-create-auto "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-pr-create-auto.py"

# Deploy automation
git config --global alias.deploy "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-release-auto.py"

# Nettoyage des branches
git config --global alias.cleanup-branches "!f() { echo '🧹 Nettoyage des branches locales...'; git fetch --prune origin; git branch --merged develop | grep -v 'develop\\|main\\|master' | xargs -n 1 git branch -d 2>/dev/null || true; git branch --merged main | grep -v 'develop\\|main\\|master' | xargs -n 1 git branch -d 2>/dev/null || true; echo '✅ Branches mergées supprimées'; }; f"


echo "📋 Configuration des alias pour la gestion de projets..."

# ═════════════════════════════════════════════════════════════════
# 🎯 GESTION DE PROJETS GITHUB  
# ═════════════════════════════════════════════════════════════════

# Configuration projets
git config --global alias.project-config "!cd \$(git rev-parse --show-toplevel 2>/dev/null || pwd) && python3 ${INSTALL_DIR}/src/git-project-config.py"
git config --global alias.pc "!git project-config"  # Alias court


echo -e "${GREEN}✅ Alias Git Auto-Flow configurés proprement${NC}"

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
        
        # Configuration auto-suppression des branches après merge
        gh api repos/:owner/:repo \
          --method PATCH \
          --field delete_branch_on_merge=true \
          >/dev/null 2>&1 && echo -e "${GREEN}✅ Auto-suppression branches activée${NC}" || echo -e "${YELLOW}⚠️  Auto-suppression échouée${NC}"
        
        # Création du label 'release' pour les PRs de release
        echo -e "${YELLOW}🏷️  Création du label 'release'...${NC}"
        gh label create release --color "0052CC" --description "Release PR develop->main" \
          >/dev/null 2>&1 && echo -e "${GREEN}✅ Label 'release' créé${NC}" || echo -e "${YELLOW}⚠️  Label 'release' existe déjà ou erreur${NC}"
    else
        echo -e "${YELLOW}⚠️  GitHub CLI non connecté - lancez: gh auth login${NC}"
        echo -e "${YELLOW}💡 Protection manuelle requise sur GitHub.com${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  GitHub CLI non trouvé - protection manuelle requise${NC}"
fi

# Revenir sur develop pour setup
git checkout develop >/dev/null 2>&1 || true

# Créer tag initial v0.0.0 pour semantic-release (si pas déjà créé)
if ! git tag -l | grep -q "^v0\.0\.0$"; then
    echo -e "${YELLOW}🏷️  Création du tag initial v0.0.0 pour versioning...${NC}"
    if git tag v0.0.0 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Tag v0.0.0 créé localement${NC}"
        
        # Push le tag vers origin si possible
        if git remote get-url origin >/dev/null 2>&1; then
            if git push origin v0.0.0 >/dev/null 2>&1; then
                echo -e "${GREEN}✅ Tag v0.0.0 pushé vers origin${NC}"
                echo -e "${YELLOW}💡 Semantic-release démarrera à v0.1.0${NC}"
            else
                echo -e "${YELLOW}⚠️  Push tag échoué - pushez manuellement: git push origin v0.0.0${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  Tag créé localement uniquement${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Création du tag échouée${NC}"
    fi
else
    echo -e "${GREEN}✅ Tag v0.0.0 existe déjà${NC}"
fi

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

# Vérifier si le fichier global existe déjà
GLOBAL_ENV_FILE="$HOME/.env.gitautoflow"
if [ -f "$GLOBAL_ENV_FILE" ]; then
    echo -e "${GREEN}✅ Configuration API trouvée: $GLOBAL_ENV_FILE${NC}"
    echo -e "${YELLOW}💡 Clés API déjà configurées - installation continue...${NC}"
    echo ""
else
    # Configuration interactive seulement si le fichier n'existe pas
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

    # Écriture dans le fichier global
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


# Vérification finale de la configuration
if [ -f "$GLOBAL_ENV_FILE" ]; then
    # Vérifier si au moins une clé est configurée dans le fichier
    if grep -q "GEMINI_API_KEY=.\+" "$GLOBAL_ENV_FILE" || grep -q "GROQ_API_KEY=.\+" "$GLOBAL_ENV_FILE"; then
        echo -e "${GREEN}✅ Clés API configurées${NC}"
    else
        echo -e "${YELLOW}⚠️  Fichier .env.gitautoflow existe mais aucune clé valide trouvée${NC}"
    fi
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
echo -e "${BLUE}🚀 WORKFLOW COMPLET - Git Auto-Flow:${NC}"
echo ""
echo -e "${YELLOW}📋 Développement d'une feature:${NC}"
echo -e "   1️⃣  ${GREEN}git feature-start ma-feature${NC}  # Crée feature/ma-feature depuis develop"
echo -e "   2️⃣  ${GREEN}git commit-auto${NC} (ou ${GREEN}git ca${NC})    # Commit avec IA + rebase auto"  
echo -e "   3️⃣  ${GREEN}git feature-finish${NC}            # Finalise feature (rebase + push)"
echo -e "   4️⃣  ${GREEN}git pr-create-auto${NC}            # Crée PR avec analyse IA complète"
echo ""
echo -e "${YELLOW}📋 Gestion des releases:${NC}"
echo -e "   5️⃣  Merge PR → ${GREEN}develop${NC}         # (branche auto-supprimée)"
echo -e "   6️⃣  ${GREEN}git deploy${NC}                  # 🚀 Deploy AUTO: develop→main + auto-merge"
echo -e "   7️⃣  Auto-merge → ${GREEN}main${NC} = 🏷️ ${YELLOW}v0.1.0 Tag + Release automatique !${NC}"
echo ""
echo -e "${YELLOW}🧹 Maintenance:${NC}"
echo -e "   🔧  ${GREEN}git cleanup-branches${NC}          # Nettoie branches locales mergées"
echo ""
echo -e "${YELLOW}🤖 APIs supportées:${NC}"
if [ ! -z "$GEMINI_KEY" ]; then
    echo -e "   ✅  ${GREEN}Gemini${NC} (Google AI) - Configuré"
else
    echo -e "   ⚠️   ${YELLOW}Gemini${NC} (Google AI) - À configurer"
fi
if [ ! -z "$GROQ_KEY" ]; then
    echo -e "   ✅  ${GREEN}Groq${NC} (Fallback) - Configuré"  
else
    echo -e "   ⚠️   ${YELLOW}Groq${NC} (Fallback) - À configurer"
fi
echo ""
echo -e "${YELLOW}🎯 Résultat: Workflow Git 100% automatisé avec IA !${NC}"
echo ""
echo -e "${BLUE}🔧 Configuration:${NC}"
echo -e "   1. Éditez: ${YELLOW}$HOME/.env.gitautoflow${NC}"
echo -e "   2. Ajoutez vos clés API (Gemini + Groq)"
echo -e "   3. Testez: ${GREEN}git commit-auto${NC} dans un repo Git"
echo ""
echo -e "${BLUE}📚 Documentation complète:${NC}"
echo -e "   ${YELLOW}${INSTALL_DIR}/README.md${NC}"
echo ""
echo -e "${GREEN}✨ Git Auto-Flow est prêt à l'emploi!${NC}"
