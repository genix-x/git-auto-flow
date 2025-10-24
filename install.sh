#!/usr/bin/env bash
# install.sh — GitAutoFlow installer with smart binary detection
set -euo pipefail

#############################
# Config
#############################
OWNER="${OWNER:-genix-x}"
REPO="${REPO:-git-auto-flow}"
BINARY_PREFIX="${BINARY_PREFIX:-gitautoflow}"
INSTALL_NAME="${INSTALL_NAME:-gitautoflow}"
VERSION="${VERSION:-}"
FORCE_SOURCE="${FORCE_SOURCE:-false}"

#############################
# Internals
#############################
API_BASE="https://api.github.com/repos/${OWNER}/${REPO}/releases"
TMP_DIR="$(mktemp -d -t ${BINARY_PREFIX}_install.XXXXXX)"
trap 'rm -rf "${TMP_DIR}"' EXIT INT TERM

PREFERRED_DIRS=( "/usr/local/bin" "/opt/homebrew/bin" "$HOME/.local/bin" "/usr/bin" )
INSTALL_DIR_SOURCE="/opt/${REPO}"

curl_api() {
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    curl -s -H "Authorization: token ${GITHUB_TOKEN}" -H "Accept: application/vnd.github.v3+json" "$@"
  else
    curl -s -H "Accept: application/vnd.github.v3+json" "$@"
  fi
}

#############################
# Test if binary works
#############################
test_binary() {
  local bin_path="$1"
  
  echo "🔍 Testing binary..."
  
  # Test 1: Can execute?
  if ! "${bin_path}" --help >/dev/null 2>&1; then
    echo "❌ Binary fails to execute (--help test)"
    return 1
  fi
  
  # Test 2: Check for dyld errors
  if "${bin_path}" --help 2>&1 | grep -q "dyld.*Library not loaded"; then
    echo "❌ Binary has missing Python dependencies (dyld error)"
    return 1
  fi
  
  # Test 3: Version check
  if ! "${bin_path}" version >/dev/null 2>&1; then
    echo "⚠️  Binary works but 'version' command fails"
    # Non-bloquant
  fi
  
  echo "✅ Binary test passed"
  return 0
}

#############################
# Uninstall
#############################
if [[ "${1:-}" == "--uninstall" || "${1:-}" == "uninstall" ]]; then
  echo "🧹 Uninstalling ${INSTALL_NAME}..."

  for d in "${PREFERRED_DIRS[@]}"; do
    if [[ -f "${d}/${INSTALL_NAME}" || -L "${d}/${INSTALL_NAME}" ]]; then
      if [[ -w "${d}" ]]; then
        rm -f "${d}/${INSTALL_NAME}"
      elif command -v sudo >/dev/null; then
        sudo rm -f "${d}/${INSTALL_NAME}"
      else
        echo "❌ Cannot remove ${d}/${INSTALL_NAME} (no permission)"
        exit 1
      fi
      echo "✅ Removed ${d}/${INSTALL_NAME}"
    fi
  done

  if [[ -d "${INSTALL_DIR_SOURCE}" ]]; then
    if [[ -w "$(dirname ${INSTALL_DIR_SOURCE})" ]]; then
      rm -rf "${INSTALL_DIR_SOURCE}"
    elif command -v sudo >/dev/null; then
      sudo rm -rf "${INSTALL_DIR_SOURCE}"
    fi
    echo "✅ Removed ${INSTALL_DIR_SOURCE}"
  fi

  echo "✅ Uninstall complete!"
  exit 0
fi

#############################
# Install from source
#############################
install_from_source() {
  echo ""
  echo "📦 Installing from Python source..."

  # Check Git
  if ! command -v git >/dev/null; then
    echo "❌ git not found. Install git first:"
    echo "   macOS: brew install git"
    echo "   Linux: sudo apt install git"
    exit 1
  fi

  # Check Python
  if ! command -v python3 >/dev/null; then
    echo "❌ python3 not found. Install Python 3.11+ first:"
    echo "   macOS: brew install python@3.11"
    echo "   Linux: sudo apt install python3.11 python3.11-venv"
    exit 1
  fi

  PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
  echo "✅ Found Python ${PYTHON_VERSION}"

  # Install UV
  if ! command -v uv >/dev/null; then
    echo "📥 Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add to PATH for this session
    export PATH="$HOME/.local/bin:$PATH"
    if [[ -f "$HOME/.cargo/env" ]]; then
      source "$HOME/.cargo/env"
    fi
    
    # Verify UV installed
    if ! command -v uv >/dev/null; then
      echo "⚠️  UV installed but not in PATH. Add to your shell:"
      echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
      echo ""
      echo "Retrying with explicit path..."
      UV_BIN="$HOME/.local/bin/uv"
      if [[ ! -f "${UV_BIN}" ]]; then
        echo "❌ UV installation failed"
        exit 1
      fi
    else
      UV_BIN="uv"
    fi
  else
    UV_BIN="uv"
  fi

  # Determine branch
  BRANCH="main"
  if [[ -n "${VERSION}" && "${VERSION}" != "latest" ]]; then
    BRANCH="${VERSION}"
  fi

  # Clone
  echo "📥 Cloning ${OWNER}/${REPO} (${BRANCH})..."
  if [[ -d "${INSTALL_DIR_SOURCE}" ]]; then
    echo "🗑️  Removing existing source..."
    if [[ -w "$(dirname ${INSTALL_DIR_SOURCE})" ]]; then
      rm -rf "${INSTALL_DIR_SOURCE}"
    elif command -v sudo >/dev/null; then
      sudo rm -rf "${INSTALL_DIR_SOURCE}"
    fi
  fi

  # Create parent dir with sudo if needed
  PARENT_DIR="$(dirname ${INSTALL_DIR_SOURCE})"
  if [[ ! -d "${PARENT_DIR}" ]]; then
    if [[ -w "$(dirname ${PARENT_DIR})" ]]; then
      mkdir -p "${PARENT_DIR}"
    elif command -v sudo >/dev/null; then
      sudo mkdir -p "${PARENT_DIR}"
      sudo chown "$(whoami)" "${PARENT_DIR}"
    fi
  fi

  git clone --depth 1 --branch "${BRANCH}" \
    "https://github.com/${OWNER}/${REPO}.git" "${INSTALL_DIR_SOURCE}"

  # Install deps
  echo "📦 Installing dependencies with UV..."
  cd "${INSTALL_DIR_SOURCE}"
  
  # Use explicit UV path if needed
  "${UV_BIN}" sync

  # Verify venv created
  if [[ ! -f ".venv/bin/activate" ]]; then
    echo "❌ Virtual environment not created"
    exit 1
  fi

  # Find wrapper location
  WRAPPER_DIR=""
  USE_SUDO_WRAPPER=false
  for d in "${PREFERRED_DIRS[@]}"; do
    if [[ -d "${d}" && -w "${d}" ]]; then
      WRAPPER_DIR="${d}"
      break
    elif [[ -d "${d}" ]] && command -v sudo >/dev/null; then
      WRAPPER_DIR="${d}"
      USE_SUDO_WRAPPER=true
      break
    fi
  done

  if [[ -z "${WRAPPER_DIR}" ]]; then
    echo "❌ No writable directory found in PATH"
    echo "💡 Candidates checked: ${PREFERRED_DIRS[*]}"
    exit 1
  fi

  # Create wrapper
  echo "🔗 Creating wrapper in ${WRAPPER_DIR}..."
  WRAPPER_CONTENT="#!/bin/bash
# GitAutoFlow wrapper (source installation)
set -e
VENV_DIR=\"${INSTALL_DIR_SOURCE}/.venv\"

if [[ ! -f \"\${VENV_DIR}/bin/activate\" ]]; then
  echo \"❌ Virtual environment not found at \${VENV_DIR}\"
  exit 1
fi

source \"\${VENV_DIR}/bin/activate\"
exec python -m gitautoflow.cli.main \"\$@\"
"

  if [[ "${USE_SUDO_WRAPPER}" == true ]]; then
    echo "${WRAPPER_CONTENT}" | sudo tee "${WRAPPER_DIR}/${INSTALL_NAME}" > /dev/null
    sudo chmod +x "${WRAPPER_DIR}/${INSTALL_NAME}"
  else
    echo "${WRAPPER_CONTENT}" > "${WRAPPER_DIR}/${INSTALL_NAME}"
    chmod +x "${WRAPPER_DIR}/${INSTALL_NAME}"
  fi

  echo ""
  echo "🎉 ${INSTALL_NAME} installed from source!"
  echo "📍 Wrapper: ${WRAPPER_DIR}/${INSTALL_NAME}"
  echo "📦 Source: ${INSTALL_DIR_SOURCE}"
  echo ""

  # Verify installation
  if "${WRAPPER_DIR}/${INSTALL_NAME}" version >/dev/null 2>&1; then
    VERSION_OUTPUT=$("${WRAPPER_DIR}/${INSTALL_NAME}" version 2>/dev/null | head -1)
    echo "✅ Verified: ${VERSION_OUTPUT}"
  else
    echo "⚠️  Installed but 'version' command failed (non-critical)"
  fi

  echo ""
  echo "👉 Run: ${INSTALL_NAME} --help"
  exit 0
}

#############################
# Force source mode
#############################
if [[ "${FORCE_SOURCE}" == "true" ]]; then
  install_from_source
fi

#############################
# Binary installation
#############################

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "⚠️  GITHUB_TOKEN not set — assuming public repo"
fi

# Detect platform
case "$(uname -s)" in
  Darwin) PLATFORM="macos" ;;
  Linux)  PLATFORM="linux" ;;
  *)
    echo "🚨 Unsupported OS: $(uname -s)"
    echo "ℹ️  Falling back to source installation..."
    install_from_source
    ;;
esac

# Detect arch
case "$(uname -m)" in
  x86_64) ARCH="x64" ;;
  arm64|aarch64) ARCH="arm64" ;;
  *)
    echo "🚨 Unsupported arch: $(uname -m)"
    echo "ℹ️  Falling back to source installation..."
    install_from_source
    ;;
esac

# Resolve version
if [[ -z "${VERSION}" ]]; then
  echo "ℹ️  Fetching latest release..."
  VERSION="$(curl_api "${API_BASE}/latest" 2>/dev/null | grep -m1 '"tag_name":' || true)"
  VERSION="$(echo "${VERSION}" | sed -E 's/.*"([^"]+)".*/\1/' || true)"
  if [[ -z "${VERSION}" ]]; then
    echo "❌ Cannot determine latest release"
    echo "ℹ️  Falling back to source..."
    install_from_source
  fi
fi

echo "📦 Installing ${INSTALL_NAME} ${VERSION} (${PLATFORM}-${ARCH})"

# Find asset
ASSET_URL="$(curl_api "${API_BASE}/tags/${VERSION}" \
  | grep -E 'browser_download_url' \
  | grep "${BINARY_PREFIX}" \
  | grep "${PLATFORM}" \
  | grep "${ARCH}" \
  | head -n1 \
  | sed -E 's/.*"([^"]+)".*/\1/' || true)"

if [[ -z "${ASSET_URL}" ]]; then
  echo "❌ No binary for ${PLATFORM}-${ARCH}"
  echo "ℹ️  Falling back to source..."
  install_from_source
fi

echo "📥 Downloading: ${ASSET_URL}"

# Download
DOWNLOAD_PATH="${TMP_DIR}/${INSTALL_NAME}.download"
if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  curl -sL -H "Authorization: token ${GITHUB_TOKEN}" -o "${DOWNLOAD_PATH}" "${ASSET_URL}"
else
  curl -sL -o "${DOWNLOAD_PATH}" "${ASSET_URL}"
fi

if [[ ! -s "${DOWNLOAD_PATH}" ]]; then
  echo "❌ Download failed"
  echo "ℹ️  Falling back to source..."
  install_from_source
fi

chmod +x "${DOWNLOAD_PATH}"

# Find install dir
INSTALL_DIR=""
USE_SUDO=false
for d in "${PREFERRED_DIRS[@]}"; do
  if [[ -d "${d}" && -w "${d}" ]]; then
    INSTALL_DIR="${d}"
    break
  elif [[ -d "${d}" ]] && command -v sudo >/dev/null; then
    INSTALL_DIR="${d}"
    USE_SUDO=true
    break
  fi
done

if [[ -z "${INSTALL_DIR}" ]]; then
  echo "❌ No install directory found"
  echo "ℹ️  Falling back to source..."
  install_from_source
fi

echo "🔧 Installing to ${INSTALL_DIR} (sudo: ${USE_SUDO})"

# Backup existing
if command -v "${INSTALL_NAME}" >/dev/null 2>&1; then
  EXISTING_PATH="$(command -v ${INSTALL_NAME})"
  BACKUP_PATH="${EXISTING_PATH}.bak-$(date +%s)"
  echo "💾 Backing up existing binary..."

  if [[ "${USE_SUDO}" == true ]]; then
    sudo mv "${EXISTING_PATH}" "${BACKUP_PATH}" 2>/dev/null || {
      echo "⚠️  Cannot backup, removing instead..."
      sudo rm -f "${EXISTING_PATH}"
    }
  else
    mv "${EXISTING_PATH}" "${BACKUP_PATH}" 2>/dev/null || {
      echo "⚠️  Cannot backup, removing instead..."
      rm -f "${EXISTING_PATH}"
    }
  fi
fi

# Install binary
TARGET_PATH="${INSTALL_DIR}/${INSTALL_NAME}"
if [[ "${USE_SUDO}" == true ]]; then
  sudo mv "${DOWNLOAD_PATH}" "${TARGET_PATH}"
  sudo chmod +x "${TARGET_PATH}"
else
  mv "${DOWNLOAD_PATH}" "${TARGET_PATH}"
  chmod +x "${TARGET_PATH}"
fi

echo ""
echo "🎉 ${INSTALL_NAME} ${VERSION} installed!"
echo "📍 ${TARGET_PATH}"
echo ""

# Test binary (NEW!)
if ! test_binary "${TARGET_PATH}"; then
  echo ""
  echo "⚠️  Binary installation failed validation"
  echo "ℹ️  Removing broken binary and falling back to source..."
  if [[ "${USE_SUDO}" == true ]]; then
    sudo rm -f "${TARGET_PATH}"
  else
    rm -f "${TARGET_PATH}"
  fi
  install_from_source
fi

echo ""
echo "✅ Installation complete!"
echo "👉 Run: ${INSTALL_NAME} --help"
echo ""
