import streamlit as st
import fitz  # PyMuPDF
import tempfile
import os
import io
from PIL import Image, ImageDraw
import numpy as np

# Configurações do Streamlit
st.set_page_config(
    page_title="Buscador de Coordenadas PDF",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Buscador de Coordenadas em PDF")

# Criar três colunas
col1, col2, col3 = st.columns([2, 1, 1])

# Coluna para upload do PDF
with col1:
    uploaded_file = st.file_uploader(
        "Faça upload do arquivo PDF",
        type=['pdf'],
        help="Selecione um arquivo PDF"
    )

# Coluna para inputs de coordenadas
with col2:
    st.subheader("Coordenadas")
    x = st.number_input("Coordenada X", value=0.0, step=0.1)
    y = st.number_input("Coordenada Y", value=0.0, step=0.1)
    zoom_level = st.slider("Nível de Zoom", min_value=1, max_value=10, value=2)
    buscar = st.button("Buscar Coordenadas")

def draw_point(draw, x, y, color="red", size=10):
    """Desenha um ponto circular nas coordenadas especificadas"""
    x, y = int(x), int(y)
    draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=color)

def get_zoomed_area(pix, x, y, zoom_level):
    # Converter o pixmap para imagem PIL
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Definir o tamanho da área de zoom
    window_size = 100 * zoom_level
    
    # Calcular as coordenadas da janela de zoom
    x_pixel = int(x)
    y_pixel = int(pix.height - y)  # Inverter Y pois PDF usa coordenadas de baixo para cima
    
    # Definir os limites da área de zoom
    x_start = max(0, x_pixel - window_size//2)
    x_end = min(pix.width, x_pixel + window_size//2)
    y_start = max(0, y_pixel - window_size//2)
    y_end = min(pix.height, y_pixel + window_size//2)
    
    # Criar uma cópia da imagem original para o mapa de localização
    location_map = img.copy()
    draw = ImageDraw.Draw(location_map)
    
    # Desenhar retângulo vermelho na área de zoom
    draw.rectangle(
        [(x_start, y_start), (x_end, y_end)],
        outline="red",
        width=10
    )
    
    # Desenhar ponto vermelho nas coordenadas exatas
    draw_point(draw, x_pixel, y_pixel, "red", 20)
    
    # Redimensionar o mapa de localização para um tamanho menor
    location_map.thumbnail((500, 500), Image.Resampling.LANCZOS)
    
    # Criar uma cópia da área de zoom para adicionar o ponto
    zoomed_img = img.crop((x_start, y_start, x_end, y_end))
    zoom_draw = ImageDraw.Draw(zoomed_img)
    
    # Desenhar ponto vermelho nas coordenadas exatas na área ampliada
    relative_x = x_pixel - x_start
    relative_y = y_pixel - y_start
    draw_point(zoom_draw, relative_x, relative_y, "red", 15)
    
    # Converter para array numpy
    zoomed_area = np.array(zoomed_img)
    
    return zoomed_area, location_map, (x_start, y_start, x_end, y_end)

if uploaded_file is not None:
    try:
        # Ler o arquivo diretamente na memória
        pdf_data = uploaded_file.read()
        pdf_stream = io.BytesIO(pdf_data)
        
        try:
            # Abrir o PDF usando o stream de memória
            doc = fitz.open(stream=pdf_stream, filetype="pdf")
            page = doc[0]
            
            # Criar o pixmap com fundo branco e maior resolução
            zoom_matrix = fitz.Matrix(2, 2)  # Aumentar a resolução base
            pix = page.get_pixmap(matrix=zoom_matrix, alpha=False)
            
            # Criar imagem base com ponto para coordenadas encontradas
            base_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            base_draw = ImageDraw.Draw(base_img)
            
            # Mostrar a imagem completa na interface
            with col1:
                st.image(base_img, caption="Página do PDF", use_column_width=True)
            
            if buscar:
                st.write(f"Buscando nas coordenadas: X={x}, Y={y}")
                
                # Obter a área ampliada e o mapa de localização
                zoomed_area, location_map, (x1, y1, x2, y2) = get_zoomed_area(
                    pix, x, y, zoom_level
                )
                
                # Mostrar a área ampliada e o mapa de localização
                with col3:
                    st.subheader("Área Ampliada")
                    st.image(zoomed_area, caption=f"Zoom nas coordenadas (X={x}, Y={y})")
                    
                    st.subheader("Mapa de Localização")
                    st.image(location_map, caption="Área selecionada em vermelho")
                
                # Obter o texto próximo às coordenadas
                words = page.get_text("words")
                encontrou = False
                
                for word in words:
                    # word = (x0, y0, x1, y1, "palavra", block_no, line_no, word_no)
                    if abs(word[0] - x) < 20 and abs(word[1] - y) < 20:
                        with col2:
                            st.success(f"Texto encontrado: {word[4]}")
                            st.write(f"Posição exata: X={word[0]:.1f}, Y={word[1]:.1f}")
                        encontrou = True
                
                if not encontrou:
                    with col2:
                        st.warning("Nenhum texto encontrado próximo a essas coordenadas.")
            
            # Fechar o documento
            doc.close()
            
        except Exception as e:
            st.error(f"Erro ao processar o PDF: {str(e)}")
            st.info("Verifique se o arquivo PDF não está corrompido ou protegido.")
            
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")
        st.info("Por favor, tente novamente com outro arquivo PDF.") 