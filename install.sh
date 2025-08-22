#!/bin/bash
# 🚀 Git Auto-Flow - Installation Ultra-Simple
set -e

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${BLUE}🤖 Git Auto-Flow - Installation Ultra-Simple${NC}"
echo "=================================================="
echo ""

# Répertoire d'installation
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Vérifications rapides
echo -e "${BLUE}🔍 Vérifications...${NC}"

# Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 requis: brew install python3 (macOS) ou sudo apt install python3 (Ubuntu)"
    exit 1
fi

# Git
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "❌ Lancez cette commande depuis un repository Git"
    exit 1
fi

echo -e "${GREEN}✅ Environnement OK${NC}"
echo ""

# 2. Demande des clés API (ultra-simple)
echo -e "${BLUE}🔑 Configuration des clés API${NC}"
echo ""
echo -e "${YELLOW}⚡ Les clés API sont optionnelles (fonctions IA)${NC}"
echo ""

# Gemini
echo -e "${BLUE}🤖 Gemini API (Gratuit):${NC}"
echo -e "   Lien: ${YELLOW}https://makersuite.google.com/app/apikey${NC}"
read -p "   Clé Gemini (ENTER pour ignorer): " GEMINI_KEY
echo ""

# Groq
echo -e "${BLUE}⚡ Groq API (Fallback gratuit):${NC}"
echo -e "   Lien: ${YELLOW}https://console.groq.com/keys${NC}"
read -p "   Clé Groq (ENTER pour ignorer): " GROQ_KEY
echo ""

# 3. Installation rapide
echo -e "${BLUE}📦 Installation...${NC}"

# Dépendances Python
pip3 install google-generativeai python-dotenv groq --quiet --break-system-packages 2>/dev/null || pip3 install google-generativeai python-dotenv groq --quiet

# Création fichier .env
cat > "${INSTALL_DIR}/.env" << EOF
# Git Auto-Flow - Clés API
GEMINI_API_KEY=${GEMINI_KEY}
GROQ_API_KEY=${GROQ_KEY}
EOF

# 4. Configuration Git aliases
echo -e "${GREEN}⚙️ Configuration aliases Git...${NC}"

# Ajout aliases dans .gitconfig
git config --global alias.commit-auto "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-commit-auto.py"
git config --global alias.ca "!git commit-auto"
git config --global alias.pr-create-auto "!cd \$(git rev-parse --show-toplevel) && python3 ${INSTALL_DIR}/src/git-pr-create-auto.py"
git config --global alias.pr "!git pr-create-auto"

git config --global alias.feature-start "!f() { 
    echo '🚀 Feature: '\$1; 
    echo '🧹 Nettoyage des branches mergées...'; 
    git fetch --prune origin 2>/dev/null || true; 
    git branch --merged main 2>/dev/null | grep 'feature/' | xargs -n 1 git branch -d 2>/dev/null || true; 
    git branch --merged develop 2>/dev/null | grep 'feature/' | xargs -n 1 git branch -d 2>/dev/null || true; 
    git branch -r --merged main 2>/dev/null | grep 'origin/feature/' | sed 's/origin\///' | xargs -n 1 git push origin --delete 2>/dev/null || true; 
    git branch -r --merged develop 2>/dev/null | grep 'origin/feature/' | sed 's/origin\///' | xargs -n 1 git push origin --delete 2>/dev/null || true; 
    git checkout develop 2>/dev/null || git checkout -b develop; 
    git pull origin develop 2>/dev/null || true; 
    git checkout -b feature/\$1 && 
    git push -u origin feature/\$1 2>/dev/null || true; 
    echo '✅ Feature créée: feature/'\$1; 
}; f"

git config --global alias.feature-finish "!f() { 
    git fetch origin develop 2>/dev/null || true && 
    git rebase origin/develop 2>/dev/null || git rebase develop && 
    git push --force-with-lease origin \$(git branch --show-current) && 
    echo '✅ Feature prête pour PR'; 
}; f"

git config --global alias.clean-features "!git branch --merged main | grep 'feature/' | xargs -n 1 git branch -d 2>/dev/null || true"

# 5. Configuration develop branch
if ! git show-ref --verify --quiet refs/heads/develop; then
    git checkout -b develop 2>/dev/null || git checkout develop
    git push -u origin develop 2>/dev/null || echo "⚠️ Push develop: configurez origin"
fi

# 6. Configuration auto-delete branches (GitHub)
if command -v gh &> /dev/null; then
    echo -e "${BLUE}🗑️  Configuration auto-suppression branches...${NC}"
    if gh api repos/:owner/:repo --method PATCH --field delete_branch_on_merge=true >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Auto-suppression branches activée${NC}"
    else
        echo -e "${YELLOW}⚠️  Auto-suppression échouée (permissions GitHub?)${NC}"
        echo -e "${YELLOW}💡 Activez manuellement: Repo Settings > Pull Requests > Auto-delete${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🎉 Installation terminée !${NC}"
echo ""
echo -e "${BLUE}🚀 UTILISATION:${NC}"
echo ""
echo -e "  ${GREEN}git feature-start ma-feature${NC}  # Nouvelle feature"
echo -e "  ${GREEN}git ca${NC}                        # Commit automatique IA"
echo -e "  ${GREEN}git pr-create-auto${NC}            # PR automatique"
echo -e "  ${GREEN}git clean-features${NC}            # Nettoyage"
echo ""
echo -e "${YELLOW}💡 Testez: ${GREEN}git ca${NC} pour voir l'IA en action !${NC}"
echo ""