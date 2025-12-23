Arch Jarvis 🧠

Assistente modular inteligente para Arch Linux, integrado com Hyprland e alimentado pelo Google Gemini (Dual Core: Pro & Flash).

📋 Pré-requisitos

Python 3.x

Uma chave de API do Google Gemini (AI Studio ou Vertex AI)

Git

🏛 Arquitetura Modular

O projeto segue uma estrutura de Monorepo Modular. Todos os módulos vivem neste repositório, mas operam de forma independente dentro de src/.

Estrutura Planejada:

arch_jarvis/
├── src/
│   ├── brain.py       # [Concluído] Módulo de Inteligência (LLM)
│   ├── ears.py        # [Planejado] Reconhecimento de Voz (STT)
│   ├── mouth.py       # [Planejado] Síntese de Voz (TTS)
│   └── actions/       # [Planejado] Comandos do Sistema (Arch/Hyprland)
├── .env               # Segredos (Não versionado)
└── requirements.txt   # Dependências Globais


Esta organização permite desenvolver novos módulos sem quebrar a funcionalidade dos existentes.

🚀 Instalação

Clone ou crie a pasta do projeto:

git clone [https://github.com/Mrtnsz777/Arch.Jarvis.git](https://github.com/Mrtnsz777/Arch.Jarvis.git)
cd Arch.Jarvis


Crie e ative o ambiente virtual:

python -m venv venv
source venv/bin/activate


Instale as dependências:

pip install -r requirements.txt


Configuração de Segurança:
Crie um arquivo .env na raiz do projeto com suas chaves:

# .env
GEMINI_API_KEY_PRO=sua_chave_paga_ou_com_creditos
GEMINI_API_KEY_FLASH=sua_chave_backup
# GEMINI_API_KEY=chave_padrao_fallback


🧠 Como Usar (Módulo Cérebro)

Para testar a conexão e conversar diretamente com o módulo de inteligência:

python src/brain.py


O sistema tentará usar o modelo Pro primeiro. Se falhar (cota ou erro), fará fallback automático para o modelo Flash.

📂 Estrutura Atual

src/brain.py: Núcleo de processamento LLM.

.env: Variáveis de ambiente (NÃO COMITAR).

requirements.txt: Dependências do Python.

🛠 Status e Versões

v0.1 - The Brain (Atual)

[x] Configuração de Ambiente (venv)

[x] Segurança de Chaves (.env)

[x] Integração com API Gemini

[x] Lógica Dual-Core (Pro + Flash)

Próximos Passos

[ ] Módulo de Execução de Comandos (Bash/Hyprland)

[ ] Interface de Voz (STT/TTS)