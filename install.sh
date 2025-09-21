#!/usr/bin/env bash
# install.sh — Generic GitHub release binary installer
# Usage examples:
#   OWNER=genix-x REPO=git-auto-flow BINARY_PREFIX=gitautoflow INSTALL_NAME=gitautoflow \
#     curl -sL https://example.com/install.sh | bash
#   OWNER=genix-x REPO=git-auto-flow BINARY_PREFIX=gitautoflow INSTALL_NAME=gitautoflow VERSION=v1.5.1 \
#     curl -sL https://example.com/install.sh | bash
#   curl -sL https://example.com/install.sh | bash -- --uninstall
set -euo pipefail

#############################
# Config (override with env)
#############################
OWNER="${OWNER:-genix-x}"                # ex: genix-x
REPO="${REPO:-git-auto-flow}"            # ex: git-auto-flow
BINARY_PREFIX="${BINARY_PREFIX:-gitautoflow}"  # ex: gitautoflow
INSTALL_NAME="${INSTALL_NAME:-gitautoflow}"    # ex: command name (final filename)
VERSION="${VERSION:-}"                   # ex: v1.5.1 (leave empty for latest)

#############################
# Internals
#############################
API_BASE="https://api.github.com/repos/${OWNER}/${REPO}/releases"
TMP_DIR="$(mktemp -d -t ${BINARY_PREFIX}_install.XXXXXX)"
trap 'rm -rf "${TMP_DIR}"' EXIT INT TERM

# Common install dirs to try (order matters)
PREFERRED_DIRS=( "/usr/local/bin" "/opt/homebrew/bin" "$HOME/.local/bin" "/usr/bin" )

# Helper: call GitHub API with optional auth
curl_api() {
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    curl -s -H "Authorization: token ${GITHUB_TOKEN}" -H "Accept: application/vnd.github.v3+json" "$@"
  else
    curl -s -H "Accept: application/vnd.github.v3+json" "$@"
  fi
}

# Help / Uninstall
if [[ "${1:-}" == "--uninstall" || "${1:-}" == "uninstall" ]]; then
  echo "🧹 Uninstall mode — searching for ${INSTALL_NAME} in common dirs..."
  for d in "${PREFERRED_DIRS[@]}"; do
    if [[ -f "${d}/${INSTALL_NAME}" || -L "${d}/${INSTALL_NAME}" ]]; then
      if [[ -w "${d}/${INSTALL_NAME}" ]]; then
        rm -f "${d}/${INSTALL_NAME}"
      elif command -v sudo >/dev/null; then
        sudo rm -f "${d}/${INSTALL_NAME}"
      else
        echo "❌ Found ${d}/${INSTALL_NAME} but cannot remove it (no write perm and no sudo)."
        exit 1
      fi
      echo "✅ Removed ${d}/${INSTALL_NAME}"
      exit 0
    fi
  done
  echo "ℹ️ ${INSTALL_NAME} not found in standard locations."
  exit 0
fi

# Check token notice (private repo requires token)
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "⚠️  GITHUB_TOKEN not set — assuming repo is public. If private, export GITHUB_TOKEN first."
else
  # quick sanity
  : # token present
fi

# Detect platform
case "$(uname -s)" in
  Darwin) PLATFORM="macos" ;; 
  Linux)  PLATFORM="linux" ;; 
  *)
    echo "🚨 Unsupported OS: $(uname -s). This installer supports macOS and Linux."
    exit 1
    ;; 
esac

# Detect arch
case "$(uname -m)" in
  x86_64) ARCH="x64" ;; 
  arm64|aarch64) ARCH="arm64" ;; 
  *)
    echo "🚨 Unsupported architecture: $(uname -m). Only x86_64 and arm64 supported."
    exit 1
    ;; 
esac

# Resolve version (latest if empty)
if [[ -z "${VERSION}" ]]; then
  echo "ℹ️  Fetching latest release tag from GitHub..."
  VERSION="$(curl_api "${API_BASE}/latest" 2>/dev/null | grep -m1 '"tag_name":' || true)"
  VERSION="$(echo "${VERSION}" | sed -E 's/.*"([^"]+)".*/\1/' || true)"
  if [[ -z "${VERSION}" ]]; then
    echo "❌ Failed to determine latest release. If repo is private, ensure GITHUB_TOKEN is set and has repo scope."
    exit 1
  fi
fi
echo "📦 Installing ${INSTALL_NAME} — release: ${VERSION} (looking for ${BINARY_PREFIX}-${PLATFORM}-${ARCH})"

# Find asset download URL
# Prefer exact match for prefix + platform + arch; fallback to first match containing those tokens.
ASSET_URL="$(curl_api "${API_BASE}/tags/${VERSION}" \
  | grep -E 'browser_download_url' \
  | grep "${BINARY_PREFIX}" || true)"

# filter for platform and arch
ASSET_URL="$(echo "${ASSET_URL}" | grep "${PLATFORM}" || true)"
ASSET_URL="$(echo "${ASSET_URL}" | grep "${ARCH}" || true)"
ASSET_URL="$(echo "${ASSET_URL}" | head -n1 | sed -E 's/.*"([^"]+)".*/\1/' || true)"

if [[ -z "${ASSET_URL}" ]]; then
  echo "❌ No matching asset found for '${BINARY_PREFIX}' + '${PLATFORM}' + '${ARCH}' in release ${VERSION}."
  echo "Assets found (for debug):"
  curl_api "${API_BASE}/tags/${VERSION}" | grep -E 'browser_download_url' || true
  exit 1
fi

echo "📥 Download URL found: ${ASSET_URL}"

# Download file (use auth header for private repos)
DOWNLOAD_PATH="${TMP_DIR}/${INSTALL_NAME}.download"
if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  curl -sL -H "Authorization: token ${GITHUB_TOKEN}" -o "${DOWNLOAD_PATH}" "${ASSET_URL}"
else
  curl -sL -o "${DOWNLOAD_PATH}" "${ASSET_URL}"
fi

if [[ ! -s "${DOWNLOAD_PATH}" ]]; then
  echo "❌ Download failed or file is empty."
  exit 1
fi

chmod +x "${DOWNLOAD_PATH}"

# Determine install directory (first writable or requiring sudo)
INSTALL_DIR=""
USE_SUDO=false
for d in "${PREFERRED_DIRS[@]}"; do
  if [[ -d "${d}" && -w "${d}" ]]; then
    INSTALL_DIR="${d}"
    USE_SUDO=false
    break
  elif [[ -d "${d}" ]]; then
    # exists but not writable — we can still use it with sudo
    if command -v sudo >/dev/null; then
      INSTALL_DIR="${d}"
      USE_SUDO=true
      break
    fi
  fi
done

if [[ -z "${INSTALL_DIR}" ]]; then
  echo "❌ No suitable installation directory found. Create one of: ${PREFERRED_DIRS[*]} or run with sudo."
  exit 1
fi

echo "🔧 Installing to ${INSTALL_DIR} (sudo required: ${USE_SUDO})"

# Backup existing binary if present
if command -v "${INSTALL_NAME}" >/dev/null 2>&1; then
  EXISTING_PATH="$(command -v ${INSTALL_NAME})"
  TS="$(date +%s)"
  BACKUP_PATH="${EXISTING_PATH}.bak-${TS}"
  echo "💾 Existing ${INSTALL_NAME} found at ${EXISTING_PATH}. Backing up to ${BACKUP_PATH}"
  if mv "${EXISTING_PATH}" "${BACKUP_PATH}" 2>/dev/null; then
    echo "✅ Backup done."
  elif command -v sudo >/dev/null; then
    sudo mv "${EXISTING_PATH}" "${BACKUP_PATH}"
    echo "✅ Backup done (with sudo)."
  else
    echo "⚠️ Could not backup existing binary (no permission)."
  fi
fi

# Move into place
TARGET_PATH="${INSTALL_DIR}/${INSTALL_NAME}"
if [[ "${USE_SUDO}" == true ]]; then
  echo "⚡ Using sudo to move binary..."
  sudo mv "${DOWNLOAD_PATH}" "${TARGET_PATH}"
  sudo chmod +x "${TARGET_PATH}"
else
  mv "${DOWNLOAD_PATH}" "${TARGET_PATH}"
  chmod +x "${TARGET_PATH}"
fi

echo ""
echo "🎉 ${INSTALL_NAME} ${VERSION} installed to ${TARGET_PATH}"
echo "👉 Run: ${INSTALL_NAME} (if not in PATH, add ${INSTALL_DIR} to your PATH)"
echo ""
