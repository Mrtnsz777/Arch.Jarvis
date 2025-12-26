import os
import shutil
import subprocess
import logging

# Configuração de Logs
logging.basicConfig(level=logging.ERROR)

class Mouth:
    def __init__(self):
        """
        Sistema de áudio híbrido inteligente (Smart Router).
        - Prioridade 1: Áudios Fixos (ElevenLabs) para comandos de sistema repetitivos.
        - Prioridade 2: Piper TTS para informações dinâmicas (Horário, Respostas complexas).
        """
        # --- CONFIGURAÇÃO PIPER (Dinâmico) ---
        self.piper_binary = (
            shutil.which("piper-tts") or 
            shutil.which("piper") or 
            "/usr/bin/piper-tts"
        )
        
        # Verifica opcionais
        self.sox_binary = shutil.which("sox")
        self.ffmpeg_binary = shutil.which("ffmpeg")
        
        # Verifica se o controlador de volume está presente
        if not shutil.which("pamixer"):
            print("[Boca] ⚠️ Aviso Crítico: 'pamixer' não encontrado. O controle de volume falhará. Instale: sudo pacman -S pamixer")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Caminhos
        self.piper_model = os.path.join(project_root, "models", "pt_BR-cadu-medium.onnx")
        self.sounds_dir = os.path.join(project_root, "assets", "sounds")

        if not self.ffmpeg_binary:
            print("[Boca] ⚠️ Aviso: 'ffmpeg' ausente. Áudios fixos podem não tocar.")

        # --- MAPA DE ÁUDIOS INTELIGENTE ---
        # Mapeia frases de retorno do sistema para os arquivos de áudio premium.
        # Se o texto contiver a chave, toca o arquivo .mp3/.wav correspondente.
        self.smart_audio_map = {
            # --- Novos Áudios Específicos ---
            "Janela fechada": "WindowClosed",
            "Movido": "WindowMoved",
            "Mídia": "MediaControl",
            "Volume": "VolumeControl",
            "Workspace": "WorkspaceSwitch",
            
            # --- Áudios Essenciais (Já Existentes) ---
            "Tela bloqueada": "SysBlock",
            "Desligando": "PowerOff",
            "Reiniciando": "Reboot",
            "Beep": "Beep", # Adicionado mapeamento explicito para Beep
            
            # --- Fallback para 'Exec' (Genéricos) ---
            # Tudo o que não tem áudio específico mas é uma ação curta usa o 'Exec'
            "Feito": "Exec",
            "Entendido": "Exec",
            "iniciado": "Exec",   # Ex: "Brave iniciado", "Code iniciado"
            "Digitado": "Exec"    # Ex: "Digitado"
        }

    def play_fixed(self, sound_name, wait=True):
        """
        Toca um arquivo de áudio pré-gravado via pipeline ffmpeg -> paplay.
        Args:
            sound_name (str): Nome do arquivo (sem extensão).
            wait (bool): Se True, espera o áudio terminar antes de liberar o código.
                         Se False (fire-and-forget), toca em background. Ideal para Bips.
        """
        # Procura por .mp3 (comum no ElevenLabs) e .wav
        for ext in [".mp3", ".wav"]:
            file_path = os.path.join(self.sounds_dir, sound_name + ext)
            if os.path.exists(file_path):
                # print(f"[Boca] 🔊 Áudio Premium: {sound_name}")
                try:
                    if self.ffmpeg_binary:
                        # Pipeline com volume boost (150%)
                        cmd_str = (
                            f'{self.ffmpeg_binary} -v error -i "{file_path}" -filter:a "volume=1.5" '
                            f'-f s16le -ar 44100 -ac 2 - | '
                            f'paplay --raw --rate=44100 --channels=2 --format=s16le --client-name="JarvisFixed"'
                        )
                        if wait:
                            subprocess.run(cmd_str, shell=True, check=True)
                        else:
                            subprocess.Popen(cmd_str, shell=True) # Não bloqueia
                    else:
                        if wait:
                            subprocess.run(["paplay", file_path], check=True)
                        else:
                            subprocess.Popen(["paplay", file_path])
                    return True
                except Exception as e:
                    print(f"[Boca] Erro ao tocar {sound_name}: {e}")
                    return False
        
        return False

    def speak(self, text):
        """
        Decide inteligentemente se usa Áudio Fixo ou Piper TTS.
        """
        if not text or not text.strip(): return

        # 1. Tenta interceptação manual (AUDIO:Nome)
        if text.startswith("AUDIO:"):
            sound_name = text.split(":")[1].strip()
            # Bips e sons curtos não devem bloquear a execução
            is_beep = sound_name.lower() in ["beep", "exec"]
            if self.play_fixed(sound_name, wait=not is_beep): return

        # 2. Tenta interceptação inteligente por conteúdo
        for key, sound_file in self.smart_audio_map.items():
            if key.lower() in text.lower():
                # Sons de sistema podem bloquear, exceto se for feedback muito rápido
                if self.play_fixed(sound_file):
                    return 

        # 3. Fallback: Piper TTS (Para horário, notícias, conversas)
        text_clean = text.replace("*", "").replace("#", "").replace("_", "").strip()
        print(f"[Boca] Piper (Dinâmico): '{text_clean}'")

        if not self.piper_binary or not os.path.exists(self.piper_model):
            # Se não tiver Piper, tenta pelo menos um som de confirmação genérico
            self.play_fixed("Exec", wait=False)
            return

        # Pipeline de Áudio Dinâmico
        if self.sox_binary:
            cmd_str = (
                f'echo "{text_clean}" | '
                f'{self.piper_binary} --model "{self.piper_model}" --length_scale 0.9 --output_raw | '
                f'{self.sox_binary} -t raw -r 22050 -e signed -b 16 -c 1 - -t raw - vol 1.5 | '
                f'paplay --raw --rate=22050 --channels=1 --format=s16le --client-name="JarvisTTS"'
            )
        else:
            cmd_str = (
                f'echo "{text_clean}" | '
                f'{self.piper_binary} --model "{self.piper_model}" --length_scale 0.9 --output_raw | '
                f'paplay --raw --rate=22050 --channels=1 --format=s16le --client-name="JarvisTTS"'
            )

        try:
            subprocess.run(["sh", "-c", cmd_str], check=True)
        except Exception:
            pass

if __name__ == "__main__":
    m = Mouth()
    # Teste: Deve tocar 'SystemLoad.mp3' se existir
    if not m.speak("AUDIO:SystemLoad"):
        m.speak("Sistema de áudio inteligente ativado.")