import os
import shutil
import subprocess
import logging

# Configuração de Logs
logging.basicConfig(level=logging.ERROR)

class Mouth:
    def __init__(self):
        """
        Sistema de síntese de voz (TTS) focado em estabilidade e baixa latência.
        Utiliza o Piper TTS para gerar voz localmente sem sobrecarregar a GPU.
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
        Recebe um texto e converte-o em fala imediatamente.
        """
        if not text or not text.strip():
            return

        # Limpeza simples para evitar que o sintetizador tente ler caracteres especiais
        text = text.replace("*", "").replace("#", "").replace("_", "").strip()
        
        print(f"[Boca] A falar: '{text}'")

        if not self.piper_binary or not os.path.exists(self.piper_model):
            print("[Boca] ❌ Erro: O sistema de voz não está configurado corretamente.")
            return

        # Comando otimizado para reprodução imediata via PipeWire/PulseAudio
        # --length_scale 1.05: Torna a fala ligeiramente mais natural (menos apressada)
        cmd = [
            "sh", "-c",
            f'echo "{text}" | {self.piper_binary} --model "{self.piper_model}" --length_scale 1.05 --output_raw | paplay --raw --rate=22050 --channels=1 --format=s16le'
        ]

        try:
            # Executa a síntese e reprodução
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[Boca] Erro na síntese/reprodução: {e}")
        except Exception as e:
            print(f"[Boca] Erro inesperado no módulo de voz: {e}")

if __name__ == "__main__":
    # Teste rápido do módulo de voz
    mouth = Mouth()
    mouth.speak("A voz do Jarvis foi restaurada com sucesso.")