# Git Multi-Profile & SSH Automator

🇬🇧 [English version](README.en.md)

Herramienta de escritorio (GUI) para manejar **varias identidades de Git y llaves SSH** en la misma máquina — por ejemplo, una cuenta de trabajo en Azure DevOps y una personal en GitHub — sin tener que tocar `~/.gitconfig` ni `~/.ssh/config` a mano.

La interfaz está disponible en **español e inglés**, cambiables en cualquier momento desde la propia app.

---

## Índice

1. [¿Qué problema resuelve?](#qué-problema-resuelve)
2. [Requisitos](#requisitos)
3. [Instalación y ejecución](#instalación-y-ejecución)
4. [Generar un ejecutable standalone](#generar-un-ejecutable-standalone)
   - [Compilar el `.exe` de Windows desde Linux](#compilar-el-exe-de-windows-desde-linux-sin-tener-windows)
   - [Construir los tres con GitHub Actions](#construir-los-tres-ejecutables-automáticamente-con-github-actions)
   - [Alternativa: Azure Pipelines](#alternativa-azure-pipelines)
5. [Conceptos clave](#conceptos-clave)
6. [Guía de uso](#guía-de-uso)
   - [Crear un perfil](#1-crear-un-perfil)
   - [Ver y editar perfiles](#2-ver-y-editar-perfiles)
   - [Eliminar un perfil](#3-eliminar-un-perfil)
   - [Clonar un repositorio](#4-clonar-un-repositorio)
7. [Cambiar el idioma de la interfaz](#cambiar-el-idioma-de-la-interfaz)
8. [Dónde escribe la aplicación](#dónde-escribe-la-aplicación)
9. [Preguntas frecuentes / solución de problemas](#preguntas-frecuentes--solución-de-problemas)

---

## ¿Qué problema resuelve?

Cuando trabajas con Git en varios proveedores u organizaciones distintas (tu empresa, un cliente, tu cuenta personal), normalmente necesitas:

- Un nombre/email de Git distinto para cada uno.
- Una llave SSH distinta para cada uno (para no mezclar permisos entre cuentas).
- Configurar manualmente `~/.gitconfig` con bloques `includeIf` y `~/.ssh/config` con alias de `Host` — algo tedioso y fácil de hacer mal.

Esta app automatiza todo ese proceso con una interfaz gráfica: crea la carpeta del proyecto, genera la llave SSH, registra el alias en `~/.ssh/config`, y enlaza esa carpeta con el nombre/email correcto en `~/.gitconfig`. También te ayuda a clonar repositorios asegurando que terminen en la carpeta y con la identidad correctas.

## Requisitos

- Python 3.9 o superior.
- Git instalado y disponible en el `PATH`.
- `ssh-keygen` disponible en el `PATH` (viene con OpenSSH; en Linux/macOS ya está instalado, en Windows viene con Git for Windows o el cliente OpenSSH de Windows).
- La librería `customtkinter` (ver instalación abajo).

## Instalación y ejecución

```bash
# (opcional pero recomendado) crear un entorno virtual
python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate

# instalar dependencias
pip install -r requirements.txt

# ejecutar la app
python3 git_complete_automator.py
```

No requiere ninguna configuración adicional ni permisos especiales — solo lee y escribe en tu carpeta personal (`~/.gitconfig`, `~/.ssh/config`, etc.).

## Generar un ejecutable standalone

Si prefieres distribuir la app como un ejecutable de doble clic (sin que quien la use necesite instalar Python), se puede empaquetar con [PyInstaller](https://pyinstaller.org/) usando el script `build.py` incluido:

```bash
pip install -r requirements-dev.txt
python3 build.py
```

Esto genera el ejecutable en `dist/`:

- **Linux**: `dist/GitMultiProfileSSH` (binario ELF, márcalo ejecutable con `chmod +x` si es necesario).
- **Windows**: `dist/GitMultiProfileSSH.exe` (corriendo `build.py` en una máquina Windows real — funciona igual de bien que en Linux/macOS, es el mismo script Python sin nada específico de Wine).
- **macOS**: `dist/GitMultiProfileSSH.app` (corriendo `build.py` en una Mac real — no hace falta nada más, el mismo script ya detecta macOS y genera el bundle `.app` correcto; PyInstaller siempre empaqueta así cuando se usa `--windowed`, incluso con `--onefile`).

**Importante:** PyInstaller **no compila de forma cruzada** — el ejecutable generado solo funciona en el mismo sistema operativo donde lo construiste.

- Si tienes acceso físico a Windows y macOS, simplemente corre `python3 build.py` en cada uno.
- Si solo tienes Linux, para **Windows** puedes usar `./build_windows.sh` (ver abajo). Para **macOS no existe un atajo real** desde Linux — no hay "Wine para macOS", así que se necesita una Mac física, un servicio de Mac en la nube, o CI (ver siguiente sección).

### Compilar el `.exe` de Windows desde Linux (sin tener Windows)

`build_windows.sh` usa [Wine](https://www.winehq.org/) para instalar un Python real de Windows dentro de un prefix de Wine dedicado a este proyecto (`.wine-build/`, no toca tu `~/.wine`), y corre PyInstaller ahí dentro:

```bash
./build_windows.sh
```

- Si Wine no está instalado, el script te muestra el comando exacto para tu distro y se detiene (no instala nada por su cuenta).
- La primera vez descarga el instalador oficial de Python para Windows (~25 MB, se cachea en `.build-cache/`) y lo instala dentro del prefix — puede tardar unos minutos. Las siguientes veces reutiliza ese mismo Python y solo reconstruye el ejecutable.
- El resultado es un `.exe` de Windows real (verificable con `file dist/GitMultiProfileSSH.exe`), listo para copiar a una máquina Windows.

### Compilar un binario Linux compatible con distros más viejas (glibc)

PyInstaller enlaza el binario contra la glibc de la máquina donde corre el build. Si compilas `build.py` directamente en un Linux con una glibc reciente (por ejemplo Ubuntu 24.04, glibc 2.39), el ejecutable resultante **no correrá en sistemas más viejos** como Ubuntu 22.04 (glibc 2.35) — una glibc más nueva no es retrocompatible.

`build_linux_docker.sh` resuelve esto compilando dentro de un contenedor Docker `ubuntu:22.04`, sin tocar tu sistema:

```bash
./build_linux_docker.sh
```

- Si Docker no está instalado, el script te muestra el comando exacto para tu distro y se detiene.
- La primera vez construye una imagen con Python 3.11 y las dependencias de sistema necesarias (se cachea vía Docker, así que las siguientes corridas son mucho más rápidas).
- El resultado es el mismo `dist/GitMultiProfileSSH` de siempre, pero enlazado contra glibc 2.35 — corre en Ubuntu 22.04 y en cualquier distro más nueva. Puedes verificarlo con `objdump -T dist/GitMultiProfileSSH | grep GLIBC_ | sort -V | tail -1`.

Notas por sistema:

- **macOS**: al ser una app sin firmar, Gatekeeper bloqueará la primera ejecución. Haz clic derecho sobre el `.app` → "Abrir", o corre `xattr -dr com.apple.quarantine dist/GitMultiProfileSSH.app`.
- **Windows**: un `.exe` sin firmar puede activar la advertencia de SmartScreen ("Más información" → "Ejecutar de todas formas").
- **Linux**: si el archivo no tiene permiso de ejecución, corre `chmod +x dist/GitMultiProfileSSH`.

### Construir los tres ejecutables automáticamente con GitHub Actions

El repo incluye `.github/workflows/build.yml`, que corre `build.py` en runners **nativos** de Linux, Windows y macOS provistos por GitHub — sin Wine ni trucos, cada sistema se compila a sí mismo. Se activa:

- Automáticamente al hacer push de un tag con formato `v*` — además de compilar, crea un **Release** de GitHub con los tres ejecutables adjuntos (el `.app` de macOS se sube comprimido en `.zip`, ya que es una carpeta).
- Manualmente desde la pestaña "Actions" del repo, con el botón "Run workflow" (`workflow_dispatch`).

El patrón `v*` hace match con cualquier tag que **empiece con la letra `v`** — el resto puede ser lo que sea:

| Tag | ¿Dispara el build? |
|---|---|
| `v1.0.0` | ✅ Sí |
| `v2.3.1` | ✅ Sí |
| `v1.0.0-beta` | ✅ Sí |
| `v1` | ✅ Sí |
| `1.0.0` (sin la `v`) | ❌ No |
| `release-1.0` | ❌ No |

Para usarlo necesitas que este proyecto esté en un repositorio de GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <url-de-tu-repo>
git push -u origin main

git tag v1.0.0
git push origin v1.0.0   # dispara el build + release automático
```

Los ejecutables generados quedan disponibles como "Artifacts" en cada ejecución del workflow, y además adjuntos al Release si el disparo fue por un tag.

### Alternativa: Azure Pipelines

Si usas Azure DevOps en vez de (o además de) GitHub, el repo también incluye `azure-pipelines.yml`, equivalente al workflow anterior: usa los agentes hospedados de Microsoft (`ubuntu-22.04`, `windows-latest`, `macOS-latest`) para compilar nativamente en los tres sistemas — mismo principio, sin Wine. El agente Linux está fijado a `ubuntu-22.04` (glibc 2.35) en vez de `ubuntu-latest` para que el ejecutable siga corriendo en sistemas con glibc más antigua.

- Se activa automáticamente al pushear un tag `v*` (mismo patrón que en la sección anterior: `v1.0.0` sí dispara el build, `1.0.0` sin la `v` no).
- También se puede correr manualmente con el botón "Run pipeline" desde Azure DevOps, sin configuración extra.
- Los ejecutables quedan publicados como *Pipeline Artifacts* (`GitMultiProfileSSH-linux`, `-windows`, `-macos`) descargables desde cada ejecución. A diferencia del workflow de GitHub, este no crea un Release automáticamente (Azure DevOps maneja "Releases" como un concepto separado de despliegue multi-etapa); si lo necesitas, se puede agregar después.

Para usarlo: conecta el repositorio en Azure DevOps → Pipelines → "New pipeline" → "Existing Azure Pipelines YAML file" → selecciona `azure-pipelines.yml`.

## Conceptos clave

Antes de usar la app conviene entender dos ideas que se repiten en toda la interfaz:

### El "Host SSH" es un alias, no un dominio real

Cuando SSH se conecta a un repositorio, decide qué llave usar según el nombre de host que aparece en la URL. Para poder tener varias llaves para el **mismo** proveedor (por ejemplo dos cuentas distintas de GitHub), la app crea un **alias** en `~/.ssh/config`, del tipo `github.com-trabajo`, que apunta al dominio real (`github.com`) pero usa una llave específica.

Por eso, al clonar o configurar el remoto de un repo, **siempre debes usar el alias**, no el dominio real. La app hace esto automáticamente por ti en la pestaña de clonado.

### El "ID de Perfil" debe ser el nombre de la organización

El ID que le pones a un perfil (por ejemplo `acme`, `trabajo`, `cliente-x`) no es solo una etiqueta: **debe coincidir exactamente con el nombre de la organización o dueño del repositorio** en el proveedor.

- En **Azure DevOps**, es la palabra que aparece justo después de `v3/` en la URL SSH:
  `git@ssh.dev.azure.com:v3/MiOrganizacion/MiProyecto/MiRepo` → el ID de perfil debe ser `miorganizacion`.
- En **GitHub / GitLab / Bitbucket** (o self-hosted), es el usuario u organización que aparece antes del nombre del repo:
  `git@github.com:MiOrganizacion/mi-repo.git` → el ID de perfil debe ser `miorganizacion`.

Esto permite que, al clonar, la app **valide que el repositorio realmente pertenece a esa organización** antes de dejarte clonarlo — así evitas mezclar por error un repo de una empresa dentro de la carpeta/perfil de otra.

## Guía de uso

La ventana tiene tres pestañas: **Crear Perfil**, **Perfiles Configurados** y **Clonar Repo** (esta última solo se activa cuando ya existe al menos un perfil).

### 1. Crear un perfil

Pestaña **"➕ Crear Perfil"**:

1. **Carpeta del Proyecto**: elige o crea la carpeta donde vivirá este perfil (y los repos que clones con él). Es la carpeta *final*, no una carpeta base a la que se le añade nada automáticamente.
   - **Examinar...**: selecciona una carpeta que ya existe.
   - **➕ Nueva**: elige una carpeta padre y escribe el nombre de la nueva carpeta a crear.
2. **ID de Perfil**: el nombre de la organización (ver [Conceptos clave](#conceptos-clave)).
3. **Nombre del Desarrollador** y **Email**: los datos que Git usará para los commits hechos dentro de esa carpeta.
4. **Host SSH (alias)**: se sugiere automáticamente combinando el proveedor real y el ID de perfil (por ejemplo `github.com-acme`). Puedes editarlo si lo prefieres.
5. **Proveedor**: elige GitHub, GitLab, Bitbucket, Azure DevOps, u "Otro (manual)" para self-hosted. Esto autocompleta el campo "Proveedor Real".
6. **Generar nueva llave SSH automáticamente**: si lo dejas activado, se genera una llave Ed25519 nueva para este perfil (o se reutiliza si ya existe una con ese nombre).
7. Pulsa **"🔥 CONFIGURAR TODO AHORA"**.

Esto **no guarda nada todavía**: se abre una ventana de confirmación con el resumen de los datos. Ahí puedes:
   - **Cancelar** → no se toca el disco, vuelves al formulario para corregir.
   - **💾 Guardar y Crear Perfil** → recién ahí se crea la carpeta, se escribe la configuración de Git y SSH, y se genera la llave.

Al terminar, aparece una ventana con:
- La llave pública SSH (con botón para copiarla al portapapeles) — cópiala y agrégala a tu cuenta en el proveedor correspondiente.
- Una guía personalizada explicando cómo clonar, hacer `push`/`pull`, migrar un repo ya existente a este perfil, y cómo probar la conexión SSH.

### 2. Ver y editar perfiles

Pestaña **"📋 Perfiles Configurados"**: lista todos los perfiles detectados leyendo `~/.gitconfig`, los archivos `~/.gitconfig-<id>` y `~/.ssh/config`. Usa **🔄 Refrescar** si hiciste cambios manuales a esos archivos.

Cada perfil tiene un botón **✏️ Editar** que permite cambiar el nombre, email, alias SSH y proveedor real. El ID de perfil y la carpeta no se pueden editar aquí (si necesitas cambiarlos, elimina el perfil y crea uno nuevo).

Desde ese mismo diálogo de edición también puedes **rotar la llave SSH**: elige el tipo (`rsa`, `ed25519` o `ecdsa`) y pulsa **🔁 Rotar / Regenerar Llave**. Esto genera una llave nueva, actualiza `~/.ssh/config` automáticamente y te muestra la nueva clave pública para que la agregues en tu proveedor Git — no hace falta borrar ni recrear el perfil. La llave anterior queda inválida hasta que agregues la nueva.

### 3. Eliminar un perfil

Botón **🗑️ Eliminar** en la lista de perfiles. Al confirmar, se elimina:

- La entrada `includeIf` correspondiente en `~/.gitconfig`.
- El archivo `~/.gitconfig-<id>`.
- El bloque `Host` correspondiente en `~/.ssh/config`.
- Opcionalmente (checkbox, desmarcado por defecto), la llave SSH del disco.

**La carpeta del proyecto nunca se borra ni se modifica** — solo se limpia la configuración de Git/SSH.

### 4. Clonar un repositorio

Pestaña **"📥 Clonar Repo"** (solo disponible si ya tienes al menos un perfil creado):

1. Elige el **perfil** con el que quieres clonar.
2. Pega la **URL SSH** del repositorio (la que obtienes con el botón "Clone" → SSH en GitHub/GitLab/Bitbucket/Azure DevOps). Debe verse como `git@host:ruta/repo.git` o `ssh://git@host/ruta/repo`.
3. La app valida automáticamente, en vivo:
   - Que el **host** de la URL coincida con el "Proveedor Real" del perfil.
   - Que la **organización** de la URL coincida con el ID del perfil.
   - Si algo no coincide, el botón "Clonar" queda deshabilitado y se explica por qué.
4. Si todo coincide, pulsa **"📥 Clonar Repositorio"**. El repo se clona dentro de la carpeta del perfil, y la URL se reescribe automáticamente para usar el alias SSH correcto — no necesitas hacer `git remote set-url` a mano.

## Cambiar el idioma de la interfaz

En la esquina superior derecha hay un selector **ES / EN**. Al cambiarlo:

- Toda la interfaz se traduce al instante.
- Los datos que hayas escrito en los formularios (perfil en creación, URL de clonado, etc.) **se conservan**.
- La preferencia se guarda en `~/.git_multiprofile_lang` y se recuerda la próxima vez que abras la app.

## Dónde escribe la aplicación

La app solo lee/escribe en estos archivos de tu carpeta personal — nunca modifica nada fuera de `$HOME`, y nunca borra carpetas de proyectos:

| Archivo | Qué contiene |
|---|---|
| `~/.gitconfig` | Bloques `includeIf` que redirigen cada carpeta de perfil a su configuración específica. |
| `~/.gitconfig-<id>` | Nombre y email de Git para el perfil `<id>`. |
| `~/.ssh/config` | Bloques `Host <alias>` con el `HostName` real, el usuario y la llave a usar. |
| `~/.ssh/id_rsa_<id>` y `.pub` | Llave SSH privada/pública generada para el perfil `<id>`. |
| `~/.git_multiprofile_lang` | Idioma de la interfaz (`es` o `en`). |

## Preguntas frecuentes / solución de problemas

**¿Por qué el botón "Clonar" está deshabilitado?**
Puede ser por varias razones, todas explicadas en el mensaje que aparece justo arriba del botón: no hay perfiles creados, el perfil elegido no tiene SSH configurado, la URL no es válida, el proveedor no coincide, o la organización de la URL no coincide con el ID del perfil.

**Pegué la URL de HTTPS y no funciona.**
La app solo acepta URLs SSH (`git@host:...` o `ssh://git@host/...`). En la página del repositorio, cambia la pestaña de clonado de "HTTPS" a "SSH" y copia esa URL.

**¿Cómo sé si mi llave SSH fue aceptada por el proveedor?**
Corre `ssh -T git@<tu-alias>` en una terminal. La guía que se muestra al crear cada perfil incluye una nota específica de qué esperar para GitHub, GitLab, Bitbucket y Azure DevOps (algunos, como Azure DevOps y Bitbucket, no dan una shell interactiva — la ausencia de un error de "Permission denied" ya significa que funcionó).

**Ya tenía un repo clonado antes de crear el perfil, ¿qué hago?**
Actualiza su remoto para que use el alias del perfil:
```bash
git remote set-url origin git@<alias-del-perfil>:<misma-ruta-que-tenía-después-de-los-":">
git remote -v   # para confirmar el cambio
```
Este comando exacto, con tus valores, también aparece en la guía que se muestra al crear el perfil.

**Edité un perfil y parece que no guardó.**
Asegúrate de presionar "💾 Guardar Cambios" dentro de la ventana de edición (no solo cerrarla). Si el problema persiste, revisa la consola al final de la ventana principal — cualquier error al guardar se muestra ahí.
