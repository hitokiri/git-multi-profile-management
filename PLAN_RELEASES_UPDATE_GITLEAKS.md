# Plan: DMG + AppImage real + Auto-update + Gitleaks

> **Estado**: `PENDING` — planificado, nada implementado todavía.
> **Creado**: 2026-09-12 · **Reescrito**: 2026-11-17 (reemplaza el plan anterior de solo auto-update, que tenía errores — ver §7).
> **Esfuerzo estimado**: ~1.5–2 días (la mitad es probar en las 3 plataformas reales).

## Progreso

| Fase | Qué | Estado |
|---|---|---|
| 0 | Versión en runtime + ícono | `DONE` (2026-11-17) |
| 1 | AppImage real (Linux) | `PENDING` |
| 2 | DMG (macOS) | `PENDING` |
| 3 | Auto-update in-app | `PENDING` |
| 4 | Gitleaks (CI + pre-commit) | `DONE` (2026-11-17) |
| 5 | Documentación (README es/en) | `PENDING` |

Orden: 0 → 1 → 2 → 3 (el updater depende de los formatos finales) · 4 es independiente, se puede hacer primero.

---

## Contexto (estado actual verificado)

| Aspecto | Hoy |
|---|---|
| App | Un solo archivo `git_complete_automator.py`, `GitSSHAutomationApp(ctk.CTk)`, solo stdlib + `customtkinter` |
| Build | `build.py` → PyInstaller `--onefile --windowed`, un build por SO |
| Versión | `build.py` la saca del tag git (`v1.2.0` → `1.2.0`) o auto-bumpea `VERSION`. **La app NO conoce su propia versión en runtime** (solo va en el nombre del archivo). |
| Linux | `GitMultiProfileSSH-<v>.AppImage` — **AppImage falso**: binario onefile renombrado |
| macOS | `GitMultiProfileSSH-<v>-macos.app` → el workflow lo zipea como `.app.zip` |
| Windows | `GitMultiProfileSSH-<v>.exe` |
| CI | `.github/workflows/build.yml` (tag `v*` → build 3 SO → GitHub Release). `azure-pipelines.yml` equivalente sin release |
| Repo GitHub | `hitokiri/git-multi-profile-management` |
| Ícono | No existe ninguno en el repo |
| Secretos | Scan baseline con gitleaks (2026-11-17): 11 commits, **0 leaks** |

---

## Fase 0 — Versión en runtime + ícono

**Por qué**: el updater necesita comparar "mi versión" vs "último release". El plan anterior proponía hardcodear `APP_VERSION` a mano → se desincroniza del tag que usa `build.py`. Mejor una sola fuente.

1. `build.py`: escribir siempre la versión resuelta en `VERSION` (hoy solo lo hace en builds locales; con tag no) y empaquetarla: `--add-data VERSION{os.pathsep}.`
2. App: una función que lea `VERSION` desde `getattr(sys, "_MEIPASS", <dir del script>)`. Desde código fuente lee el `VERSION` del repo.
3. Mostrar la versión en el header/título (barato, útil para soporte).
4. Ícono `assets/icon.png` (512×512) + derivados `.ico` (Windows) y `.icns` (macOS). AppImage **exige** ícono; DMG y .exe lo agradecen. Pasarlo a PyInstaller con `--icon`.
   - ✅ Hecho: ícono simple generado por `assets/make_icon.py` (rama git sobre azul CustomTkinter). También se usa como ícono de ventana en runtime.

## Fase 1 — AppImage real (Linux)

Estructura AppDir:
```
AppDir/
  AppRun                      # sh: exec "$APPDIR/usr/bin/GitMultiProfileSSH/GitMultiProfileSSH" "$@"
  gitmultiprofilessh.desktop  # Name, Exec=GitMultiProfileSSH, Icon=gitmultiprofilessh, Categories=Development;
  gitmultiprofilessh.png
  usr/bin/GitMultiProfileSSH/ # salida de PyInstaller --onedir
```

1. Linux pasa a `--onedir` (dentro del AppImage no tiene sentido onefile: doble extracción y arranque más lento).
2. `build.py` arma el AppDir y llama a `appimagetool` → `dist/GitMultiProfileSSH-<v>-x86_64.AppImage`.
3. `appimagetool`: `build.py` lo descarga a `.build-cache/` si no está en `PATH` (mismo patrón que `build_windows.sh` con el instalador de Python). **Pinear un release con tag + verificar sha256**, no `continuous`.
4. Correrlo con `APPIMAGE_EXTRACT_AND_RUN=1` → funciona en CI/Docker sin FUSE.
5. `build_linux_docker.sh`: ajustar el `find` final (ahora busca `-type f -name "GitMultiProfileSSH-*"`; sigue sirviendo) y confirmar que el contenedor tiene `file`/`desktop-file-validate` si appimagetool los pide.
6. Probar en Ubuntu 22.04 limpio (glibc 2.35) y en una distro reciente.

Bonus que da gratis: el runtime del AppImage exporta `$APPIMAGE` = ruta real del archivo → el updater sabe exactamente qué reemplazar (el plan anterior no tenía forma confiable de saberlo).

## Fase 2 — DMG (macOS)

1. macOS pasa a `--onedir` (PyInstaller 6 marca `--onefile` + `.app` como deprecado en macOS; además arranca más rápido).
2. Nombre del bundle **sin versión**: `GitMultiProfileSSH.app` — así en `/Applications` la ruta es estable entre updates. La versión va en el nombre del DMG.
3. `build.py` (rama Darwin), solo stdlib + `hdiutil` del sistema:
   ```
   staging/ ← GitMultiProfileSSH.app + symlink "Applications" -> /Applications
   hdiutil create -volname "Git Multi-Profile SSH" -srcfolder staging -fs HFS+ -format UDZO -ov dist/GitMultiProfileSSH-<v>-macos.dmg
   ```
4. `build.yml`: borrar el loop que zipea `.app` (el `find -type f -not -path "*.app/*"` ya copia el `.dmg`). Release queda: `.dmg`, `.AppImage`, `.exe`.
5. Sin firma/notarización (requiere Apple Developer $99/año) → Gatekeeper sigue pidiendo clic derecho → Abrir la primera vez. Fuera de alcance.
6. ⚠️ `macos-latest` es arm64 → el DMG solo corre en Apple Silicon. Problema preexistente; si hace falta Intel, agregar `macos-13` a la matriz (fuera de alcance salvo que lo pidas).

## Fase 3 — Auto-update in-app

### Flujo de usuario
1. App inicia → si está empaquetada (`sys.frozen`) chequea en background `GET https://api.github.com/repos/hitokiri/git-multi-profile-management/releases/latest` (timeout 10 s, cualquier error = silencio).
2. Si `tag_name` > versión actual → banner bajo el header: "Nueva versión X.Y.Z disponible" + **[Descargar y reiniciar]** + **[Después]**.
3. Descargar → barra de progreso en el banner → verificar → reemplazar → relanzar → cerrar la vieja.
4. Error en cualquier paso → mensaje en el banner + link al release para descarga manual. Nunca deja la instalación rota.

### Diseño (más simple y correcto que el plan anterior)
- **Sin proceso `--updater` separado.** Truco de rename-swap, todo dentro de la app:
  - Descargar a `<destino>.new` en **la misma carpeta** que el destino (mismo filesystem → `os.replace` atómico).
  - Verificar sha256 contra el campo `digest` que la API de GitHub da por asset.
  - Swap y relanzar:

| SO | Destino | Swap |
|---|---|---|
| Linux | `os.environ["APPIMAGE"]` | `chmod 755` + `os.replace(new, destino)` (el proceso viejo sigue montado del inode viejo, no molesta) |
| Windows | `sys.executable` (el `.exe` real) | Windows **sí permite renombrar** un exe en ejecución: `destino → destino.old`, `new → destino`. Al próximo arranque se borra `*.old`. |
| macOS | `Path(sys.executable).parents[2]` (el `.app`) | `hdiutil attach -nobrowse -readonly` del DMG → `ditto` el `.app` a `X.app.new` → `detach` → `X.app → X.app.old`, `X.app.new → X.app`, borrar `.old`. Se usa `ditto` y no `zipfile` porque `zipfile` rompe symlinks/permisos del bundle. |

  - Relanzar: `subprocess.Popen([...], start_new_session=True)` (macOS: `open -n X.app`) con `PYINSTALLER_RESET_ENVIRONMENT=1` en el env — sin eso, un exe PyInstaller lanzado desde otro hereda sus variables `_MEI*`/`_PYI*` y puede arrancar roto. Luego `self.destroy()`.
- **Threads**: red y descarga en `threading.Thread`; comunicar a la UI con `queue.Queue` + `self.after(100, poll)` — el mismo patrón que ya usa el clonado (`_clone_worker` / `_poll_clone_queue`). Nunca tocar widgets desde el thread.
- Comparación de versiones: tupla de ints. `releases/latest` ya excluye prereleases y drafts.
- Selección de asset por sufijo: `.AppImage` / `.exe` / `.dmg`.
- Si la carpeta destino no es escribible (ej. `C:\Program Files`) → no intentar, mostrar link de descarga manual.
- Ejecutando desde código fuente (`python git_complete_automator.py`) → no se chequea nada (si no, "reemplazaría" el intérprete de Python).

### Firma de updates (idea tomada de Handy — `cjpais/handy`)
Handy (Tauri) firma cada asset del release con minisign (`<asset>.sig`) y la app trae embebida la llave pública: solo instala si la firma verifica. Eso protege incluso si alguien sube un binario falso al release. Lo replicamos **sin dependencias nuevas** usando `ssh-keygen`, que la app ya exige en el `PATH`:
- Una vez: `ssh-keygen -t ed25519 -f update_signing_key -N ""`. Privada → secret de GitHub `UPDATE_SIGNING_KEY`. Pública → constante en el código (`UPDATE_PUBKEY = "ssh-ed25519 AAAA..."`).
- CI (job `release`, antes de publicar): por cada asset `ssh-keygen -Y sign -f key -n gitmultiprofile-update <asset>` → sube `<asset>.sig`.
- App: descarga asset + `.sig`, escribe un `allowed_signers` temporal con la pública y corre `ssh-keygen -Y verify -f allowed_signers -I gitmultiprofile -n gitmultiprofile-update -s <asset>.sig < <asset>`. Exit ≠ 0 → aborta y borra el `.new`.
- Requiere OpenSSH ≥ 8.0 (2019; Windows 10/11 y Git for Windows lo traen). Si `ssh-keygen -Y` no existe → banner con link de descarga manual, nunca instalar sin verificar.
- Reemplaza al chequeo sha256 de `digest` (la firma ya cubre integridad).

### Otras ideas de Handy que sí aplican (baratas)
- **Kill-switch por variable de entorno**: Handy respeta `HANDY_DISABLE_UPDATER`. Acá: `GITMULTIPROFILE_DISABLE_UPDATER=1` → no se consulta nada. Útil para equipos corporativos/gestionados. Una línea.
- **Instalación "portable"/no actualizable** → en vez de fallar, diálogo con link al release (ya cubierto por "carpeta no escribible").
- **Estados del banner** como en su footer: buscando → disponible → descargando NN% → instalando → error. Sin "estás al día" (no hay botón de chequeo manual — se agrega si lo piden).

### Lo que NO se toma de Handy
- `tauri-plugin-updater` / `latest.json`: es del stack Tauri. La API `releases/latest` + `.sig` cubre lo mismo sin generar un manifiesto.
- Firma de código de SO (Azure Trusted Signing, Apple Developer ID): cuesta dinero; sigue fuera de alcance.
- Artefacto aparte `.app.tar.gz` para el updater de macOS: alternativa válida (`tarfile` preserva symlinks), pero con el DMG + `hdiutil` se publica un solo asset por SO.

### Detalles
- I18N: ~6 claves nuevas en `es` y `en` (`update_available`, `update_now`, `update_later`, `update_downloading`, `update_failed`, `update_manual_link`).
- "Después" solo oculta el banner por esta sesión (sin persistir "saltar esta versión" — se agrega si molesta).
- La versión 1.1.1 actual no tiene updater: los usuarios existentes deben actualizar a mano **una vez**.
- Nota: el archivo mantiene su nombre original tras actualizar (ej. `GitMultiProfileSSH-1.2.0.exe` contiene 1.3.0). Aceptable: cambiar el nombre rompería accesos directos. En macOS no pasa (bundle sin versión).
- Test: la comparación de versiones y la selección de asset son funciones puras → un par de asserts. El swap se prueba manualmente en cada SO publicando un release `vX.Y.Z` de prueba.

### Riesgos
- Rate limit API GitHub sin token: 60 req/h por IP → 1 request por arranque, irrelevante.
- Windows SmartScreen / macOS Gatekeeper: los archivos bajados con `urllib` no reciben el atributo de cuarentena, así que el relanzamiento no debería disparar avisos. Verificar en la prueba real.
- Firma: si se pierde la llave privada, las apps instaladas no aceptan más updates (habría que actualizar a mano una vez con una llave nueva). Guardar backup offline. Si se filtra, rotarla igual.

## Fase 4 — Gitleaks como función de la app — `DONE` 2026-11-17

Decisiones del usuario: la **app** instala/configura/actualiza gitleaks de forma transparente; solo carpetas de **perfiles**; **descarga al primer uso** + auto-update; **bloquear** el commit; escaneo 100% local (nada de CI ni nube).

- `ensure_gitleaks()` (hilo al iniciar): consulta `releases/latest` de gitleaks, baja el asset del SO/arquitectura, verifica sha256 contra el `digest` de la API, extrae solo el ejecutable, swap atómico. Offline con versión instalada = sigue OK. Carpeta: `<datos de la app>/gitleaks/` (`~/.local/share/GitMultiProfileSSH`, `~/Library/Application Support/...`, `%LOCALAPPDATA%\...`).
- Hooks gestionados (`gitleaks/hooks/`, reescritos en cada arranque): `pre-commit` corre `gitleaks git --pre-commit --staged --redact` y bloquea; todos los hooks de cliente **encadenan** al `.git/hooks/<name>` del repo (git-lfs, etc. siguen funcionando). Sin binario aún → avisa y deja pasar.
- Activación por perfil: `core.hooksPath` en `~/.gitconfig-<id>` vía `git config --file` (no pisa otras claves). **Obligatoria** (decisión del usuario): todo perfil nuevo la lleva, sin casilla ni botón Desactivar; perfiles viejos → botón Activar por tarjeta + aviso "N perfiles sin protección → Activar en todos". `save_profile_edit` ahora usa `git config --file` para name/email (antes reescribía el archivo y habría borrado el hook).
- UI: indicador `🛡 gitleaks X.Y.Z` en la cabecera + **barra de avisos bajo la cabecera** (visible desde cualquier pestaña, cerrable con ✕): gitleaks instalado/actualizado, error con Reintentar, perfiles sin protección con Activar en todos. **Fase 3 debe reutilizar esta barra** (`_pick_notice`/`_render_notice`) para el aviso de nueva versión de la app.
- Pruebas: `tests/test_secret_scan.py` (offline, gitleaks falso: bloqueo, encadenado, sin binario). E2E real: descarga 1.5 s, segunda vez sin descargar, secreto real bloqueado. UI verificada en Xvfb (toggle, editar conserva protección, activar en todos).
- Límite conocido: repos con `core.hooksPath` local propio (husky) no quedan cubiertos.

**Hallazgo colateral**: todas las acciones de `build.yml` corrían en Node 20, que GitHub retiró de sus runners el 2026-09-16 → el pipeline de release estaba roto. Subidas a la mayor más baja con Node 24: `checkout@v5`, `setup-python@v6`, `upload-artifact@v6`, `download-artifact@v7`, `action-gh-release@v3` (sin cambios incompatibles para este uso). Sin verificar en CI todavía.

## Fase 5 — Documentación

Al cerrar cada fase, actualizar `README.md` y `README.en.md`:
- Instalación: nombres de assets nuevos (`.dmg`, `.AppImage` real, `.exe`).
- Nueva sección "Actualizaciones automáticas" (qué consulta, que solo hace 1 request a GitHub al iniciar, que verifica la firma, `GITMULTIPROFILE_DISABLE_UPDATER=1` para desactivarlo).
- Para mantenedores: cómo generar/rotar la llave de firma y el secret `UPDATE_SIGNING_KEY`.
- Build: AppImage/DMG, `appimagetool`, `--onedir`.
- Sección de seguridad/contribuir: gitleaks + pre-commit.
- "Dónde escribe la aplicación": el updater solo escribe junto al ejecutable (`.new` / `.old` temporales).

> Los nombres de archivo actuales (`-<versión>`, sufijo `.AppImage`) ya se corrigieron en los README el 2026-11-17; estaban desactualizados.

---

## §7 Qué se corrigió del plan anterior

- Owner del repo era `hiko` → es `hitokiri`.
- `APP_VERSION` hardcodeado a mano → se desincroniza del tag de `build.py`. Ahora se empaqueta `VERSION`.
- Proceso `--updater` que sobreescribe el `.exe`: no funciona — ese proceso es el mismo `.exe` bloqueado. Reemplazado por rename-swap.
- "En Linux `sys.argv[0]` apunta al temp dir": falso para onefile; y con AppImage real se usa `$APPIMAGE`.
- Descomprimir el `.app.zip` con Python rompe el bundle → se usa DMG + `ditto`.
- Faltaba: verificación de firma (ssh-keygen -Y, idea de Handy), `PYINSTALLER_RESET_ENVIRONMENT`, no chequear updates corriendo desde código fuente, threading seguro con Tk.

## Fuera de alcance
Firma de código (Apple/Authenticode), build Intel para macOS, rollback automático, canal beta, delta updates/zsync, ícono en bandeja del sistema.
