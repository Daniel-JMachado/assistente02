"""
Módulo para gerenciamento do estado da sessão no Streamlit.
Gerencia persistência de dados entre interações com o usuário.
"""

import streamlit as st
import os
import tempfile
import shutil
import uuid
from datetime import datetime

def initialize_session():
    """
    Inicializa todos os estados necessários para a sessão do Streamlit.
    Chamado no início da aplicação para garantir que todos os estados estejam disponíveis.
    """
    # Estado para histórico de mensagens
    if 'mensagens' not in st.session_state:
        st.session_state.mensagens = []
    
    # Estado para fonte de dados atual
    if 'fonte_dados' not in st.session_state:
        st.session_state.fonte_dados = None
    
    # Estado para o documento atual
    if 'documento' not in st.session_state:
        st.session_state.documento = ""
    
    # ID de sessão único
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    # Timestamp da última interação
    if 'last_interaction' not in st.session_state:
        st.session_state.last_interaction = datetime.now()
    
    # Diretório temporário para arquivos
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = tempfile.mkdtemp()
        print(f"Diretório temporário criado: {st.session_state.temp_dir}")

def update_last_interaction():
    """Atualiza o timestamp da última interação."""
    st.session_state.last_interaction = datetime.now()

def clear_conversation():
    """
    Limpa o histórico de conversas e reinicia o estado.
    Também limpa os arquivos temporários, se houverem.
    """
    # Limpa o histórico de mensagens
    st.session_state.mensagens = []
    
    # Limpa e recria o diretório temporário
    if 'temp_dir' in st.session_state and os.path.exists(st.session_state.temp_dir):
        try:
            shutil.rmtree(st.session_state.temp_dir)
            st.session_state.temp_dir = tempfile.mkdtemp()
            print(f"Diretório temporário recriado: {st.session_state.temp_dir}")
        except Exception as e:
            print(f"Erro ao limpar diretório temporário: {str(e)}")

def get_session_info():
    """
    Retorna informações sobre a sessão atual.
    
    Returns:
        Dicionário com informações da sessão
    """
    return {
        'id': st.session_state.get('session_id', 'unknown'),
        'start_time': st.session_state.get('session_start', datetime.now()),
        'last_interaction': st.session_state.get('last_interaction', datetime.now()),
        'message_count': len(st.session_state.get('mensagens', [])),
        'current_source': st.session_state.get('fonte_dados', None)
    }

def add_message(role, content):
    """
    Adiciona uma mensagem ao histórico de conversas.
    
    Args:
        role: Papel do mensageiro ('user' ou 'assistant')
        content: Conteúdo da mensagem
    """
    st.session_state.mensagens.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    update_last_interaction()