"""
Módulo para carregamento e processamento de transcrições de vídeos do YouTube.
Utiliza a API youtube_transcript_api para extrair transcrições.
"""

import os
import requests
import urllib3
import random
import time
from bs4 import BeautifulSoup
from langchain_community.document_loaders import YoutubeLoader
from config.settings import WEB_HEADERS

# Desativa avisos de SSL para evitar warnings no console
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Lista de proxies gratuitos (atualize esta lista conforme necessário)
FREE_PROXIES = [
    # Formato: "http://ip:porta"
    # Adicione alguns proxies da lista https://free-proxy-list.net/
    # Exemplo:
    "http://8.219.74.58:8080",
    "http://34.23.45.223:80",
    "http://51.254.121.123:8088",
    "http://51.83.241.108:80",
    "http://165.154.243.209:80",
    # Adicione mais proxies para aumentar as chances de sucesso
]

def carrega_youtube(url_youtube=None):
    """
    Carrega a transcrição de um vídeo do YouTube.
    
    Args:
        url_youtube: URL do vídeo do YouTube
        
    Returns:
        Dicionário com informações e transcrição do vídeo
    """
    # Validação da URL
    if url_youtube is None or not url_youtube.strip():
        url_youtube = os.getenv('YOUTUBE_URL')
        if not url_youtube:
            return {
                'tipo': 'Vídeo do YouTube (erro)',
                'url': '',
                'titulo': 'URL não fornecida',
                'conteudo': 'É necessário fornecer uma URL válida para carregar o vídeo do YouTube.'
            }
    
    # Formatação da URL para garantir compatibilidade
    if 'youtube.com' in url_youtube and '&' in url_youtube:
        url_youtube = url_youtube.split('&')[0]  # Mantém apenas a parte principal da URL
    
    try:
        # Verifica se a API do YouTube está instalada
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            # Importa exceções específicas para tratamento mais preciso
            from youtube_transcript_api.errors import (
                TranscriptsDisabled,
                NoTranscriptFound,
                VideoUnavailable,
                TooManyRequests,
                NoTranscriptAvailable
            )
        except ImportError:
            return {
                'tipo': 'Erro de Dependência',
                'url': url_youtube,
                'titulo': 'Biblioteca não instalada',
                'conteudo': 'A biblioteca youtube-transcript-api não está instalada. Execute o comando: pip install youtube-transcript-api'
            }
            
        # Extrai o ID do vídeo da URL
        video_id = None
        if 'youtube.com/watch?v=' in url_youtube:
            video_id = url_youtube.split('youtube.com/watch?v=')[1].split('&')[0]
        elif 'youtu.be/' in url_youtube:
            video_id = url_youtube.split('youtu.be/')[1].split('?')[0]
            
        if not video_id:
            raise ValueError("Não foi possível extrair o ID do vídeo a partir da URL fornecida.")
        
        # Função para tentar obter a transcrição com proxies
        def obter_transcricao_com_proxy():
            # Tenta primeiro sem proxy (pode funcionar em ambiente local)
            try:
                print("Tentando obter transcrição sem proxy...")
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                return transcript_list
            except Exception as e:
                print(f"Erro ao tentar sem proxy: {str(e)}")
                
                # Se falhar, tenta com cada proxy disponível
                if FREE_PROXIES:
                    # Embaralha a lista para usar proxies diferentes a cada tentativa
                    proxies_aleatorios = FREE_PROXIES.copy()
                    random.shuffle(proxies_aleatorios)
                    
                    for proxy in proxies_aleatorios:
                        try:
                            print(f"Tentando com proxy: {proxy}")
                            # Configura o proxy para a API
                            os.environ["HTTP_PROXY"] = proxy
                            os.environ["HTTPS_PROXY"] = proxy
                            
                            # Pequeno delay para evitar sobrecarregar os servidores
                            time.sleep(1)
                            
                            # Tenta obter a lista de transcrições
                            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                            print("Sucesso com proxy!")
                            return transcript_list
                        except Exception as e:
                            print(f"Falha com o proxy {proxy}: {str(e)}")
                            continue
                
                # Se todas as tentativas falharem, levanta a exceção original
                raise Exception("Não foi possível obter a transcrição - todos os proxies falharam ou nenhum proxy disponível")
        
        # Tenta obter a lista de transcrições usando proxies se necessário
        try:
            transcript_list = obter_transcricao_com_proxy()
        except Exception as e:
            # Se falhar com todos os proxies, tenta o método alternativo do LangChain
            print(f"Erro ao obter transcrições com proxies: {str(e)}")
            print("Tentando método alternativo com LangChain YoutubeLoader...")
            
            try:
                # Configurar proxies para o requests (usado pelo LangChain)
                proxy = None
                if FREE_PROXIES:
                    proxy = random.choice(FREE_PROXIES)
                
                session = requests.Session()
                if proxy:
                    session.proxies = {"http": proxy, "https": proxy}
                
                loader = YoutubeLoader.from_youtube_url(
                    url_youtube,
                    language=['pt', 'en'],
                    add_video_info=True,
                    custom_requests_session=session
                )
                
                docs = loader.load()
                
                if not docs:
                    raise ValueError("Nenhuma transcrição encontrada pelo LangChain YoutubeLoader")
                
                documento = '\n'.join([doc.page_content for doc in docs])
                
                # Tenta extrair o título
                titulo = "Vídeo do YouTube"
                try:
                    titulo = docs[0].metadata.get('title', titulo)
                except:
                    pass
                
                # Retorna o resultado do método alternativo
                return {
                    'tipo': 'Vídeo do YouTube',
                    'url': url_youtube,
                    'titulo': titulo,
                    'conteudo': documento
                }
                
            except Exception as e2:
                raise ValueError(f"Todos os métodos de obtenção de transcrição falharam. Detalhes: {str(e)}, {str(e2)}")
        
        # Se chegou aqui, obteve a transcript_list com sucesso
        # Tenta português primeiro, depois inglês ou qualquer idioma disponível
        transcript = None
        try:
            transcript = transcript_list.find_transcript(['pt', 'pt-BR'])
        except:
            try:
                transcript = transcript_list.find_transcript(['en'])
            except:
                # Tenta obter transcrição gerada automaticamente
                try:
                    for t in transcript_list:
                        transcript = t
                        break
                except:
                    pass
                
        if not transcript:
            raise ValueError("Nenhuma transcrição disponível para este vídeo.")
            
        # Obter o conteúdo da transcrição e formata com timestamps
        transcript_data = transcript.fetch()
        
        documento = ""
        for item in transcript_data:
            # Trata o item de forma segura, independente de seu tipo
            try:
                # Trata como dicionário primeiro
                if isinstance(item, dict):
                    texto = item.get('text', '')
                    start = item.get('start', 0)
                # Se não for dicionário, tenta acessar como objeto com atributos
                else:
                    # Acessa diretamente os atributos do objeto
                    texto = getattr(item, 'text', '')
                    start = getattr(item, 'start', 0)
                
                minutos = int(start // 60)
                segundos = int(start % 60)
                timestamp = f"{minutos:02d}:{segundos:02d}"
                documento += f"[{timestamp}] {texto}\n"
            except Exception as e:
                print(f"Erro ao processar item da transcrição: {str(e)}")
                continue
            
        # Extrai o título do vídeo
        titulo = "Vídeo do YouTube"
        try:
            # Configura uma sessão para usar proxy se necessário
            session = requests.Session()
            if FREE_PROXIES:
                proxy = random.choice(FREE_PROXIES)
                session.proxies = {"http": proxy, "https": proxy}
            
            # Obtém o título da página do vídeo
            response = session.get(url_youtube, headers=WEB_HEADERS, verify=False, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            title_tag = soup.find('title')
            
            if title_tag and title_tag.string:
                titulo = title_tag.string.strip().replace(' - YouTube', '')
        except Exception as e:
            print(f"Aviso: Não foi possível extrair o título do vídeo: {str(e)}")
        
        # Limpa variáveis de ambiente de proxy para não afetar outras partes do código
        if "HTTP_PROXY" in os.environ:
            del os.environ["HTTP_PROXY"]
        if "HTTPS_PROXY" in os.environ:
            del os.environ["HTTPS_PROXY"]
        
        # Retorna as informações do vídeo
        return {
            'tipo': 'Vídeo do YouTube',
            'url': url_youtube,
            'titulo': titulo,
            'conteudo': documento
        }
    except Exception as e:
        # Limpa variáveis de ambiente de proxy em caso de erro
        if "HTTP_PROXY" in os.environ:
            del os.environ["HTTP_PROXY"]
        if "HTTPS_PROXY" in os.environ:
            del os.environ["HTTPS_PROXY"]
            
        # Captura e retorna erros detalhados
        error_msg = str(e)
        print(f"Erro ao carregar o vídeo do YouTube {url_youtube}: {error_msg}")
        return {
            'tipo': 'Vídeo do YouTube (erro)',
            'url': url_youtube,
            'titulo': 'Erro ao carregar',
            'conteudo': f'Não foi possível carregar a transcrição do vídeo: {error_msg}'
        }