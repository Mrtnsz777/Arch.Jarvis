import subprocess
import os
import shutil
import time

# Verifica se o wtype (digitador para Wayland/Hyprland) está instalado
WTYPE_PATH = shutil.which("wtype")

# --- LISTA BRANCA DE COMANDOS (SEGURANÇA) ---
COMMAND_MAP = {
    # --- Aplicações (Atalhos do Hyprland) ---
    "OPEN_BRAVE": ["hyprctl", "dispatch", "exec", "brave"],
    "OPEN_CODE": ["hyprctl", "dispatch", "exec", "code"],
    "OPEN_SPOTIFY": ["hyprctl", "dispatch", "exec", "spotify"],
    "OPEN_OBS": ["hyprctl", "dispatch", "exec", "obs"],
    "OPEN_DISCORD": ["hyprctl", "dispatch", "exec", "discord"],
    "OPEN_TERMINAL": ["hyprctl", "dispatch", "exec", "kitty"],
    "OPEN_FILES": ["hyprctl", "dispatch", "exec", "dolphin"],
    "OPEN_MENU": ["hyprctl", "dispatch", "exec", "wofi --show drun"],
    
    # --- Controle de Janelas e Sistema ---
    "CLOSE_WINDOW": ["hyprctl", "dispatch", "killactive"],
    "TOGGLE_FLOATING": ["hyprctl", "dispatch", "togglefloating"],
    "LOCK_SCREEN": ["hyprctl", "dispatch", "exec", "hyprlock"], 
    
    # --- Energia (Sem sudo, via systemd) ---
    "SYSTEM_POWEROFF": ["systemctl", "poweroff"],
    "SYSTEM_REBOOT": ["systemctl", "reboot"],

    # --- Controle de Mídia ---
    "VOLUME_UP": ["pamixer", "-i", "5"],
    "VOLUME_DOWN": ["pamixer", "-d", "5"],
    "VOLUME_MUTE": ["pamixer", "-t"],
    "MEDIA_PLAY_PAUSE": ["playerctl", "play-pause"],
    "MEDIA_NEXT": ["playerctl", "next"],
    "MEDIA_PREV": ["playerctl", "previous"],
}

# Gera dinamicamente os comandos para Workspaces 1 a 10
for i in range(1, 11):
    COMMAND_MAP[f"WORKSPACE_{i}"] = ["hyprctl", "dispatch", "workspace", str(i)]
    COMMAND_MAP[f"MOVE_TO_WORKSPACE_{i}"] = ["hyprctl", "dispatch", "movetoworkspace", str(i)]

def execute_command(action_intent):
    """
    Executa comandos do sistema mapeados.
    """
    action_intent = action_intent.upper().strip()
    
    if action_intent not in COMMAND_MAP:
        return False, "Comando desconhecido."

    cmd = COMMAND_MAP[action_intent]
    
    try:
        subprocess.Popen(cmd)
        
        # Feedbacks curtos para o orquestrador (se necessário)
        if "LOCK" in action_intent: return True, "Bloqueado."
        if "POWEROFF" in action_intent: return True, "Desligando..."
        if "REBOOT" in action_intent: return True, "Reiniciando..."
        if "MEDIA" in action_intent: return True, "Mídia."
        if "VOLUME" in action_intent: return True, "Volume."
        if "MOVE" in action_intent: return True, "Movido."
        if "WORKSPACE" in action_intent: return True, "Workspace."
        
        target = action_intent.replace("OPEN_", "").replace("_", " ").lower().capitalize()
        return True, f"{target}."
        
    except Exception as e:
        print(f"[Ações] Erro ao executar '{action_intent}': {e}")
        return False, "Erro na execução."

def type_text(text):
    """
    Digita texto usando wtype.
    """
    if not WTYPE_PATH:
        print("[Ações] Erro: 'wtype' não encontrado.")
        return False, "Erro de digitação."
        
    try:
        subprocess.run([WTYPE_PATH, text], check=True)
        return True, "Digitado."
    except Exception as e:
        print(f"[Ações] Erro ao digitar: {e}")
        return False, "Erro na digitação."

def press_key(key_name):
    """
    Pressiona uma tecla específica (ex: Return, Tab, Escape).
    """
    if not WTYPE_PATH:
        return False, "Wtype não instalado."

    # Mapeamento simples para nomes comuns se necessário
    key_map = {
        "ENTER": "Return",
        "ESC": "Escape",
        "TAB": "Tab",
        "SPACE": "space",
        "BACKSPACE": "BackSpace"
    }
    
    # Usa o nome mapeado ou o próprio nome se não estiver na lista (ex: F1, F2)
    linux_key = key_map.get(key_name.upper(), key_name)
    
    try:
        # wtype -k [key] pressiona e solta a tecla
        subprocess.run([WTYPE_PATH, "-k", linux_key], check=True)
        return True, "Tecla pressionada."
    except Exception as e:
        print(f"[Ações] Erro ao pressionar tecla: {e}")
        return False, "Erro de tecla."