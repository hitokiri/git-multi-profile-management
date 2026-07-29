# Git Multi-Profile & SSH Automator

🇪🇸 [Versión en español](README.md)

Desktop (GUI) tool for managing **multiple Git identities and SSH keys** on the same machine — for example, a work account on Azure DevOps and a personal one on GitHub — without having to hand-edit `~/.gitconfig` or `~/.ssh/config`.

The interface is available in **Spanish and English**, switchable at any time from within the app itself.

---

## Table of contents

1. [What problem does it solve?](#what-problem-does-it-solve)
2. [Requirements](#requirements)
3. [Installation and running](#installation-and-running)
4. [Building a standalone executable](#building-a-standalone-executable)
   - [Building the Windows `.exe` from Linux](#building-the-windows-exe-from-linux-without-windows)
   - [Building all three with GitHub Actions](#automatically-building-all-three-executables-with-github-actions)
   - [Alternative: Azure Pipelines](#alternative-azure-pipelines)
5. [Key concepts](#key-concepts)
6. [Usage guide](#usage-guide)
   - [Create a profile](#1-create-a-profile)
   - [View and edit profiles](#2-view-and-edit-profiles)
   - [Delete a profile](#3-delete-a-profile)
   - [Clone a repository](#4-clone-a-repository)
7. [Changing the interface language](#changing-the-interface-language)
8. [Where the app writes files](#where-the-app-writes-files)
9. [FAQ / troubleshooting](#faq--troubleshooting)

---

## What problem does it solve?

When you work with Git across several different providers or organizations (your employer, a client, your personal account), you normally need:

- A different Git name/email for each one.
- A different SSH key for each one (so you don't mix up permissions between accounts).
- Manually configuring `~/.gitconfig` with `includeIf` blocks and `~/.ssh/config` with `Host` aliases — tedious, and easy to get wrong.

This app automates that whole process through a graphical interface: it creates the project folder, generates the SSH key, registers the alias in `~/.ssh/config`, and links that folder to the right name/email in `~/.gitconfig`. It also helps you clone repositories, making sure they end up in the right folder with the right identity.

## Requirements

- Python 3.9 or newer.
- Git installed and available on the `PATH`.
- `ssh-keygen` available on the `PATH` (ships with OpenSSH; already installed on Linux/macOS, and comes with Git for Windows or the Windows OpenSSH client on Windows).
- The `customtkinter` library (see installation below).

## Installation and running

```bash
# (optional but recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# run the app
python3 git_complete_automator.py
```

No extra configuration or special permissions required — it only reads/writes inside your home folder (`~/.gitconfig`, `~/.ssh/config`, etc.).

## Building a standalone executable

If you'd rather distribute the app as a double-clickable executable (so whoever uses it doesn't need to install Python), it can be packaged with [PyInstaller](https://pyinstaller.org/) using the included `build.py` script:

```bash
pip install -r requirements-dev.txt
python3 build.py
```

This produces the executable in `dist/`:

- **Linux**: `dist/GitMultiProfileSSH` (an ELF binary; mark it executable with `chmod +x` if needed).
- **Windows**: `dist/GitMultiProfileSSH.exe` (running `build.py` on a real Windows machine — it works exactly as well as on Linux/macOS, it's the same Python script with nothing Wine-specific in it).
- **macOS**: `dist/GitMultiProfileSSH-macos.app` (running `build.py` on a real Mac — nothing else needed, the same script already detects macOS and produces the correct `.app` bundle; PyInstaller always packages this way with `--windowed`, even combined with `--onefile`).

**Important:** PyInstaller does **not** cross-compile — the resulting executable only runs on the same operating system you built it on.

- If you have physical access to Windows and macOS, just run `python3 build.py` on each one.
- If you only have Linux, for **Windows** you can use `./build_windows.sh` (see below). For **macOS there is no real shortcut** from Linux — there's no "Wine for macOS" — so you'll need a physical Mac, a cloud Mac service, or CI (see the next section).

### Building the Windows `.exe` from Linux (without Windows)

`build_windows.sh` uses [Wine](https://www.winehq.org/) to install a real Windows Python inside a Wine prefix dedicated to this project (`.wine-build/`, it does not touch your `~/.wine`), then runs PyInstaller inside it:

```bash
./build_windows.sh
```

- If Wine isn't installed, the script prints the exact install command for your distro and stops (it won't install anything on its own).
- The first run downloads the official Windows Python installer (~25 MB, cached in `.build-cache/`) and installs it inside the prefix — this can take a few minutes. Subsequent runs reuse that same Python and only rebuild the executable.
- The result is a real Windows `.exe` (verifiable with `file dist/GitMultiProfileSSH.exe`), ready to copy to a Windows machine.

### Building a Linux binary compatible with older distros (glibc)

PyInstaller links the binary against the glibc of the machine that runs the build. If you run `build.py` directly on a Linux box with a recent glibc (e.g. Ubuntu 24.04, glibc 2.39), the resulting executable **won't run on older systems** like Ubuntu 22.04 (glibc 2.35) — a newer glibc isn't backward compatible.

`build_linux_docker.sh` solves this by building inside an `ubuntu:22.04` Docker container, without touching your host system:

```bash
./build_linux_docker.sh
```

- If Docker isn't installed, the script prints the exact install command for your distro and stops.
- The first run builds an image with Python 3.11 and the required system dependencies (cached by Docker, so later runs are much faster).
- The result is the same `dist/GitMultiProfileSSH` as always, but linked against glibc 2.35 — it runs on Ubuntu 22.04 and any newer distro. You can verify this with `objdump -T dist/GitMultiProfileSSH | grep GLIBC_ | sort -V | tail -1`.

Per-OS notes:

- **macOS**: being an unsigned app, Gatekeeper will block the first run. Right-click the `.app` → "Open", or run `xattr -dr com.apple.quarantine dist/GitMultiProfileSSH-macos.app`.
- **Windows**: an unsigned `.exe` may trigger a SmartScreen warning ("More info" → "Run anyway" to bypass it).
- **Linux**: if the file isn't executable, run `chmod +x dist/GitMultiProfileSSH`.

### Automatically building all three executables with GitHub Actions

The repo includes `.github/workflows/build.yml`, which runs `build.py` on **native** Linux, Windows and macOS runners provided by GitHub — no Wine, no tricks, each OS builds itself. It triggers:

- Automatically on pushing a tag matching `v*` — besides building, it creates a GitHub **Release** with all three executables attached (the macOS `.app` is uploaded zipped, since it's a folder).
- Manually from the repo's "Actions" tab, with the "Run workflow" button (`workflow_dispatch`).

The `v*` pattern matches any tag that **starts with the letter `v`** — the rest can be anything:

| Tag | Triggers the build? |
|---|---|
| `v1.0.0` | ✅ Yes |
| `v2.3.1` | ✅ Yes |
| `v1.0.0-beta` | ✅ Yes |
| `v1` | ✅ Yes |
| `1.0.0` (no `v`) | ❌ No |
| `release-1.0` | ❌ No |

To use it, this project needs to be in a GitHub repository:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main

git tag v1.0.0
git push origin v1.0.0   # triggers the build + automatic release
```

The generated executables are available as "Artifacts" on every workflow run, and additionally attached to the Release if it was triggered by a tag.

### Alternative: Azure Pipelines

If you use Azure DevOps instead of (or alongside) GitHub, the repo also includes `azure-pipelines.yml`, equivalent to the workflow above: it uses Microsoft-hosted agents (`ubuntu-22.04`, `windows-latest`, `macOS-latest`) to build natively on all three systems — same idea, no Wine. The Linux agent is pinned to `ubuntu-22.04` (glibc 2.35) rather than `ubuntu-latest` so the resulting executable keeps running on systems with an older glibc.

- It triggers automatically on pushing a `v*` tag (same pattern as above: `v1.0.0` triggers the build, `1.0.0` without the `v` does not).
- It can also be run manually with the "Run pipeline" button in Azure DevOps, no extra configuration needed.
- The executables are published as *Pipeline Artifacts* (`GitMultiProfileSSH-linux`, `-windows`, `-macos`) downloadable from each run. Unlike the GitHub workflow, this one does not automatically create a Release (Azure DevOps treats "Releases" as a separate, multi-stage deployment concept); it can be added later if needed.

To use it: connect the repository in Azure DevOps → Pipelines → "New pipeline" → "Existing Azure Pipelines YAML file" → select `azure-pipelines.yml`.

## Key concepts

Before using the app, it helps to understand two ideas that come up throughout the interface:

### The "SSH Host" is an alias, not a real domain

When SSH connects to a repository, it decides which key to use based on the hostname in the URL. To be able to have several keys for the **same** provider (for example, two different GitHub accounts), the app creates an **alias** in `~/.ssh/config`, like `github.com-work`, which points to the real domain (`github.com`) but uses a specific key.

That's why, when cloning or configuring a repo's remote, you should **always use the alias**, not the real domain. The app does this for you automatically in the clone tab.

### The "Profile ID" must be the organization name

The ID you give a profile (e.g. `acme`, `work`, `client-x`) isn't just a label: it **must exactly match the name of the organization or owner of the repository** on the provider.

- On **Azure DevOps**, it's the word that appears right after `v3/` in the SSH URL:
  `git@ssh.dev.azure.com:v3/MyOrganization/MyProject/MyRepo` → the profile ID must be `myorganization`.
- On **GitHub / GitLab / Bitbucket** (or self-hosted), it's the user or organization that appears before the repo name:
  `git@github.com:MyOrganization/my-repo.git` → the profile ID must be `myorganization`.

This lets the app **validate that the repository really belongs to that organization** before letting you clone it — preventing you from accidentally mixing a repo from one company into another company's folder/profile.

## Usage guide

The window has three tabs: **Create Profile**, **Configured Profiles**, and **Clone Repo** (the latter only becomes active once at least one profile exists).

### 1. Create a profile

**"➕ Create Profile"** tab:

1. **Project Folder**: choose or create the folder where this profile (and the repos you clone with it) will live. It's the *final* folder — nothing gets appended to it automatically.
   - **Browse...**: select a folder that already exists.
   - **➕ New**: pick a parent folder and type the name of the new folder to create.
2. **Profile ID**: the organization's name (see [Key concepts](#key-concepts)).
3. **Developer Name** and **Email**: the data Git will use for commits made inside that folder.
4. **SSH Host (alias)**: auto-suggested by combining the real provider and the profile ID (e.g. `github.com-acme`). You can edit it if you prefer.
5. **Provider**: choose GitHub, GitLab, Bitbucket, Azure DevOps, or "Other (manual)" for self-hosted. This auto-fills the "Real Provider" field.
6. **Automatically generate a new SSH key**: if left on, a new Ed25519 key is generated for this profile (or reused if one with that name already exists).
7. Press **"🔥 SET UP EVERYTHING NOW"**.

This **doesn't save anything yet**: a confirmation window opens with a summary of the data. From there you can:
   - **Cancel** → nothing is written to disk, you go back to the form to fix things.
   - **💾 Save and Create Profile** → only then does it create the folder, write the Git/SSH configuration, and generate the key.

Once it's done, a window appears with:
- The SSH public key (with a button to copy it to the clipboard) — copy it and add it to your account on the corresponding provider.
- A personalized guide explaining how to clone, `push`/`pull`, migrate an existing repo to this profile, and test the SSH connection.

### 2. View and edit profiles

**"📋 Configured Profiles"** tab: lists every profile detected by reading `~/.gitconfig`, the `~/.gitconfig-<id>` files, and `~/.ssh/config`. Use **🔄 Refresh** if you made manual changes to those files.

Each profile has an **✏️ Edit** button that lets you change the name, email, SSH alias, and real provider. The profile ID and folder can't be edited here (if you need to change those, delete the profile and create a new one).

From that same edit dialog you can also **rotate the SSH key**: pick the type (`rsa`, `ed25519`, or `ecdsa`) and click **🔁 Rotate / Regenerate Key**. This generates a new key, updates `~/.ssh/config` automatically, and shows you the new public key to add to your Git provider — no need to delete or recreate the profile. The old key becomes invalid until you add the new one.

### 3. Delete a profile

**🗑️ Delete** button in the profile list. On confirmation, it removes:

- The matching `includeIf` entry in `~/.gitconfig`.
- The `~/.gitconfig-<id>` file.
- The matching `Host` block in `~/.ssh/config`.
- Optionally (checkbox, unchecked by default), the SSH key on disk.

**The project folder is never deleted or modified** — only the Git/SSH configuration is cleaned up.

### 4. Clone a repository

**"📥 Clone Repo"** tab (only available once you've created at least one profile):

1. Choose the **profile** you want to clone with.
2. Paste the repository's **SSH URL** (the one you get from the "Clone" → SSH button on GitHub/GitLab/Bitbucket/Azure DevOps). It should look like `git@host:path/repo.git` or `ssh://git@host/path/repo`.
3. The app validates automatically, live:
   - That the URL's **host** matches the profile's "Real Provider".
   - That the URL's **organization** matches the profile ID.
   - If anything doesn't match, the "Clone" button stays disabled and the reason is explained.
4. If everything matches, press **"📥 Clone Repository"**. The repo is cloned inside the profile's folder, and the URL is automatically rewritten to use the correct SSH alias — you don't need to run `git remote set-url` by hand.

## Changing the interface language

There's an **ES / EN** selector in the top-right corner. When you switch it:

- The whole interface is translated instantly.
- Anything you've typed into the forms (profile being created, clone URL, etc.) **is preserved**.
- The preference is saved to `~/.git_multiprofile_lang` and remembered the next time you open the app.

## Where the app writes files

The app only reads/writes these files inside your home folder — it never touches anything outside `$HOME`, and it never deletes project folders:

| File | What it holds |
|---|---|
| `~/.gitconfig` | `includeIf` blocks that redirect each profile's folder to its specific config. |
| `~/.gitconfig-<id>` | Git name and email for profile `<id>`. |
| `~/.ssh/config` | `Host <alias>` blocks with the real `HostName`, user, and key to use. |
| `~/.ssh/id_rsa_<id>` and `.pub` | The SSH private/public key generated for profile `<id>`. |
| `~/.git_multiprofile_lang` | Interface language (`es` or `en`). |

## FAQ / troubleshooting

**Why is the "Clone" button disabled?**
Could be several reasons, all explained in the message right above the button: no profiles exist yet, the selected profile has no SSH configured, the URL isn't valid, the provider doesn't match, or the URL's organization doesn't match the profile ID.

**I pasted the HTTPS URL and it doesn't work.**
The app only accepts SSH URLs (`git@host:...` or `ssh://git@host/...`). On the repository's page, switch the clone tab from "HTTPS" to "SSH" and copy that URL instead.

**How do I know if my SSH key was accepted by the provider?**
Run `ssh -T git@<your-alias>` in a terminal. The guide shown when you create each profile includes a specific note on what to expect for GitHub, GitLab, Bitbucket, and Azure DevOps (some, like Azure DevOps and Bitbucket, don't give an interactive shell — the absence of a "Permission denied" error already means it worked).

**I already had a repo cloned before creating the profile — what do I do?**
Update its remote to use the profile's alias:
```bash
git remote set-url origin git@<profile-alias>:<the-same-path-it-had-after-the-":">
git remote -v   # to confirm the change
```
This exact command, with your values filled in, also appears in the guide shown when you create the profile.

**I edited a profile and it seems like it didn't save.**
Make sure you press "💾 Save Changes" inside the edit window (not just close it). If the problem persists, check the console at the bottom of the main window — any error while saving shows up there.
