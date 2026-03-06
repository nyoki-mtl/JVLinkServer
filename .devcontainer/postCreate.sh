#!/usr/bin/env bash
set -euo pipefail

# 作業ディレクトリをワークスペースに揃える
cd "${containerWorkspaceFolder:-/workspaces/JVLinkServer}" || exit 1

echo "[postCreate] Running apt-get update..."
sudo apt-get update

echo "[postCreate] Installing build dependencies..."
sudo apt-get install -y \
  clang \
  build-essential \
  pkg-config \
  lsb-release \
  wget \
  software-properties-common \
  gnupg \
  ripgrep

wget https://apt.llvm.org/llvm.sh
chmod +x llvm.sh
sudo ./llvm.sh 18 all
rm llvm.sh
sudo update-alternatives --install /usr/bin/clang clang /usr/bin/clang-18 100
sudo update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-18 100

echo "[postCreate] Installing Node CLI tools (claude-code, gemini-cli)..."
npm install -g @anthropic-ai/claude-code @google/gemini-cli @openai/codex

echo "[postCreate] Syncing Python environment with uv..."
uv sync --all-extras

echo "[postCreate] Done."
