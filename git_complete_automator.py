# -*- coding: utf-8 -*-
import os
import re
import subprocess
import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog

# Visual setup
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

LANG_FILE = os.path.expanduser("~/.git_multiprofile_lang")
GITHUB_COM = "github.com"

I18N = {
    "es": {
        "window_title": "Git Multi-Profile & SSH Automator",
        "header_title": "⚡ Git Multi-Profile & SSH Suite",
        "console_ready": "--- Consola del sistema lista para automatizar ---",

        "tab_create": "➕ Crear Perfil",
        "tab_list": "📋 Perfiles Configurados",
        "tab_clone": "📥 Clonar Repo",

        "other_provider_label": "Otro (manual)",
        "default_clone_example": "git clone git@{host}:usuario/repositorio.git",
        "azure_clone_example": "git clone git@{host}:v3/Organizacion/Proyecto/Repositorio",
        "default_test_note": "Si NO ves un error de 'Permission denied (publickey)', la llave fue aceptada.",
        "provider_note_github": "Si ves 'Hi <usuario>! You've successfully authenticated...', quedó listo.",
        "provider_note_gitlab": "Si ves 'Welcome to GitLab, @<usuario>!', quedó listo.",
        "provider_note_bitbucket": "Bitbucket no da una shell interactiva por SSH: si ves 'authenticated via ssh key' o 'logged in as', quedó listo (no es un error).",
        "provider_note_azure": "Azure DevOps no da una shell interactiva por SSH: si NO ves 'Permission denied (publickey)', tu llave fue aceptada (aunque la conexión se cierre igual).",

        # Section 1 - folder
        "section1_title": "1. Carpeta del Proyecto (será la carpeta final, no una base)",
        "path_placeholder": "Elige o crea la carpeta final del proyecto",
        "browse_btn": "Examinar...",
        "new_folder_btn": "➕ Nueva",

        # Section 2 - profile data
        "section2_title": "2. Datos del Perfil (Git & SSH)",
        "profile_id_label": "ID de Perfil (= nombre de la organización):",
        "profile_id_placeholder": "nombre-organizacion",
        "profile_id_help": (
            "⚠️ Debe ser EXACTAMENTE el nombre de la organización/dueño del repo: en Azure DevOps es la palabra "
            "después de 'v3/' en la URL SSH; en GitHub/GitLab/Bitbucket es el usuario u organización antes del "
            "nombre del repo (ej. 'git@github.com:ESTO/repo.git'). Así, al clonar, se valida que el repo "
            "pertenezca a esta organización y no se mezclan repos de otra empresa en la carpeta equivocada."
        ),
        "git_name_label": "Nombre del Desarrollador (Git):",
        "git_name_placeholder": "Tu Nombre Completo",
        "git_email_label": "Email para este Perfil:",
        "git_email_placeholder": "tu-correo@empresa.com",
        "ssh_host_label": "Host SSH (alias, se sugiere automáticamente):",
        "ssh_host_placeholder": "github.com-trabajo",
        "provider_label": "Proveedor:",
        "real_host_label": "Proveedor Real (ej: github.com):",
        "real_host_placeholder": GITHUB_COM,
        "self_hosted_placeholder": "tu-dominio-self-hosted.com",
        "gen_ssh_checkbox": "Generar nueva llave SSH automáticamente",
        "run_btn": "🔥 CONFIGURAR TODO AHORA",

        # Create confirmation dialog
        "confirm_dialog_title": "Confirmar creación de perfil",
        "confirm_review_title": "Revisa los datos antes de crear el perfil",
        "summary_profile_id": "ID de Perfil: {v}",
        "summary_folder": "Carpeta: {v}",
        "summary_name": "Nombre: {v}",
        "summary_email": "Email: {v}",
        "summary_provider": "Proveedor: {v}",
        "summary_ssh_alias": "Host SSH (alias): {v}",
        "summary_real_provider": "Proveedor Real: {v}",
        "summary_gen_ssh": "Generar llave SSH nueva: {v}",
        "yes": "Sí",
        "no": "No",
        "confirm_hint": "Nada se ha guardado todavía. Si algo está mal, presiona Cancelar y corrige el formulario.",
        "confirm_save_btn": "💾 Guardar y Crear Perfil",
        "cancel_btn": "Cancelar",

        "incomplete_fields_title": "Campos Incompletos",
        "incomplete_fields_msg": "Por favor llena todos los campos de configuración.",
        "error_title": "Error",
        "error_unexpected": "Ocurrió un error inesperado:\n{e}",

        # create_profile logs
        "log_start": "Iniciando flujo para el perfil: '{profile_id}'",
        "log_folder_ready": "Carpeta creada/verificada: {target_dir}",
        "log_gitconfig_written": "Configuración Git local escrita en {path}",
        "log_already_mapped": "El perfil ya se encuentra mapeado en tu ~/.gitconfig global.",
        "log_include_added": "Se agregó la redirección 'includeIf' a tu ~/.gitconfig global.",
        "log_ssh_key_skip": "La llave SSH {name} ya existe. Saltando generación para no sobreescribir.",
        "log_ssh_generating": "Generando nueva llave SSH {type} para {email}...",
        "log_ssh_created": "Llave SSH creada en: {path}",
        "log_host_registered": "El Host SSH '{host}' ya está registrado en tu ~/.ssh/config.",
        "log_ssh_mapping_saved": "Mapeo de hosts guardado en ~/.ssh/config.",
        "log_process_success": "✅ ¡PROCESO DE AUTOMATIZACIÓN COMPLETADO CON ÉXITO!",
        "log_process_error": "ERROR DURANTE EL PROCESO: {e}",
        "no_ssh_key_generated": "Llave SSH no generada",

        # list tab
        "list_title": "Perfiles detectados en ~/.gitconfig y ~/.ssh/config",
        "refresh_btn": "🔄 Refrescar",
        "list_empty": "No hay perfiles configurados todavía.",
        "list_no_name": "Sin nombre",
        "list_no_email": "sin email",
        "list_ssh_host_line": "🔑 Host SSH: {host} → {real_host}",
        "delete_row_btn": "🗑️ Eliminar",
        "edit_row_btn": "✏️ Editar",

        # orphan ssh key cleanup
        "orphan_clean_btn": "🧹 Limpiar huérfanos",
        "orphan_scan_error_title": "Error al escanear",
        "orphan_scan_error_msg": "No se pudo escanear ~/.ssh en busca de llaves huérfanas:\n{e}",
        "orphan_none_title": "Sin huérfanos",
        "orphan_none_msg": "No se encontró configuración SSH huérfana.",
        "orphan_dialog_title": "Configuración SSH huérfana",
        "orphan_warn": "Estos bloques 'Host' de ~/.ssh/config y/o llaves de ~/.ssh ya no corresponden a ningún perfil configurado en ~/.gitconfig (perfiles eliminados sin marcar 'borrar también la llave SSH', o cuyo includeIf se quitó a mano). Se eliminará el bloque de config (si aplica) y sus archivos de llave.",
        "orphan_item_no_pub": " (sin archivo .pub)",
        "orphan_confirm_btn": "🗑️ Eliminar seleccionadas",
        "orphan_none_selected_title": "Nada seleccionado",
        "orphan_none_selected_msg": "Selecciona al menos una llave para eliminar.",
        "orphan_delete_error_title": "Error al eliminar",
        "orphan_delete_error_msg": "No se pudo eliminar {name}:\n{e}",
        "orphan_done_title": "Huérfanos eliminados",
        "orphan_done_msg": "Se eliminaron {n} llave(s) huérfana(s).",
        "log_orphan_removed": "🧹 Llave huérfana eliminada: {name}",

        # edit dialog
        "edit_dialog_title": "Editar perfil: {id}",
        "edit_profile_label": "Perfil: {id}",
        "edit_folder_label": "Carpeta: {dir}",
        "edit_name_label": "Nombre del Desarrollador:",
        "edit_email_label": "Email:",
        "edit_ssh_host_label": "Host SSH (alias):",
        "edit_real_host_label": "Proveedor Real:",
        "edit_no_ssh_placeholder": "(sin SSH configurado)",
        "edit_incomplete_title": "Campos incompletos",
        "edit_incomplete_msg": "Nombre y email son obligatorios.",
        "edit_save_error_msg": "No se pudo guardar el perfil:\n{e}",
        "edit_save_btn": "💾 Guardar Cambios",
        "edit_updated_title": "Perfil actualizado",
        "edit_updated_msg": "El perfil '{id}' se actualizó correctamente.",

        # edit dialog - key rotation
        "edit_key_type_label": "Tipo de llave SSH:",
        "edit_rotate_key_btn": "🔁 Rotar / Regenerar Llave",
        "edit_rotate_hint": "Genera una llave nueva con el tipo elegido y actualiza ~/.ssh/config automáticamente. La llave anterior deja de funcionar: deberás agregar la nueva clave pública en tu proveedor Git.",
        "edit_rotate_no_key_msg": "Este perfil no tiene una llave SSH configurada para rotar.",
        "edit_rotate_confirm_title": "Confirmar rotación de llave",
        "edit_rotate_confirm_msg": "¿Rotar la llave SSH del perfil '{id}' a tipo {type}?\n\nLa llave actual quedará inválida hasta que agregues la nueva clave pública en tu proveedor Git.",
        "edit_rotate_error_msg": "No se pudo rotar la llave SSH:\n{e}",
        "edit_rotate_ssh_block_not_found": "no se encontró el bloque SSH esperado en ~/.ssh/config",
        "edit_rotate_done_title": "Llave rotada",
        "edit_rotate_done_msg": "La llave SSH del perfil '{id}' fue rotada correctamente. Copia la nueva clave pública y agrégala en tu proveedor Git.",

        # save_profile_edit logs
        "log_edit_git_updated": "Perfil '{id}': datos de Git actualizados en {path}.",
        "log_edit_ssh_updated": "Perfil '{id}': mapeo SSH actualizado ({host} → {real_host}).",
        "log_edit_ssh_not_found": "Perfil '{id}': no se encontró el bloque SSH esperado en ~/.ssh/config, no se modificó.",

        # rotate_ssh_key logs
        "log_rotate_error": "ERROR AL ROTAR LA LLAVE DEL PERFIL '{id}': {e}",
        "log_rotate_done": "Perfil '{id}': llave SSH rotada a {type} en {path}.",

        # delete dialog
        "delete_dialog_title": "Eliminar perfil: {id}",
        "delete_warn": "⚠️ Vas a eliminar la configuración del perfil '{id}'",
        "delete_will_remove": "Esto eliminará:",
        "delete_item_includeif": "• La entrada 'includeIf' en ~/.gitconfig",
        "delete_item_file": "• El archivo {path}",
        "delete_item_ssh_block": "• El bloque 'Host {host}' en ~/.ssh/config",
        "delete_keep_folder": "La carpeta del proyecto ({dir}) NO se eliminará ni se tocará su contenido.",
        "delete_key_checkbox": "También borrar la llave SSH del disco ({name} y .pub) — irreversible",
        "delete_error_msg": "No se pudo eliminar el perfil:\n{e}",
        "delete_confirm_btn": "🗑️ Eliminar Definitivamente",
        "delete_done_title": "Perfil eliminado",
        "delete_done_msg": "El perfil '{id}' fue eliminado correctamente.",

        # delete_profile logs
        "log_del_removed_file": "Perfil '{id}': eliminado {path}.",
        "log_del_includeif_removed": "Perfil '{id}': redirección 'includeIf' eliminada de ~/.gitconfig.",
        "log_del_includeif_not_found": "Perfil '{id}': no se encontró la redirección esperada en ~/.gitconfig, no se modificó.",
        "log_del_ssh_removed": "Perfil '{id}': bloque eliminado de ~/.ssh/config.",
        "log_del_ssh_not_found": "Perfil '{id}': no se encontró el bloque SSH esperado, no se modificó ~/.ssh/config.",
        "log_del_key_removed": "Perfil '{id}': llave SSH eliminada del disco.",
        "log_del_done": "Perfil '{id}' eliminado. La carpeta del proyecto no fue modificada.",

        # clone tab
        "clone_title": "Clonar un repositorio dentro de la carpeta de un perfil",
        "clone_profile_label": "Perfil a usar:",
        "clone_no_profiles_option": "(sin perfiles)",
        "clone_no_profiles_create_first": "(sin perfiles, crea uno primero)",
        "clone_url_label": "URL SSH del repo (botón 'Clone' → SSH del proveedor):",
        "clone_url_placeholder": "git@github.com:usuario/repositorio.git",
        "clone_status_initial": "Selecciona un perfil y pega la URL SSH del repositorio.",
        "clone_btn": "📥 Clonar Repositorio",
        "clone_status_no_profiles": "Crea un perfil primero en la pestaña 'Crear Perfil'.",
        "clone_status_no_ssh": "El perfil '{id}' no tiene configuración SSH (no se generó llave al crearlo). No se puede clonar con este perfil.",
        "clone_status_no_url": "Pega la URL SSH del repositorio.",
        "clone_status_invalid_url": "Esa URL no parece una URL SSH válida (debe verse como 'git@host:usuario/repo.git').",
        "clone_status_host_mismatch": "❌ Este repositorio es de '{host}', pero el perfil '{id}' está configurado para '{real_host}'. Elige el perfil correcto o corrige la URL.",
        "clone_status_org_mismatch": "❌ Este repositorio pertenece a la organización '{org}', pero el perfil '{id}' es para la organización '{id}'. El ID de perfil debe ser igual a la organización del repositorio (así se evita clonar repos de otra empresa en la carpeta equivocada).",
        "clone_status_ok": "✅ Coincide. Se clonará con el alias '{alias}' dentro de:\n{dir}",
        "clone_error_title": "Error al clonar",
        "clone_error_msg": "No se pudo clonar el repositorio:\n{e}",
        "clone_done_title": "Repositorio clonado",
        "clone_done_msg": "Se clonó correctamente dentro de:\n{dir}",
        "log_clone_start": "Clonando en '{dir}' usando el perfil '{id}'...",
        "log_clone_cmd": "Comando: git clone {url}",
        "log_clone_ok": "✅ Repositorio clonado correctamente en {dir}",
        "log_clone_error": "ERROR AL CLONAR: {e}",
        "git_clone_failed": "git clone falló",

        # new folder flow
        "new_folder_dialog_title": "Elige dónde crear la nueva carpeta",
        "new_folder_prompt_title": "Nueva Carpeta",
        "new_folder_prompt_msg": "Nombre de la nueva carpeta del proyecto:",
        "folder_exists_title": "La carpeta ya existe",
        "folder_exists_msg": "Ya existe una carpeta en:\n{path}\nElige otro nombre o selecciónala con 'Examinar...'.",
        "folder_error_msg": "No se pudo crear la carpeta:\n{e}",
        "log_folder_created": "Carpeta creada: {path}",

        # usage guide
        "guide_header": "📌 CÓMO FUNCIONA EL PERFIL '{profile_id}'\n",
        "guide_intro": (
            "Cualquier repo dentro de:\n"
            "    {target_dir}\n"
            "usará automáticamente el nombre/email y la llave SSH de este perfil, "
            "pero SOLO si el remoto usa el alias '{ssh_host}' (no '{real_host}' directamente).\n\n"
        ),
        "guide_clone": (
            "1) CLONAR UN REPO NUEVO\n"
            "   {clone_example}\n"
            "   Usa siempre el alias '{ssh_host}' en la URL — así Git elige la llave SSH correcta.\n\n"
        ),
        "guide_pushpull": (
            "2) PUSH / PULL\n"
            "   No necesitas nada extra: 'git push' y 'git pull' funcionan igual que siempre, "
            "porque el remoto del repo ya apunta al alias '{ssh_host}'.\n\n"
        ),
        "guide_existing": (
            "3) SI YA TENÍAS UN REPO CLONADO CON LA URL NORMAL (con '{real_host}')\n"
            "   Actualiza su remoto para que use este perfil:\n"
            "     git remote set-url origin git@{ssh_host}:<la-misma-ruta-que-tenía-después-de-los-':'>\n"
            "     git remote -v   (para confirmar el cambio)\n\n"
        ),
        "guide_test": (
            "4) PROBAR LA CONEXIÓN SSH\n"
            "   ssh -T git@{ssh_host}\n"
            "   {test_note}"
        ),

        # ssh copier dialog
        "copier_dialog_title": "Configuración Completada con Éxito",
        "copier_header": "🎉 ¡Perfil configurado y listo!",
        "copier_key_label": "Copia esta clave pública y agrégala a tu cuenta de {provider}:",
        "copier_copy_btn": "Copiar Clave SSH",
        "copier_copied_title": "Copiado",
        "copier_copied_msg": "¡Clave SSH copiada al portapapeles!",
        "copier_guide_label": "Guía de uso para este perfil:",
        "copier_close_btn": "Cerrar",
    },
    "en": {
        "window_title": "Git Multi-Profile & SSH Automator",
        "header_title": "⚡ Git Multi-Profile & SSH Suite",
        "console_ready": "--- System console ready to automate ---",

        "tab_create": "➕ Create Profile",
        "tab_list": "📋 Configured Profiles",
        "tab_clone": "📥 Clone Repo",

        "other_provider_label": "Other (manual)",
        "default_clone_example": "git clone git@{host}:user/repository.git",
        "azure_clone_example": "git clone git@{host}:v3/Organization/Project/Repository",
        "default_test_note": "If you do NOT see a 'Permission denied (publickey)' error, the key was accepted.",
        "provider_note_github": "If you see 'Hi <user>! You've successfully authenticated...', you're all set.",
        "provider_note_gitlab": "If you see 'Welcome to GitLab, @<user>!', you're all set.",
        "provider_note_bitbucket": "Bitbucket doesn't give an interactive SSH shell: if you see 'authenticated via ssh key' or 'logged in as', you're all set (it's not an error).",
        "provider_note_azure": "Azure DevOps doesn't give an interactive SSH shell: if you do NOT see 'Permission denied (publickey)', your key was accepted (even though the connection still closes).",

        # Section 1 - folder
        "section1_title": "1. Project Folder (this will be the final folder, not a base)",
        "path_placeholder": "Choose or create the final project folder",
        "browse_btn": "Browse...",
        "new_folder_btn": "➕ New",

        # Section 2 - profile data
        "section2_title": "2. Profile Data (Git & SSH)",
        "profile_id_label": "Profile ID (= organization name):",
        "profile_id_placeholder": "organization-name",
        "profile_id_help": (
            "⚠️ Must be EXACTLY the organization/owner name of the repo: on Azure DevOps it's the word "
            "right after 'v3/' in the SSH URL; on GitHub/GitLab/Bitbucket it's the user or organization before "
            "the repo name (e.g. 'git@github.com:THIS/repo.git'). This way, when cloning, the app checks that "
            "the repo belongs to this organization so repos from another company don't end up in the wrong folder."
        ),
        "git_name_label": "Developer Name (Git):",
        "git_name_placeholder": "Your Full Name",
        "git_email_label": "Email for this Profile:",
        "git_email_placeholder": "your-email@company.com",
        "ssh_host_label": "SSH Host (alias, auto-suggested):",
        "ssh_host_placeholder": "github.com-work",
        "provider_label": "Provider:",
        "real_host_label": "Real Provider (e.g: github.com):",
        "real_host_placeholder": GITHUB_COM,
        "self_hosted_placeholder": "your-self-hosted-domain.com",
        "gen_ssh_checkbox": "Automatically generate a new SSH key",
        "run_btn": "🔥 SET UP EVERYTHING NOW",

        # Create confirmation dialog
        "confirm_dialog_title": "Confirm profile creation",
        "confirm_review_title": "Review the data before creating the profile",
        "summary_profile_id": "Profile ID: {v}",
        "summary_folder": "Folder: {v}",
        "summary_name": "Name: {v}",
        "summary_email": "Email: {v}",
        "summary_provider": "Provider: {v}",
        "summary_ssh_alias": "SSH Host (alias): {v}",
        "summary_real_provider": "Real Provider: {v}",
        "summary_gen_ssh": "Generate new SSH key: {v}",
        "yes": "Yes",
        "no": "No",
        "confirm_hint": "Nothing has been saved yet. If something is wrong, press Cancel and fix the form.",
        "confirm_save_btn": "💾 Save and Create Profile",
        "cancel_btn": "Cancel",

        "incomplete_fields_title": "Incomplete Fields",
        "incomplete_fields_msg": "Please fill in all the configuration fields.",
        "error_title": "Error",
        "error_unexpected": "An unexpected error occurred:\n{e}",

        # create_profile logs
        "log_start": "Starting flow for profile: '{profile_id}'",
        "log_folder_ready": "Folder created/verified: {target_dir}",
        "log_gitconfig_written": "Local Git config written to {path}",
        "log_already_mapped": "This profile is already mapped in your global ~/.gitconfig.",
        "log_include_added": "'includeIf' redirect added to your global ~/.gitconfig.",
        "log_ssh_key_skip": "SSH key {name} already exists. Skipping generation to avoid overwriting it.",
        "log_ssh_generating": "Generating new {type} SSH key for {email}...",
        "log_ssh_created": "SSH key created at: {path}",
        "log_host_registered": "SSH Host '{host}' is already registered in your ~/.ssh/config.",
        "log_ssh_mapping_saved": "Host mapping saved to ~/.ssh/config.",
        "log_process_success": "✅ AUTOMATION PROCESS COMPLETED SUCCESSFULLY!",
        "log_process_error": "ERROR DURING PROCESS: {e}",
        "no_ssh_key_generated": "SSH key not generated",

        # list tab
        "list_title": "Profiles detected in ~/.gitconfig and ~/.ssh/config",
        "refresh_btn": "🔄 Refresh",
        "list_empty": "No profiles configured yet.",
        "list_no_name": "No name",
        "list_no_email": "no email",
        "list_ssh_host_line": "🔑 SSH Host: {host} → {real_host}",
        "delete_row_btn": "🗑️ Delete",
        "edit_row_btn": "✏️ Edit",

        # orphan ssh key cleanup
        "orphan_clean_btn": "🧹 Clean orphans",
        "orphan_scan_error_title": "Scan error",
        "orphan_scan_error_msg": "Could not scan ~/.ssh for orphaned keys:\n{e}",
        "orphan_none_title": "No orphans",
        "orphan_none_msg": "No orphaned SSH configuration was found.",
        "orphan_dialog_title": "Orphaned SSH configuration",
        "orphan_warn": "These ~/.ssh/config 'Host' blocks and/or ~/.ssh keys no longer match any profile configured in ~/.gitconfig (profiles deleted without checking 'also delete the SSH key', or whose includeIf was removed by hand). The config block (if any) and its key files will be deleted.",
        "orphan_item_no_pub": " (no .pub file)",
        "orphan_confirm_btn": "🗑️ Delete selected",
        "orphan_none_selected_title": "Nothing selected",
        "orphan_none_selected_msg": "Select at least one key to delete.",
        "orphan_delete_error_title": "Delete error",
        "orphan_delete_error_msg": "Could not delete {name}:\n{e}",
        "orphan_done_title": "Orphans deleted",
        "orphan_done_msg": "Deleted {n} orphaned key(s).",
        "log_orphan_removed": "🧹 Orphaned key deleted: {name}",

        # edit dialog
        "edit_dialog_title": "Edit profile: {id}",
        "edit_profile_label": "Profile: {id}",
        "edit_folder_label": "Folder: {dir}",
        "edit_name_label": "Developer Name:",
        "edit_email_label": "Email:",
        "edit_ssh_host_label": "SSH Host (alias):",
        "edit_real_host_label": "Real Provider:",
        "edit_no_ssh_placeholder": "(no SSH configured)",
        "edit_incomplete_title": "Incomplete fields",
        "edit_incomplete_msg": "Name and email are required.",
        "edit_save_error_msg": "Could not save the profile:\n{e}",
        "edit_save_btn": "💾 Save Changes",
        "edit_updated_title": "Profile updated",
        "edit_updated_msg": "Profile '{id}' was updated successfully.",

        # edit dialog - key rotation
        "edit_key_type_label": "SSH key type:",
        "edit_rotate_key_btn": "🔁 Rotate / Regenerate Key",
        "edit_rotate_hint": "Generates a new key with the chosen type and updates ~/.ssh/config automatically. The old key stops working: you'll need to add the new public key to your Git provider.",
        "edit_rotate_no_key_msg": "This profile doesn't have an SSH key configured to rotate.",
        "edit_rotate_confirm_title": "Confirm key rotation",
        "edit_rotate_confirm_msg": "Rotate the SSH key for profile '{id}' to type {type}?\n\nThe current key will become invalid until you add the new public key to your Git provider.",
        "edit_rotate_error_msg": "Could not rotate the SSH key:\n{e}",
        "edit_rotate_ssh_block_not_found": "expected SSH block not found in ~/.ssh/config",
        "edit_rotate_done_title": "Key rotated",
        "edit_rotate_done_msg": "The SSH key for profile '{id}' was rotated successfully. Copy the new public key and add it to your Git provider.",

        # save_profile_edit logs
        "log_edit_git_updated": "Profile '{id}': Git data updated in {path}.",
        "log_edit_ssh_updated": "Profile '{id}': SSH mapping updated ({host} → {real_host}).",
        "log_edit_ssh_not_found": "Profile '{id}': expected SSH block not found in ~/.ssh/config, nothing changed.",

        # rotate_ssh_key logs
        "log_rotate_error": "ERROR ROTATING KEY FOR PROFILE '{id}': {e}",
        "log_rotate_done": "Profile '{id}': SSH key rotated to {type} at {path}.",

        # delete dialog
        "delete_dialog_title": "Delete profile: {id}",
        "delete_warn": "⚠️ You are about to delete the configuration for profile '{id}'",
        "delete_will_remove": "This will remove:",
        "delete_item_includeif": "• The 'includeIf' entry in ~/.gitconfig",
        "delete_item_file": "• The file {path}",
        "delete_item_ssh_block": "• The 'Host {host}' block in ~/.ssh/config",
        "delete_keep_folder": "The project folder ({dir}) will NOT be deleted, and its content will not be touched.",
        "delete_key_checkbox": "Also delete the SSH key from disk ({name} and .pub) — irreversible",
        "delete_error_msg": "Could not delete the profile:\n{e}",
        "delete_confirm_btn": "🗑️ Delete Permanently",
        "delete_done_title": "Profile deleted",
        "delete_done_msg": "Profile '{id}' was deleted successfully.",

        # delete_profile logs
        "log_del_removed_file": "Profile '{id}': removed {path}.",
        "log_del_includeif_removed": "Profile '{id}': 'includeIf' redirect removed from ~/.gitconfig.",
        "log_del_includeif_not_found": "Profile '{id}': expected redirect not found in ~/.gitconfig, nothing changed.",
        "log_del_ssh_removed": "Profile '{id}': block removed from ~/.ssh/config.",
        "log_del_ssh_not_found": "Profile '{id}': expected SSH block not found, ~/.ssh/config was not changed.",
        "log_del_key_removed": "Profile '{id}': SSH key removed from disk.",
        "log_del_done": "Profile '{id}' deleted. The project folder was not modified.",

        # clone tab
        "clone_title": "Clone a repository into a profile's folder",
        "clone_profile_label": "Profile to use:",
        "clone_no_profiles_option": "(no profiles)",
        "clone_no_profiles_create_first": "(no profiles, create one first)",
        "clone_url_label": "Repo SSH URL ('Clone' button → SSH from the provider):",
        "clone_url_placeholder": "git@github.com:user/repository.git",
        "clone_status_initial": "Select a profile and paste the repository's SSH URL.",
        "clone_btn": "📥 Clone Repository",
        "clone_status_no_profiles": "Create a profile first in the 'Create Profile' tab.",
        "clone_status_no_ssh": "Profile '{id}' has no SSH configuration (no key was generated when it was created). You can't clone with this profile.",
        "clone_status_no_url": "Paste the repository's SSH URL.",
        "clone_status_invalid_url": "That URL doesn't look like a valid SSH URL (it should look like 'git@host:user/repo.git').",
        "clone_status_host_mismatch": "❌ This repository is from '{host}', but profile '{id}' is configured for '{real_host}'. Pick the right profile or fix the URL.",
        "clone_status_org_mismatch": "❌ This repository belongs to organization '{org}', but profile '{id}' is for organization '{id}'. The profile ID must match the repository's organization (this prevents cloning another company's repos into the wrong folder).",
        "clone_status_ok": "✅ Match. It will be cloned with alias '{alias}' inside:\n{dir}",
        "clone_error_title": "Clone error",
        "clone_error_msg": "Could not clone the repository:\n{e}",
        "clone_done_title": "Repository cloned",
        "clone_done_msg": "Successfully cloned into:\n{dir}",
        "log_clone_start": "Cloning into '{dir}' using profile '{id}'...",
        "log_clone_cmd": "Command: git clone {url}",
        "log_clone_ok": "✅ Repository cloned successfully into {dir}",
        "log_clone_error": "CLONE ERROR: {e}",
        "git_clone_failed": "git clone failed",

        # new folder flow
        "new_folder_dialog_title": "Choose where to create the new folder",
        "new_folder_prompt_title": "New Folder",
        "new_folder_prompt_msg": "Name of the new project folder:",
        "folder_exists_title": "The folder already exists",
        "folder_exists_msg": "A folder already exists at:\n{path}\nChoose another name or select it with 'Browse...'.",
        "folder_error_msg": "Could not create the folder:\n{e}",
        "log_folder_created": "Folder created: {path}",

        # usage guide
        "guide_header": "📌 HOW PROFILE '{profile_id}' WORKS\n",
        "guide_intro": (
            "Any repo inside:\n"
            "    {target_dir}\n"
            "will automatically use this profile's name/email and SSH key, "
            "but ONLY if the remote uses the alias '{ssh_host}' (not '{real_host}' directly).\n\n"
        ),
        "guide_clone": (
            "1) CLONE A NEW REPO\n"
            "   {clone_example}\n"
            "   Always use the alias '{ssh_host}' in the URL — this is how Git picks the right SSH key.\n\n"
        ),
        "guide_pushpull": (
            "2) PUSH / PULL\n"
            "   You don't need anything extra: 'git push' and 'git pull' work just like always, "
            "because the repo's remote already points to the alias '{ssh_host}'.\n\n"
        ),
        "guide_existing": (
            "3) IF YOU ALREADY HAD A REPO CLONED WITH THE NORMAL URL (with '{real_host}')\n"
            "   Update its remote to use this profile:\n"
            "     git remote set-url origin git@{ssh_host}:<the-same-path-it-had-after-the-':'>\n"
            "     git remote -v   (to confirm the change)\n\n"
        ),
        "guide_test": (
            "4) TEST THE SSH CONNECTION\n"
            "   ssh -T git@{ssh_host}\n"
            "   {test_note}"
        ),

        # ssh copier dialog
        "copier_dialog_title": "Setup Completed Successfully",
        "copier_header": "🎉 Profile configured and ready!",
        "copier_key_label": "Copy this public key and add it to your {provider} account:",
        "copier_copy_btn": "Copy SSH Key",
        "copier_copied_title": "Copied",
        "copier_copied_msg": "SSH key copied to clipboard!",
        "copier_guide_label": "Usage guide for this profile:",
        "copier_close_btn": "Close",
    },
}


class GitSSHAutomationApp(ctk.CTk):
    KEY_RELEASE_EVENT = "<KeyRelease>"

    GITHUB = "GitHub"
    GITLAB = "GitLab"
    BITBUCKET = "Bitbucket"
    AZURE_DEVOPS = "Azure DevOps"

    SSH_KEY_TYPES = ["rsa", "ed25519", "ecdsa"]
    SSH_KEY_TYPE_BY_PREFIX = {
        "ssh-rsa": "rsa",
        "ssh-ed25519": "ed25519",
        "ecdsa-sha2-nistp256": "ecdsa",
        "ecdsa-sha2-nistp384": "ecdsa",
        "ecdsa-sha2-nistp521": "ecdsa",
    }

    def __init__(self):
        super().__init__()

        self.geometry("680x730")
        self.resizable(False, False)

        # Paths
        self.gitconfig_path = os.path.expanduser("~/.gitconfig")
        self.ssh_config_path = os.path.expanduser("~/.ssh/config")
        self.ssh_dir = os.path.expanduser("~/.ssh")
        self.default_projects_base = os.path.expanduser("~/proyectos")

        # Variables
        self.selected_base_path = ctk.StringVar(value="")
        self._last_ssh_host_suggestion = ""

        self.lang = self._load_language()
        self._build_provider_data()
        self.create_widgets()

    # ------------------------------------------------------------------
    # i18n
    # ------------------------------------------------------------------

    def tr(self, key, **kwargs):
        text = I18N.get(self.lang, I18N["es"]).get(key, key)
        return text.format(**kwargs) if kwargs else text

    @staticmethod
    def _load_language():
        try:
            with open(LANG_FILE, "r", encoding="utf-8") as f:
                lang = f.read().strip().lower()
            return lang if lang in I18N else "es"
        except OSError:
            return "es"

    @staticmethod
    def _save_language(lang):
        try:
            with open(LANG_FILE, "w", encoding="utf-8") as f:
                f.write(lang)
        except OSError:
            pass

    def _build_provider_data(self):
        """(Re)builds every provider-related dict from the current language.
        Instance-level (not class-level) because the 'Other' label and every
        example/note is translated text, and must change when the language does."""
        other = self.tr("other_provider_label")
        default_clone_example = self.tr("default_clone_example")
        default_test_note = self.tr("default_test_note")

        self.OTHER_PROVIDER_LABEL = other
        self.DEFAULT_CLONE_EXAMPLE = default_clone_example
        self.DEFAULT_TEST_NOTE = default_test_note

        # Real SSH host used by each provider (visible in their "Clone with SSH" URL: git@HOST:path/repo.git)
        self.PROVIDER_HOSTS = {
            self.GITHUB: GITHUB_COM,
            self.GITLAB: "gitlab.com",
            self.BITBUCKET: "bitbucket.org",
            self.AZURE_DEVOPS: "ssh.dev.azure.com",
            other: "",
        }

        # Clone URL shape differs by provider (Azure DevOps uses v3/Org/Project/Repo, not user/repo.git)
        self.PROVIDER_CLONE_EXAMPLES = {
            self.GITHUB: default_clone_example,
            self.GITLAB: default_clone_example,
            self.BITBUCKET: default_clone_example,
            self.AZURE_DEVOPS: self.tr("azure_clone_example"),
            other: default_clone_example,
        }

        # What a successful `ssh -T` auth looks like per provider (some, like Azure/Bitbucket, don't give a friendly shell)
        self.PROVIDER_TEST_NOTES = {
            self.GITHUB: self.tr("provider_note_github"),
            self.GITLAB: self.tr("provider_note_gitlab"),
            self.BITBUCKET: self.tr("provider_note_bitbucket"),
            self.AZURE_DEVOPS: self.tr("provider_note_azure"),
            other: default_test_note,
        }

    def on_language_changed(self, choice):
        new_lang = choice.strip().lower()
        if new_lang == self.lang or new_lang not in I18N:
            return

        state = self._capture_form_state()

        self.lang = new_lang
        self._save_language(new_lang)
        self._build_provider_data()

        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()

        self._restore_form_state(state)

    def _capture_form_state(self):
        active_tab = None
        current = self.tabview.get()
        if current == self.TAB_CREATE:
            active_tab = "create"
        elif current == self.TAB_LIST:
            active_tab = "list"
        elif current == self.TAB_CLONE:
            active_tab = "clone"

        provider_value = self.provider_menu.get()
        provider = "OTHER" if provider_value == self.OTHER_PROVIDER_LABEL else provider_value

        return {
            "active_tab": active_tab,
            "profile_id": self.profile_id_entry.get(),
            "git_name": self.git_name_entry.get(),
            "git_email": self.git_email_entry.get(),
            "ssh_host": self.ssh_host_entry.get(),
            "provider": provider,
            "real_host": self.ssh_real_host_entry.get(),
            "gen_ssh": self.gen_ssh_var.get(),
            "target_dir": self.selected_base_path.get(),
            "clone_profile": self.clone_profile_menu.get() if self._clone_profiles else None,
            "clone_url": self.clone_url_entry.get(),
        }

    def _restore_form_state(self, state):
        self.profile_id_entry.delete(0, "end")
        self.profile_id_entry.insert(0, state["profile_id"])

        self.git_name_entry.delete(0, "end")
        self.git_name_entry.insert(0, state["git_name"])

        self.git_email_entry.delete(0, "end")
        self.git_email_entry.insert(0, state["git_email"])

        provider_value = self.OTHER_PROVIDER_LABEL if state["provider"] == "OTHER" else state["provider"]
        if provider_value in self.PROVIDER_HOSTS:
            self.provider_menu.set(provider_value)

        self.ssh_real_host_entry.delete(0, "end")
        self.ssh_real_host_entry.insert(0, state["real_host"])

        self.ssh_host_entry.delete(0, "end")
        self.ssh_host_entry.insert(0, state["ssh_host"])
        self._last_ssh_host_suggestion = state["ssh_host"]

        self.gen_ssh_var.set(state["gen_ssh"])
        self.selected_base_path.set(state["target_dir"])

        self.clone_url_entry.configure(state="normal")
        self.clone_url_entry.delete(0, "end")
        self.clone_url_entry.insert(0, state["clone_url"])
        if state["clone_profile"] and state["clone_profile"] in self._clone_profiles:
            self.clone_profile_menu.set(state["clone_profile"])
        if not self._clone_profiles:
            self.clone_url_entry.configure(state="disabled")
        self.validate_clone_form()

        if state["active_tab"] == "create":
            self.tabview.set(self.TAB_CREATE)
        elif state["active_tab"] == "list":
            self.tabview.set(self.TAB_LIST)
        elif state["active_tab"] == "clone" and self._clone_profiles:
            self.tabview.set(self.TAB_CLONE)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def create_widgets(self):
        self.title(self.tr("window_title"))
        self.TAB_CREATE = self.tr("tab_create")
        self.TAB_LIST = self.tr("tab_list")
        self.TAB_CLONE = self.tr("tab_clone")

        # Header: title + language switcher
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 0))

        title_lbl = ctk.CTkLabel(header, text=self.tr("header_title"), font=ctk.CTkFont(size=22, weight="bold"))
        title_lbl.pack(side="left")

        lang_switch = ctk.CTkSegmentedButton(header, values=["ES", "EN"], width=100, command=self.on_language_changed)
        lang_switch.set(self.lang.upper())
        lang_switch.pack(side="right")

        # Tabs: creation form, profile list/management, then cloning (last, needs an existing profile)
        self.tabview = ctk.CTkTabview(self, command=self.on_tab_change)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=5)
        tab_create = self.tabview.add(self.TAB_CREATE)
        tab_list = self.tabview.add(self.TAB_LIST)
        tab_clone = self.tabview.add(self.TAB_CLONE)

        self.create_form_tab(tab_create)
        # Populate the clone tab before the list tab: refresh_profile_list() (called while
        # building the list tab) also refreshes the clone tab's enabled state, so its widgets must exist first.
        self.create_clone_tab(tab_clone)
        self.create_list_tab(tab_list)

        # CONSOLE LOG
        self.log_box = ctk.CTkTextbox(self, height=170, width=640)
        self.log_box.pack(padx=20, pady=(5, 15))
        self.log_box.insert("0.0", f"{self.tr('console_ready')}\n")
        self.log_box.configure(state="disabled")

    def create_form_tab(self, parent):
        # Main Container
        container = ctk.CTkFrame(parent)
        container.pack(fill="both", expand=True, padx=5, pady=5)

        # SECTION 1: Folder setup
        sect1_lbl = ctk.CTkLabel(container, text=self.tr("section1_title"), font=ctk.CTkFont(size=14, weight="bold"))
        sect1_lbl.grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(10, 5))

        self.path_entry = ctk.CTkEntry(
            container,
            textvariable=self.selected_base_path,
            placeholder_text=self.tr("path_placeholder"),
            width=330,
        )
        self.path_entry.grid(row=1, column=0, columnspan=2, padx=(15, 10), pady=5, sticky="w")

        path_buttons = ctk.CTkFrame(container, fg_color="transparent")
        path_buttons.grid(row=1, column=2, padx=(0, 15), pady=5, sticky="w")

        browse_btn = ctk.CTkButton(path_buttons, text=self.tr("browse_btn"), width=95, command=self.browse_folder)
        browse_btn.pack(side="left", padx=(0, 5))

        new_folder_btn = ctk.CTkButton(path_buttons, text=self.tr("new_folder_btn"), width=95, command=self.create_new_folder)
        new_folder_btn.pack(side="left")

        # SECTION 2: Profile Info
        sect2_lbl = ctk.CTkLabel(container, text=self.tr("section2_title"), font=ctk.CTkFont(size=14, weight="bold"))
        sect2_lbl.grid(row=2, column=0, columnspan=3, sticky="w", padx=15, pady=(15, 5))

        # Profile ID
        p_id_lbl = ctk.CTkLabel(container, text=self.tr("profile_id_label"))
        p_id_lbl.grid(row=3, column=0, sticky="w", padx=15, pady=5)
        self.profile_id_entry = ctk.CTkEntry(container, placeholder_text=self.tr("profile_id_placeholder"), width=250)
        self.profile_id_entry.grid(row=3, column=1, columnspan=2, sticky="w", padx=15, pady=5)
        self.profile_id_entry.bind(self.KEY_RELEASE_EVENT, self.update_ssh_host_suggestion)

        p_id_help_lbl = ctk.CTkLabel(
            container,
            text=self.tr("profile_id_help"),
            text_color="gray", justify="left", anchor="w", wraplength=480, font=ctk.CTkFont(size=11),
        )
        p_id_help_lbl.grid(row=4, column=0, columnspan=3, sticky="w", padx=15, pady=(0, 5))

        # Git Name
        p_name_lbl = ctk.CTkLabel(container, text=self.tr("git_name_label"))
        p_name_lbl.grid(row=5, column=0, sticky="w", padx=15, pady=5)
        self.git_name_entry = ctk.CTkEntry(container, placeholder_text=self.tr("git_name_placeholder"), width=250)
        self.git_name_entry.grid(row=5, column=1, columnspan=2, sticky="w", padx=15, pady=5)

        # Git Email
        p_email_lbl = ctk.CTkLabel(container, text=self.tr("git_email_label"))
        p_email_lbl.grid(row=6, column=0, sticky="w", padx=15, pady=5)
        self.git_email_entry = ctk.CTkEntry(container, placeholder_text=self.tr("git_email_placeholder"), width=250)
        self.git_email_entry.grid(row=6, column=1, columnspan=2, sticky="w", padx=15, pady=5)

        # Host SSH (custom mapping)
        ssh_host_lbl = ctk.CTkLabel(container, text=self.tr("ssh_host_label"))
        ssh_host_lbl.grid(row=7, column=0, sticky="w", padx=15, pady=5)
        self.ssh_host_entry = ctk.CTkEntry(container, placeholder_text=self.tr("ssh_host_placeholder"), width=250)
        self.ssh_host_entry.grid(row=7, column=1, columnspan=2, sticky="w", padx=15, pady=5)

        # Provider preset selector
        provider_lbl = ctk.CTkLabel(container, text=self.tr("provider_label"))
        provider_lbl.grid(row=8, column=0, sticky="w", padx=15, pady=5)
        self.provider_menu = ctk.CTkOptionMenu(
            container,
            values=list(self.PROVIDER_HOSTS.keys()),
            width=250,
            command=self.on_provider_selected,
        )
        self.provider_menu.set(self.GITHUB)
        self.provider_menu.grid(row=8, column=1, columnspan=2, sticky="w", padx=15, pady=5)

        # True Host
        ssh_real_host_lbl = ctk.CTkLabel(container, text=self.tr("real_host_label"))
        ssh_real_host_lbl.grid(row=9, column=0, sticky="w", padx=15, pady=5)
        self.ssh_real_host_entry = ctk.CTkEntry(container, placeholder_text=self.tr("real_host_placeholder"), width=250)
        self.ssh_real_host_entry.grid(row=9, column=1, columnspan=2, sticky="w", padx=15, pady=5)
        self.ssh_real_host_entry.insert(0, self.PROVIDER_HOSTS[self.GITHUB])
        self.ssh_real_host_entry.bind(self.KEY_RELEASE_EVENT, self.update_ssh_host_suggestion)

        # Auto-gen SSH Checkbox
        self.gen_ssh_var = ctk.BooleanVar(value=True)
        self.gen_ssh_chk = ctk.CTkCheckBox(container, text=self.tr("gen_ssh_checkbox"), variable=self.gen_ssh_var)
        self.gen_ssh_chk.grid(row=10, column=0, columnspan=3, sticky="w", padx=15, pady=(10, 5))

        # ACTION BUTTON
        self.run_btn = ctk.CTkButton(container, text=self.tr("run_btn"), font=ctk.CTkFont(size=15, weight="bold"), height=40, command=self.execute_automation)
        self.run_btn.grid(row=11, column=0, columnspan=3, pady=(15, 10))

        self.update_ssh_host_suggestion()

    def on_provider_selected(self, choice):
        host = self.PROVIDER_HOSTS.get(choice, "")
        self.ssh_real_host_entry.delete(0, "end")
        if host:
            self.ssh_real_host_entry.insert(0, host)
            self.ssh_real_host_entry.configure(state="normal")
        else:
            self.ssh_real_host_entry.configure(placeholder_text=self.tr("self_hosted_placeholder"))
        self.update_ssh_host_suggestion()

    def update_ssh_host_suggestion(self, _event=None):
        """Keep the SSH alias in sync with 'provider-profile' unless the user typed a custom one."""
        real_host = self.ssh_real_host_entry.get().strip()
        profile_id = self.profile_id_entry.get().strip().lower()
        if not real_host:
            return

        suggestion = f"{real_host}-{profile_id}" if profile_id else real_host
        current = self.ssh_host_entry.get().strip()

        if current == "" or current == self._last_ssh_host_suggestion:
            self.ssh_host_entry.delete(0, "end")
            self.ssh_host_entry.insert(0, suggestion)
            self._last_ssh_host_suggestion = suggestion

    def create_clone_tab(self, parent):
        self._clone_profiles = {}

        container = ctk.CTkFrame(parent)
        container.pack(fill="both", expand=True, padx=5, pady=5)

        title_lbl = ctk.CTkLabel(container, text=self.tr("clone_title"), font=ctk.CTkFont(size=14, weight="bold"))
        title_lbl.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 15))

        profile_lbl = ctk.CTkLabel(container, text=self.tr("clone_profile_label"))
        profile_lbl.grid(row=1, column=0, sticky="w", padx=15, pady=5)

        profile_row = ctk.CTkFrame(container, fg_color="transparent")
        profile_row.grid(row=1, column=1, sticky="w", padx=15, pady=5)
        self.clone_profile_menu = ctk.CTkOptionMenu(
            profile_row, values=[self.tr("clone_no_profiles_option")], width=250, command=self.on_clone_profile_selected,
        )
        self.clone_profile_menu.pack(side="left", padx=(0, 5))
        refresh_clone_btn = ctk.CTkButton(profile_row, text="🔄", width=32, command=self.refresh_clone_profiles)
        refresh_clone_btn.pack(side="left")

        url_lbl = ctk.CTkLabel(container, text=self.tr("clone_url_label"))
        url_lbl.grid(row=2, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 0))

        self.clone_url_entry = ctk.CTkEntry(container, placeholder_text=self.tr("clone_url_placeholder"), width=480)
        self.clone_url_entry.grid(row=3, column=0, columnspan=2, sticky="w", padx=15, pady=5)
        self.clone_url_entry.bind(self.KEY_RELEASE_EVENT, lambda _e: self.validate_clone_form())

        self.clone_status_lbl = ctk.CTkLabel(container, text=self.tr("clone_status_initial"), justify="left", anchor="w", wraplength=480)
        self.clone_status_lbl.grid(row=4, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 15))

        self.clone_btn = ctk.CTkButton(container, text=self.tr("clone_btn"), state="disabled", command=self.do_clone_repo)
        self.clone_btn.grid(row=5, column=0, columnspan=2, pady=10)

        self.refresh_clone_profiles()

    def refresh_clone_profiles(self):
        profiles = self.parse_profiles()
        self._clone_profiles = {p["id"]: p for p in profiles}

        has_profiles = bool(self._clone_profiles)
        values = list(self._clone_profiles.keys()) or [self.tr("clone_no_profiles_create_first")]
        self.clone_profile_menu.configure(values=values, state="normal" if has_profiles else "disabled")
        if self.clone_profile_menu.get() not in values:
            self.clone_profile_menu.set(values[0])

        self.clone_url_entry.configure(state="normal" if has_profiles else "disabled")
        self._set_clone_tab_enabled(has_profiles)

        self.validate_clone_form()

    def _set_clone_tab_enabled(self, enabled):
        """Locks the 'Clone Repo' tab itself (not just the button inside it) until a profile exists."""
        try:
            tab_button = self.tabview._segmented_button._buttons_dict.get(self.TAB_CLONE)
        except AttributeError:
            tab_button = None
        if tab_button is None:
            return

        tab_button.configure(state="normal" if enabled else "disabled")

        # If the tab just got disabled while the user was on it, bounce back to a usable tab.
        if not enabled and self.tabview.get() == self.TAB_CLONE:
            self.tabview.set(self.TAB_CREATE)

    def on_clone_profile_selected(self, _choice=None):
        self.validate_clone_form()

    @staticmethod
    def parse_ssh_clone_url(url):
        """Accepts both scp-like (git@host:path) and ssh:// (ssh://git@host[:port]/path) SSH clone URLs."""
        url = url.strip()

        m = re.match(r"^ssh://(?P<user>[^@/]+)@(?P<host>[^:/]+)(?P<port>:\d+)?/(?P<path>.+)$", url)
        if m:
            return {"user": m.group("user"), "host": m.group("host"), "port": m.group("port") or "", "path": m.group("path"), "style": "ssh"}

        m = re.match(r"^(?P<user>[^@\s]+)@(?P<host>[^:\s]+):(?P<path>.+)$", url)
        if m:
            return {"user": m.group("user"), "host": m.group("host"), "port": "", "path": m.group("path"), "style": "scp"}

        return None

    @staticmethod
    def build_aliased_clone_url(parsed, alias_host):
        if parsed["style"] == "ssh":
            return f"ssh://{parsed['user']}@{alias_host}{parsed['port']}/{parsed['path']}"
        return f"{parsed['user']}@{alias_host}:{parsed['path']}"

    @staticmethod
    def extract_repo_organization(path):
        """Get the organization/owner segment from a repo path.
        Azure DevOps paths look like 'v3/Organization/Project/Repo'; every other
        provider (GitHub/GitLab/Bitbucket/self-hosted) puts the owner/org first."""
        segments = [s for s in path.strip("/").split("/") if s]
        if not segments:
            return ""
        if segments[0].lower() == "v3" and len(segments) >= 2:
            return segments[1]
        return segments[0]

    def _set_clone_status(self, text, ok):
        self.clone_status_lbl.configure(text=text, text_color="#2e7d32" if ok else "#a83232")
        self.clone_btn.configure(state="normal" if ok else "disabled")

    def validate_clone_form(self):
        profile_id = self.clone_profile_menu.get()
        profile = self._clone_profiles.get(profile_id)
        url = self.clone_url_entry.get().strip()

        if not profile:
            self._set_clone_status(self.tr("clone_status_no_profiles"), ok=False)
            return

        if not profile.get("ssh_key_path"):
            self._set_clone_status(self.tr("clone_status_no_ssh", id=profile_id), ok=False)
            return

        if not url:
            self._set_clone_status(self.tr("clone_status_no_url"), ok=False)
            return

        parsed = self.parse_ssh_clone_url(url)
        if not parsed:
            self._set_clone_status(self.tr("clone_status_invalid_url"), ok=False)
            return

        if parsed["host"].lower() != profile["real_host"].lower():
            self._set_clone_status(
                self.tr("clone_status_host_mismatch", host=parsed["host"], id=profile_id, real_host=profile["real_host"]),
                ok=False,
            )
            return

        org = self.extract_repo_organization(parsed["path"])
        if org.lower() != profile_id.lower():
            self._set_clone_status(self.tr("clone_status_org_mismatch", org=org, id=profile_id), ok=False)
            return

        self._set_clone_status(
            self.tr("clone_status_ok", alias=profile["ssh_host"], dir=profile["target_dir"]),
            ok=True,
        )

    def do_clone_repo(self):
        profile_id = self.clone_profile_menu.get()
        profile = self._clone_profiles.get(profile_id)
        url = self.clone_url_entry.get().strip()
        parsed = self.parse_ssh_clone_url(url) if url else None

        if not profile or not parsed:
            self.validate_clone_form()
            return

        host_ok = parsed["host"].lower() == profile["real_host"].lower()
        org_ok = self.extract_repo_organization(parsed["path"]).lower() == profile_id.lower()
        if not host_ok or not org_ok:
            self.validate_clone_form()
            return

        aliased_url = self.build_aliased_clone_url(parsed, profile["ssh_host"])

        try:
            os.makedirs(profile["target_dir"], exist_ok=True)
            self.log(self.tr("log_clone_start", dir=profile["target_dir"], id=profile_id))
            self.log(self.tr("log_clone_cmd", url=aliased_url))

            clone_env = os.environ.copy()
            # accept-new: acepta llaves de hosts nuevos sin prompt interactivo
            # (la app no tiene terminal), pero sigue rechazando llaves cambiadas.
            clone_env["GIT_SSH_COMMAND"] = "ssh -o StrictHostKeyChecking=accept-new -o BatchMode=yes"
            result = subprocess.run(
                ["git", "clone", aliased_url],
                cwd=profile["target_dir"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                env=clone_env,
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or self.tr("git_clone_failed"))

            self.log(self.tr("log_clone_ok", dir=profile["target_dir"]))
            messagebox.showinfo(self.tr("clone_done_title"), self.tr("clone_done_msg", dir=profile["target_dir"]))
            self.clone_url_entry.delete(0, "end")
            self.validate_clone_form()

        except Exception as e:
            self.log(self.tr("log_clone_error", e=str(e)))
            messagebox.showerror(self.tr("clone_error_title"), self.tr("clone_error_msg", e=str(e)))

    def create_list_tab(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=(5, 0))

        list_lbl = ctk.CTkLabel(header, text=self.tr("list_title"), font=ctk.CTkFont(size=14, weight="bold"))
        list_lbl.pack(side="left", padx=10, pady=10)

        refresh_btn = ctk.CTkButton(header, text=self.tr("refresh_btn"), width=100, command=self.refresh_profile_list)
        refresh_btn.pack(side="right", padx=10, pady=10)

        clean_orphans_btn = ctk.CTkButton(header, text=self.tr("orphan_clean_btn"), width=150, command=self.open_orphan_cleanup_dialog)
        clean_orphans_btn.pack(side="right", padx=(10, 0), pady=10)

        self.profiles_scroll = ctk.CTkScrollableFrame(parent, width=600, height=400)
        self.profiles_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        self.refresh_profile_list()

    def on_tab_change(self):
        current_tab = self.tabview.get()
        if current_tab == self.TAB_LIST:
            self.refresh_profile_list()
        elif current_tab == self.TAB_CLONE:
            self.refresh_clone_profiles()

    def log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f">> {text}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def browse_folder(self):
        # Selects an EXISTING folder as-is (no subfolder appended later).
        current = self.selected_base_path.get().strip()
        initial_dir = current if os.path.isdir(current) else self.default_projects_base
        folder = filedialog.askdirectory(initialdir=initial_dir, mustexist=True)
        if folder:
            self.selected_base_path.set(folder)

    def create_new_folder(self):
        # The native directory chooser doesn't reliably expose a "Create Folder" button
        # on every platform/toolkit, so we build that flow explicitly: pick a parent, name it, create it.
        current = self.selected_base_path.get().strip()
        initial_dir = current if os.path.isdir(current) else self.default_projects_base
        parent_dir = filedialog.askdirectory(
            title=self.tr("new_folder_dialog_title"),
            initialdir=initial_dir,
            mustexist=True,
        )
        if not parent_dir:
            return

        folder_name = simpledialog.askstring(
            self.tr("new_folder_prompt_title"),
            self.tr("new_folder_prompt_msg"),
            parent=self,
        )
        if not folder_name or not folder_name.strip():
            return
        folder_name = folder_name.strip()

        new_path = os.path.join(parent_dir, folder_name)
        if os.path.exists(new_path):
            messagebox.showerror(self.tr("folder_exists_title"), self.tr("folder_exists_msg", path=new_path))
            return

        try:
            os.makedirs(new_path)
        except OSError as e:
            messagebox.showerror(self.tr("error_title"), self.tr("folder_error_msg", e=str(e)))
            return

        self.selected_base_path.set(new_path)
        self.log(self.tr("log_folder_created", path=new_path))

    def execute_automation(self):
        # 1. Validations — nothing is written to disk yet, this only reads the form
        profile_id = self.profile_id_entry.get().strip().lower()
        git_name = self.git_name_entry.get().strip()
        git_email = self.git_email_entry.get().strip()
        ssh_host = self.ssh_host_entry.get().strip()
        real_host = self.ssh_real_host_entry.get().strip()
        target_dir = self.selected_base_path.get().strip()
        provider = self.provider_menu.get()
        gen_ssh = self.gen_ssh_var.get()

        if not all([profile_id, git_name, git_email, ssh_host, real_host, target_dir]):
            messagebox.showerror(self.tr("incomplete_fields_title"), self.tr("incomplete_fields_msg"))
            return

        self.open_create_confirmation(profile_id, git_name, git_email, ssh_host, real_host, target_dir, provider, gen_ssh)

    def open_create_confirmation(self, profile_id, git_name, git_email, ssh_host, real_host, target_dir, provider, gen_ssh):
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.tr("confirm_dialog_title"))
        dialog.geometry("480x420")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        title_lbl = ctk.CTkLabel(frame, text=self.tr("confirm_review_title"), font=ctk.CTkFont(size=15, weight="bold"), wraplength=420, justify="left")
        title_lbl.pack(anchor="w", pady=(0, 10))

        summary_text = "\n".join([
            self.tr("summary_profile_id", v=profile_id),
            self.tr("summary_folder", v=target_dir),
            self.tr("summary_name", v=git_name),
            self.tr("summary_email", v=git_email),
            self.tr("summary_provider", v=provider),
            self.tr("summary_ssh_alias", v=ssh_host),
            self.tr("summary_real_provider", v=real_host),
            self.tr("summary_gen_ssh", v=self.tr("yes") if gen_ssh else self.tr("no")),
        ])
        summary_lbl = ctk.CTkLabel(frame, text=summary_text, justify="left", anchor="w", wraplength=420)
        summary_lbl.pack(anchor="w", pady=(0, 15))

        hint_lbl = ctk.CTkLabel(
            frame,
            text=self.tr("confirm_hint"),
            text_color="gray", justify="left", anchor="w", wraplength=420,
        )
        hint_lbl.pack(anchor="w", pady=(0, 15))

        def confirm_create():
            dialog.destroy()
            self.create_profile(profile_id, git_name, git_email, ssh_host, real_host, target_dir, provider, gen_ssh)

        confirm_btn = ctk.CTkButton(frame, text=self.tr("confirm_save_btn"), command=confirm_create)
        confirm_btn.pack(pady=(5, 5))

        cancel_btn = ctk.CTkButton(frame, text=self.tr("cancel_btn"), fg_color="gray", command=dialog.destroy)
        cancel_btn.pack(pady=5)

    def _ssh_keygen_cmd(self, key_type, key_path, email):
        cmd = ["ssh-keygen", "-t", key_type]
        if key_type == "rsa":
            cmd += ["-b", "4096"]
        elif key_type == "ecdsa":
            cmd += ["-b", "521"]
        cmd += ["-C", email, "-f", key_path, "-N", ""]  # No passphrase for automatic operation
        return cmd

    def _detect_ssh_key_type(self, pub_key_path):
        if not os.path.exists(pub_key_path):
            return ""
        try:
            with open(pub_key_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except OSError:
            return ""
        prefix = content.split(" ", 1)[0] if content else ""
        return self.SSH_KEY_TYPE_BY_PREFIX.get(prefix, "")

    def create_profile(self, profile_id, git_name, git_email, ssh_host, real_host, target_dir, provider, gen_ssh):
        sub_gitconfig = os.path.expanduser(f"~/.gitconfig-{profile_id}")
        ssh_key_name = f"id_rsa_{profile_id}"
        ssh_key_path = os.path.join(self.ssh_dir, ssh_key_name)

        try:
            self.log(self.tr("log_start", profile_id=profile_id))

            # A. Create Project Folder
            os.makedirs(target_dir, exist_ok=True)
            self.log(self.tr("log_folder_ready", target_dir=target_dir))

            # B. Create the sub-gitconfig file
            with open(sub_gitconfig, "w", encoding="utf-8") as f:
                f.write(f"[user]\n\tname = {git_name}\n\temail = {git_email}\n")
            self.log(self.tr("log_gitconfig_written", path=sub_gitconfig))

            # C. Register profile in main ~/.gitconfig using includeIf
            gitconfig_data = ""
            if os.path.exists(self.gitconfig_path):
                with open(self.gitconfig_path, "r", encoding="utf-8") as f:
                    gitconfig_data = f.read()

            include_block = f'\n[includeIf "gitdir:{target_dir}/"]\n\tpath = {sub_gitconfig}\n'

            # Use trailing slash check to match safely
            if f"gitdir:{target_dir}/" in gitconfig_data:
                self.log(self.tr("log_already_mapped"))
            else:
                with open(self.gitconfig_path, "a", encoding="utf-8") as f:
                    f.write(include_block)
                self.log(self.tr("log_include_added"))

            # D. Handle SSH Keys (if checked)
            pub_key_content = self.tr("no_ssh_key_generated")
            if gen_ssh:
                os.makedirs(self.ssh_dir, exist_ok=True)
                os.chmod(self.ssh_dir, 0o700)

                if os.path.exists(ssh_key_path):
                    self.log(self.tr("log_ssh_key_skip", name=ssh_key_name))
                else:
                    # Execute ssh-keygen (RSA, required by servers expecting "ssh-rsa" keys)
                    self.log(self.tr("log_ssh_generating", type="RSA", email=git_email))
                    cmd = self._ssh_keygen_cmd("rsa", ssh_key_path, git_email)
                    # Run without prompting
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    self.log(self.tr("log_ssh_created", path=ssh_key_path))

                # Read public key to show to the user
                pub_key_path = f"{ssh_key_path}.pub"
                if os.path.exists(pub_key_path):
                    with open(pub_key_path, "r") as pk_f:
                        pub_key_content = pk_f.read().strip()

                # E. Update SSH Config file (~/.ssh/config)
                ssh_config_block = (
                    f"\n# Perfil Autogenerado: {profile_id}\n"
                    f"Host {ssh_host}\n"
                    f"    HostName {real_host}\n"
                    f"    User git\n"
                    f"    IdentityFile {ssh_key_path}\n"
                    f"    IdentitiesOnly yes\n"
                )

                ssh_config_data = ""
                if os.path.exists(self.ssh_config_path):
                    with open(self.ssh_config_path, "r", encoding="utf-8") as f:
                        ssh_config_data = f.read()

                if f"Host {ssh_host}" in ssh_config_data:
                    self.log(self.tr("log_host_registered", host=ssh_host))
                else:
                    with open(self.ssh_config_path, "a", encoding="utf-8") as f:
                        f.write(ssh_config_block)
                    self.log(self.tr("log_ssh_mapping_saved"))

            # Show Success Summary
            self.log(self.tr("log_process_success"))

            # Create a simple scrollable window for the user to copy their SSH key easily
            self.show_ssh_copier(pub_key_content, profile_id, target_dir, ssh_host, real_host, provider)

            self.refresh_profile_list()

        except Exception as e:
            self.log(self.tr("log_process_error", e=str(e)))
            messagebox.showerror(self.tr("error_title"), self.tr("error_unexpected", e=str(e)))

    # ------------------------------------------------------------------
    # Profile listing & editing
    # ------------------------------------------------------------------

    def parse_profiles(self):
        """Scan ~/.gitconfig, ~/.gitconfig-<id> and ~/.ssh/config to build the list of configured profiles."""
        profiles = {}

        if os.path.exists(self.gitconfig_path):
            with open(self.gitconfig_path, "r", encoding="utf-8") as f:
                gitconfig_data = f.read()

            include_pattern = r'\[includeIf\s+"gitdir:(?P<dir>[^"]+?)/?"\][ \t]*\n[ \t]*path[ \t]*=[ \t]*(?P<path>[^\r\n]+)'
            for m in re.finditer(include_pattern, gitconfig_data):
                target_dir = m.group("dir")
                cfg_path = os.path.expanduser(m.group("path").strip())
                basename = os.path.basename(cfg_path)
                prefix = ".gitconfig-"
                profile_id = basename[len(prefix):] if basename.startswith(prefix) else basename
                profiles[profile_id] = {
                    "id": profile_id,
                    "target_dir": target_dir,
                    "gitconfig_path": cfg_path,
                    "name": "",
                    "email": "",
                    "ssh_host": "",
                    "real_host": "",
                    "ssh_key_path": "",
                    "ssh_key_type": "",
                }

        for info in profiles.values():
            if os.path.exists(info["gitconfig_path"]):
                with open(info["gitconfig_path"], "r", encoding="utf-8") as f:
                    sub_data = f.read()
                m_name = re.search(r'name\s*=\s*(.+)', sub_data)
                m_email = re.search(r'email\s*=\s*(.+)', sub_data)
                if m_name:
                    info["name"] = m_name.group(1).strip()
                if m_email:
                    info["email"] = m_email.group(1).strip()

        if os.path.exists(self.ssh_config_path):
            with open(self.ssh_config_path, "r", encoding="utf-8") as f:
                ssh_data = f.read()

            pattern = (
                r"# Perfil Autogenerado:[ \t]*(?P<id>\S+)[ \t]*\n"
                r"Host[ \t]+(?P<host>\S+)[ \t]*\n"
                r"[ \t]*HostName[ \t]+(?P<real_host>\S+)[ \t]*\n"
                r"[ \t]*User[ \t]+\S+[ \t]*\n"
                r"[ \t]*IdentityFile[ \t]+(?P<key>\S+)"
            )
            for m in re.finditer(pattern, ssh_data):
                pid = m.group("id")
                if pid in profiles:
                    profiles[pid]["ssh_host"] = m.group("host")
                    profiles[pid]["real_host"] = m.group("real_host")
                    profiles[pid]["ssh_key_path"] = m.group("key")
                    profiles[pid]["ssh_key_type"] = self._detect_ssh_key_type(f"{m.group('key')}.pub")

        return sorted(profiles.values(), key=lambda p: p["id"])

    def _find_orphan_ssh_host_blocks(self, active_ids):
        """'# Perfil Autogenerado: <id>' Host blocks in ~/.ssh/config whose id is no longer
        in ~/.gitconfig — e.g. the includeIf was removed by hand, or the profile was deleted
        before this app cleaned up its own SSH block. Also returns every key path referenced
        by ANY block (active or orphan), so loose-key scanning below doesn't double-report them."""
        orphans, referenced_key_paths = [], set()
        if not os.path.exists(self.ssh_config_path):
            return orphans, referenced_key_paths

        with open(self.ssh_config_path, "r", encoding="utf-8") as f:
            ssh_data = f.read()

        block_pattern = (
            r"\n?# Perfil Autogenerado:[ \t]*(?P<id>\S+)[ \t]*\n"
            r"Host[ \t]+(?P<host>\S+)[ \t]*\n"
            r"[ \t]*HostName[ \t]+(?P<real_host>\S+)[ \t]*\n"
            r"[ \t]*User[ \t]+\S+[ \t]*\n"
            r"[ \t]*IdentityFile[ \t]+(?P<key>\S+)[ \t]*\n"
            r"[ \t]*IdentitiesOnly[ \t]+\S+[ \t]*\n?"
        )
        for m in re.finditer(block_pattern, ssh_data):
            referenced_key_paths.add(m.group("key"))
            if m.group("id") in active_ids:
                continue
            key_path = m.group("key")
            orphans.append({
                "kind": "block",
                "label": f"{m.group('id')} ({m.group('host')})",
                "block_text": m.group(0),
                "priv_path": key_path,
                "pub_path": f"{key_path}.pub",
            })
        return orphans, referenced_key_paths

    def _find_loose_orphan_ssh_keys(self, referenced_key_paths):
        """SSH key pairs in ~/.ssh named like this app's own keys (id_<type>_<profile_id>)
        that aren't referenced by ANY Host block — typically left behind by deleting a
        profile without checking 'also delete the SSH key'."""
        if not os.path.isdir(self.ssh_dir):
            return []

        type_pattern = "|".join(re.escape(t) for t in self.SSH_KEY_TYPES)
        name_re = re.compile(rf"^id_(?:{type_pattern})_.+$")

        loose = []
        for entry in sorted(os.listdir(self.ssh_dir)):
            if entry.endswith(".pub") or not name_re.match(entry):
                continue
            priv_path = os.path.join(self.ssh_dir, entry)
            if priv_path in referenced_key_paths or not os.path.isfile(priv_path):
                continue
            pub_path = f"{priv_path}.pub"
            loose.append({
                "kind": "key",
                "label": entry,
                "block_text": "",
                "priv_path": priv_path,
                "pub_path": pub_path if os.path.isfile(pub_path) else "",
            })
        return loose

    def find_orphan_ssh_entries(self):
        """Combines orphaned ~/.ssh/config Host blocks (dead profile references, possibly
        with dangling IdentityFile paths) and loose key files with no Host block at all."""
        active_ids = {p["id"] for p in self.parse_profiles()}
        block_orphans, referenced_key_paths = self._find_orphan_ssh_host_blocks(active_ids)
        return block_orphans + self._find_loose_orphan_ssh_keys(referenced_key_paths)

    def _remove_ssh_config_block(self, block_text):
        with open(self.ssh_config_path, "r", encoding="utf-8") as f:
            data = f.read()
        new_data = data.replace(block_text, "\n", 1) if block_text in data else data
        if new_data != data:
            with open(self.ssh_config_path, "w", encoding="utf-8") as f:
                f.write(new_data)

    def open_orphan_cleanup_dialog(self):
        try:
            orphans = self.find_orphan_ssh_entries()
        except OSError as e:
            messagebox.showerror(self.tr("orphan_scan_error_title"), self.tr("orphan_scan_error_msg", e=str(e)))
            return

        if not orphans:
            messagebox.showinfo(self.tr("orphan_none_title"), self.tr("orphan_none_msg"))
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(self.tr("orphan_dialog_title"))
        dialog.geometry("460x420")
        dialog.transient(self)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        warn_lbl = ctk.CTkLabel(frame, text=self.tr("orphan_warn"), justify="left", anchor="w", wraplength=420)
        warn_lbl.pack(anchor="w", pady=(0, 10))

        list_frame = ctk.CTkScrollableFrame(frame, height=220)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        item_vars = []
        for orphan in orphans:
            label = orphan["label"] if orphan["pub_path"] or orphan["kind"] == "block" else orphan["label"] + self.tr("orphan_item_no_pub")
            var = ctk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(list_frame, text=label, variable=var)
            chk.pack(anchor="w", pady=3, padx=5)
            item_vars.append((var, orphan))

        def confirm_delete():
            selected = [orphan for var, orphan in item_vars if var.get()]
            if not selected:
                messagebox.showinfo(self.tr("orphan_none_selected_title"), self.tr("orphan_none_selected_msg"), parent=dialog)
                return

            deleted = 0
            for orphan in selected:
                try:
                    if orphan["kind"] == "block":
                        self._remove_ssh_config_block(orphan["block_text"])
                    for path in (orphan["priv_path"], orphan["pub_path"]):
                        if path and os.path.exists(path):
                            os.remove(path)
                    self.log(self.tr("log_orphan_removed", name=orphan["label"]))
                    deleted += 1
                except OSError as e:
                    messagebox.showerror(
                        self.tr("orphan_delete_error_title"),
                        self.tr("orphan_delete_error_msg", name=orphan["label"], e=str(e)),
                        parent=dialog,
                    )

            dialog.destroy()
            if deleted:
                messagebox.showinfo(self.tr("orphan_done_title"), self.tr("orphan_done_msg", n=deleted))

        confirm_btn = ctk.CTkButton(frame, text=self.tr("orphan_confirm_btn"), fg_color="#a83232", hover_color="#802424", command=confirm_delete)
        confirm_btn.pack(pady=(5, 5))

        cancel_btn = ctk.CTkButton(frame, text=self.tr("cancel_btn"), fg_color="gray", command=dialog.destroy)
        cancel_btn.pack(pady=5)

    def refresh_profile_list(self):
        for widget in self.profiles_scroll.winfo_children():
            widget.destroy()

        profiles = self.parse_profiles()
        self.refresh_clone_profiles()

        if not profiles:
            empty_lbl = ctk.CTkLabel(self.profiles_scroll, text=self.tr("list_empty"))
            empty_lbl.pack(padx=10, pady=20)
            return

        for profile in profiles:
            row = ctk.CTkFrame(self.profiles_scroll)
            row.pack(fill="x", padx=5, pady=4)

            name_text = profile["name"] or self.tr("list_no_name")
            email_text = profile["email"] or self.tr("list_no_email")
            details = f"🧩 {profile['id']}  —  {name_text} <{email_text}>\n"
            details += f"📁 {profile['target_dir']}"
            if profile["ssh_host"]:
                details += "\n" + self.tr("list_ssh_host_line", host=profile["ssh_host"], real_host=profile["real_host"])

            lbl = ctk.CTkLabel(row, text=details, justify="left", anchor="w")
            lbl.pack(side="left", padx=10, pady=8, fill="x", expand=True)

            delete_btn = ctk.CTkButton(
                row, text=self.tr("delete_row_btn"), width=90, fg_color="#a83232", hover_color="#802424",
                command=lambda p=profile: self.open_delete_dialog(p),
            )
            delete_btn.pack(side="right", padx=(0, 10), pady=8)

            edit_btn = ctk.CTkButton(row, text=self.tr("edit_row_btn"), width=90, command=lambda p=profile: self.open_edit_dialog(p))
            edit_btn.pack(side="right", padx=10, pady=8)

    def open_edit_dialog(self, profile):
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.tr("edit_dialog_title", id=profile['id']))
        dialog.geometry("480x680")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        form = ctk.CTkFrame(dialog)
        form.pack(fill="both", expand=True, padx=15, pady=15)

        id_lbl = ctk.CTkLabel(form, text=self.tr("edit_profile_label", id=profile['id']), font=ctk.CTkFont(size=15, weight="bold"))
        id_lbl.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        dir_lbl = ctk.CTkLabel(form, text=self.tr("edit_folder_label", dir=profile['target_dir']), text_color="gray")
        dir_lbl.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 15))

        ctk.CTkLabel(form, text=self.tr("edit_name_label")).grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))
        name_entry = ctk.CTkEntry(form, width=380)
        name_entry.insert(0, profile["name"])
        name_entry.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        ctk.CTkLabel(form, text=self.tr("edit_email_label")).grid(row=4, column=0, columnspan=2, sticky="w", pady=(5, 0))
        email_entry = ctk.CTkEntry(form, width=380)
        email_entry.insert(0, profile["email"])
        email_entry.grid(row=5, column=0, columnspan=2, sticky="w", pady=5)

        ctk.CTkLabel(form, text=self.tr("edit_ssh_host_label")).grid(row=6, column=0, columnspan=2, sticky="w", pady=(5, 0))
        ssh_host_entry = ctk.CTkEntry(form, width=380)
        ssh_host_entry.insert(0, profile["ssh_host"])
        ssh_host_entry.grid(row=7, column=0, columnspan=2, sticky="w", pady=5)

        ctk.CTkLabel(form, text=self.tr("edit_real_host_label")).grid(row=8, column=0, columnspan=2, sticky="w", pady=(5, 0))
        real_host_entry = ctk.CTkEntry(form, width=380)
        real_host_entry.insert(0, profile["real_host"])
        real_host_entry.grid(row=9, column=0, columnspan=2, sticky="w", pady=5)

        if not profile["ssh_key_path"]:
            no_ssh_placeholder = self.tr("edit_no_ssh_placeholder")
            ssh_host_entry.configure(state="disabled", placeholder_text=no_ssh_placeholder)
            real_host_entry.configure(state="disabled", placeholder_text=no_ssh_placeholder)

        ctk.CTkLabel(form, text=self.tr("edit_key_type_label")).grid(row=10, column=0, columnspan=2, sticky="w", pady=(15, 0))

        key_type_var = ctk.StringVar(value=profile["ssh_key_type"] or self.SSH_KEY_TYPES[0])
        key_type_menu = ctk.CTkOptionMenu(form, values=self.SSH_KEY_TYPES, variable=key_type_var, width=150)
        key_type_menu.grid(row=11, column=0, sticky="w", pady=5)

        rotate_btn = ctk.CTkButton(
            form, text=self.tr("edit_rotate_key_btn"), width=220, fg_color="#7a5c00", hover_color="#5c4500",
            command=lambda: self.rotate_ssh_key(profile, key_type_var.get(), dialog),
        )
        rotate_btn.grid(row=11, column=1, sticky="e", pady=5)

        rotate_hint_lbl = ctk.CTkLabel(
            form, text=self.tr("edit_rotate_hint"), text_color="gray", justify="left", anchor="w", wraplength=420,
        )
        rotate_hint_lbl.grid(row=12, column=0, columnspan=2, sticky="w", pady=(0, 10))

        if not profile["ssh_key_path"]:
            key_type_menu.configure(state="disabled")
            rotate_btn.configure(state="disabled")

        def save_changes():
            new_name = name_entry.get().strip()
            new_email = email_entry.get().strip()
            new_ssh_host = ssh_host_entry.get().strip()
            new_real_host = real_host_entry.get().strip()

            if not new_name or not new_email:
                messagebox.showerror(self.tr("edit_incomplete_title"), self.tr("edit_incomplete_msg"), parent=dialog)
                return

            try:
                self.save_profile_edit(profile, new_name, new_email, new_ssh_host, new_real_host)
            except Exception as e:
                messagebox.showerror(self.tr("error_title"), self.tr("edit_save_error_msg", e=str(e)), parent=dialog)
                return

            dialog.destroy()
            self.refresh_profile_list()
            messagebox.showinfo(self.tr("edit_updated_title"), self.tr("edit_updated_msg", id=profile['id']))

        save_btn = ctk.CTkButton(form, text=self.tr("edit_save_btn"), command=save_changes)
        save_btn.grid(row=13, column=0, columnspan=2, pady=(20, 5))

        cancel_btn = ctk.CTkButton(form, text=self.tr("cancel_btn"), fg_color="gray", command=dialog.destroy)
        cancel_btn.grid(row=14, column=0, columnspan=2, pady=5)

    def save_profile_edit(self, profile, new_name, new_email, new_ssh_host, new_real_host):
        # Update the sub-gitconfig (name/email)
        with open(profile["gitconfig_path"], "w", encoding="utf-8") as f:
            f.write(f"[user]\n\tname = {new_name}\n\temail = {new_email}\n")
        self.log(self.tr("log_edit_git_updated", id=profile['id'], path=profile['gitconfig_path']))

        # Update the SSH config block, if this profile has one
        if profile["ssh_key_path"] and os.path.exists(self.ssh_config_path):
            with open(self.ssh_config_path, "r", encoding="utf-8") as f:
                ssh_data = f.read()

            pattern = (
                r"(# Perfil Autogenerado:[ \t]*" + re.escape(profile["id"]) + r"[ \t]*\n"
                r"Host[ \t]+)\S+([ \t]*\n"
                r"[ \t]*HostName[ \t]+)\S+([ \t]*\n"
                r"[ \t]*User[ \t]+\S+[ \t]*\n"
                r"[ \t]*IdentityFile[ \t]+\S+[ \t]*\n"
                r"[ \t]*IdentitiesOnly[ \t]+\S+[ \t]*\n)"
            )

            def replace_block(m):
                return f"{m.group(1)}{new_ssh_host}{m.group(2)}{new_real_host}{m.group(3)}"

            new_ssh_data, count = re.subn(pattern, replace_block, ssh_data)
            if count:
                with open(self.ssh_config_path, "w", encoding="utf-8") as f:
                    f.write(new_ssh_data)
                self.log(self.tr("log_edit_ssh_updated", id=profile['id'], host=new_ssh_host, real_host=new_real_host))
            else:
                self.log(self.tr("log_edit_ssh_not_found", id=profile['id']))

    @staticmethod
    def _backup_key_files(key_path):
        backups = {}
        for path in (key_path, f"{key_path}.pub"):
            if os.path.exists(path):
                backup_path = f"{path}.bak-rotate"
                os.replace(path, backup_path)
                backups[path] = backup_path
        return backups

    @staticmethod
    def _restore_key_backups(backups):
        for original, backup_path in backups.items():
            if os.path.exists(backup_path):
                os.replace(backup_path, original)

    @staticmethod
    def _discard_key_backups(backups):
        for backup_path in backups.values():
            if os.path.exists(backup_path):
                os.remove(backup_path)

    def _update_ssh_identity_file(self, profile_id, new_key_path):
        with open(self.ssh_config_path, "r", encoding="utf-8") as f:
            ssh_data = f.read()

        pattern = (
            r"(# Perfil Autogenerado:[ \t]*" + re.escape(profile_id) + r"[ \t]*\n"
            r"Host[ \t]+\S+[ \t]*\n"
            r"[ \t]*HostName[ \t]+\S+[ \t]*\n"
            r"[ \t]*User[ \t]+\S+[ \t]*\n"
            r"[ \t]*IdentityFile[ \t]+)\S+([ \t]*\n)"
        )
        new_ssh_data, count = re.subn(pattern, lambda m: f"{m.group(1)}{new_key_path}{m.group(2)}", ssh_data)
        if not count:
            raise RuntimeError(self.tr("edit_rotate_ssh_block_not_found"))

        with open(self.ssh_config_path, "w", encoding="utf-8") as f:
            f.write(new_ssh_data)

    def _generate_rotated_key(self, profile, new_type, new_key_path):
        self.log(self.tr("log_ssh_generating", type=new_type.upper(), email=profile["email"]))
        cmd = self._ssh_keygen_cmd(new_type, new_key_path, profile["email"])
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        self._update_ssh_identity_file(profile["id"], new_key_path)
        with open(f"{new_key_path}.pub", "r", encoding="utf-8") as pk_f:
            return pk_f.read().strip()

    def rotate_ssh_key(self, profile, new_type, parent_dialog=None):
        """Regenerate the SSH key for a profile with the chosen algorithm, in place.

        Renames the old key aside instead of deleting it outright, so a failed
        ssh-keygen/config update can be rolled back without leaving the profile keyless.
        """
        owner = parent_dialog or self

        if not profile["ssh_key_path"]:
            messagebox.showerror(self.tr("error_title"), self.tr("edit_rotate_no_key_msg"), parent=owner)
            return

        if not messagebox.askyesno(
            self.tr("edit_rotate_confirm_title"),
            self.tr("edit_rotate_confirm_msg", id=profile['id'], type=new_type.upper()),
            parent=owner,
        ):
            return

        new_key_path = os.path.join(self.ssh_dir, f"id_{new_type}_{profile['id']}")
        backups = self._backup_key_files(profile["ssh_key_path"])

        try:
            new_pub_key = self._generate_rotated_key(profile, new_type, new_key_path)
        except Exception as e:
            for path in (new_key_path, f"{new_key_path}.pub"):
                if os.path.exists(path):
                    os.remove(path)
            self._restore_key_backups(backups)
            self.log(self.tr("log_rotate_error", id=profile['id'], e=str(e)))
            messagebox.showerror(self.tr("error_title"), self.tr("edit_rotate_error_msg", e=str(e)), parent=owner)
            return

        self._discard_key_backups(backups)
        self.log(self.tr("log_rotate_done", id=profile['id'], type=new_type.upper(), path=new_key_path))

        if parent_dialog is not None:
            parent_dialog.destroy()
        self.refresh_profile_list()
        self.show_ssh_copier(new_pub_key, profile['id'], profile['target_dir'], profile['ssh_host'], profile['real_host'])
        messagebox.showinfo(self.tr("edit_rotate_done_title"), self.tr("edit_rotate_done_msg", id=profile['id']))

    def open_delete_dialog(self, profile):
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.tr("delete_dialog_title", id=profile['id']))
        dialog.geometry("460x440")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        warn_lbl = ctk.CTkLabel(
            frame,
            text=self.tr("delete_warn", id=profile['id']),
            font=ctk.CTkFont(size=15, weight="bold"),
            wraplength=400,
            justify="left",
        )
        warn_lbl.pack(anchor="w", pady=(0, 10))

        details = [self.tr("delete_item_includeif"), self.tr("delete_item_file", path=profile['gitconfig_path'])]
        if profile["ssh_key_path"]:
            details.append(self.tr("delete_item_ssh_block", host=profile['ssh_host']))
        detail_lbl = ctk.CTkLabel(frame, text=self.tr("delete_will_remove") + "\n" + "\n".join(details), justify="left", anchor="w", wraplength=400)
        detail_lbl.pack(anchor="w", pady=(0, 10))

        keep_lbl = ctk.CTkLabel(
            frame,
            text=self.tr("delete_keep_folder", dir=profile['target_dir']),
            text_color="gray", justify="left", anchor="w", wraplength=400,
        )
        keep_lbl.pack(anchor="w", pady=(0, 15))

        delete_key_var = ctk.BooleanVar(value=False)
        if profile["ssh_key_path"]:
            key_chk = ctk.CTkCheckBox(
                frame,
                text=self.tr("delete_key_checkbox", name=os.path.basename(profile['ssh_key_path'])),
                variable=delete_key_var,
            )
            key_chk.pack(anchor="w", pady=(0, 15))

        def confirm_delete():
            try:
                self.delete_profile(profile, delete_ssh_key=delete_key_var.get())
            except Exception as e:
                messagebox.showerror(self.tr("error_title"), self.tr("delete_error_msg", e=str(e)), parent=dialog)
                return
            dialog.destroy()
            self.refresh_profile_list()
            messagebox.showinfo(self.tr("delete_done_title"), self.tr("delete_done_msg", id=profile['id']))

        delete_btn = ctk.CTkButton(frame, text=self.tr("delete_confirm_btn"), fg_color="#a83232", hover_color="#802424", command=confirm_delete)
        delete_btn.pack(pady=(5, 5))

        cancel_btn = ctk.CTkButton(frame, text=self.tr("cancel_btn"), fg_color="gray", command=dialog.destroy)
        cancel_btn.pack(pady=5)

    def delete_profile(self, profile, delete_ssh_key=False):
        # 1. Remove the sub-gitconfig file
        if os.path.exists(profile["gitconfig_path"]):
            os.remove(profile["gitconfig_path"])
            self.log(self.tr("log_del_removed_file", id=profile['id'], path=profile['gitconfig_path']))

        # 2. Remove the includeIf block from ~/.gitconfig
        if os.path.exists(self.gitconfig_path):
            with open(self.gitconfig_path, "r", encoding="utf-8") as f:
                gitconfig_data = f.read()

            include_pattern = (
                r"\n?\[includeIf[ \t]+\"gitdir:" + re.escape(profile["target_dir"]) + r"/?\"\][ \t]*\n"
                r"[ \t]*path[ \t]*=[ \t]*" + re.escape(profile["gitconfig_path"]) + r"[ \t]*\n?"
            )
            new_gitconfig_data, count = re.subn(include_pattern, "\n", gitconfig_data, count=1)
            if count:
                with open(self.gitconfig_path, "w", encoding="utf-8") as f:
                    f.write(new_gitconfig_data)
                self.log(self.tr("log_del_includeif_removed", id=profile['id']))
            else:
                self.log(self.tr("log_del_includeif_not_found", id=profile['id']))

        # 3. Remove the SSH config block, if this profile had one
        if profile["ssh_key_path"] and os.path.exists(self.ssh_config_path):
            with open(self.ssh_config_path, "r", encoding="utf-8") as f:
                ssh_data = f.read()

            ssh_pattern = (
                r"\n?# Perfil Autogenerado:[ \t]*" + re.escape(profile["id"]) + r"[ \t]*\n"
                r"Host[ \t]+" + re.escape(profile["ssh_host"]) + r"[ \t]*\n"
                r"[ \t]*HostName[ \t]+" + re.escape(profile["real_host"]) + r"[ \t]*\n"
                r"[ \t]*User[ \t]+\S+[ \t]*\n"
                r"[ \t]*IdentityFile[ \t]+" + re.escape(profile["ssh_key_path"]) + r"[ \t]*\n"
                r"[ \t]*IdentitiesOnly[ \t]+\S+[ \t]*\n?"
            )
            new_ssh_data, count = re.subn(ssh_pattern, "\n", ssh_data, count=1)
            if count:
                with open(self.ssh_config_path, "w", encoding="utf-8") as f:
                    f.write(new_ssh_data)
                self.log(self.tr("log_del_ssh_removed", id=profile['id']))
            else:
                self.log(self.tr("log_del_ssh_not_found", id=profile['id']))

        # 4. Optionally remove the SSH key files themselves
        if delete_ssh_key and profile["ssh_key_path"]:
            for key_file in (profile["ssh_key_path"], f"{profile['ssh_key_path']}.pub"):
                if os.path.exists(key_file):
                    os.remove(key_file)
            self.log(self.tr("log_del_key_removed", id=profile['id']))

        self.log(self.tr("log_del_done", id=profile['id']))

    def build_usage_guide(self, provider, ssh_host, real_host, profile_id, target_dir, clone_example):
        test_note = self.PROVIDER_TEST_NOTES.get(provider, self.DEFAULT_TEST_NOTE)
        return (
            self.tr("guide_header", profile_id=profile_id)
            + self.tr("guide_intro", target_dir=target_dir, ssh_host=ssh_host, real_host=real_host)
            + self.tr("guide_clone", clone_example=clone_example, ssh_host=ssh_host)
            + self.tr("guide_pushpull", ssh_host=ssh_host)
            + self.tr("guide_existing", real_host=real_host, ssh_host=ssh_host)
            + self.tr("guide_test", ssh_host=ssh_host, test_note=test_note)
        )

    def show_ssh_copier(self, ssh_key, profile, folder, host, real_host="", provider=None):
        provider = provider or self.OTHER_PROVIDER_LABEL
        copier = ctk.CTkToplevel(self)
        copier.title(self.tr("copier_dialog_title"))
        copier.geometry("640x680")
        copier.resizable(False, False)
        copier.transient(self)
        copier.grab_set()

        lbl = ctk.CTkLabel(copier, text=self.tr("copier_header"), font=ctk.CTkFont(size=18, weight="bold"))
        lbl.pack(pady=(15, 5))

        clone_template = self.PROVIDER_CLONE_EXAMPLES.get(provider, self.DEFAULT_CLONE_EXAMPLE)
        clone_example = clone_template.format(host=host)

        key_lbl = ctk.CTkLabel(copier, text=self.tr("copier_key_label", provider=provider))
        key_lbl.pack(padx=20, pady=(5, 0), anchor="w")

        # Text Box to easily copy SSH key
        ssh_txt = ctk.CTkTextbox(copier, height=100, width=600)
        ssh_txt.pack(padx=20, pady=10)
        ssh_txt.insert("0.0", ssh_key)

        def copy_to_clipboard():
            self.clipboard_clear()
            self.clipboard_append(ssh_key)
            messagebox.showinfo(self.tr("copier_copied_title"), self.tr("copier_copied_msg"))

        copy_btn = ctk.CTkButton(copier, text=self.tr("copier_copy_btn"), command=copy_to_clipboard)
        copy_btn.pack(pady=(0, 10))

        # Personalized guide: clone, push/pull and connection testing for this profile/provider
        guide_lbl = ctk.CTkLabel(copier, text=self.tr("copier_guide_label"), font=ctk.CTkFont(size=14, weight="bold"))
        guide_lbl.pack(padx=20, pady=(5, 0), anchor="w")

        guide_text = self.build_usage_guide(provider, host, real_host, profile, folder, clone_example)
        guide_box = ctk.CTkTextbox(copier, height=280, width=600, wrap="word")
        guide_box.pack(padx=20, pady=10)
        guide_box.insert("0.0", guide_text)
        guide_box.configure(state="disabled")

        close_btn = ctk.CTkButton(copier, text=self.tr("copier_close_btn"), fg_color="gray", command=copier.destroy)
        close_btn.pack(pady=(0, 10))


if __name__ == "__main__":
    app = GitSSHAutomationApp()
    app.mainloop()
