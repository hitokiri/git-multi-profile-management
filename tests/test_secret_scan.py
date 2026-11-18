"""Offline checks for the gitleaks hook wiring. Run: python tests/test_secret_scan.py
Uses a fake gitleaks binary, so no network and no real gitleaks needed (POSIX shell required)."""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
tmp = tempfile.mkdtemp()
os.environ["XDG_DATA_HOME"] = tmp  # keep the app data folder inside the temp dir
import git_complete_automator as g  # noqa: E402

# Asset selection
assert g.gitleaks_asset_name("8.30.1", "linux", "x86_64") == "gitleaks_8.30.1_linux_x64.tar.gz"
assert g.gitleaks_asset_name("8.30.1", "darwin", "arm64") == "gitleaks_8.30.1_darwin_arm64.tar.gz"
assert g.gitleaks_asset_name("8.30.1", "win32", "AMD64") == "gitleaks_8.30.1_windows_x64.zip"
assert g.gitleaks_asset_name("8.30.1", "linux", "mips") is None


def git(*args, cwd, check=True):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=check)


paths = g.gitleaks_paths()
os.makedirs(paths["root"], exist_ok=True)
g.write_hook_scripts()

repo = os.path.join(tmp, "repo")
os.makedirs(repo)
git("init", "-q", cwd=repo)
git("config", "user.email", "t@t", cwd=repo)
git("config", "user.name", "t", cwd=repo)
git("config", "core.hooksPath", paths["hooks"], cwd=repo)

# The repo's own hooks must keep running (chained), e.g. git-lfs/commit-msg tooling.
marker = os.path.join(tmp, "repo-hooks-ran")
for name in ("pre-commit", "commit-msg"):
    hook = os.path.join(repo, ".git", "hooks", name)
    with open(hook, "w") as f:
        f.write(f"#!/bin/sh\necho {name} >> '{marker}'\n")
    os.chmod(hook, 0o755)


def fake_gitleaks(exit_code):
    with open(paths["bin"], "w") as f:
        f.write(f"#!/bin/sh\nexit {exit_code}\n")
    os.chmod(paths["bin"], 0o755)


def commit(name):
    with open(os.path.join(repo, name), "w") as f:
        f.write(name)
    git("add", name, cwd=repo)
    return git("commit", "-qm", name, cwd=repo, check=False)


# gitleaks finds a secret -> commit blocked, repo hooks not reached
fake_gitleaks(1)
r = commit("a.txt")
assert r.returncode != 0 and "Commit blocked" in r.stderr, r.stderr
assert not os.path.exists(marker)

# clean -> commit goes through and both repo hooks ran
fake_gitleaks(0)
assert commit("b.txt").returncode == 0
assert open(marker).read().split() == ["pre-commit", "commit-msg"]

# gitleaks not installed yet -> warn, don't block
os.remove(paths["bin"])
r = commit("c.txt")
assert r.returncode == 0 and "not installed" in r.stderr, r.stderr

print("ok: secret scan hooks")
