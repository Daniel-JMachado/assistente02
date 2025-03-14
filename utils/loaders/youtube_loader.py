"""
Módulo para carregamento e processamento de transcrições de vídeos do YouTube.
Utiliza a API youtube_transcript_api para extrair transcrições.
"""

import os
import re
import requests
import urllib3
import tempfile
from bs4 import BeautifulSoup
from langchain_community.document_loaders import YoutubeLoader
from config.settings import WEB_HEADERS, USER_AGENT

# Desativa avisos de SSL para evitar warnings no console
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configura a variável de ambiente USER_AGENT para o pytube (usado pelo YoutubeLoader)
os.environ["USER_AGENT"] = USER_AGENT

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
        elif 'm.youtube.com' in url_youtube:
            # Suporte para YouTube mobile
            match = re.search(r'v=([^&]+)', url_youtube)
            if match:
                video_id = match.group(1)
        elif 'youtube.com/shorts/' in url_youtube:
            # Suporte para YouTube shorts
            video_id = url_youtube.split('youtube.com/shorts/')[1].split('?')[0]
            
        if not video_id:
            raise ValueError("Não foi possível extrair o ID do vídeo a partir da URL fornecida.")
            
        # Tenta obter a transcrição em diferentes idiomas
        documento = ""
        transcript_error = None
        
        # Método 1: Usar YouTubeTranscriptApi
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Tenta português primeiro, depois inglês ou qualquer idioma disponível
            transcript = None
            try:
                transcript = transcript_list.find_transcript(['pt', 'pt-BR'])
            except:
                try:
                    transcript = transcript_list.find_transcript(['en'])
                except:
                    # Tenta obter transcrição gerada automaticamente
                    for t in transcript_list:
                        transcript = t
                        break
                    
            if not transcript:
                raise ValueError("Nenhuma transcrição disponível para este vídeo.")
                
            # Obter o conteúdo da transcrição e formata com timestamps
            transcript_data = transcript.fetch()
            
            for entry in transcript_data:
                texto = entry['text'] if isinstance(entry, dict) else str(entry)
                start = entry.get('start', 0) if isinstance(entry, dict) else 0
                minutos = int(start // 60)
                segundos = int(start % 60)
                timestamp = f"{minutos:02d}:{segundos:02d}"
                documento += f"[{timestamp}] {texto}\n"
                
            print(f"Transcrição obtida com sucesso usando YouTubeTranscriptApi")
            
        except Exception as e:
            transcript_error = e
            print(f"Erro ao usar YouTubeTranscriptApi: {str(e)}")
            documento = ""  # Limpa documento para tentar outro método
        
        # Método 2: Usar LangChain YoutubeLoader se o método 1 falhar
        if not documento:
            try:
                print(f"Tentando método alternativo com LangChain YoutubeLoader")
                
                # Cria diretório temporário para o download
                temp_dir = tempfile.mkdtemp()
                print(f"Diretório temporário criado: {temp_dir}")
                
                # Tratamento manual fallback
                full_text = ""
                try:
                    # Primeiro tenta com método direto via requests
                    # Isso é um fallback para quando os outros métodos falham
                    print("Tentando obter conteúdo via método de fallback...")
                    proxied_url = f"https://projectlounge.pw/ytdl/download?url={url_youtube}"
                    response = requests.get(proxied_url, headers=WEB_HEADERS, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        transcript_tag = soup.find('div', {'class': 'transcript'})
                        if transcript_tag:
                            full_text = transcript_tag.get_text()
                            print("Conteúdo obtido via método de fallback!")
                except Exception as proxy_error:
                    print(f"Método de fallback falhou: {str(proxy_error)}")
                
                if full_text:
                    # Se conseguiu obter texto pelo método de fallback
                    documento = full_text
                    print(f"Usando conteúdo obtido via método de fallback")
                else:
                    # Tenta com YoutubeLoader como último recurso
                    print("Tentando YoutubeLoader como último recurso...")
                    try:
                        loader = YoutubeLoader.from_youtube_url(
                            url_youtube,
                            add_video_info=True,
                            language=["pt", "en", "auto"],
                            continue_on_failure=True,
                            use_ytdlp=False  # Use pytube em vez de yt-dlp
                        )
                        
                        docs = loader.load()
                        if docs and len(docs) > 0:
                            documento = docs[0].page_content
                            print(f"Transcrição obtida com sucesso usando LangChain YoutubeLoader")
                        else:
                            raise ValueError("YoutubeLoader não retornou documentos")
                    except Exception as yt_error:
                        # Se falhou, tenta extrair pelo menos alguma informação
                        print(f"YoutubeLoader falhou: {str(yt_error)}")
                        # Cria um texto informativo para o usuário
                        documento = f"""
[OBSERVAÇÃO] Não foi possível obter a transcrição completa deste vídeo.

Possíveis razões:
- O vídeo não tem legendas disponíveis
- O canal desativou a opção de transcrição
- Problemas técnicos na conexão com o YouTube

ID do vídeo: {video_id}
URL: {url_youtube}

Você ainda pode fazer perguntas sobre o vídeo com base nas informações disponíveis,
mas a análise será limitada sem a transcrição completa.
"""
                    
            except Exception as alt_error:
                # Se todos os métodos falharam, mas já temos um documento com mensagem de erro amigável,
                # vamos usar ele em vez de lançar uma exceção
                if not documento or documento.strip() == "":
                    if transcript_error:
                        error_msg = f"Falha em ambos os métodos. YouTubeTranscriptApi: {str(transcript_error)}. LangChain: {str(alt_error)}"
                    else:
                        error_msg = f"Falha ao obter transcrição com LangChain: {str(alt_error)}"
                    print(error_msg)
                    
                    # Cria um documento informativo de falha
                    documento = f"""
[OBSERVAÇÃO] Não foi possível obter a transcrição deste vídeo devido a um erro técnico.

ID do vídeo: {video_id}
URL: {url_youtube}

Você ainda pode conversar sobre outros tópicos ou tentar com outro vídeo que tenha legendas disponíveis.
"""
        
        # Se chegou aqui sem conteúdo, algo deu errado
        if not documento or documento.strip() == "":
            raise ValueError("Não foi possível extrair conteúdo do vídeo com nenhum método disponível.")
            
        # Extrai o título do vídeo
        titulo = "Vídeo do YouTube"
        try:
            # Método 1: Tenta obter título através do API
            try:
                import urllib.parse
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                api_url = f"https://noembed.com/embed?url={urllib.parse.quote(video_url)}"
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'title' in data:
                        titulo = data['title']
                        print(f"Título obtido via noembed API: {titulo}")
            except Exception as api_error:
                print(f"Não foi possível obter título via API: {str(api_error)}")
                pass
                
            # Método 2: Obtém o título da página do vídeo (fallback)
            if titulo == "Vídeo do YouTube":
                response = requests.get(url_youtube, headers=WEB_HEADERS, verify=False, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                title_tag = soup.find('title')
                
                if title_tag and title_tag.string:
                    titulo = title_tag.string.strip().replace(' - YouTube', '')
                    print(f"Título obtido via página web: {titulo}")
        except Exception as e:
            print(f"Aviso: Não foi possível extrair o título do vídeo: {str(e)}")
        
        # Retorna as informações do vídeo
        return {
            'tipo': 'Vídeo do YouTube',
            'url': url_youtube,
            'titulo': titulo,
            'conteudo': documento
        }
    except Exception as e:
        # Captura e retorna erros detalhados
        error_msg = str(e)
        print(f"Erro ao carregar o vídeo do YouTube {url_youtube}: {error_msg}")
        return {
            'tipo': 'Vídeo do YouTube (erro)',
            'url': url_youtube,
            'titulo': 'Erro ao carregar',
            'conteudo': f'Não foi possível carregar a transcrição do vídeo: {error_msg}'
        }