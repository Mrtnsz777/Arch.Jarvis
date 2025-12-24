import sys
import os
import time
import warnings
from datetime import datetime # Importação necessária para o tempo

# --- CONFIGURAÇÕES DE SILENCIAMENTO (Evita poluição no terminal) ---
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Silencia avisos do Tensorflow/Whisper
os.environ['GRPC_VERBOSITY'] = 'ERROR'     # Silencia logs de conexão do Google
os.environ['GLOG_minloglevel'] = '2'       # Silencia logs internos C++

# Ignora avisos de depreciação para manter a interface limpa
warnings.filterwarnings("ignore")

# Adiciona o diretório atual ao path para garantir que as importações funcionem
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.brain import ask_gemini, configurar_gemini
from src.ears import Ears
from src.mouth import Mouth

# --- SYSTEM PROMPT (O Cérebro do Jarvis - Módulo 3) ---
# Otimizado para TTS: Respostas frias, sem enrolação e com pontuação mínima para evitar pausas.
SYSTEM_PROMPT = (
    "Sua identidade é Jarvis assistente técnico integrado ao Arch Linux com Hyprland. "
    "Sua personalidade é fria direta e eficiente. "
    "REGRAS OBRIGATÓRIAS: "
    "1. JAMAIS use saudações como Olá ou Como posso ajudar. Vá direto ao ponto. "
    "2. JAMAIS use emojis ou formatação Markdown como negritos ou listas. Texto puro apenas. "
    "3. Use pontuação mínima. Evite vírgulas desnecessárias para não causar pausas no áudio. "
    "4. Navegador: Use exclusivamente o Brave. Ignore Firefox ou Chrome. "
    "5. Atalhos do Hyprland: "
    "- Brave: SUPER B | VS Code: SUPER Z | Spotify: SUPER S | "
    "- OBS: SUPER O | Discord: SUPER D | Floating: SUPER + V | Terminal: SUPER Q. "
    "6. Se pedirem para abrir um app cite o atalho de forma curta. "
    "7. Fale como um sistema operacional de alto desempenho. Sem papo furado."
)

def selecionar_modo_cerebro():
    """
    Menu para escolher o modo de operação da Inteligência Artificial.
    """
    print("\n--- SELEÇÃO DE MODELO ---")
    print("1. Auto (Tenta Pro, fallback para Flash) [Recomendado]")
    print("2. Pro (Apenas Gemini 2.5 Pro - Mais inteligente)")
    print("3. Flash (Apenas Gemini 2.5 Flash - Mais rápido)")
    
    escolha = input("Escolha uma opção [1-3]: ").strip()
    
    if escolha == "2":
        return "pro"
    elif escolha == "3":
        return "flash"
    else:
        return "auto"

def main():
    print("--- ARCH JARVIS v0.3 | Módulo 3: Refinamento de Personalidade + Time Aware ---")
    
    # 1. Configurar o Cérebro (Gemini)
    if not configurar_gemini():
        print("Erro crítico: Chaves de API não configuradas no ficheiro .env.")
        return
    
    # Seleção do modelo para esta sessão
    modo_cerebro = selecionar_modo_cerebro()
    print(f"Modo selecionado: {modo_cerebro.upper()}")

    # 2. Configurar os Sentidos (Ouvidos e Boca)
    try:
        # Inicializa o Whisper (Faster-Whisper via CPU conforme estabilizado anteriormente)
        print("A carregar ouvidos (Faster-Whisper)...")
        ears = Ears(model_size="medium") 
        
        # Inicializa o Piper TTS
        print("A carregar boca (Piper)...")
        mouth = Mouth()
        
        # Inicialização rápida
        mouth.speak("Sistemas online") 
        
    except Exception as e:
        print(f"Erro crítico ao carregar os sentidos: {e}")
        return

    print("\n>>> JARVIS PRONTO <<<")
    print("(Pressiona Ctrl+C para encerrar)")

    while True:
        try:
            # Fluxo de Interação: O utilizador controla quando começar a gravar (Trigger on Demand)
            input("\n🎤 Pressiona ENTER para INICIAR a gravação...")
            
            # Ouve e transcreve diretamente
            user_text = ears.listen_toggle()
            
            if not user_text or user_text.strip() == "":
                print("⚠️ Silêncio detectado ou comando não compreendido.")
                continue

            # Comandos de saída rápida por voz
            if user_text.lower().strip() in ["sair", "desligar", "encerrar", "tchau"]:
                mouth.speak("Encerrando")
                break

            # Processamento de IA
            print(f"🧠 A processar ({modo_cerebro})...")
            
            # --- INJEÇÃO DE CONTEXTO TEMPORAL ---
            # Pega a hora atual do sistema e formata (Ex: "14:30")
            hora_atual = datetime.now().strftime("%H:%M")
            data_atual = datetime.now().strftime("%d/%m/%Y")
            
            # Adiciona ao prompt como uma informação de sistema invisível
            contexto_tempo = f"\n[DADOS DO SISTEMA]: Hora atual: {hora_atual}. Data: {data_atual}."
            
            # Combinação do Prompt de Sistema + Tempo + entrada do usuário
            prompt_final = f"{SYSTEM_PROMPT}\n{contexto_tempo}\n\nUsuário: {user_text}"
            
            # Chama o Gemini com o modo selecionado no menu inicial
            ai_response = ask_gemini(prompt_final, mode=modo_cerebro)
            
            print(f"🤖 Jarvis: {ai_response}")

            # Reprodução da resposta por voz
            mouth.speak(ai_response)

        except KeyboardInterrupt:
            print("\nEncerrando sessão...")
            break
        except Exception as e:
            print(f"Erro no loop principal: {e}")

if __name__ == "__main__":
    main()