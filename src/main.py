import sys
import os
import time
import warnings

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
    print("--- INICIALIZANDO ARCH JARVIS v0.3 (Stable Mode) ---")
    
    # 1. Configurar o Cérebro (Gemini)
    if not configurar_gemini():
        print("Erro crítico: Chaves de API não configuradas no ficheiro .env.")
        return
    
    # Seleção do modelo para esta sessão
    modo_cerebro = selecionar_modo_cerebro()
    print(f"Modo selecionado: {modo_cerebro.upper()}")

    # 2. Configurar os Sentidos (Ouvidos e Boca)
    try:
        # Inicializa o Whisper Medium (Versão direta sem filtros)
        print("A carregar ouvidos (Whisper Medium)...")
        ears = Ears(model_size="medium") 
        
        # Inicializa o Piper TTS
        print("A carregar boca (Piper)...")
        mouth = Mouth()
        
        mouth.speak(f"Sistemas online no modo {modo_cerebro}. Aguardando comando.")
        
    except Exception as e:
        print(f"Erro crítico ao carregar os sentidos: {e}")
        return

    print("\n>>> JARVIS PRONTO <<<")
    print("(Pressiona Ctrl+C para encerrar)")

    while True:
        try:
            # Fluxo de Interação: O utilizador controla quando começar a gravar
            input("\n🎤 Pressiona ENTER para INICIAR a gravação...")
            
            # Ouve e transcreve diretamente
            user_text = ears.listen_toggle()
            
            if not user_text or user_text.strip() == "":
                print("⚠️ Silêncio detectado ou comando não compreendido.")
                continue

            # Comandos de saída rápida por voz
            if user_text.lower().strip() in ["sair", "desligar", "encerrar", "tchau"]:
                mouth.speak("A encerrar sistemas. Até logo.")
                break

            # Processamento de IA
            print(f"🧠 A processar ({modo_cerebro})...")
            
            # Instruções de sistema para garantir que a IA responda apenas com texto falável
            instrucoes_sistema = (
                "\n\n[INSTRUÇÃO DE SISTEMA]: "
                "Atue como o assistente Jarvis. "
                "1. NÃO USE EMOJIS (o sintetizador de voz não os lê corretamente). "
                "2. Não use formatação Markdown (como negritos ou asteriscos). "
                "3. Seja direto, conciso e use linguagem natural para fala."
            )
            
            prompt_final = user_text + instrucoes_sistema
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