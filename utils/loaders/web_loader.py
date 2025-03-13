"""
Módulo para carregamento e processamento de conteúdo de sites web.
Utiliza WebBaseLoader da LangChain e BeautifulSoup para extrair conteúdo.
"""

import os
import requests
import urllib3
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader
from config.settings import USER_AGENT, WEB_HEADERS

# Desativa avisos de SSL para evitar warnings no console
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def carrega_site(url_site=None):
    """
    Carrega o conteúdo de um site web.
    
    Args:
        url_site: URL do site a ser carregado
        
    Returns:
        Dicionário com informações e conteúdo do site
    """
    # Validação da URL
    if url_site is None or not url_site.strip():
        url_site = os.getenv('SITE_URL')
        if not url_site:
            return {
                'tipo': 'Site Web (erro)',
                'url': '',
                'titulo': 'URL não fornecida',
                'conteudo': 'É necessário fornecer uma URL válida para carregar o site.'
            }
    
    # Adiciona protocolo se necessário
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
            header_template=WEB_HEADERS  # User agent para evitar bloqueios
        )
        
        # Carrega documentos e concatena o conteúdo
        lista_documentos = loader.load()
        documento = '\n'.join([doc.page_content for doc in lista_documentos])
        
        # Extrai o título do site
        titulo = "Site Web"
        try:
            # Usa BeautifulSoup para extrair o título
            response = requests.get(url_site, headers=WEB_HEADERS, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            title_tag = soup.find('title')
            
            if title_tag and title_tag.string:
                titulo = title_tag.string.strip()
        except Exception as e:
            print(f"Aviso: Não foi possível extrair o título do site: {str(e)}")
        
        # Retorna as informações do site
        return {
            'tipo': 'Site Web',
            'url': url_site,
            'titulo': titulo,
            'conteudo': documento
        }
    except Exception as e:
        # Captura e retorna erros detalhados
        error_msg = str(e)
        print(f"Erro ao carregar o site {url_site}: {error_msg}")
        return {
            'tipo': 'Site Web (erro)',
            'url': url_site,
            'titulo': 'Erro ao carregar',
            'conteudo': f'Não foi possível carregar o conteúdo do site: {error_msg}'
        }