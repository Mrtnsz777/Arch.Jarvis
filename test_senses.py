import sys
import os

print("--- Iniciando Diagnóstico do Jarvis ---")

# Verifica se os módulos existem
if not os.path.exists("src/ears.py"):
    print("ERRO CRÍTICO: src/ears.py não encontrado!")
    sys.exit(1)
if not os.path.exists("src/mouth.py"):
    print("ERRO CRÍTICO: src/mouth.py não encontrado!")
    sys.exit(1)

print("Importando módulos (pode demorar alguns segundos)...")

try:
    from src.ears import Ears
    from src.mouth import Mouth
except ImportError as e:
    print(f"ERRO de Importação: {e}")
    print("Verifique se o venv está ativo e as dependências instaladas.")
    sys.exit(1)

def main():
    print("\n--- Teste de Sentidos do Arch Jarvis ---")
    print("A carregar o modelo Whisper (isto baixa ~150MB na 1ª vez)...")
    
    try:
        # Usa 'base' para ser rápido. Se tiveres GPU NVIDIA, ele será mais veloz.
        ears = Ears(model_size="base") 
        mouth = Mouth()
    except Exception as e:
        print(f"ERRO ao iniciar sentidos: {e}")
        return
    
    print("\n>>> SISTEMA PRONTO <<<")
    
    while True:
        try:
            input("\nPressiona ENTER para falar (5 segundos) ou Ctrl+C para sair...")
            
            # 1. Escutar
            print(">> A OUVIR AGORA... (Fale algo!)")
            texto_ouvido = ears.listen(duration=5)
            
            if not texto_ouvido:
                print(">> Não ouvi nada (silêncio ou erro de mic).")
                continue
                
            # 2. Falar (Eco)
            resposta = f"Tu disseste: {texto_ouvido}"
            mouth.speak(resposta)
            
        except KeyboardInterrupt:
            print("\nEncerrando teste.")
            break
        except Exception as e:
            print(f"Erro durante o loop: {e}")

if __name__ == "__main__":
    main()