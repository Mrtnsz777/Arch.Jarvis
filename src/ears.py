import sounddevice as sd
import soundfile as sf
import numpy as np
import whisper
import os
import warnings
import sys

# Suprime avisos do Whisper
warnings.filterwarnings("ignore")

class Ears:
    def __init__(self, model_size="base"):
        """
        Inicializa o modelo Whisper.
        """
        print(f"[Ouvidos] Carregando modelo Whisper '{model_size}'...")
        self.model = whisper.load_model(model_size)
        print("[Ouvidos] Modelo pronto.")

    def listen(self, duration=5, sample_rate=16000):
        """
        Grava áudio por tempo fixo (Método antigo, mantido para compatibilidade).
        """
        print(f"[Ouvidos] Ouvindo por {duration} segundos...")
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()
        return self._process_audio(audio_data, sample_rate)

    def listen_toggle(self, sample_rate=16000):
        """
        Grava áudio indefinidamente até o usuário pressionar ENTER.
        Usa um InputStream não-bloqueante para capturar o áudio enquanto espera o input.
        """
        print("\n[🔴 GRAVANDO] Pressione ENTER novamente para PARAR...")
        
        # Lista para armazenar os blocos de áudio
        audio_blocks = []

        # Função de callback que o sounddevice chama repetidamente com novos dados de áudio
        def callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            # Copia os dados recebidos para nossa lista
            audio_blocks.append(indata.copy())

        # Abre o stream de entrada (microfone)
        with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback):
            # O input() aqui bloqueia o programa principal, esperando o Enter
            # Enquanto isso, o 'callback' continua rodando em background gravando o áudio
            input() 
        
        print("[⏹️ PARADO] Processando áudio...")

        # Concatena todos os blocos em um único array numpy
        if not audio_blocks:
            return ""
            
        audio_data = np.concatenate(audio_blocks)
        return self._process_audio(audio_data, sample_rate)

    def _process_audio(self, audio_data, sample_rate):
        """
        Função auxiliar interna para salvar e transcrever.
        """
        # Salva arquivo temporário
        temp_file = "/tmp/jarvis_input_manual.wav"
        sf.write(temp_file, audio_data, sample_rate)
        
        # Transcrição
        try:
            result = self.model.transcribe(temp_file, fp16=False, language='pt')
            text = result['text'].strip()
            print(f"[Ouvidos] Ouvi: '{text}'")
        except Exception as e:
            print(f"[Ouvidos] Erro na transcrição: {e}")
            text = ""
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        return text

if __name__ == "__main__":
    ears = Ears()
    print("Pressione Enter para começar a gravar.")
    input()
    texto = ears.listen_toggle()
    print(f"Resultado: {texto}")