# Bitácora UI/UX — Git Multi-Profile & SSH Automator

Registro de trabajo sobre la interfaz de escritorio (CustomTkinter), para retomar
sin tener que reconstruir el contexto desde cero. Se actualiza en cada sesión.

> **Nota de alcance:** la app es de **escritorio** (CustomTkinter 6.0), no web,
> aunque en la conversación original se la llamó "interfaz web". Se descartó
> migrar a Flet/PySide6 salvo que en algún momento se necesite acceso remoto
> por navegador — una app que escribe en `~/.ssh` y ejecuta `ssh-keygen` es
> conceptualmente de escritorio.

---

## Checklist del plan (7 fases + Parte 1)

- [x] **Parte 1 — Clonado con feedback visual.** El problema original: al
  darle "Clonar" no pasaba nada visible hasta el final (ventana congelada).
- [x] **Fase 0 — Tokens de diseño.** Colores y tipografía centralizados.
- [x] **Fase 1 — Tamaño de ventana correcto.** *(Redimensionado se intentó y
  se revirtió — ver bitácora. Lo que quedó es el tamaño fijo correcto.)*
- [ ] **Fase 2 — Sidebar en vez de `CTkTabview`** (elimina el hack de API
  privada `tabview._segmented_button._buttons_dict` usado para deshabilitar
  la pestaña "Clonar" sin perfiles).
- [~] **Fase 3 — Validación inline por campo** *(sesión 3: "Avanzado" colapsado hecho; falta validación inline y tooltips)* + `CTkToolTip` + colapsar
  "Avanzado" (alias SSH, tipo de llave) en el formulario de creación.
- [~] **Fase 4 — Estados vacíos** *(sesión 3: lista vacía con CTA hecha; Clonar bloqueada aún sin explicación propia)* (lista de perfiles vacía, pestaña Clonar
  bloqueada sin perfiles — hoy no explican por qué).
- [ ] **Fase 5 — Unificar feedback.** Hay ~21 `messagebox.*` nativos de Tk
  mezclados con 5 `CTkToplevel` propios; los nativos no siguen el tema ni el
  modo oscuro. Pasar a banners inline + `CTkMessagebox` (add-on de Akascape).
- [~] **Fase 6 — Tema.** *(Toggle Claro/Oscuro/Auto hecho en sesión 3; falta el JSON de tema propio.)* JSON de tema propio (partiendo de CTkThemesPack o
  CTkThemeMaker) + toggle Claro/Oscuro/Sistema en la cabecera. *(Siguiente
  paso pendiente de arrancar.)*
- [~] **Fase 7 — Pulido.** *(sesión 3: Enter envía el formulario; ícono de app/ventana)* Iconos en vez de emoji (se ven mal en Linux),
  orden de foco, atajos de teclado (Enter para enviar).

Extra de alto valor, aún no agendado en ninguna fase: botón "Probar conexión"
(`ssh -T git@alias`) en cada tarjeta de perfil.

---

## Bitácora cronológica

### Sesión 1 — Parte 1: clonado con feedback visual

**Problema reportado:** al clonar un repo no había ninguna señal visual tras
darle al botón.

**Diagnóstico:** `subprocess.run` bloqueaba el hilo de la UI → la ventana se
congelaba y Tk nunca repintaba, aunque el código sí escribía en el log.

**Implementado** (`git_complete_automator.py`, alrededor de `create_clone_tab`
línea 1109 y `do_clone_repo` línea 1488):
- Clonado en hilo aparte + `queue.Queue` + `self.after(100, ...)` para no
  bloquear el mainloop nunca.
- Progreso real parseado de `git clone --progress` (stderr, separado por
  `\r`, no por líneas). Barra `indeterminate` mientras git conecta,
  `determinate` en cuanto llega el primer `%`. Método `_clone_worker`.
- Botón "Cancelar clonado" (`terminate()` + limpieza de carpeta parcial).
- Pre-flight checks: `git` en PATH, llave SSH en disco, carpeta destino
  escribible, carpeta destino no existe ya.
- Errores de git traducidos a 5 casos reales (llave rechazada, repo sin
  acceso, host key cambiada, red, destino ocupado) con el stderr crudo
  detrás de un "▸ Ver detalle técnico" colapsable.
- Tarjeta de éxito persistente (ya no un `messagebox` que se pierde al
  cerrar) con **Abrir carpeta** / **Copiar ruta** / **Clonar otro**.
- ~35 claves de i18n nuevas (ES/EN) para todo lo anterior.

**Verificado con:** script E2E que levanta la app real (`withdraw()`, sin
mostrarse en pantalla), clona contra un repo local vía `insteadOf` en
`.gitconfig` (sin red real), y cubre éxito, pre-flight, error con detalle
expandible, y cancelación de un clon lento con un `git` falso que emite
progreso con `\r` real. 37/37 checks en verde.

---

### Sesión 2 — Fase 0 (tokens de diseño) + Fase 1 (ventana)

**Fase 0 — Tokens de diseño.** Clase `UI` (`git_complete_automator.py:23`)
centralizando:
- Colores de estado como tuplas `(claro, oscuro)`: `SUCCESS`, `ERROR`,
  `WARNING`, `MUTED` — antes eran hex fijos (`#2e7d32`, `"gray"`...) que
  quedaban casi ilegibles en modo oscuro.
- Colores de botones destructivos/cautelosos: `DANGER_BG/HOVER`,
  `CAUTION_BG/HOVER`, `NEUTRAL_BTN` (se dejaron como hex fijo a propósito:
  un botón "eliminar" debe verse rojo igual en ambos modos).
- Escala tipográfica `SIZE_HELP` (11, antes había 9 y 10 — ilegible) hasta
  `SIZE_HEADER` (22).
- Sustituidos ~24 `font=ctk.CTkFont(size=N)` y ~20 colores hex sueltos por
  todo el archivo.

**Fase 1 — Ventana redimensionable → PROBADA Y REVERTIDA.**

Se implementó completa: `minsize` calculado dinámicamente, consola de log
colapsable con botón ▸/▾, lógica para forzar el crecimiento de la ventana
si el usuario la había encogido y luego reabría la consola. Pasó toda la
verificación automatizada (21 checks, incluyendo redimensionados agresivos
y cambios de idioma).

**Hallazgo real en el camino** (esto **no** se revirtió, es un bug de
verdad): con la ventana fija original en `720x850`, la pestaña "Crear
Perfil" ya necesitaba ~1002-1010px de alto. Tk resolvía ese déficit
**aplastando la consola de log a ~18px** — casi invisible. Es probablemente
parte de por qué el feedback de la consola "no se veía" en el problema
original de la Parte 1, aparte del bloqueo de hilo.

**El usuario probó la versión redimensionable a mano y no le gustó** ("da
muchos problemas con lo que tenemos hasta ahora"). Se revirtió:
- Se quitó toda la lógica dinámica: `_apply_resizable_floor`, `minsize`,
  la consola colapsable (`_toggle_console`, botón, claves i18n
  `console_toggle_*`).
- Se mantuvo el arreglo real del tamaño: `_size_window_to_content()`
  (`git_complete_automator.py:876`) mide el tamaño real que necesita el
  contenido una sola vez (en `__init__` y en `on_language_changed`, justo
  después de `create_widgets()`) y llama `self.geometry(...)` +
  `self.resizable(False, False)`. Ventana **fija**, pero del tamaño
  correcto (~720x1010 en vez del `720x850` adivinado).

**Detalles técnicos por si se reintenta el redimensionado en el futuro**
(explican por qué la primera versión "daba problemas", no son un veto):
- `winfo_reqheight()` en CustomTkinter deja de ser confiable **después**
  de que la ventana pasó por al menos un resize (reproducido: encogerla
  por debajo de su mínimo y volver a crecerla deja el valor "pegado" a un
  número viejo — le pasa tanto al toplevel como a `CTkTabview`). Por eso
  cualquier futuro intento debe medir **una sola vez, justo tras
  construir los widgets**, y cachear ese valor en vez de remedir después
  de cualquier resize.
- `wm minsize()` no crece retroactivamente una ventana ya abierta — solo
  limita futuros arrastres del usuario. Hay que forzar `geometry()` a mano
  si el piso mínimo sube por encima del tamaño actual.

**Efecto secundario descubierto y arreglado en esta sesión:** el venv
(`venv/`) tenía rutas absolutas viejas hardcodeadas — se creó/vivió en
`/home/hiko/Documents/personal/git_multiprofile/venv` y el proyecto se
movió a la carpeta actual sin regenerarlo. `source venv/bin/activate` +
`python3 script.py` fallaba con `ModuleNotFoundError: No module named
'customtkinter'` porque el `PATH` apuntaba a un directorio inexistente.
Arreglado a mano en `venv/bin/{activate,activate.csh,activate.fish,pip,
pip3,pip3.12,pyinstaller,pyi-*}` (sed reemplazando la ruta vieja por la
actual) más `python3 -m venv --upgrade venv` para `pyvenv.cfg`. Verificado
en un subshell limpio.

### Sesión 3 (2026-11-17) — "más usable y bonita"

- **Tema**: selector Claro / Oscuro / Auto en la cabecera, persistido en
  `~/.git_multiprofile_theme` (la constante `THEME_FILE` ya existía sin usarse).
- **Formulario Crear Perfil**: Proveedor va primero (es lo que define host
  real, alias y tipo de llave); Host SSH, Proveedor Real, generar llave y tipo
  de llave pasan a "▸ Opciones avanzadas" plegado (se abre solo con "Otro
  (manual)" porque ahí el host es obligatorio). La ventana se re-mide con
  `_size_window_to_content()` al plegar/desplegar — probado: 771px ↔ 954px,
  estable también tras cambiar de idioma. Ayuda del ID de perfil acortada;
  texto de tipo de llave pasado a i18n (`key_type_help`, se borraron las
  claves muertas `ssh_key_type_help_es/_en`). Botón "Crear perfil y
  configurar" en vez de "🔥 CONFIGURAR TODO AHORA". Enter envía.
- **Lista vacía**: título + explicación + botón "Crear primer perfil".
- **Clonar**: "Pega la URL SSH" con URL vacía ya no se pinta en rojo (era un
  error sin que el usuario hiciera nada); ahora gris.
- Consola 170 → 140px de alto.
- Versión (`vX.Y.Z`) e ícono propio en cabecera/título/ventana.
- Verificado en Xvfb aislado (HOME falso): capturas Claro/Oscuro × ES/EN ×
  con/sin perfiles, y chequeo de comportamiento (estado tras cambiar idioma,
  self-hosted abre avanzadas, tema persistido, Enter envía).

### Sesión 4 (2026-11-17) — avisos visibles, consola plegable, manual con imágenes

- **Barra de avisos** bajo la cabecera (`_pick_notice` / `_render_notice`), visible desde cualquier pestaña y cerrable con ✕: gitleaks no instalado (Reintentar), perfiles sin protección (Activar en todos), gitleaks instalado/actualizado. Pensada para reutilizarse con el aviso de nueva versión (auto-update).
- **Consola plegable** (pedido explícito del usuario, distinto de la Fase 1 revertida: la ventana sigue sin ser redimensionable por el usuario). Con la consola oculta, el botón cuenta mensajes nuevos.
- `_size_window_to_content()` fija el **ancho** en la primera medición y luego solo ajusta el alto: re-medir con la pestaña Perfiles abierta ensanchaba la ventana a 736px.
- **Manual con imágenes**: `docs/make_screenshots.py` genera capturas y un GIF de recorrido (es/en) desde la app real en Xvfb con HOME de demo; embebidos en ambos README.

---

## Estado actual del código (al cierre de esta sesión)

- `git_complete_automator.py`: modificado, sin commitear (`VERSION` también
  tiene un cambio pendiente de antes de esta sesión, no relacionado).
- Compila limpio (`python -m py_compile`), paridad de claves i18n ES/EN
  verificada (única asimetría preexistente y no tocada: `ssh_key_type_help_es`
  / `_en` están definidas pero no se usan — el texto de ayuda de tipo de
  llave SSH sigue hardcodeado con un `if self.lang == "es"` en
  `create_form_tab`, en vez de pasar por `self.tr(...)`).
- Ventana: fija, `resizable(False, False)`, tamaño medido del contenido real.
- Pestaña Clonar: hilo + progreso real + cancelar + resultado persistente,
  todo de la Parte 1, sin cambios en esta sesión.

## Próximo paso sugerido

Fase 6 (tema + toggle claro/oscuro) — es la mejora que más se nota de un
vistazo, y no toca nada de lo que ya se revirtió o probó.
