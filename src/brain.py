import os
import warnings
import google.generativeai as genai
from dotenv import load_dotenv

# Suprime o aviso de depreciação para manter o terminal limpo
warnings.filterwarnings("ignore", category=FutureWarning)

# Carrega as variáveis de ambiente
load_dotenv()

def obter_chave(tipo_chave):
    """
    Busca a chave de API correta.
    Prioridade: Chave Específica (PRO/FLASH) -> Chave Genérica (GEMINI_API_KEY)
    """
    chave = os.getenv(tipo_chave)
    if not chave:
        chave = os.getenv("GEMINI_API_KEY")
    return chave

def tentar_gerar_resposta(model_name, api_key, text_prompt):
    """
    Tenta gerar conteúdo com um modelo e chave específicos.
    """
    if not api_key:
        return False, "Chave de API não configurada."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(text_prompt)
        
        try:
            return True, response.text
        except ValueError:
            feedback = "Resposta bloqueada pelo filtro de segurança."
            if hasattr(response, 'prompt_feedback'):
                 feedback += f" Detalhes: {response.prompt_feedback}"
            return True, feedback 

    except Exception as e:
        return False, str(e)

def ask_gemini(text_prompt, mode="auto"):
    """
    Sistema inteligente de roteamento de modelos.
    
    Args:
        text_prompt (str): O texto para enviar.
        mode (str): 'auto', 'pro' ou 'flash'.
    """
    
    # Definição das estratégias disponíveis
    todas_estrategias = [
        {
            "id": "pro",
            "nome": "Cérebro Principal (Pro)",
            "modelo": "gemini-2.5-pro",
            "chave_env": "GEMINI_API_KEY_PRO"
        },
        {
            "id": "flash",
            "nome": "Cérebro Secundário (Flash)",
            "modelo": "gemini-2.5-flash",
            "chave_env": "GEMINI_API_KEY_FLASH"
        }
    ]

    # Filtra as estratégias baseado no modo escolhido
    if mode == "pro":
        estrategias_ativas = [s for s in todas_estrategias if s["id"] == "pro"]
    elif mode == "flash":
        estrategias_ativas = [s for s in todas_estrategias if s["id"] == "flash"]
    else:
        # Modo Auto: Tenta Pro, depois Flash
        estrategias_ativas = todas_estrategias

    erros_acumulados = []

    for tentativa in estrategias_ativas:
        chave = obter_chave(tentativa["chave_env"])
        
        if not chave:
            erros_acumulados.append(f"{tentativa['nome']}: Chave não encontrada.")
            continue

        sucesso, resposta = tentar_gerar_resposta(tentativa["modelo"], chave, text_prompt)
        
        if sucesso:
            # Se estiver no modo auto e usou o backup, avisa (opcional)
            if mode == "auto" and tentativa["id"] != "pro":
                 print(f"[Sistema] Fallback ativado: Respondendo via {tentativa['nome']}.")
            return resposta
        else:
            erros_acumulados.append(f"{tentativa['nome']} falhou: {resposta}")

    return f"Erro Crítico ({mode}): Não foi possível gerar resposta.\nDetalhes:\n" + "\n".join(erros_acumulados)

def configurar_gemini():
    """
    Verifica se existe pelo menos uma chave válida para operar.
    """
    chaves_existentes = [
        os.getenv("GEMINI_API_KEY"),
        os.getenv("GEMINI_API_KEY_PRO"),
        os.getenv("GEMINI_API_KEY_FLASH")
    ]
    
    if any(chaves_existentes):
        return True
    
    print("ERRO: Nenhuma chave de API encontrada (.env).")
    return False

if __name__ == "__main__":
    # Teste simples
    configurar_gemini()
    print(ask_gemini("Teste rápido", mode="flash"))