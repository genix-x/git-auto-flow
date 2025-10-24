#!/usr/bin/env bash
# install.sh — GitAutoFlow installer with binary fallback to Python source
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
  
  if ! command -v git >/dev/null; then
    echo "❌ git not found. Install git first."
    exit 1
  fi
  
  if ! command -v python3 >/dev/null; then
    echo "❌ python3 not found. Install Python 3.8+ first."
    exit 1
  fi
  
  # Install UV
  if ! command -v uv >/dev/null; then
    echo "📥 Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    source "$HOME/.cargo/env" 2>/dev/null || true
  fi
  
  # Determine branch
  BRANCH="main"
  if [[ -n "${VERSION}" && "${VERSION}" != "latest" ]]; then
    BRANCH="${VERSION}"
  fi
  
  # Clone
  echo "📥 Cloning ${OWNER}/${REPO} (${BRANCH})..."
  if [[ -d "${INSTALL_DIR_SOURCE}" ]]; then
    if [[ -w "$(dirname ${INSTALL_DIR_SOURCE})" ]]; then
      rm -rf "${INSTALL_DIR_SOURCE}"
    elif command -v sudo >/dev/null; then
      sudo rm -rf "${INSTALL_DIR_SOURCE}"
    fi
  fi
  
  if [[ -w "$(dirname ${INSTALL_DIR_SOURCE})" ]]; then
    git clone --depth 1 --branch "${BRANCH}" \
      "https://github.com/${OWNER}/${REPO}.git" "${INSTALL_DIR_SOURCE}"
  elif command -v sudo >/dev/null; then
    sudo git clone --depth 1 --branch "${BRANCH}" \
      "https://github.com/${OWNER}/${REPO}.git" "${INSTALL_DIR_SOURCE}"
    sudo chown -R "$(whoami)" "${INSTALL_DIR_SOURCE}"
  else
    echo "❌ Cannot write to $(dirname ${INSTALL_DIR_SOURCE})"
    exit 1
  fi
  
  # Install deps
  echo "📦 Installing dependencies..."
  cd "${INSTALL_DIR_SOURCE}"
  uv sync
  
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
    echo "❌ No directory found for wrapper"
    exit 1
  fi
  
  # Create wrapper
  echo "🔗 Creating wrapper in ${WRAPPER_DIR}..."
  WRAPPER_CONTENT="#!/bin/bash
source ${INSTALL_DIR_SOURCE}/.venv/bin/activate
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
  
  if "${WRAPPER_DIR}/${INSTALL_NAME}" --version >/dev/null 2>&1; then
    echo "✅ Verified!"
  else
    echo "⚠️  Installed but verification failed"
  fi
  
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
    exit 1
    ;;
esac

# Detect arch
case "$(uname -m)" in
  x86_64) ARCH="x64" ;;
  arm64|aarch64) ARCH="arm64" ;;
  *)
    echo "🚨 Unsupported arch: $(uname -m)"
    exit 1
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
  exit 1
fi

echo "🔧 Installing to ${INSTALL_DIR} (sudo: ${USE_SUDO})"

# Backup existing (FIXED)
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

# Install
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

# Verify
echo "🔍 Verifying..."
if ! "${TARGET_PATH}" --version >/dev/null 2>&1; then
  echo "⚠️  Binary failed verification"
  echo "ℹ️  Falling back to source..."
  if [[ "${USE_SUDO}" == true ]]; then
    sudo rm -f "${TARGET_PATH}"
  else
    rm -f "${TARGET_PATH}"
  fi
  install_from_source
fi

echo "✅ Verified!"
echo "👉 Run: ${INSTALL_NAME} --help"
echo ""
