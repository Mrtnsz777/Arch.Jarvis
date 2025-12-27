# 🤖 Arch Jarvis - JARVIS do Iron Man para Arch Linux

Um assistente de IA modular e inteligente, inspirado no **JARVIS do Tony Stark** (Homem de Ferro), totalmente integrado ao **Arch Linux** com **Hyprland** e **Waybar**. Inteligência pura alimentada pelo **Google Gemini** com sistema de áudio premium e fallback inteligente.

---

## 🎯 O que é Arch Jarvis?

Assim como **JARVIS** gerencia a mansão de Tony Stark com elegância, precisão e inteligência, **Arch Jarvis** é seu assistente pessoal para Arch Linux. Ele responde comandos de voz, executa ações do sistema, integra-se ao seu ambiente Hyprland/Waybar e oferece uma experiência totalmente conversacional e automatizada.

> *"Sir, might I suggest a more efficient approach?"* - Mas em Arch Linux.

---

## 📋 Pré-requisitos

- **Arch Linux** com kernel atualizado
- **Hyprland** (compositor Wayland)
- **Waybar** (barra de status)
- **Python 3.10+**
- **Git**
- Chave de API do **Google Gemini** (AI Studio ou Vertex AI)
- Microfone e alto-falante funcionais

---

## 🏛️ Arquitetura Modular

O projeto segue uma estrutura **Monorepo Modular** com todos os módulos independentes operando harmoniosamente:

```
arch_jarvis/
├── src/
│   ├── brain.py              # [✓ Concluído] Processamento de IA (Gemini)
│   ├── ears.py               # [✓ Concluído] Reconhecimento de Voz (STT)
│   ├── mouth.py              # [✓ Concluído] Síntese de Voz (TTS)
│   ├── actions/
│   │   ├── system.py         # [✓ Concluído] Comandos do Sistema
│   │   ├── hyprland.py       # [✓ Concluído] Controle Hyprland
│   │   └── waybar.py         # [✓ Concluído] Integração Waybar
│   └── core.py               # [✓ Concluído] Orquestrador Principal
├── config/
│   ├── hyprland/
│   │   └── hyprland.conf     # Configuração Hyprland com Jarvis
│   └── waybar/
│       ├── config            # Configuração Waybar
│       └── style.css         # Estilo Waybar
├── audio/
│   ├── premium/              # Áudios pré-gravados (qualidade premium)
│   └── cache/                # Cache de áudios gerados
├── .env                      # Variáveis de ambiente (NÃO VERSIONADO)
├── requirements.txt          # Dependências Python
└── setup.sh                  # Script de instalação automatizado
```

---

## 🛠️ Tecnologias e Aplicativos Utilizados

### **Core de IA**
- **Google Gemini API** (Pro & Flash) - Inteligência artificial dual-core
- **Python 3** - Linguagem principal

### **Reconhecimento de Voz (STT)**
- **Whisper (OpenAI)** - Transcrição de áudio

### **Síntese de Voz (TTS)**
- **Piper** - Engine TTS leve (fallback quando não há áudio premium)
- **Áudios Premium** - Pré-gravados em alta qualidade

### **Integração do Sistema**
- **Hyprland** - Compositor Wayland
- **Waybar** - Barra de status minimalista
- **D-Bus** - Comunicação inter-processo
- **PulseAudio/Pipewire** - Servidor de áudio

### **Dependências Python**
```
google-generativeai      # API Gemini
python-dotenv            # Gerenciamento de .env
piper-tts                # Síntese de voz
openai-whisper           # Reconhecimento de voz
pyaudio                  # Captura de áudio
requests                 # HTTP requests
subprocess              # Execução de comandos
```

---

## 🚀 Instalação Completa

### **1. Clone o Repositório**

```bash
git clone https://github.com/Mrtnsz777/Arch.Jarvis.git
cd Arch.Jarvis
```

### **2. Configurar Permissões Executáveis**

```bash
# Permissões para scripts principais
chmod +x setup.sh
chmod +x src/brain.py
chmod +x src/ears.py
chmod +x src/mouth.py
chmod +x src/core.py

# Permissões para scripts de controle
chmod +x control_jarvis.sh
chmod +x start_jarvis.sh

# Permissões para módulos de ações
chmod +x src/actions/*.py

# Permissões para Hyprland config
chmod +x config/hyprland/hyprland.conf

# Permissões gerais da pasta
chmod -R 755 .
chmod 600 .env  # Arquivo de secrets com permissão restrita
```

### **3. Criar Ambiente Virtual**

```bash
python -m venv venv
source venv/bin/activate
```

### **4. Instalar Dependências**

```bash
pip install -r requirements.txt

# Dependências do sistema (Arch Linux)
sudo pacman -S python-pyaudio pipewire pipewire-pulse hyprland waybar
```

### **5. Configurar Segurança**

Crie um arquivo `.env` na raiz do projeto:

```bash
# .env (NÃO COMITAR)
GEMINI_API_KEY_PRO=sua_chave_paga_aqui
GEMINI_API_KEY_FLASH=sua_chave_backup_aqui
AUDIO_PREMIUM_PATH=./audio/premium
PIPER_VOICE=pt_BR  # Idioma padrão
```

```bash
# Proteger arquivo .env
chmod 600 .env
```

---

## 🎙️ Sistema de Áudio Inteligente

### **Como Funciona:**

1. **Áudio Premium** (Prioridade 1)
   - Arquivos `.wav` pré-gravados em `audio/premium/`
   - Qualidade superior
   - Resposta instantânea (sem latência de síntese)

2. **Piper TTS** (Fallback)
   - Ativado quando não há áudio premium correspondente
   - Síntese em tempo real
   - Suporte a múltiplos idiomas

### **Estrutura de Áudio:**

```
audio/
├── premium/
│   ├── greeting.wav          # "Olá, sou Jarvis"
│   ├── error.wav             # Som de erro
│   └── command_executed.wav  # Confirmação de comando
└── cache/
    └── generated_*.wav       # Áudios gerados por Piper
```

---

## 🧠 Como Usar

### **1. Teste a Inteligência**

```bash
python src/brain.py
# Conversa direta com Gemini (Pro → Flash fallback)
```

### **2. Teste Entrada de Voz**

```bash
python src/ears.py
# Transcreve áudio do microfone
```

### **3. Teste Saída de Voz**

```bash
python src/mouth.py "Olá, sou Jarvis"
# Reproduz com áudio premium ou Piper
```

### **4. Execute o Sistema Completo**

```bash
python src/core.py
# Ativa assistente em tempo real (escuta + responde + executa)
```

---

## 🎮 Integração Hyprland (Auto-Execução)

Adicione estas linhas ao seu `~/.config/hypr/hyprland.conf`:

```bash
Iniciar Arch Jarvis na inicialização
exec-once = /home/SEU_USER/Arch.Jarvis/arch_jarvis/scripts/start_jarvis.sh

Hotkey para ativar Jarvis ($mainMod + J)
bind = $mainMod, J, exec, /home/SEU_USER/Arch.Jarvis/arch_jarvis/scripts/control_jarvis.sh

Hotkey para parar Jarvis ($mainMod + J)
bind = $mainMod, J, exec, /home/SEU_USER/Arch.Jarvis/arch_jarvis/scripts/control_jarvis.sh

($mainMod + J) = WIN + J // SUPER + J
```

---

## 📊 Status do Projeto

### **v1.0 - JARVIS OPERACIONAL** ✅

- [x] Configuração de Ambiente (venv + Arch Linux)
- [x] Segurança de Chaves (.env)
- [x] Integração Google Gemini (Dual-Core)
- [x] Reconhecimento de Voz (Whisper)
- [x] Síntese de Voz Premium + Piper
- [x] Integração Hyprland + Waybar
- [x] Execução de Comandos do Sistema
- [x] Auto-execução no boot

### **Próximas Melhorias**

- [ ] Interface gráfica customizada
- [ ] Machine Learning local para otimizações
- [ ] Suporte a extensões/plugins
- [ ] Dashboard Waybar interativo

---

## 🔒 Segurança

```bash
# Verificar permissões
ls -la | grep -E "(\.env|src/)"

# Nunca commitar secrets
git update-index --skip-worktree .env

# Verificar arquivos rastreados
git status
```

---

## 🐛 Troubleshooting

### **Áudio não funciona**
```bash
# Verificar PulseAudio/Pipewire
pactl list short sinks
systemctl --user status pipewire
```

### **Permissões negadas**
```bash
# Re-aplicar permissões
chmod -R 755 ~/SAAS/Arch.Jarvis
chmod 600 ~/SAAS/Arch.Jarvis/.env
```

### **Gemini API não conecta**
```bash
# Testar conexão
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_KEY
```

---

## 📞 Suporte

- **Documentação:** Veja `/docs`
- **Issues:** GitHub Issues
- **Discussões:** GitHub Discussions

---

## 📜 Licença

MIT License - Sinta-se livre para usar, modificar e distribuir.

---

**Feito com ❤️ para Arch Linux. Sir, your system is ready.** 🎩
