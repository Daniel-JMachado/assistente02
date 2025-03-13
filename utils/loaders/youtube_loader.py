"""
Módulo para carregamento e processamento de transcrições de vídeos do YouTube.
Utiliza a API youtube_transcript_api para extrair transcrições.
"""

import os
import requests
import urllib3
from bs4 import BeautifulSoup
from langchain_community.document_loaders import YoutubeLoader
from config.settings import WEB_HEADERS

# Desativa avisos de SSL para evitar warnings no console
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
            
        if not video_id:
            raise ValueError("Não foi possível extrair o ID do vídeo a partir da URL fornecida.")
            
        # Tenta obter a transcrição em diferentes idiomas
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
            texto = item.get('text', '')
            start = item.get('start', 0)
            minutos = int(start // 60)
            segundos = int(start % 60)
            timestamp = f"{minutos:02d}:{segundos:02d}"
            documento += f"[{timestamp}] {texto}\n"
            
        # Extrai o título do vídeo
        titulo = "Vídeo do YouTube"
        try:
            # Obtém o título da página do vídeo
            response = requests.get(url_youtube, headers=WEB_HEADERS, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            title_tag = soup.find('title')
            
            if title_tag and title_tag.string:
                titulo = title_tag.string.strip().replace(' - YouTube', '')
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