"""
Configurações globais para o projeto TARS.
Centraliza constantes, configurações de ambiente e parâmetros do sistema.
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações da aplicação
APP_NAME = "TARS"
APP_ICON = "🤖"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Assistente de IA avançado para análise de conteúdo de múltiplas fontes"

# Configurações do modelo LLM
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
MODEL = "claude-3-5-sonnet-20240620"
MAX_TOKENS = 4000
TEMPERATURE = 0.8  # Levemente reduzido para respostas mais consistentes

# User-Agent para requisições web
USER_AGENT = "TARS-Assistant/1.0"
WEB_HEADERS = {"User-Agent": "Mozilla/5.0"}

# Caminhos de diretórios
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
CSS_DIR = os.path.join(ASSETS_DIR, "css")
IMG_DIR = os.path.join(ASSETS_DIR, "img")
DOCUMENTS_DIR = os.path.join(ROOT_DIR, "documentos")

# Configuração de cache
CACHE_TTL = 3600  # Tempo de vida do cache em segundos (1 hora)

# Mensagens do sistema
SYSTEM_MESSAGE_TEMPLATE = """
Você é um assistente amigável chamado TARS que sempre responde de forma simples e objetiva.
Fonte atual: {fonte_tipo}
{fonte_url_formatada}
{fonte_titulo_formatada}

Base suas respostas nas informações recebidas abaixo:

{documento}

Instruções adicionais:
- Se perguntarem sobre qual site/documento você está analisando, informe o título e URL/nome do arquivo.
- Se as informações não forem suficientes para responder, informe que você não tem dados suficientes sobre o assunto.
- Mantenha suas respostas concisas e diretas ao ponto.
- Quando citar informações do documento, indique a fonte.
- Você é um assistente projetado para auxiliar estudantes em seus estudos, então use exemplos e analogias técnicas quando apropriado.
- Se perguntar quem te criou, responda que foi desenvolvido pelo Daniel J Machado com auxílio do Claude AI da Anthropic.
"""

# Verificação de configurações críticas
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY não encontrada no arquivo .env. Por favor, configure esta variável de ambiente.")