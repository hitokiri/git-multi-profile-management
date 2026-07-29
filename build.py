#!/usr/bin/env python3
"""Build a standalone executable for the CURRENT operating system using PyInstaller.

PyInstaller does not cross-compile: a build made on Linux produces a Linux binary,
one made on Windows produces a .exe, one made on macOS produces a macOS binary/.app.
To ship all three, run this script on each target OS (locally or via CI).

Usage:
    pip install -r requirements-dev.txt
    python3 build.py
"""
import platform
import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "GitMultiProfileSSH"
ENTRY_POINT = "git_complete_automator.py"


def _cleanup_build_artifacts(root):
    """build/ (PyInstaller's scratch dir) and the generated .spec file are only needed
    while PyInstaller is running — the final binary is what lands in dist/. Since the
    build name embeds the version, each build leaves its own build/<name> and <name>.spec
    behind, and they'd otherwise pile up forever, one per version."""
    build_dir = root / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    for spec_file in root.glob("*.spec"):
        spec_file.unlink()


def _git_tag_version(root):
    """Exact git tag for HEAD (e.g. 'v1.2.3' -> '1.2.3'), or None if HEAD isn't tagged
    or git/the repo isn't available. CI builds are only triggered by pushing a 'v*' tag
    (see azure-pipelines.yml / .github/workflows/build.yml), so this is how release
    builds get their version."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--exact-match"],
            cwd=root, capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    tag = result.stdout.strip()
    return tag.lstrip("v") if tag else None


def _bump_local_version(version_file):
    """No git tag to pin to (a plain local/manual build) -> bump the patch number in
    VERSION so each local build gets a distinct, increasing version."""
    current = version_file.read_text().strip() if version_file.exists() else "0.1.0"
    major, minor, patch = (current.split(".") + ["0", "0"])[:3]
    bumped = f"{major}.{minor}.{int(patch) + 1}"
    version_file.write_text(bumped + "\n")
    return bumped


def get_version(root):
    return _git_tag_version(root) or _bump_local_version(root / "VERSION")


def main():
    root = Path(__file__).resolve().parent
    entry = root / ENTRY_POINT
    if not entry.exists():
        sys.exit(f"Could not find {ENTRY_POINT} next to build.py")

    system = platform.system()
    version = get_version(root)
    exe_name = f"{APP_NAME}-{version}"
    # Not a real AppImage (no appimagetool/desktop integration) — just the plain onefile
    # binary named with a .AppImage suffix so file managers show an executable icon and
    # offer a "run" click, instead of a generic file icon.
    pyinstaller_name = f"{exe_name}.AppImage" if system == "Linux" else exe_name
    print(f"Building a standalone {system} executable for {APP_NAME} v{version}...\n")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name", pyinstaller_name,
        # customtkinter ships its own theme JSON files and fonts as package data;
        # PyInstaller won't pick those up automatically without this.
        "--collect-all", "customtkinter",
        str(entry),
    ]
    subprocess.run(cmd, check=True, cwd=root)
    _cleanup_build_artifacts(root)

    dist_dir = root / "dist"
    if system == "Windows":
        binary = dist_dir / f"{exe_name}.exe"
    elif system == "Darwin":
        # --windowed always produces a full .app bundle on macOS, even with --onefile.
        binary = dist_dir / f"{exe_name}.app"
    else:
        binary = dist_dir / pyinstaller_name
    print(f"\nDone. Executable: {binary}")

    if system == "Darwin":
        print("Note: unsigned apps are blocked by Gatekeeper on first run.")
        print(f"Right-click {exe_name}.app -> Open, or run: xattr -dr com.apple.quarantine '{binary}'")
    elif system == "Windows":
        print("Note: unsigned .exe files may trigger a Windows SmartScreen warning")
        print("('More info' -> 'Run anyway' to bypass it).")
    elif system == "Linux":
        print(f"Note: mark it executable if needed: chmod +x '{binary}'")


if __name__ == "__main__":
    main()
