import os
import sys
import numpy as np
import sounddevice as sd
import soundfile as sf
import gc
import warnings
from faster_whisper import WhisperModel

# --- CONFIGURAÇÃO DE ESTABILIDADE TOTAL ---
# Ignoramos completamente a GPU para evitar o pesadelo do ROCm
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Silencia avisos de bibliotecas
warnings.filterwarnings("ignore")

class Ears:
    def __init__(self, model_size="medium"):
        """
        Ouvidos utilizando Faster-Whisper (CTranslate2).
        Otimizado para rodar em CPU com alta precisão e sem dependência de drivers de vídeo.
        """
        print(f"[Ouvidos] Inicializando Faster-Whisper '{model_size}' (CPU Otimizada)...")
        
        try:
            # device="cpu": Força uso do processador
            # compute_type="int8": Reduz o uso de RAM e aumenta a velocidade sem perder precisão
            # cpu_threads: Usa 4 núcleos para não engasgar o sistema
            self.model = WhisperModel(
                model_size, 
                device="cpu", 
                compute_type="int8",
                cpu_threads=4
            )
            print("[Ouvidos] Sistema de audição pronto (Modo Ultra-Estável).")
        except Exception as e:
            print(f"[Ouvidos] Erro crítico ao carregar modelo: {e}")
            sys.exit(1)

    def listen_toggle(self, sample_rate=16000):
        """
        Captura áudio e transcreve usando o motor Faster-Whisper.
        """
        print("\n[🔴 A OUVIR] Pressione ENTER para enviar o comando...")
        
        audio_blocks = []

        def callback(indata, frames, time, status):
            audio_blocks.append(indata.copy())

        # Captura via SoundDevice
        try:
            with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback):
                input() # Aguarda o usuário
        except KeyboardInterrupt:
            return ""

        if not audio_blocks:
            return ""
            
        print("[⏹️ Transcrevendo via CTranslate2 (CPU)...]")
        
        # Concatena os blocos capturados
        audio_data = np.concatenate(audio_blocks).flatten().astype(np.float32)
        
        text = ""
        try:
            # O Faster-Whisper processa diretamente o array numpy, é muito mais rápido
            # beam_size=5: Aumenta a precisão para o Português
            segments, info = self.model.transcribe(
                audio_data, 
                language="pt",
                beam_size=5,
                initial_prompt="O usuário está no Arch Linux. Responda em português brasileiro."
            )
            
            # Une os segmentos transcritos
            text = "".join([segment.text for segment in segments]).strip()
            print(f"[Ouvidos] Resultado: '{text}'")
            
        except Exception as e:
            print(f"[Ouvidos] Erro na transcrição: {e}")
        
        # Limpeza de memória
        del audio_data
        gc.collect()

        return text

if __name__ == "__main__":
    # Teste isolado
    ears = Ears(model_size="medium")
    ears.listen_toggle()