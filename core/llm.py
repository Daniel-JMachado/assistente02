"""
Módulo responsável pela interação com o modelo de linguagem Claude da Anthropic.
Fornece interfaces para gerar respostas com base no contexto fornecido.
"""

from anthropic import Anthropic
from config.settings import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS, TEMPERATURE, SYSTEM_MESSAGE_TEMPLATE

# Inicializa o cliente Anthropic
client = Anthropic(api_key=ANTHROPIC_API_KEY)

def format_system_prompt(documento_info):
    """
    Formata o prompt do sistema com base nas informações do documento.
    
    Args:
        documento_info: Dicionário ou string contendo as informações do documento
        
    Returns:
        String formatada com o prompt do sistema
    """
    # Valores padrão
    documento = ""
    fonte_tipo = "Chat"
    fonte_url = ""
    fonte_titulo = ""
    
    # Extrai informações do documento
    if documento_info:
        if isinstance(documento_info, dict):
            documento = documento_info.get('conteudo', '')
            fonte_tipo = documento_info.get('tipo', 'Chat')
            fonte_url = documento_info.get('url', '')
            fonte_titulo = documento_info.get('titulo', '')
        elif isinstance(documento_info, str):
            documento = documento_info
            fonte_tipo = "Texto"
    
    # Formata campos opcionais
    fonte_url_formatada = f"URL: {fonte_url}" if fonte_url else ""
    fonte_titulo_formatada = f"Título: {fonte_titulo}" if fonte_titulo else ""
    
    # Formata o prompt final
    return SYSTEM_MESSAGE_TEMPLATE.format(
        fonte_tipo=fonte_tipo,
        fonte_url_formatada=fonte_url_formatada,
        fonte_titulo_formatada=fonte_titulo_formatada,
        documento=documento
    )

def format_messages(historico):
    """
    Converte o histórico de mensagens para o formato esperado pela API da Anthropic.
    
    Args:
        historico: Lista de tuplas (role, content) ou lista de dicionários {"role": role, "content": content}
        
    Returns:
        Lista formatada para a API da Anthropic
    """
    messages = []
    
    for item in historico:
        if isinstance(item, tuple):
            role, content = item
            if role != "system":  # Ignora mensagens do sistema, pois serão enviadas separadamente
                messages.append({"role": role, "content": content})
        elif isinstance(item, dict):
            if item.get("role") != "system":
                messages.append({"role": item["role"], "content": item["content"]})
    
    return messages

def generate_response(historico, documento_info):
    """
    Gera uma resposta usando o modelo LLM com base no histórico de conversas e no documento.
    
    Args:
        historico: Histórico de mensagens (lista de tuplas ou dicionários)
        documento_info: Informações do documento para contexto
        
    Returns:
        String contendo a resposta gerada pelo modelo
    """
    try:
        # Formata o prompt do sistema
        system_prompt = format_system_prompt(documento_info)
        
        # Prepara as mensagens para a API
        messages = format_messages(historico)
        
        # Chama a API da Anthropic
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system=system_prompt,
            messages=messages
        )
        
        # Retorna o texto da resposta
        return response.content[0].text
    
    except Exception as e:
        error_msg = str(e)
        print(f"Erro ao gerar resposta: {error_msg}")
        return f"Desculpe, ocorreu um erro ao processar sua pergunta. Detalhes: {error_msg}"