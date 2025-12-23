import subprocess
import os
import shutil

class Mouth:
    def __init__(self, voice_name="pt_BR-cadu-medium.onnx"):
        """
        Inicializa o sistema de fala (Piper TTS).
        Usa caminhos absolutos e verifica dependências do sistema.
        """
        # 1. Descobre o nome do binário do Piper
        self.piper_binary = None
        if shutil.which("piper"):
            self.piper_binary = "piper"
        elif shutil.which("piper-tts"):
            self.piper_binary = "piper-tts"
        
        if not self.piper_binary:
            print("\n[Boca] ⚠️ AVISO: 'piper' não encontrado. Instale com 'yay -S piper-tts-bin'")
            self.piper_binary = "piper"
        
        # 2. Verifica reprodutor de áudio (Prefere paplay, fallback para aplay)
        self.player_binary = None
        if shutil.which("paplay"):
            self.player_binary = "paplay"
        elif shutil.which("aplay"):
            self.player_binary = "aplay"
        
        if not self.player_binary:
            print("\n[Boca] ❌ ERRO CRÍTICO: Nenhum player (paplay ou aplay) encontrado.")
            print("Solução: Instale 'pulseaudio-utils' ou 'alsa-utils'.")

        # 3. Descobre caminhos
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        self.model_path = os.path.join(project_root, "models", voice_name)
        self.config_path = self.model_path + ".json"
        
        # Verifica arquivos
        if not os.path.exists(self.model_path) or not os.path.exists(self.config_path):
            print(f"\n[Boca] ❌ ERRO: Arquivos da voz não encontrados em {self.model_path}")

    def speak(self, text):
        """
        Fala o texto usando Piper TTS.
        """
        if not text or not text.strip():
            return

        print(f"[Boca] Falando: '{text}'")
        
        # Constrói o comando baseado no player disponível
        if self.player_binary == "paplay":
            # paplay aceita raw data com --raw
            # rate=22050 é o padrão para vozes medium quality
            command = (
                f'echo "{text}" | '
                f'{self.piper_binary} --model "{self.model_path}" --output_raw | '
                f'paplay --raw --rate=22050 --channels=1 --format=s16le'
            )
        else:
            # Fallback para aplay
            command = (
                f'echo "{text}" | '
                f'{self.piper_binary} --model "{self.model_path}" --output_raw | '
                f'aplay -r 22050 -f S16_LE -t raw -'
            )
        
        try:
            # shell=True permite o pipe |
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[Boca] Erro ao falar: {e}")

if __name__ == "__main__":
    mouth = Mouth()
    mouth.speak("Testando novo driver de áudio. Som via PulseAudio.")