import sys
import os
import time
import warnings
import re  # Regex para múltiplos comandos e digitação
import subprocess # Necessário para comandos wtype customizados (CTRL+K)
from datetime import datetime

# --- CONFIGURAÇÕES DE SILENCIAMENTO ---
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'

warnings.filterwarnings("ignore")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.brain import ask_gemini, configurar_gemini
from src.ears import Ears
from src.mouth import Mouth
from src.actions import execute_command, type_text, press_key # Importa funções básicas

# --- SYSTEM PROMPT (Cérebro do Jarvis - Módulo 4.5 Full Integration) ---
SYSTEM_PROMPT = (
    "Sua identidade é Jarvis, assistente do Arch Linux. Personalidade: Fria, eficiente, técnica. "
    "REGRAS DE AÇÃO: "
    "1. Responda com TAGS DE AÇÃO no início. Não descreva o processo. Se citar o comando, dê uma explicação breve. "
    "2. Suporte a MÚLTIPLAS ações e MACROS. "
    "3. Lista de TAGS autorizadas: "
    "- Macro de Trabalho: [ACTION: START_WORK_MODE] (Ativa com 'começar trabalho', 'vamos ao trabalho', 'abrir area de trabalho'). "
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
    "4. Para perguntas gerais, responda curto, sem tags e sem emojis."
)

def selecionar_modo_cerebro():
    """Menu para escolher o modo de operação."""
    print("\n--- SELEÇÃO DE MODELO ---")
    print("1. Auto [Recomendado]")
    print("2. Pro (Gemini 2.5 Pro)")
    print("3. Flash (Gemini 2.5 Flash)")
    escolha = input("Opção [1-3]: ").strip()
    return "pro" if escolha == "2" else "flash" if escolha == "3" else "auto"

def processar_resposta_ia(resposta_texto, mouth):
    """
    Processa ações, macros e dispara áudios fixos (ElevenLabs) quando disponível.
    """
    # Regex captura: ACTION, TYPE, WAIT ou KEY
    comandos_encontrados = re.findall(r"\[(ACTION|TYPE|WAIT|KEY): (.*?)\]", resposta_texto)
    
    texto_para_falar = resposta_texto
    feedbacks_sistema = []

    if comandos_encontrados:
        print(f"⚡ COMANDOS: {comandos_encontrados}")
        
        for tipo, conteudo in comandos_encontrados:
            sucesso = False
            msg = ""
            conteudo = conteudo.strip()
            
            if tipo == "ACTION":
                # --- TRIGGERS DE ÁUDIO FIXO (Prioridade) ---
                if conteudo == "LOCK_SCREEN":
                    mouth.play_fixed("SysBlock")
                elif conteudo == "SYSTEM_POWEROFF":
                    mouth.play_fixed("PowerOff")
                    time.sleep(2) # Espera o áudio
                elif conteudo == "SYSTEM_REBOOT":
                    mouth.play_fixed("Reboot")
                    time.sleep(2)
                elif "SEARCH" in conteudo:
                    mouth.play_fixed("Searching")
                elif "OPEN_" in conteudo:
                    mouth.play_fixed("Exec")

                # --- MACRO DE TRABALHO ---
                if conteudo == "START_WORK_MODE":
                    print(f"⚡ MACRO TRABALHO: Iniciando setup produtivo...")
                    # Toca o áudio de Workspace Pronto
                    mouth.play_fixed("WorkspaceReady")
                    
                    # Workspace 1: Navegador
                    execute_command("WORKSPACE_1")
                    time.sleep(0.5)
                    execute_command("OPEN_BRAVE")
                    
                    # Workspace 2: Terminal e Code
                    time.sleep(1.0)
                    execute_command("WORKSPACE_2")
                    time.sleep(0.5)
                    execute_command("OPEN_TERMINAL")
                    time.sleep(0.3)
                    execute_command("OPEN_CODE")
                    
                    # Workspace 3: Discord (Com delay longo)
                    time.sleep(1.0)
                    execute_command("WORKSPACE_3")
                    time.sleep(0.5)
                    execute_command("OPEN_DISCORD")
                    print("⏳ Aguardando inicialização do Discord...")
                    time.sleep(6.0) 
                    
                    # Workspace 4: Spotify
                    execute_command("WORKSPACE_4")
                    time.sleep(0.5)
                    execute_command("OPEN_SPOTIFY")
                    
                    sucesso = True
                    msg = "" # Já tocou áudio fixo, não precisa falar

                # --- MACROS DE PESQUISA ---
                elif conteudo.startswith("SEARCH_YOUTUBE:"):
                    termo = conteudo.split(":", 1)[1].strip()
                    print(f"⚡ MACRO YOUTUBE: Pesquisando '{termo}'...")
                    
                    execute_command("OPEN_BRAVE")
                    time.sleep(2.5) 
                    
                    type_text("youtube.com")
                    press_key("ENTER")
                    time.sleep(3.5) 
                    
                    for _ in range(4):
                        press_key("TAB")
                        time.sleep(0.1)
                        
                    print(f"⌨️ Digitando busca: {termo}")
                    type_text(termo)
                    time.sleep(0.2)
                    press_key("ENTER")
                    
                    sucesso = True
                    msg = "" # Audio 'Searching' já tocou

                else:
                    # Comandos Normais
                    sucesso, msg = execute_command(conteudo)
                    if conteudo == "CLOSE_WINDOW": msg = "Janela fechada."
                    
                    # Delay Automático para Discord isolado
                    if conteudo == "OPEN_DISCORD":
                        print("⏳ Aguardando 5s para o Discord...")
                        time.sleep(5)
                    else:
                        time.sleep(0.2)
                
            elif tipo == "TYPE":
                time.sleep(0.5) 
                print(f"⌨️ Digitando: {conteudo}")
                sucesso, msg = type_text(conteudo)
                
            elif tipo == "KEY":
                time.sleep(0.2)
                sucesso, msg = press_key(conteudo)
                
            elif tipo == "WAIT":
                try:
                    segundos = float(conteudo)
                    print(f"⏳ Aguardando {segundos}s...")
                    time.sleep(segundos)
                    sucesso = True
                except ValueError: pass

            if sucesso and msg:
                feedbacks_sistema.append(msg)

        # Limpa tags do texto final
        texto_para_falar = re.sub(r"\[(ACTION|TYPE|WAIT|KEY): .*?\]", "", resposta_texto).strip()
        
        # Se não sobrou texto e não há feedback do sistema, retorna vazio (silêncio)
        if not texto_para_falar:
            texto_para_falar = " ".join(feedbacks_sistema)

    return texto_para_falar

def main():
    print("--- ARCH JARVIS v0.5 | Audio Premium & Macros ---")
    
    if not configurar_gemini():
        return
    
    modo_cerebro = selecionar_modo_cerebro()
    
    try:
        print("Inicializando sentidos...")
        ears = Ears(model_size="medium") 
        mouth = Mouth()
        
        # BOAS VINDAS (Toca o áudio do ElevenLabs se existir)
        if not mouth.play_fixed("SystemLoad"):
            mouth.speak("Interface de comando ativa.") 
            
    except Exception as e:
        print(f"Erro: {e}")
        return

    print("\n>>> JARVIS PRONTO <<<")

    while True:
        try:
            input("\n🎤 [ENTER] para falar...")
            user_text = ears.listen_toggle()
            
            if not user_text or user_text.strip() == "":
                continue

            # Saída rápida (Usa o áudio fixo se disponível)
            if user_text.lower() in ["sair", "desligar"]:
                if not mouth.play_fixed("PowerOff"):
                    mouth.speak("Desligando.")
                break

            print(f"🧠 Processando...")
            
            hora = datetime.now().strftime("%H:%M")
            prompt_final = f"{SYSTEM_PROMPT}\n[SISTEMA] Hora: {hora}\nUsuário: {user_text}"
            
            raw_response = ask_gemini(prompt_final, mode=modo_cerebro)
            print(f"🤖 Raw: {raw_response}")

            # Passamos o objeto 'mouth' para tocar sons dentro da função
            speech_text = processar_resposta_ia(raw_response, mouth)
            
            # Fala o texto restante (se houver) via Piper
            if speech_text:
                mouth.speak(speech_text)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erro no loop: {e}")
            mouth.play_fixed("NetError") # Tenta tocar som de erro

if __name__ == "__main__":
    main()