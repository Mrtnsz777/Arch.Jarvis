import sys
import os
import time

# Adiciona o diretório atual ao path para garantir que as importações funcionem
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.brain import ask_gemini, configurar_gemini
from src.ears import Ears
from src.mouth import Mouth

def main():
    print("--- INICIALIZANDO ARCH JARVIS ---")
    
    # 1. Configurar Cérebro
    if not configurar_gemini():
        print("Erro no cérebro. Verifique o .env")
        return

    # 2. Configurar Sentidos
    try:
        print("Carregando ouvidos (Whisper)...")
        ears = Ears(model_size="base")
        
        print("Carregando boca (Piper)...")
        mouth = Mouth()
        
        # Som de boas-vindas
        mouth.speak("Sistemas online. Estou à escuta.")
        
    except Exception as e:
        print(f"Erro crítico nos sentidos: {e}")
        return

    print("\n>>> JARVIS PRONTO PARA CONVERSAR <<<")
    print("(Pressione Ctrl+C para encerrar)")

    while True:
        try:
            # Loop principal de interação
            input("\nPressione ENTER para falar...")
            
            # A. Ouvir
            print("🎤 Ouvindo...")
            user_text = ears.listen(duration=5)
            
            if not user_text or user_text.strip() == "":
                print("⚠️ Não entendi ou houve silêncio.")
                continue

            print(f"👤 Você disse: {user_text}")
            
            # Comandos de saída rápida
            if user_text.lower().strip() in ["sair", "desligar", "encerrar", "tchau"]:
                mouth.speak("A encerrar sistemas. Até logo.")
                break

            # B. Pensar
            print("🧠 Processando...")
            # Opcional: Feedback de áudio para latência de rede
            # mouth.speak("Um momento.") 
            
            ai_response = ask_gemini(user_text)
            print(f"🤖 Jarvis: {ai_response}")

            # C. Falar
            mouth.speak(ai_response)

        except KeyboardInterrupt:
            print("\nEncerrando forçadamente...")
            break
        except Exception as e:
            print(f"Erro no loop principal: {e}")
            mouth.speak("Ocorreu um erro interno.")

if __name__ == "__main__":
    main()