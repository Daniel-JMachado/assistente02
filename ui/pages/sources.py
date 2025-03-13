"""
Módulo que implementa as interfaces específicas para cada fonte de dados.
Contém componentes para upload de PDFs, carregamento de sites, etc.
"""

import streamlit as st
import os
from utils.loaders.web_loader import carrega_site
from utils.loaders.youtube_loader import carrega_youtube
from utils.loaders.pdf_loader import carrega_pdf
from utils.loaders.image_loader import carrega_imagem

def render_site_panel():
    """
    Renderiza o painel para entrada e carregamento de sites web.
    """
    st.sidebar.markdown(
        """
        <div class="source-panel">
            <h4>Carregar Site</h4>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    url_site = st.sidebar.text_input(
        "URL do site:",
        placeholder="exemplo.com",
        help="Digite o endereço do site que você deseja analisar."
    )
    
    if st.sidebar.button("Carregar Site", type="primary", use_container_width=True):
        if not url_site or url_site.isspace():
            st.sidebar.error("Por favor, informe uma URL válida.")
            return
        
        # Mostra mensagem de carregamento na sidebar
        status_placeholder = st.sidebar.empty()
        status_placeholder.info("Carregando conteúdo do site...")
        
        # Carrega o site
        st.session_state.documento = carrega_site(url_site)
        st.session_state.fonte_dados = "Site"
        
        # Verifica se houve erro e atualiza o status
        if st.session_state.documento.get('tipo', '').endswith('(erro)'):
            status_placeholder.error(st.session_state.documento.get('conteudo', 'Erro ao carregar o site.'))
        else:
            status_placeholder.markdown(
                """
                <div style="background-color: #d4edda; color: #155724; padding: 10px; 
                border-radius: 4px; font-size: 16px; font-weight: bold; text-align: center;">
                ✅ Site carregado com sucesso!
                </div>
                """, 
                unsafe_allow_html=True
            )

def render_youtube_panel():
    """
    Renderiza o painel para entrada e carregamento de vídeos do YouTube.
    """
    st.sidebar.markdown(
        """
        <div class="source-panel">
            <h4>Carregar Vídeo do YouTube</h4>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    url_youtube = st.sidebar.text_input(
        "URL do vídeo:",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Cole aqui o link completo do vídeo do YouTube."
    )
    
    if st.sidebar.button("Carregar Vídeo", type="primary", use_container_width=True):
        if not url_youtube or url_youtube.isspace():
            st.sidebar.error("Por favor, informe uma URL válida.")
            return
        
        # Mostra mensagem de carregamento na sidebar
        status_placeholder = st.sidebar.empty()
        status_placeholder.info("Carregando transcrição do vídeo...")
        
        # Carrega o vídeo
        st.session_state.documento = carrega_youtube(url_youtube)
        st.session_state.fonte_dados = "YouTube"
        
        # Verifica se houve erro e atualiza o status
        if st.session_state.documento.get('tipo', '').endswith('(erro)'):
            status_placeholder.error(st.session_state.documento.get('conteudo', 'Erro ao carregar o vídeo.'))
        else:
            status_placeholder.markdown(
                """
                <div style="background-color: #d4edda; color: #155724; padding: 10px; 
                border-radius: 4px; font-size: 16px; font-weight: bold; text-align: center;">
                ✅ Vídeo carregado com sucesso!
                </div>
                """, 
                unsafe_allow_html=True
            )

def render_pdf_panel():
    """
    Renderiza o painel para upload e processamento de PDFs.
    """
    st.sidebar.markdown(
        """
        <div class="source-panel">
            <h4>Carregar PDFs</h4>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    uploaded_files = st.sidebar.file_uploader(
        "Selecione um ou mais PDFs:",
        type=["pdf"],
        accept_multiple_files=True,
        help="Arraste e solte arquivos PDF ou clique para selecioná-los."
    )
    
    if st.sidebar.button("Processar PDFs", type="primary", use_container_width=True):
        if not uploaded_files:
            st.sidebar.error("Por favor, selecione pelo menos um arquivo PDF.")
            return
        
        # Mostra mensagem de carregamento na sidebar
        status_placeholder = st.sidebar.empty()
        status_placeholder.info("Processando documentos...")
        
        # Salva os arquivos enviados no diretório temporário
        pdf_paths = []
        for uploaded_file in uploaded_files:
            file_path = os.path.join(st.session_state.temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            pdf_paths.append(file_path)
        
        # Processa os PDFs
        documento_info = carrega_pdf(pdf_paths)
        st.session_state.documento = documento_info
        st.session_state.fonte_dados = "PDF"
        
        # Verifica se houve erro e atualiza o status
        if documento_info.get('tipo', '').endswith('(erro)'):
            status_placeholder.error(documento_info.get('conteudo', 'Erro ao processar os PDFs.'))
        else:
            status_placeholder.markdown(
                """
                <div style="background-color: #d4edda; color: #155724; padding: 10px; 
                border-radius: 4px; font-size: 16px; font-weight: bold; text-align: center;">
                ✅ PDFs processados com sucesso!
                </div>
                """, 
                unsafe_allow_html=True
            )

def render_image_panel():
    """
    Renderiza o painel para upload e processamento de imagens.
    """
    st.sidebar.markdown(
        """
        <div class="source-panel">
            <h4>Carregar Imagem</h4>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    uploaded_image = st.sidebar.file_uploader(
        "Selecione uma imagem:",
        type=["jpg", "jpeg", "png", "webp"],
        help="Arraste e solte uma imagem ou clique para selecioná-la."
    )
    
    if st.sidebar.button("Analisar Imagem", type="primary", use_container_width=True):
        if not uploaded_image:
            st.sidebar.error("Por favor, selecione uma imagem.")
            return
        
        # Mostra mensagem de carregamento na sidebar
        status_placeholder = st.sidebar.empty()
        status_placeholder.info("Analisando imagem...")
        
        # Processa a imagem
        st.session_state.documento = carrega_imagem(uploaded_image)
        st.session_state.fonte_dados = "Imagem"
        
        # Verifica se houve erro e atualiza o status
        if st.session_state.documento.get('tipo', '').endswith('(erro)'):
            status_placeholder.error(st.session_state.documento.get('conteudo', 'Erro ao analisar a imagem.'))
        else:
            status_placeholder.markdown(
                """
                <div style="background-color: #d4edda; color: #155724; padding: 10px; 
                border-radius: 4px; font-size: 16px; font-weight: bold; text-align: center;">
                ✅ Imagem analisada com sucesso!
                </div>
                """, 
                unsafe_allow_html=True
            )

def render_chat_panel():
    """
    Renderiza o painel para chat livre sem contexto específico.
    """
    st.sidebar.markdown(
        """
        <div class="source-panel">
            <h4>Chat Livre</h4>
            <p style="font-size: 0.9rem; color: #757575;">
                Converse livremente sem fonte de dados específica.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    if st.sidebar.button("Iniciar Chat Livre", type="primary", use_container_width=True):
        st.session_state.documento = {
            'tipo': 'Chat Livre',
            'url': '',
            'titulo': 'Conversa sem contexto adicional',
            'conteudo': ''
        }
        st.session_state.fonte_dados = "Chat"
        st.sidebar.markdown(
            """
            <div style="background-color: #d4edda; color: #155724; padding: 10px; 
            border-radius: 4px; font-size: 16px; font-weight: bold; text-align: center;">
            ✅ Chat livre ativado!
            </div>
            """, 
            unsafe_allow_html=True
        )

def render_source_interface(fonte):
    """
    Renderiza a interface específica para a fonte de dados selecionada.
    
    Args:
        fonte: Tipo de fonte selecionada ('Site', 'YouTube', 'PDF', 'Imagem', 'Chat')
    """
    if fonte == "Site":
        render_site_panel()
    elif fonte == "YouTube":
        render_youtube_panel()
    elif fonte == "PDF":
        render_pdf_panel()
    elif fonte == "Imagem":
        render_image_panel()
    elif fonte == "Chat":
        render_chat_panel()