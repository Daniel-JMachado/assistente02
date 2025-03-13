import os
import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic # type: ignore
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders import PyPDFLoader
import warnings

# Suprimir warnings
warnings.filterwarnings("ignore")

# Carrega as variáveis de ambiente do arquivo .env
# Importante para manter chaves de API seguras fora do código
load_dotenv()

# Inicializa o cliente Anthropic diretamente (sem usar LangChain)
anthropic_api_key = st.secrets["ANTHROPIC_API_KEY"]
if not anthropic_api_key:
    raise ValueError("ANTHROPIC_API_KEY não encontrada no arquivo .env")

# Define um USER_AGENT para identificar requisições
os.environ["USER_AGENT"] = "TARS-Assistant/1.0"

client = Anthropic(api_key=anthropic_api_key)
MODEL = "claude-3-5-sonnet-20240620"

def bot(historico, documento_info):
    """
    Processa a entrada do usuário e gera uma resposta usando o modelo LLM.
    
    Args:
        historico: Lista de tuplas (role, content) com o histórico de mensagens
        documento_info: Informações do documento atual para contexto
        
    Returns:
        Resposta gerada pelo modelo LLM
    """
    # Extrai informações do documento para usar como contexto
    # Tratamento robusto para diferentes formatos de entrada
    documento = ""
    fonte_tipo = "Chat"
    fonte_url = ""
    fonte_titulo = ""
    
    if documento_info:
        if isinstance(documento_info, dict):
            documento = documento_info.get('conteudo', '')
            fonte_tipo = documento_info.get('tipo', 'Chat')
            fonte_url = documento_info.get('url', '')
            fonte_titulo = documento_info.get('titulo', '')
        elif isinstance(documento_info, str):
            documento = documento_info
            fonte_tipo = "Texto"
    
    # Constrói o prompt do sistema de forma mais estruturada
    sistema_info = [
        "Você é um assistente amigável chamado TARS que sempre responde de forma simples e objetiva.",
        f"Fonte atual: {fonte_tipo}"
    ]
    
    # Adiciona informações opcionais apenas se existirem
    if fonte_url:
        sistema_info.append(f"URL: {fonte_url}")
    if fonte_titulo:
        sistema_info.append(f"Título: {fonte_titulo}")
    
    # Adiciona instruções específicas
    sistema_info.extend([
        "",
        "Base suas respostas nas informações recebidas abaixo:",
        "",
        documento,
        "",
        "Instruções adicionais:",
        "- Se perguntarem sobre qual site/documento você está analisando, informe o título e URL/nome do arquivo.",
        "- Se as informações não forem suficientes para responder, informe que você não tem dados suficientes sobre o assunto.",
        "- Mantenha suas respostas concisas e diretas ao ponto.",
        "- Quando citar informações do documento, indique a fonte."
    ])
    
    # Monta a mensagem do sistema combinando todos os elementos
    system_prompt = "\n".join(sistema_info)
    
    # Prepara as mensagens para a API da Anthropic
    messages = []
    
    # Adiciona o histórico de conversa se existir
    if historico:
        for role, content in historico:
            # Pula a mensagem do sistema, pois será enviada separadamente
            if role != "system":
                messages.append({"role": role, "content": content})
    
    # Invoca o modelo diretamente com a API da Anthropic
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,  # Reduzido para ficar abaixo do limite de 4096 tokens
            temperature=0.8,
            system=system_prompt,
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        error_msg = str(e)
        print(f"Erro ao gerar resposta: {error_msg}")
        return f"Desculpe, ocorreu um erro ao processar sua pergunta. Detalhes: {error_msg}"

def carrega_site(url_site=None):
    """
    Carrega o conteúdo de um site web usando WebBaseLoader.
    
    Args:
        url_site: URL do site a ser carregado
        
    Returns:
        Dicionário com informações e conteúdo do site
    """
    # Se nenhuma URL fornecida, tenta obter de variáveis de ambiente
    if url_site is None or not url_site.strip():
        url_site = os.getenv('SITE_URL')
        if not url_site:
            return {
                'tipo': 'Site Web (erro)',
                'url': '',
                'titulo': 'URL não fornecida',
                'conteudo': 'É necessário fornecer uma URL válida para carregar o site.'
            }
    
    # Adiciona protocolo http:// se não estiver presente
    if not url_site.startswith(('http://', 'https://')):
        url_site = 'https://' + url_site
    
    try:
        # Verifica se a biblioteca BeautifulSoup está instalada
        try:
            import bs4
        except ImportError:
            return {
                'tipo': 'Erro de Dependência',
                'url': url_site,
                'titulo': 'Biblioteca não instalada',
                'conteudo': 'A biblioteca Beautiful Soup (bs4) não está instalada. Execute o comando: pip install beautifulsoup4'
            }
        
        # Configuração e carregamento do conteúdo do site
        loader = WebBaseLoader(
            url_site,
            verify_ssl=False,  # Ignora erros de SSL para maior compatibilidade
            header_template={"User-Agent": "Mozilla/5.0"}  # User agent para evitar bloqueios
        )
        
        # Carrega documentos e concatena o conteúdo de forma eficiente
        lista_documentos = loader.load()
        documento = '\n'.join([doc.page_content for doc in lista_documentos])
        
        # Extrai o título do site com tratamento melhorado de erros
        titulo = "Site Web"
        try:
            # Usa BeautifulSoup para extrair o título de forma mais robusta
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url_site, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            title_tag = soup.find('title')
            
            if title_tag and title_tag.string:
                titulo = title_tag.string.strip()
        except Exception as e:
            print(f"Aviso: Não foi possível extrair o título do site: {str(e)}")
        
        # Retorna as informações e conteúdo do site em um dicionário estruturado
        return {
            'tipo': 'Site Web',
            'url': url_site,
            'titulo': titulo,
            'conteudo': documento
        }
    except Exception as e:
        # Captura, registra e retorna erros detalhados
        error_msg = str(e)
        print(f"Erro ao carregar o site {url_site}: {error_msg}")
        return {
            'tipo': 'Site Web (erro)',
            'url': url_site,
            'titulo': 'Erro ao carregar',
            'conteudo': f'Não foi possível carregar o conteúdo do site: {error_msg}'
        }

def carrega_pdf(pdf_paths=None):
    """
    Carrega e processa arquivos PDF fornecidos pelo usuário.
    
    Args:
        pdf_paths: Lista de caminhos para os arquivos PDF a serem processados.
                  Se não fornecido, procura PDFs na pasta documentos.
        
    Returns:
        Dicionário com informações e conteúdo dos PDFs processados
    """
    documento = ''
    arquivos_processados = []
    
    # Verifica se foram fornecidos caminhos de PDFs
    if pdf_paths is None:
        # Método antigo: procura PDFs na pasta documentos
        pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documentos')
        
        # Verifica se a pasta existe
        if not os.path.exists(pasta):
            return {
                'tipo': 'PDF (erro)',
                'url': pasta,
                'titulo': 'Pasta não encontrada',
                'conteudo': f'Pasta não encontrada: {pasta}'
            }
        
        # Lista apenas arquivos PDF na pasta usando filtro de extensão
        arquivos_pdf = [os.path.join(pasta, f) for f in os.listdir(pasta) if f.lower().endswith('.pdf')]
    else:
        # Usa os caminhos de arquivo fornecidos
        arquivos_pdf = pdf_paths
    
    # Verifica se existem PDFs para processar
    if not arquivos_pdf:
        return {
            'tipo': 'PDF (erro)',
            'url': '',
            'titulo': 'Nenhum PDF encontrado',
            'conteudo': 'Nenhum arquivo PDF foi fornecido para processamento.'
        }
    
    # Processa cada arquivo PDF
    for caminho_completo in arquivos_pdf:
        try:
            # Extrai apenas o nome do arquivo sem o caminho
            nome_arquivo = os.path.basename(caminho_completo)
            
            # Carrega e extrai texto do PDF usando PyPDFLoader
            loader = PyPDFLoader(caminho_completo)
            # Carrega todos os documentos de uma vez
            lista_documentos = loader.load()
            # Concatena o conteúdo de todas as páginas
            documento += f"\n\n--- INÍCIO DO DOCUMENTO: {nome_arquivo} ---\n\n"
            documento += '\n'.join([doc.page_content for doc in lista_documentos])
            documento += f"\n\n--- FIM DO DOCUMENTO: {nome_arquivo} ---\n\n"
            # Adiciona à lista de arquivos processados
            arquivos_processados.append(nome_arquivo)
            print(f"Arquivo processado com sucesso: {nome_arquivo}")
        except Exception as e:
            print(f"Erro ao processar arquivo {caminho_completo}: {str(e)}")
    
    # Retorna as informações e conteúdo dos PDFs em um dicionário estruturado
    return {
        'tipo': 'Documentos PDF',
        'url': '',
        'titulo': f"Arquivos: {', '.join(arquivos_processados)}",
        'conteudo': documento
    }

def carrega_youtube(url_youtube=None):
    """
    Carrega a transcrição de um vídeo do YouTube.
    
    Args:
        url_youtube: URL do vídeo do YouTube
        
    Returns:
        Dicionário com informações e transcrição do vídeo
    """
    # Validação e obtenção da URL do vídeo
    if url_youtube is None or not url_youtube.strip():
        url_youtube = os.getenv('YOUTUBE_URL')
        if not url_youtube:
            return {
                'tipo': 'Vídeo do YouTube (erro)',
                'url': '',
                'titulo': 'URL não fornecida',
                'conteudo': 'É necessário fornecer uma URL válida para carregar o vídeo do YouTube.'
            }
    
    # Formatação da URL para garantir que funcione com o loader
    # Remove parâmetros desnecessários da URL que podem causar problemas
    if 'youtube.com' in url_youtube and '&' in url_youtube:
        url_youtube = url_youtube.split('&')[0]  # Mantém apenas a parte principal da URL
    
    try:
        # Instalação dinâmica da dependência necessária se não estiver presente
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError:
            import sys
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube_transcript_api"])
            from youtube_transcript_api import YouTubeTranscriptApi
        
        # Extrai o ID do vídeo da URL
        video_id = url_youtube.split('v=')[-1].split('&')[0] if 'v=' in url_youtube else url_youtube.split('/')[-1]
        
        # Configuração do carregador com suporte para múltiplos idiomas
        try:
            # Tenta com o loader do LangChain primeiro
            loader = YoutubeLoader.from_youtube_url(
                url_youtube,
                language=['pt', 'en'],  # Tenta carregar em português ou inglês
                add_video_info=True     # Adiciona informações do vídeo nos metadados
            )
            
            # Carrega a transcrição do vídeo
            lista_documentos = loader.load()
            
            # Se não encontrou documentos, tenta método alternativo
            if not lista_documentos:
                raise Exception("Nenhuma transcrição encontrada com o loader padrão.")
                
            # Extrai informações do vídeo dos metadados
            titulo = "Vídeo do YouTube"
            try:
                # Tenta obter o título do primeiro documento
                titulo = lista_documentos[0].metadata.get('title', titulo)
                # Se não conseguir, tenta obter dos metadados do vídeo
                if not titulo or titulo == "Vídeo do YouTube":
                    titulo = lista_documentos[0].metadata.get('video_title', titulo)
            except Exception:
                pass
                
            # Concatena todo o conteúdo transcrito de forma eficiente
            documento = '\n'.join([doc.page_content for doc in lista_documentos])
            
        except Exception as e:
            # Método alternativo usando a API diretamente
            print(f"Tentando método alternativo para transcrição: {str(e)}")
            
            try:
                # Obtém transcrições disponíveis
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # Tenta obter transcrição em português primeiro, depois em inglês, ou qualquer disponível
                try:
                    transcript = transcript_list.find_transcript(['pt', 'pt-BR'])
                except:
                    try:
                        transcript = transcript_list.find_transcript(['en'])
                    except:
                        # Pega a primeira transcrição disponível
                        transcript = transcript_list.find_generated_transcript()
                
                # Obtém a transcrição como texto
                transcript_data = transcript.fetch()
                documento = '\n'.join([item['text'] for item in transcript_data])
                
                # Tenta obter o título do vídeo com requests e beautifulsoup
                titulo = "Vídeo do YouTube"
                try:
                    import requests
                    from bs4 import BeautifulSoup
                    response = requests.get(f"https://www.youtube.com/watch?v={video_id}", 
                                           headers={"User-Agent": "Mozilla/5.0"})
                    soup = BeautifulSoup(response.text, 'html.parser')
                    titulo_tag = soup.find('title')
                    if titulo_tag:
                        titulo = titulo_tag.text.replace(' - YouTube', '')
                except Exception:
                    pass
            except Exception as e2:
                raise Exception(f"Falha ao obter transcrição: {str(e2)}")
        
        # Retorna as informações e conteúdo da transcrição em um dicionário estruturado
        return {
            'tipo': 'Vídeo do YouTube',
            'url': url_youtube,
            'titulo': titulo,
            'conteudo': documento
        }
    except Exception as e:
        # Captura, registra e retorna erros detalhados
        error_msg = str(e)
        print(f"Erro ao carregar o vídeo do YouTube {url_youtube}: {error_msg}")
        return {
            'tipo': 'Vídeo do YouTube (erro)',
            'url': url_youtube,
            'titulo': 'Erro ao carregar',
            'conteudo': f'Não foi possível carregar a transcrição do vídeo: {error_msg}'
        }