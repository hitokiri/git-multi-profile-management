#!/usr/bin/env python3
"""Regenerates the README screenshots and the walkthrough (demo.gif + demo.mp4) in docs/images/<lang>/
from the real app, using demo data.

Runs on a virtual display with a throwaway HOME, so it never touches (or shows) your real
~/.gitconfig, ~/.ssh or desktop. Needs Xvfb, Pillow and the app's requirements (plus ffmpeg for the MP4):

    pip install Pillow -r requirements.txt
    xvfb-run -a -s "-screen 0 1600x1400x24" python3 docs/make_screenshots.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = tempfile.mkdtemp(prefix="gmp-demo-")
os.environ["HOME"] = HOME  # before importing the app: it resolves ~ paths at import time
os.environ.pop("XDG_DATA_HOME", None)
sys.path.insert(0, ROOT)

import customtkinter as ctk  # noqa: E402
from PIL import ImageGrab  # noqa: E402

import git_complete_automator as g  # noqa: E402

LANG = sys.argv[1] if len(sys.argv) > 1 else None
GITLEAKS = ["ok", "8.30.1", None]  # mutated per shot; no network while capturing
g.ensure_gitleaks = lambda: tuple(GITLEAKS)


def write_demo_profiles():
    hooks = g.GitSSHAutomationApp._to_gitconfig_path(g.gitleaks_paths()["hooks"])
    os.makedirs(os.path.join(HOME, ".ssh"), exist_ok=True)
    demo = (("acme", "github.com", True), ("contoso", "ssh.dev.azure.com", False))
    with open(os.path.join(HOME, ".gitconfig"), "w") as gc, open(os.path.join(HOME, ".ssh", "config"), "w") as sc:
        for pid, host, protected in demo:
            # Shown in the profile cards: a neutral path instead of the temp HOME.
            gc.write(f'[includeIf "gitdir:/home/usuario/proyectos/{pid}/"]\n    path = {HOME}/.gitconfig-{pid}\n')
            with open(os.path.join(HOME, f".gitconfig-{pid}"), "w") as f:
                f.write(f"[user]\n    name = Ana {pid.title()}\n    email = ana@{pid}.com\n")
                if protected:
                    f.write(f"[core]\n    hooksPath = {hooks}\n")
            sc.write(f"# Perfil Autogenerado: {pid}\nHost {host}-{pid}\n    HostName {host}\n"
                     f"    User git\n    IdentityFile {HOME}/.ssh/id_ed25519_{pid}\n\n")


def run(lang):
    out = os.path.join(ROOT, "docs", "images", lang)
    os.makedirs(out, exist_ok=True)
    write_demo_profiles()
    with open(os.path.join(HOME, ".git_multiprofile_lang"), "w") as f:
        f.write(lang)
    with open(os.path.join(HOME, ".git_multiprofile_theme"), "w") as f:
        f.write("Light")

    app = g.GitSSHAutomationApp()

    def grab(name, crop_height=None):
        app.update()
        x, y = app.winfo_rootx(), app.winfo_rooty()
        h = crop_height or app.winfo_height()
        ImageGrab.grab(bbox=(x, y, x + app.winfo_width(), y + h), xdisplay=os.environ["DISPLAY"]).save(
            os.path.join(out, f"{name}.png"), optimize=True)
        print("wrote", os.path.join(out, f"{name}.png"))

    def notice_shot(status):
        GITLEAKS[:] = status
        app._gitleaks_status = tuple(status)
        app._render_gitleaks_badge()
        app._render_notice()

    def fill_create_form():
        app.selected_base_path.set("/home/usuario/proyectos/globex")
        app.profile_id_entry.insert(0, "globex")
        app.git_name_entry.insert(0, "Ana Globex")
        app.git_email_entry.insert(0, "ana@globex.com")
        app.update_ssh_host_suggestion()

    def fill_clone_form():
        app.tabview.set(app.TAB_CLONE)
        app.on_tab_change()
        app.clone_profile_menu.set("acme")
        app.clone_url_entry.insert(0, "git@github.com:acme/api.git")
        app.validate_clone_form()

    def go_list():
        app.tabview.set(app.TAB_LIST)
        app.on_tab_change()

    steps = [
        # (action before capture, shot name, crop height)
        (lambda: (app._dismissed_notices.add("unprotected"), app._render_notice(), fill_create_form()), "create-profile", None),
        (lambda: app._set_advanced_visible(True), "advanced-options", None),
        (lambda: (app._set_advanced_visible(False), app._dismissed_notices.clear(), go_list()), "profiles", None),
        (lambda: notice_shot(["ok", "8.30.1", "installed"]) or app._dismissed_notices.add("unprotected") or app._render_notice(), "notice-installed", 130),
        (lambda: notice_shot(["error", "offline", None]), "notice-error", 130),
        (lambda: (notice_shot(["ok", "8.30.1", None]), app._dismissed_notices.clear(), app._render_notice()), "notice-unprotected", 130),
        (fill_clone_form, "clone", None),
        (lambda: (ctk.set_appearance_mode("Dark"), app.theme_switch.set(app._theme_labels()["Dark"]), go_list()), "dark-theme", None),
        (lambda: (ctk.set_appearance_mode("Light"), app.theme_switch.set(app._theme_labels()["Light"]),
                  app.tabview.set(app.TAB_CREATE), app._set_console_visible(False), app.log("demo"), app.log("demo")), "console-hidden", None),
    ]

    def step(i=0):
        if i == len(steps):
            app.destroy()
            return
        action, name, crop = steps[i]
        action()
        app.update()
        app.after(600, lambda: (grab(name, crop), step(i + 1)))

    app.after(1000, step)
    app.mainloop()


def run_demo(lang):
    """Walkthrough as docs/images/<lang>/demo.gif (README) and demo.mp4 (needs ffmpeg).
    Each step is (action, ms to hold the frame, keep in the GIF?); typing makes one frame per
    keystroke so the video looks natural, but the GIF only keeps the final one to stay small."""
    import shutil as _shutil
    import subprocess
    from PIL import Image
    write_demo_profiles()
    with open(os.path.join(HOME, ".git_multiprofile_lang"), "w") as f:
        f.write(lang)
    with open(os.path.join(HOME, ".git_multiprofile_theme"), "w") as f:
        f.write("Light")
    app = g.GitSSHAutomationApp()
    frames = []

    def set_text(entry, text):
        entry.delete(0, "end")
        entry.insert(0, text)
        app.update_ssh_host_suggestion()
        if entry is app.clone_url_entry:
            app.validate_clone_form()

    def typing(entry_getter, text, hold):
        keys = [(lambda t=text[:i]: set_text(entry_getter(), t), 70, False) for i in range(1, len(text))]
        return keys + [(lambda: set_text(entry_getter(), text), hold, True)]

    def go(tab):
        app.tabview.set(tab)
        app.on_tab_change()

    def pick_clone_profile():
        go(app.TAB_CLONE)
        app.clone_profile_menu.set("acme")
        app.validate_clone_form()

    steps = [
        (lambda: None, 1800, True),
        (lambda: app.selected_base_path.set("/home/usuario/proyectos/globex"), 900, True),
        *typing(lambda: app.profile_id_entry, "globex", 700),
        *typing(lambda: app.git_name_entry, "Ana Globex", 700),
        *typing(lambda: app.git_email_entry, "ana@globex.com", 1500),
        (lambda: app._set_advanced_visible(True), 2500, True),
        (lambda: app._set_advanced_visible(False), 800, True),
        (lambda: go(app.TAB_LIST), 2500, True),
        (lambda: app.enable_secret_scan_for([p for p in app.parse_profiles() if not p.get("secret_scan")]), 2200, True),
        (pick_clone_profile, 900, True),
        *typing(lambda: app.clone_url_entry, "git@github.com:acme/api.git", 2500),
        (lambda: (ctk.set_appearance_mode("Dark"), app.theme_switch.set(app._theme_labels()["Dark"]), go(app.TAB_LIST)), 2200, True),
        (lambda: app._set_console_visible(False), 2500, True),
    ]

    def capture(ms, keep):
        app.update()
        x, y = app.winfo_rootx(), app.winfo_rooty()
        img = ImageGrab.grab(bbox=(x, y, x + app.winfo_width(), y + app.winfo_height()), xdisplay=os.environ["DISPLAY"])
        frames.append((img, ms, keep))

    def step(i=0):
        if i == len(steps):
            app.destroy()
            return
        action, ms, keep = steps[i]
        action()
        app.update()
        app.after(400 if keep else 60, lambda: (capture(ms, keep), step(i + 1)))

    app.after(1000, step)
    app.mainloop()

    # Window height changes between steps; pad every frame to the tallest one (even size for H.264).
    w = max(f.width for f, _, _ in frames)
    h = max(f.height for f, _, _ in frames)
    w, h = w + w % 2, h + h % 2

    def pad(f):
        canvas = Image.new("RGB", (w, h), f.getpixel((2, f.height - 2)))
        canvas.paste(f, (0, 0))
        return canvas

    out_dir = os.path.join(ROOT, "docs", "images", lang)
    gif_frames = [(pad(f), ms) for f, ms, keep in frames if keep]
    gif = os.path.join(out_dir, "demo.gif")
    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=128) for f, _ in gif_frames]
    pal[0].save(gif, save_all=True, append_images=pal[1:], duration=[ms for _, ms in gif_frames],
                loop=0, optimize=True, disposal=1)
    print("wrote", gif)

    if not _shutil.which("ffmpeg"):
        print("ffmpeg not found: skipped demo.mp4")
        return
    fps = 25
    mp4 = os.path.join(out_dir, "demo.mp4")
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
         "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "26", "-preset", "slow",
         "-movflags", "+faststart", mp4],
        stdin=subprocess.PIPE,
    )
    for f, ms, _ in frames:
        data = pad(f).tobytes()
        for _ in range(max(1, round(ms * fps / 1000))):
            ff.stdin.write(data)
    ff.stdin.close()
    if ff.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print("wrote", mp4)


if __name__ == "__main__":
    if LANG and len(sys.argv) > 2 and sys.argv[2] == "demo":
        run_demo(LANG)
    elif LANG:
        run(LANG)
    else:
        # One process per language: the app reads its language once at startup.
        import subprocess
        for lang in ("es", "en"):
            subprocess.run([sys.executable, __file__, lang], check=True)
            subprocess.run([sys.executable, __file__, lang, "demo"], check=True)
