"""
Módulo para carregamento e processamento de imagens.
Utiliza Vision API do Claude para extrair descrições e textos das imagens.
"""

import os
import io
import base64
from anthropic import Anthropic # type: ignore
from PIL import Image
from config.settings import ANTHROPIC_API_KEY, MODEL

# Inicializa o cliente Anthropic
client = Anthropic(api_key=ANTHROPIC_API_KEY)

def encode_image_to_base64(image_bytes):
    """
    Converte bytes da imagem para string base64.
    
    Args:
        image_bytes: Bytes da imagem
        
    Returns:
        String codificada em base64
    """
    return base64.b64encode(image_bytes).decode('utf-8')

def carrega_imagem(uploaded_image=None):
    """
    Carrega e processa uma imagem.
    
    Args:
        uploaded_image: Objeto de arquivo da imagem carregada
        
    Returns:
        Dicionário com informações e descrição da imagem processada
    """
    # Valida se a imagem foi fornecida
    if uploaded_image is None:
        return {
            'tipo': 'Imagem (erro)',
            'url': '',
            'titulo': 'Imagem não fornecida',
            'conteudo': 'É necessário fornecer uma imagem válida para processamento.'
        }
    
    try:
        # Lê a imagem
        image_bytes = uploaded_image.getvalue()
        
        # Tenta abrir a imagem para validar
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                width, height = img.size
                format_type = img.format
                modo = img.mode
        except Exception as e:
            return {
                'tipo': 'Imagem (erro)',
                'url': '',
                'titulo': 'Formato inválido',
                'conteudo': f'Erro ao processar a imagem: {str(e)}'
            }
        
        # Codifica a imagem em base64
        base64_image = encode_image_to_base64(image_bytes)
        
        # Utiliza o modelo Claude para descrever a imagem
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": "Descreva detalhadamente esta imagem. Se houver texto visível na imagem, transcreva-o também. Forneça uma descrição completa do conteúdo visual."
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": f"image/{format_type.lower() if format_type else 'jpeg'}",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            )
            
            # Extrai a descrição da imagem
            descricao = response.content[0].text
            
        except Exception as e:
            return {
                'tipo': 'Imagem (erro)',
                'url': '',
                'titulo': 'Erro na análise',
                'conteudo': f'Erro ao analisar a imagem com Claude: {str(e)}'
            }
        
        # Retorna as informações da imagem
        return {
            'tipo': 'Imagem',
            'url': '',
            'titulo': f'Imagem ({format_type}, {width}x{height}, {modo})',
            'conteudo': f"Análise da imagem:\n\n{descricao}"
        }
        
    except Exception as e:
        # Captura erros genéricos
        error_msg = str(e)
        print(f"Erro ao processar imagem: {error_msg}")
        return {
            'tipo': 'Imagem (erro)',
            'url': '',
            'titulo': 'Erro no processamento',
            'conteudo': f'Não foi possível processar a imagem: {error_msg}'
        }
