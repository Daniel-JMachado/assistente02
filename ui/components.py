"""
Componentes de UI reutilizáveis para a aplicação TARS.
Este módulo contém elementos de interface como cabeçalhos, mensagens e controles.
"""

import streamlit as st
import os
from datetime import datetime
from config.settings import APP_NAME, APP_ICON, CSS_DIR

def load_css():
    """Carrega arquivos CSS personalizados."""
    css_file = os.path.join(CSS_DIR, "styles.css")
    
    if os.path.exists(css_file):
        with open(css_file, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"Arquivo CSS não encontrado: {css_file}")
        
        # CSS de fallback
        st.markdown("""
        <style>
            /* Esconder barra de configuração do Streamlit */
            [data-testid="stToolbar"] {
              display: none !important;
            }
            
            header[data-testid="stHeader"] {
              display: none !important;
            }
            
            footer[data-testid="stFooter"] {
              display: none !important;
            }
            
            .tars-header { 
                display: flex; 
                justify-content: center;
                align-items: center; 
                margin-bottom: 1.5rem;
            }
            .tars-logo-centered {
                display: flex;
                align-items: center;
                gap: 12px;
                justify-content: center;
            }
            .tars-title {
                color: #1e88e5;
                font-weight: 700;
                margin: 0;
            }
        </style>
        """, unsafe_allow_html=True)

def header():
    """Renderiza o cabeçalho da aplicação com logo e título centralizado."""
    st.markdown(
        f"""
        <div class="tars-header">
            <div class="tars-logo-centered">
                <h1 class="tars-title">{APP_NAME}</h1>
                <span class="tars-icon">{APP_ICON}</span>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

def chat_message(role, content, avatar=None):
    """
    Exibe uma mensagem de chat estilizada.
    
    Args:
        role: Papel do mensageiro ('user' ou 'assistant')
        content: Conteúdo da mensagem
        avatar: Emoji para o avatar (opcional)
    """
    # Define avatares padrão se não forem fornecidos
    if avatar is None:
        avatar = "👤" if role == "user" else "🤖"
    
    with st.chat_message(role, avatar=avatar):
        st.write(content)

def sidebar_header():
    """Renderiza o cabeçalho da barra lateral."""
    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-bottom: 10px;">
            <h3 style="color: var(--primary-color); margin-bottom: 5px;">Fonte de Dados</h3> 
        </div>
        """, 
        unsafe_allow_html=True
    )

def source_selector():
    """
    Cria um seletor de fontes de dados estilizado.
    
    Returns:
        String com o tipo de fonte selecionada
    """
    st.sidebar.markdown(
        """
        <div style="margin-bottom: 5px;">  
        <p style="font-size: 0.85rem; color: var(--text-secondary);">Escolha o conteúdo para análise</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    fonte = st.sidebar.radio(
        "Selecione a fonte de dados:",
        ["Site", "YouTube", "PDF", "Imagem", "Chat"],
        label_visibility="collapsed",
        help="Escolha o tipo de conteúdo para analisar com o TARS."
    )
    
    return fonte

def source_info_panel(documento_info):
    """
    Exibe um painel com informações sobre a fonte de dados atual.
    
    Args:
        documento_info: Informações sobre o documento atual
    """
    if not documento_info:
        return
    
    fonte_tipo = "Desconhecido"
    fonte_titulo = "Sem título"
    fonte_url = ""
    
    if isinstance(documento_info, dict):
        fonte_tipo = documento_info.get('tipo', 'Desconhecido')
        fonte_titulo = documento_info.get('titulo', 'Sem título')
        fonte_url = documento_info.get('url', '')
    
    col1, col2 = st.columns([1, 5])
    
    with col1:
        # Ícone para o tipo de fonte
        if "Site" in fonte_tipo:
            st.markdown("🌐")
        elif "YouTube" in fonte_tipo:
            st.markdown("🎬")
        elif "PDF" in fonte_tipo:
            st.markdown("📄")
        elif "Chat" in fonte_tipo:
            st.markdown("💬")
        else:
            st.markdown("📁")
    
    with col2:
        st.markdown(f"**Fonte atual:** {fonte_tipo}")
        if fonte_titulo and fonte_titulo != "Sem título":
            st.markdown(f"**Título:** {fonte_titulo}")
        if fonte_url:
            st.markdown(f"**URL:** [{fonte_url}]({fonte_url})")

def clear_conversation_button():
    """
    Renderiza o botão para limpar a conversa.
    
    Returns:
        Boolean indicando se o botão foi clicado
    """
    return st.sidebar.button(
        "Limpar Conversa", 
        help="Limpa todo o histórico de mensagens e começa uma nova conversa",
        type="primary",
        use_container_width=True
    )

def timestamp_display():
    """Exibe um timestamp discreto."""
    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y %H:%M")
    
    st.sidebar.markdown(
        f"""
        <div style="margin-top: 30px; text-align: center; font-size: 0.8rem; color: #9e9e9e;">
            {timestamp}
        </div>
        """,
        unsafe_allow_html=True
    )

def footer():
    """Renderiza o rodapé da aplicação."""
    st.markdown(
        """
        <div style="margin-top: 50px; text-align: center; color: var(--text-secondary); font-size: 0.8rem;">
            <p>TARS - Assistente para Estudantes by Daniel&Claude</p>
        </div>
        """,
        unsafe_allow_html=True
    )