"""
Módulo para carregamento e processamento de arquivos PDF.
Utiliza PyPDFLoader da LangChain para extrair texto dos PDFs.
"""

import os
from langchain_community.document_loaders import PyPDFLoader
from config.settings import DOCUMENTS_DIR

def carrega_pdf(pdf_paths=None):
    """
    Carrega e processa arquivos PDF.
    
    Args:
        pdf_paths: Lista de caminhos para arquivos PDF a serem processados.
                  Se None, processa todos os PDFs na pasta 'documentos'.
        
    Returns:
        Dicionário com informações e conteúdo dos PDFs processados
    """
    documento = ''
    arquivos_processados = []
    
    # Se não foram fornecidos caminhos específicos, usa a pasta documentos
    if pdf_paths is None:
        # Define caminho da pasta de documentos
        pasta = DOCUMENTS_DIR
        
        # Verifica se a pasta existe
        if not os.path.exists(pasta):
            return {
                'tipo': 'PDF (erro)',
                'url': pasta,
                'titulo': 'Pasta não encontrada',
                'conteudo': f'Pasta de documentos não encontrada: {pasta}'
            }
        
        # Lista apenas arquivos PDF na pasta
        arquivos_pdf = [f for f in os.listdir(pasta) if f.lower().endswith('.pdf')]
        
        # Verifica se existem PDFs na pasta
        if not arquivos_pdf:
            return {
                'tipo': 'PDF (erro)',
                'url': pasta,
                'titulo': 'Nenhum PDF encontrado',
                'conteudo': f'Nenhum arquivo PDF encontrado na pasta: {pasta}'
            }
        
        # Constrói os caminhos completos para os arquivos
        pdf_paths = [os.path.join(pasta, arquivo) for arquivo in arquivos_pdf]
    
    # Valida se a lista de caminhos não está vazia
    if not pdf_paths:
        return {
            'tipo': 'PDF (erro)',
            'url': '',
            'titulo': 'Nenhum PDF fornecido',
            'conteudo': 'Nenhum arquivo PDF fornecido para processamento.'
        }
    
    # Processa cada arquivo PDF
    for caminho_completo in pdf_paths:
        try:
            # Valida se o arquivo existe
            if not os.path.exists(caminho_completo):
                print(f"Arquivo não encontrado: {caminho_completo}")
                continue
                
            # Carrega e extrai texto do PDF
            loader = PyPDFLoader(caminho_completo)
            lista_documentos = loader.load()
            
            # Concatena o conteúdo de todas as páginas
            documento += '\n\n--- ' + os.path.basename(caminho_completo) + ' ---\n\n'
            documento += '\n'.join([doc.page_content for doc in lista_documentos])
            
            # Adiciona à lista de arquivos processados
            arquivos_processados.append(os.path.basename(caminho_completo))
            print(f"Arquivo processado com sucesso: {os.path.basename(caminho_completo)}")
        except Exception as e:
            print(f"Erro ao processar arquivo {caminho_completo}: {str(e)}")
    
    # Verifica se algum arquivo foi processado
    if not arquivos_processados:
        return {
            'tipo': 'PDF (erro)',
            'url': '',
            'titulo': 'Falha no processamento',
            'conteudo': 'Não foi possível processar nenhum dos arquivos PDF fornecidos.'
        }
    
    # Retorna as informações dos PDFs processados
    return {
        'tipo': 'Documentos PDF',
        'url': ', '.join(pdf_paths),
        'titulo': f"Arquivos: {', '.join(arquivos_processados)}",
        'conteudo': documento
    }