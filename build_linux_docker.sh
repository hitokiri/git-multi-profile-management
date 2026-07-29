#!/usr/bin/env bash
# Builds a Linux executable inside a Docker ubuntu:22.04 container (glibc 2.35), so the
# resulting binary's glibc requirement stays low enough to run on Ubuntu 22.04 and later.
# PyInstaller links against the glibc of the machine that builds it, and a binary built
# on a newer glibc (e.g. this host's) refuses to run on an older one — so building
# directly on a modern dev machine can silently produce a binary that only runs there.
#
# Usage: ./build_linux_docker.sh
set -euo pipefail

APP_NAME="GitMultiProfileSSH"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_TAG="gitmultiprofile-linux-builder"

echo "==> Checking for Docker..."
if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is not installed. Install it first, then run this script again:"
    echo "  Debian/Ubuntu:  sudo apt install docker.io"
    echo "  Fedora:         sudo dnf install docker"
    echo "  Arch:           sudo pacman -S docker"
    exit 1
fi
echo "    Found: $(docker --version)"

echo "==> Building (or reusing cached) builder image [$IMAGE_TAG] ..."
docker build -t "$IMAGE_TAG" -f - "$PROJECT_DIR" <<'EOF'
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq && \
    apt-get install -y -qq python3.11 python3.11-venv python3-tk python3.11-tk libpython3.11 binutils && \
    rm -rf /var/lib/apt/lists/*
EOF

echo "==> Installing/updating build dependencies and building inside the container ..."
docker run --rm \
    -v "$PROJECT_DIR":/work \
    -w /work \
    "$IMAGE_TAG" \
    bash -c '
        set -euo pipefail
        python3.11 -m venv /tmp/buildvenv
        /tmp/buildvenv/bin/pip install --quiet --upgrade pip
        /tmp/buildvenv/bin/pip install --quiet -r requirements-dev.txt
        /tmp/buildvenv/bin/python build.py
    '

# build.py names the binary "$APP_NAME-<version>" (version from the git tag, or an
# auto-bumped VERSION file), so pick it up by prefix rather than assuming a fixed name.
BINARY="$(find "$PROJECT_DIR/dist" -maxdepth 1 -type f -name "${APP_NAME}-*" -print -quit)"
chmod +x "$BINARY"

echo
echo "Done. Linux executable: $BINARY"
echo "Built against glibc 2.35 (Ubuntu 22.04) -- runs on Ubuntu 22.04 and newer."
