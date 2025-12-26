import sys
import os
import time
import warnings
import re
import signal
import threading
import json
import gc
import builtins
from datetime import datetime

# --- CONFIGURAÇÕES DE SILENCIAMENTO ---
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.brain import ask_gemini, configurar_gemini
# Não importamos Ears e Mouth globalmente para economizar RAM inicial
from src.actions import execute_command, type_text, press_key

# --- CONFIGURAÇÃO HEADLESS E STATUS ---
trigger_event = threading.Event()
STATUS_FILE = "/tmp/jarvis_status.json"

def update_status(text="", css_class="idle", tooltip="Jarvis Offline"):
    """Atualiza o arquivo JSON para o módulo da Waybar."""
    data = {
        "text": text,
        "class": css_class,
        "tooltip": tooltip
    }
    try:
        with open(STATUS_FILE, "w") as f:
            json.dump(data, f)
        # Envia sinal para atualizar a Waybar imediatamente
        os.system("pkill -RTMIN+8 waybar")
    except Exception:
        pass

def signal_handler(sig, frame):
    """Recebe o sinal do Hyprland."""
    trigger_event.set()

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = (
    "Sua identidade é Jarvis, assistente do Arch Linux. Personalidade: Fria, eficiente, técnica. "
    "REGRAS DE AÇÃO: "
    "1. Responda com TAGS DE AÇÃO no início. Não descreva o processo. "
    "2. Tags: [ACTION: OPEN_BRAVE], [ACTION: CLOSE_WINDOW], [ACTION: LOCK_SCREEN], "
    "[ACTION: SYSTEM_POWEROFF], [ACTION: SYSTEM_REBOOT], [ACTION: START_WORK_MODE]. "
    "3. Para perguntas gerais, responda curto, sem tags e sem emojis."
    "4. Lista de TAGS autorizadas:"
    "   - 'Abrir minha área de trabalho' ou 'Começar trabalho' -> [ACTION: START_WORK_MODE]."
    "- Pesquisas: [ACTION: SEARCH_YOUTUBE: termo]. "
    "- Apps: [ACTION: OPEN_BRAVE], [ACTION: OPEN_CODE], [ACTION: OPEN_SPOTIFY], [ACTION: OPEN_DISCORD], "
    "[ACTION: OPEN_TERMINAL], [ACTION: OPEN_OBS], [ACTION: OPEN_FILES], [ACTION: OPEN_MENU]. "
    "- Sistema: [ACTION: CLOSE_WINDOW], [ACTION: TOGGLE_FLOATING], [ACTION: LOCK_SCREEN], "
    "[ACTION: SYSTEM_POWEROFF], [ACTION: SYSTEM_REBOOT]. "
    "- Digitação: [TYPE: Texto]. Teclas: [KEY: ENTER], [KEY: TAB], [KEY: ESC]. "
    "- Espera: [WAIT: Segundos]. "
    "- Workspaces: [ACTION: WORKSPACE_1] até [ACTION: WORKSPACE_10]. "
    "- Mover Janela: [ACTION: MOVE_TO_WORKSPACE_1] até [ACTION: MOVE_TO_WORKSPACE_10]. "
    "- Mídia: [ACTION: VOLUME_UP], [ACTION: VOLUME_DOWN], [ACTION: VOLUME_MUTE], "
    "[ACTION: MEDIA_PLAY_PAUSE], [ACTION: MEDIA_NEXT], [ACTION: MEDIA_PREV]. "
)

def processar_resposta_ia(resposta_texto, mouth):
    """Processa ações e toca sons."""
    comandos_encontrados = re.findall(r"\[(ACTION|TYPE|WAIT|KEY): (.*?)\]", resposta_texto)
    texto_para_falar = re.sub(r"\[(ACTION|TYPE|WAIT|KEY): .*?\]", "", resposta_texto).strip()
    
    if comandos_encontrados:
        print(f"⚡ COMANDOS: {comandos_encontrados}", flush=True)
        for tipo, conteudo in comandos_encontrados:
            conteudo = conteudo.strip()
            
            if tipo == "ACTION":
                # Lógica de Áudios Fixos
                if conteudo == "LOCK_SCREEN": mouth.play_fixed("SysBlock")
                elif conteudo == "SYSTEM_POWEROFF": mouth.play_fixed("PowerOff"); time.sleep(2)
                elif conteudo == "SYSTEM_REBOOT": mouth.play_fixed("Reboot"); time.sleep(2)
                elif "SEARCH" in conteudo: mouth.play_fixed("Searching")
                elif "OPEN_" in conteudo: mouth.play_fixed("Exec")
                
                # Execução de Comandos
                if conteudo == "START_WORK_MODE":
                    print("⚡ Iniciando sequência de trabalho...")
                    # Sequência de Abertura
                    execute_command("WORKSPACE_1"); time.sleep(0.5); execute_command("OPEN_BRAVE")
                    time.sleep(2.0)
                    execute_command("WORKSPACE_2"); time.sleep(0.5); execute_command("OPEN_TERMINAL"); time.sleep(0.3); execute_command("OPEN_CODE")
                    time.sleep(2.0)
                    execute_command("WORKSPACE_3"); time.sleep(0.5); execute_command("OPEN_DISCORD")
                    time.sleep(6.0) 
                    execute_command("WORKSPACE_4"); time.sleep(1.5); execute_command("OPEN_SPOTIFY"); time.sleep(2.0)
                    
                    # CORREÇÃO: Toca o áudio APÓS configurar tudo
                    mouth.play_fixed("WorkspaceReady")
                    
                    sucesso = True; msg = ""
                elif "SEARCH_YOUTUBE" in conteudo:
                    termo = conteudo.split(":", 1)[1].strip()
                    mouth.play_fixed("Searching")
                    execute_command("OPEN_BRAVE"); time.sleep(2.5)
                    type_text("youtube.com"); press_key("ENTER"); time.sleep(3.5)
                    for _ in range(4): press_key("TAB"); time.sleep(0.1)
                    type_text(termo); time.sleep(0.2); press_key("ENTER")
                    sucesso = True; msg = ""
                elif "SEARCH_SPOTIFY" in conteudo:
                    termo = conteudo.split(":", 1)[1].strip()
                    mouth.play_fixed("Searching")
                    execute_command("OPEN_SPOTIFY"); time.sleep(4.0)
                    try:
                        subprocess.run(["wtype", "-M", "ctrl", "-k", "k", "-m", "ctrl"])
                        time.sleep(1.5)
                        type_text(termo); time.sleep(1.0); press_key("ENTER")
                    except: pass
                else:
                    execute_command(conteudo)
                    if conteudo == "OPEN_DISCORD": time.sleep(5)
                    else: time.sleep(0.2)

            elif tipo == "TYPE":
                time.sleep(0.5); type_text(conteudo)
            elif tipo == "KEY":
                time.sleep(0.2); press_key(conteudo)
            elif tipo == "WAIT":
                try: time.sleep(float(conteudo))
                except: pass

    return texto_para_falar

def main():
    # Salva PID
    pid = os.getpid()
    with open("/tmp/arch_jarvis.pid", "w") as f:
        f.write(str(pid))

    print(f"--- ARCH JARVIS v0.6 | Headless Optimized (PID: {pid}) ---", flush=True)
    signal.signal(signal.SIGUSR1, signal_handler)
    
    if not configurar_gemini(): return
    
    # Status Inicial: Ocioso
    update_status("", "idle", "Jarvis: Aguardando Comando")

    # Importação Lazy dos Módulos
    from src.ears import Ears
    from src.mouth import Mouth
    
    # Inicialização Leve da Boca
    mouth = Mouth()
    mouth.play_fixed("SystemLoad") 

    while True:
        try:
            # 1. ESTADO OCIOSO (Baixo Consumo de RAM)
            if not sys.stdin.isatty():
                trigger_event.wait()
                trigger_event.clear()
            else:
                input("\n🎤 [ENTER] para falar...")

            # --- ACORDANDO ---
            print(">>> ATIVADO", flush=True)
            update_status("", "listening", "Ouvindo...")
            
            # ALTERADO: Toca 'Beep' em thread para não travar o início da gravação
            threading.Thread(target=mouth.play_fixed, args=("Beep",)).start()
            
            # 2. CARREGAMENTO DOS OUVIDOS (Lazy Loading)
            print("Carregando modelo Whisper...", flush=True)
            ears = Ears(model_size="medium")
            
            # Monkey Patch do input para o listen_toggle
            import builtins
            def signal_input(prompt=""):
                if not sys.stdin.isatty():
                    trigger_event.wait()
                    trigger_event.clear()
                else:
                    input(prompt)
                print(">>> PARANDO GRAVAÇÃO", flush=True)
                
                # ALTERADO: Toca 'Beep' de fim em thread
                threading.Thread(target=mouth.play_fixed, args=("Beep",)).start()
                
                # --- CORREÇÃO UI: Atualiza status imediatamente ---
                update_status("", "processing", "Transcrevendo Áudio...")
                return ""
            builtins.input = signal_input

            # 3. GRAVAÇÃO E TRANSCRIÇÃO
            user_text = ears.listen_toggle()
            
            # 4. LIMPEZA IMEDIATA (Libera RAM)
            del ears
            gc.collect() 
            print("Modelo de áudio descarregado.", flush=True)
            
            if not user_text or user_text.strip() == "":
                update_status("", "idle", "Jarvis: Aguardando Comando")
                continue

            # Saída rápida
            if user_text.lower() in ["sair", "desligar"]:
                if not mouth.play_fixed("PowerOff"): mouth.speak("Desligando.")
                break

            # 5. PROCESSAMENTO (Thinking)
            update_status("", "processing", "Gerando Resposta...")
            print(f"🧠 Processando...", flush=True)
            
            hora = datetime.now().strftime("%H:%M")
            prompt = f"{SYSTEM_PROMPT}\n[SISTEMA] Hora: {hora}\nUsuário: {user_text}"
            
            resp = ask_gemini(prompt, mode="auto")
            print(f"🤖 Jarvis: {resp}", flush=True)

            # 6. RESPOSTA E AÇÃO
            speech = processar_resposta_ia(resp, mouth)
            if speech:
                mouth.speak(speech)
            
            # Volta ao estado Ocioso
            update_status("", "idle", "Jarvis: Aguardando Comando")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erro no loop: {e}", flush=True)
            update_status("", "error", f"Erro: {str(e)}")
            mouth.play_fixed("NetError")
            # Reseta estado após erro
            time.sleep(2)
            update_status("", "idle", "Jarvis: Aguardando Comando")

if __name__ == "__main__":
    main()