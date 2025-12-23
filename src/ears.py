import sounddevice as sd
import soundfile as sf
import numpy as np
import whisper
import os
import warnings

# Suprime avisos do Whisper (FP16 warning em CPUs)
warnings.filterwarnings("ignore")

class Ears:
    def __init__(self, model_size="base"):
        """
        Inicializa o modelo Whisper.
        model_size: 'tiny', 'base', 'small', 'medium', 'large'.
        'base' é um bom equilíbrio para CPU. 'small' é melhor se tiver GPU.
        """
        print(f"[Ouvidos] Carregando modelo Whisper '{model_size}'... (pode demorar na 1ª vez)")
        # O Whisper baixa o modelo automaticamente para ~/.cache/whisper
        self.model = whisper.load_model(model_size)
        print("[Ouvidos] Modelo carregado e pronto.")

    def listen(self, duration=5, sample_rate=16000):
        """
        Grava áudio do microfone e transcreve para texto.
        
        Args:
            duration (int): Tempo de gravação em segundos.
            sample_rate (int): Taxa de amostragem (16000 é ideal para Whisper).
            
        Returns:
            str: O texto transcrito.
        """
        print(f"[Ouvidos] Ouvindo por {duration} segundos...")
        
        # Gravação usando sounddevice
        # channels=1 (Mono) é suficiente para voz
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()  # Aguarda o fim da gravação
        
        print("[Ouvidos] Processando áudio...")
        
        # Salva um arquivo temporário (Whisper funciona melhor lendo arquivos)
        temp_file = "/tmp/jarvis_input.wav"
        
        # O Whisper espera áudio flat (array 1D) ou arquivo. 
        # Vamos salvar em arquivo para garantir compatibilidade máxima.
        sf.write(temp_file, audio_data, sample_rate)
        
        # Transcrição
        # fp16=False evita avisos se estiver rodando apenas na CPU
        result = self.model.transcribe(temp_file, fp16=False, language='pt')
        
        text = result['text'].strip()
        print(f"[Ouvidos] Ouvi: '{text}'")
        
        # Limpeza (opcional)
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        return text

if __name__ == "__main__":
    # Teste unitário
    ears = Ears()
    texto = ears.listen(duration=5)
    print(f"Resultado final: {texto}")