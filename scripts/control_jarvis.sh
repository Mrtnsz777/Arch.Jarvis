#!/bin/bash

# Arquivo onde o main.py guarda o ID do processo
PID_FILE="/tmp/arch_jarvis.pid"
LOG_FILE="/tmp/arch_jarvis.log"

# Verifica se o arquivo PID existe
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    # Verifica se o processo ainda está vivo (kill -0 não mata, só checa)
    if kill -0 "$PID" 2>/dev/null; then
        # echo "Enviando sinal para PID $PID..."
        # Apenas envia o sinal. O feedback sonoro (Beep) agora é responsabilidade do Python (main.py)
        kill -SIGUSR1 "$PID"
    else
        echo "$(date): PID $PID encontrado, mas processo morreu." >> "$LOG_FILE"
        # Opcional: Reiniciar automaticamente se estiver morto
        # rm "$PID_FILE"
        # /home/martins/SAAS/Arch.Jarvis/arch_jarvis/scripts/start_jarvis.sh &
    fi
else
    echo "$(date): Erro - Arquivo PID não encontrado." >> "$LOG_FILE"
fi