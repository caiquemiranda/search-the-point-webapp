import streamlit as st
import pdf2image
from PIL import Image
import io
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("Capturador de Coordenadas")

# Inicialização das variáveis de estado
if 'coordenadas' not in st.session_state:
    st.session_state.coordenadas = []
if 'imagem_atual' not in st.session_state:
    st.session_state.imagem_atual = None

# Layout em duas colunas
col1, col2 = st.columns([2, 1])

with col1:
    # Upload do arquivo PDF
    uploaded_file = st.file_uploader("Escolha um arquivo PDF", type=['pdf'])
    
    if uploaded_file is not None:
        try:
            # Converter PDF para imagem
            images = pdf2image.convert_from_bytes(uploaded_file.read())
            st.session_state.imagem_atual = images[0]
            
            # Converter a imagem para bytes
            img_bytes = io.BytesIO()
            st.session_state.imagem_atual.save(img_bytes, format='PNG')
            
            # Criar container para a imagem clicável
            image_container = st.container()
            
            # Usar st.image com use_container_width
            image_container.image(img_bytes.getvalue(), use_container_width=True)
            
            # JavaScript para capturar cliques e calcular coordenadas corretas
            st.markdown("""
            <script>
                // Função para adicionar coordenadas
                function addCoordinates(x, y) {
                    const coordinates = window.parent.streamlitPython.setComponentValue(
                        'coordenadas',
                        [...window.parent.streamlitPython.getComponentValue('coordenadas'), {x: x, y: y}]
                    );
                }
                
                // Aguardar carregamento do DOM
                document.addEventListener('DOMContentLoaded', function() {
                    const images = document.querySelectorAll('.stImage img');
                    images.forEach(img => {
                        img.style.cursor = 'crosshair';
                        img.onclick = function(e) {
                            const rect = this.getBoundingClientRect();
                            const scaleX = this.naturalWidth / rect.width;
                            const scaleY = this.naturalHeight / rect.height;
                            
                            const x = Math.round((e.clientX - rect.left) * scaleX);
                            const y = Math.round((e.clientY - rect.top) * scaleY);
                            
                            // Adicionar coordenadas à sessão do Streamlit
                            window.parent.postMessage({
                                type: 'streamlit:setComponentValue',
                                key: 'coordenadas',
                                value: [...(window.parent.streamlitPython.getComponentValue('coordenadas') || []), {x, y}]
                            }, '*');
                            
                            // Forçar atualização da página
                            window.parent.streamlitPython.setComponentValue('_stcore:rerun', true);
                        };
                    });
                });
            </script>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Erro ao processar o PDF: {str(e)}")

with col2:
    st.subheader("Coordenadas Capturadas")
    
    # Exibir coordenadas capturadas
    if st.session_state.coordenadas:
        df = pd.DataFrame(st.session_state.coordenadas)
        st.dataframe(df, use_container_width=True)
        
        # Botão para salvar coordenadas
        if st.button("Salvar Coordenadas"):
            df.to_csv("coordenadas.csv", index=False)
            st.success("Coordenadas salvas com sucesso!")
            
        # Botão para limpar coordenadas
        if st.button("Limpar Coordenadas"):
            st.session_state.coordenadas = []
            st.experimental_rerun() 