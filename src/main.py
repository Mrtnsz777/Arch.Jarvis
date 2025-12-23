import sys
import os
import time
import warnings

# --- CONFIGURAÇÕES DE SILENCIAMENTO (Anti-Spam no Terminal) ---
# Define variáveis de ambiente para calar logs do Tensorflow, GRPC e ALSA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Silencia avisos do Tensorflow/Whisper
os.environ['GRPC_VERBOSITY'] = 'ERROR'     # Silencia logs de conexão do Google
os.environ['GLOG_minloglevel'] = '2'       # Silencia logs internos C++

# Ignora avisos de depreciação do Python
warnings.filterwarnings("ignore")

# Adiciona o diretório atual ao path para garantir que as importações funcionem
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.brain import ask_gemini, configurar_gemini
from src.ears import Ears
from src.mouth import Mouth

def selecionar_modo_cerebro():
    """Menu para escolher o modo de operação do cérebro."""
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
    print("--- INICIALIZANDO ARCH JARVIS v0.3 (Silent Mode) ---")
    
    # 1. Configurar Cérebro
    if not configurar_gemini():
        print("Erro crítico: Chaves de API não configuradas.")
        return
    
    # Pergunta qual cérebro usar nesta sessão
    modo_cerebro = selecionar_modo_cerebro()
    print(f"Modo selecionado: {modo_cerebro.upper()}")

    # 2. Configurar Sentidos
    try:
        print("Carregando ouvidos (Whisper)...")
        ears = Ears(model_size="base") 
        
        print("Carregando boca (Piper)...")
        mouth = Mouth()
        
        mouth.speak(f"Sistemas online no modo {modo_cerebro}. Aguardando comando.")
        
    except Exception as e:
        print(f"Erro crítico nos sentidos: {e}")
        return

    print("\n>>> JARVIS PRONTO <<<")
    print("(Pressione Ctrl+C para encerrar)")

    while True:
        try:
            # Novo fluxo: Controle total da gravação
            input("\n🎤 Pressione ENTER para INICIAR a gravação...")
            
            # Chama a função de gravação toggle (Grava até apertar Enter de novo)
            user_text = ears.listen_toggle()
            
            if not user_text or user_text.strip() == "":
                print("⚠️ Silêncio detectado ou áudio vazio.")
                continue

            # Comandos de saída rápida
            if user_text.lower().strip() in ["sair", "desligar", "encerrar", "tchau"]:
                mouth.speak("A encerrar sistemas. Até logo.")
                break

            # Pensar (passando o modo escolhido)
            print(f"🧠 Processando ({modo_cerebro})...")
            
            # --- INJEÇÃO DE REGRAS DE SISTEMA ---
            # Adicionamos instruções invisíveis para formatar a resposta da IA
            instrucoes_sistema = (
                "\n\n[INSTRUÇÃO DE SISTEMA - IMPORTANTE]: "
                "Você é um assistente de voz. "
                "1. NÃO USE EMOJIS. JAMAIS. (O sintetizador lê a descrição deles e fica horrível). "
                "2. NÃO use formatação Markdown (*negrito*, #títulos), apenas texto puro. "
                "3. Seja direto e conciso, ideal para fala."
            )
            
            prompt_final = user_text + instrucoes_sistema
            
            ai_response = ask_gemini(prompt_final, mode=modo_cerebro)
            
            print(f"🤖 Jarvis: {ai_response}")

            # Falar
            mouth.speak(ai_response)

        except KeyboardInterrupt:
            print("\nEncerrando forçadamente...")
            break
        except Exception as e:
            print(f"Erro no loop principal: {e}")
            # mouth.speak("Ocorreu um erro interno.") # Opcional

if __name__ == "__main__":
    main()