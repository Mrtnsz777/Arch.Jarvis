import os
import warnings

# CRÍTICO: Suprime o aviso de depreciação ANTES de importar a biblioteca
# Isso garante que o terminal fique limpo
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
from dotenv import load_dotenv

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
        # Reconfigura a biblioteca para usar a chave deste modelo específico
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

def ask_gemini(text_prompt):
    """
    Roteamento Inteligente: Tenta PRO, falha para FLASH.
    """
    estrategias = [
        {
            "nome": "Cérebro Principal (Pro)",
            "modelo": "gemini-2.5-pro",
            "chave_env": "GEMINI_API_KEY_PRO"
        },
        {
            "nome": "Cérebro Secundário (Flash)",
            "modelo": "gemini-2.5-flash",
            "chave_env": "GEMINI_API_KEY_FLASH"
        }
    ]

    erros_acumulados = []

    for tentativa in estrategias:
        chave = obter_chave(tentativa["chave_env"])
        
        # Se não houver chave disponível para esta estratégia, passa à próxima
        if not chave:
            continue

        sucesso, resposta = tentar_gerar_resposta(tentativa["modelo"], chave, text_prompt)
        
        if sucesso:
            # Se precisou usar o backup, avisa no log (opcional)
            if tentativa["modelo"] != estrategias[0]["modelo"]:
                 print(f"[Sistema] Fallback ativado: Respondendo via {tentativa['nome']}.")
            return resposta
        else:
            erros_acumulados.append(f"{tentativa['nome']} falhou: {resposta}")

    return f"Erro Crítico: Falha nos modelos Pro e Flash.\nDetalhes:\n" + "\n".join(erros_acumulados)

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
    print("Defina GEMINI_API_KEY, GEMINI_API_KEY_PRO ou GEMINI_API_KEY_FLASH.")
    return False

# Bloco de teste principal
if __name__ == "__main__":
    print("--- Arch Jarvis (Dual Core: Pro + Flash) ---")
    
    if configurar_gemini():
        print("Sistemas online. Digite 'sair' para encerrar.")
        
        while True:
            try:
                user_input = input("\nVocê: ")
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    break
                
                if not user_input.strip():
                    continue

                print("Jarvis pensando...")
                resposta = ask_gemini(user_input)
                print(f"Jarvis: {resposta}")
            except KeyboardInterrupt:
                print("\nEncerrando...")
                break
    else:
        print("Falha na inicialização.")