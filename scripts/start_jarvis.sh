#!/bin/bash

# --- CONFIGURAÇÃO (CAMINHOS ABSOLUTOS) ---
# Diretório raiz do projeto
PROJECT_DIR="/home/martins/SAAS/Arch.Jarvis/arch_jarvis"
# Caminho para o Python dentro do ambiente virtual
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
# Arquivos de log e PID
LOG_FILE="/tmp/arch_jarvis.log"
PID_FILE="/tmp/arch_jarvis.pid"

# --- AGUARDAR SISTEMA (Delay de Segurança) ---
# Espera 5 segundos para garantir que PipeWire e Internet estão ativos
sleep 5

# --- LIMPEZA ---
# Mata processos antigos que usem o mesmo arquivo python
pkill -f "$VENV_PYTHON src/main.py"

# --- VERIFICAÇÃO ---
if [ ! -f "$VENV_PYTHON" ]; then
    echo "$(date): Erro Crítico - Python do venv não encontrado em $VENV_PYTHON" >> "$LOG_FILE"
    exit 1
fi

# Entra no diretório para que os imports relativos (src.ears, etc) funcionem
cd "$PROJECT_DIR" || { echo "$(date): Erro ao entrar na pasta $PROJECT_DIR" >> "$LOG_FILE"; exit 1; }

echo "$(date): Iniciando Jarvis v0.5..." >> "$LOG_FILE"

# --- EXECUÇÃO ---
# Executa diretamente o binário do python do venv, sem precisar de 'source activate'
nohup "$VENV_PYTHON" src/main.py >> "$LOG_FILE" 2>&1 &

# Salva PID
JARVIS_PID=$!
echo $JARVIS_PID > "$PID_FILE"

echo "$(date): Jarvis PID $JARVIS_PID salvo." >> "$LOG_FILE"