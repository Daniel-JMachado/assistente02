"""
TARS - Assistente de IA para Análise de Conteúdo

Este é o ponto de entrada principal da aplicação TARS, que fornece
uma interface de chat com o modelo de IA Claude para análise de conteúdo
de diferentes fontes (sites, vídeos, PDFs, etc).

Desenvolvido para estudantes universirário
"""

import streamlit as st
from config.settings import APP_NAME, APP_ICON
from core.session import initialize_session, clear_conversation, add_message
from core.llm import generate_response
from ui.components import (
    load_css, header, chat_message, sidebar_header, 
    source_selector, source_info_panel, clear_conversation_button,
    timestamp_display, footer
)
from ui.pages.sources import render_source_interface

# Configuração da página Streamlit
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}  # Remove itens do menu
)

# Carrega os estilos CSS personalizados
load_css()

# Inicializa o estado da sessão
initialize_session()

# Exibe o cabeçalho principal
header()

# Cabeçalho da barra lateral
sidebar_header()

# Seletor de fonte de dados
fonte = source_selector()

# Renderiza interface para a fonte selecionada
render_source_interface(fonte)

# Botão para limpar a conversa
if clear_conversation_button():
    clear_conversation()
    st.rerun()

# Exibe timestamp na barra lateral
timestamp_display()

# Se uma fonte de dados foi carregada, exibe informações
if st.session_state.documento:
    # Exibe informações sobre a fonte atual
    source_info_panel(st.session_state.documento)

# Separador visual entre informações da fonte e o chat
st.markdown("---")

# Exibe o histórico de mensagens
for mensagem in st.session_state.mensagens:
    avatar = "👤" if mensagem["role"] == "user" else "🤖"
    chat_message(mensagem["role"], mensagem["content"], avatar)

# Campo de entrada de texto para o usuário
prompt = st.chat_input("Digite sua pergunta...", key="chat_input")

# Processa a entrada do usuário
if prompt:
    # Adiciona a mensagem do usuário ao histórico e exibe
    add_message("user", prompt)
    chat_message("user", prompt, "👤")
    
    # Obtém resposta do modelo com o contexto atual
    with st.spinner("TARS está processando sua pergunta..."):
        try:
            # Gera a resposta do modelo
            resposta = generate_response(st.session_state.mensagens, st.session_state.documento)
            
            # Exibe a resposta
            chat_message("assistant", resposta, "🤖")
            
            # Adiciona a resposta ao histórico
            add_message("assistant", resposta)
        except Exception as e:
            error_msg = f"Desculpe, ocorreu um erro ao processar sua pergunta: {str(e)}"
            st.error(error_msg)
            chat_message("assistant", error_msg, "🤖")
            add_message("assistant", error_msg)

# Exibe o rodapé
footer()

# Exibe uma mensagem de boas-vindas se for a primeira execução da sessão
if not st.session_state.mensagens:
    st.info(
        """👋 Bem-vindo ao TARS! Selecione uma fonte de dados na barra lateral para começar. 
        Você pode carregar sites, vídeos do YouTube, documentos PDF ou simplesmente iniciar um chat livre."""
    )