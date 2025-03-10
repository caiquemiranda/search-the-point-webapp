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

def add_coordenada(x, y):
    if 'coordenadas' not in st.session_state:
        st.session_state.coordenadas = []
    st.session_state.coordenadas.append({'x': x, 'y': y})
    st.session_state.modified = True

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
            
            # JavaScript para captura de cliques
            st.markdown("""
            <script>
                // Função para enviar coordenadas para o Streamlit
                function sendCoordinates(x, y) {
                    const data = {
                        x: x,
                        y: y
                    };
                    
                    fetch('/', {
                        method: 'POST',
                        body: JSON.stringify(data),
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    }).then(() => {
                        window.location.reload();
                    });
                }

                // Adicionar evento de clique na imagem
                window.addEventListener('load', function() {
                    const img = document.querySelector('.stImage img');
                    if (img) {
                        img.style.cursor = 'crosshair';
                        img.onclick = function(e) {
                            const rect = this.getBoundingClientRect();
                            const x = Math.round(e.clientX - rect.left);
                            const y = Math.round(e.clientY - rect.top);
                            sendCoordinates(x, y);
                        }
                    }
                });
            </script>
            """, unsafe_allow_html=True)
            
            # Capturar coordenadas dos parâmetros da query
            params = st.query_params
            if 'x' in params and 'y' in params:
                x = int(params['x'])
                y = int(params['y'])
                add_coordenada(x, y)
                # Limpar os parâmetros
                st.query_params.clear()
            
        except Exception as e:
            st.error(f"Erro ao processar o PDF: {str(e)}")

with col2:
    st.subheader("Coordenadas Capturadas")
    
    # Exibir coordenadas capturadas
    if st.session_state.coordenadas:
        df = pd.DataFrame(st.session_state.coordenadas)
        st.write("Lista de Coordenadas:")
        for idx, coord in enumerate(st.session_state.coordenadas):
            st.write(f"{idx + 1}. X: {coord['x']}, Y: {coord['y']}")
        
        col2_1, col2_2 = st.columns(2)
        
        # Botão para salvar coordenadas
        with col2_1:
            if st.button("Salvar Coordenadas"):
                df.to_csv("coordenadas.csv", index=False)
                st.success("Coordenadas salvas com sucesso!")
        
        # Botão para limpar coordenadas
        with col2_2:
            if st.button("Limpar Coordenadas"):
                st.session_state.coordenadas = []
                st.experimental_rerun()
    else:
        st.info("Clique na imagem para capturar coordenadas") 