import os
import shutil
import subprocess
import logging

# Configuração de Logs
logging.basicConfig(level=logging.ERROR)

class Mouth:
    def __init__(self):
        """
        Sistema de síntese de voz (TTS) de baixa latência.
        Otimizado para respostas rápidas e diretas no Arch Linux.
        """
        # Procura o binário do Piper (Arch Linux AUR: piper-tts-bin)
        self.piper_binary = (
            shutil.which("piper-tts") or 
            shutil.which("piper") or 
            "/usr/bin/piper-tts"
        )
        
        # Caminho para o modelo de voz PT-BR (Cadu)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        self.piper_model = os.path.join(project_root, "models", "pt_BR-cadu-medium.onnx")
        
        if not self.piper_binary:
            print("[Boca] ⚠️ Aviso: Binário do Piper não encontrado. Instale com: yay -S piper-tts-bin")
        
        if not os.path.exists(self.piper_model):
            print(f"[Boca] ⚠️ Aviso: Modelo de voz não encontrado em {self.piper_model}")

    def speak(self, text):
        """
        Converte texto em fala com velocidade otimizada para o Módulo 3.
        """
        if not text or not text.strip():
            return

        # Limpeza agressiva de caracteres que causam pausas ou erros na síntese
        text = text.replace("*", "").replace("#", "").replace("_", "").strip()
        
        # Log simplificado para o terminal
        print(f"[Boca] Output: '{text}'")

        if not self.piper_binary or not os.path.exists(self.piper_model):
            print("[Boca] ❌ Erro: Componentes de voz ausentes.")
            return

        # --- AJUSTES DO MÓDULO 3 ---
        # --length_scale 0.9: Aumenta a velocidade da fala (10% mais rápido que o padrão)
        # Isso reduz o tempo total de resposta e soa mais eficiente.
        cmd = [
            "sh", "-c",
            f'echo "{text}" | {self.piper_binary} --model "{self.piper_model}" --length_scale 0.9 --output_raw | paplay --raw --rate=22050 --channels=1 --format=s16le'
        ]

        try:
            # Executa a síntese e reprodução via PipeWire/PulseAudio
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[Boca] Erro na síntese/reprodução: {e}")
        except Exception as e:
            print(f"[Boca] Erro inesperado: {e}")

if __name__ == "__main__":
    # Teste de performance do Módulo 3
    mouth = Mouth()
    mouth.speak("Sistemas otimizados. Velocidade de resposta aumentada.")