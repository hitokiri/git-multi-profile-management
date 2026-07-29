#!/usr/bin/env bash
# Builds a Windows .exe from Linux using Wine: a real Windows Python is installed inside
# a dedicated Wine prefix (kept inside this project, not ~/.wine), then PyInstaller runs
# inside that Wine-hosted Python to produce a genuine Windows binary.
#
# Usage: ./build_windows.sh
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_VERSION="3.11.9"
PYTHON_INSTALLER="python-${PYTHON_VERSION}-amd64.exe"
PYTHON_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_INSTALLER}"

CACHE_DIR="$PROJECT_DIR/.build-cache"
export WINEPREFIX="$PROJECT_DIR/.wine-build"
export WINEARCH=win64
WIN_PYTHON="$WINEPREFIX/drive_c/Python/python.exe"

echo "==> Checking for Wine..."
if ! command -v wine >/dev/null 2>&1; then
    echo "Wine is not installed. Install it first, then run this script again:"
    echo "  Debian/Ubuntu:  sudo apt install wine"
    echo "  Fedora:         sudo dnf install wine"
    echo "  Arch:           sudo pacman -S wine"
    exit 1
fi
echo "    Found: $(wine --version)"

mkdir -p "$CACHE_DIR"

if [ ! -f "$WIN_PYTHON" ]; then
    echo "==> First run: setting up a dedicated Wine prefix at $WINEPREFIX ..."
    wineboot --init >/dev/null 2>&1
    wineserver -w

    if [ ! -f "$CACHE_DIR/$PYTHON_INSTALLER" ]; then
        echo "==> Downloading Windows Python $PYTHON_VERSION ..."
        curl -fL -o "$CACHE_DIR/$PYTHON_INSTALLER" "$PYTHON_URL"
    fi

    echo "==> Installing Windows Python inside Wine (silent, per-user) ..."
    wine "$CACHE_DIR/$PYTHON_INSTALLER" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 TargetDir='C:\Python'
    wineserver -w
fi

if [ ! -f "$WIN_PYTHON" ]; then
    echo "Setup failed: $WIN_PYTHON was not created. Check the output above."
    exit 1
fi
echo "    Windows Python ready: $WIN_PYTHON"

echo "==> Installing/updating build dependencies inside the Windows Python ..."
wine "$WIN_PYTHON" -m pip install --upgrade pip --quiet
wine "$WIN_PYTHON" -m pip install -r "$PROJECT_DIR/requirements-dev.txt" --quiet

echo "==> Building the Windows executable ..."
cd "$PROJECT_DIR"
wine "$WIN_PYTHON" build.py

echo
echo "Done. Windows executable: see the path printed above (in dist/)."
echo "(Copy it to a Windows machine to run it — Wine only builds it, it won't run natively as a Linux process.)"
