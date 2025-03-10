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
    zoom_level = st.slider("Nível de Zoom", min_value=1, max_value=5, value=2)
    
    # Adicionar controles de navegação
    st.subheader("Navegação")
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        move_left = st.button("⬅️")
        move_right = st.button("➡️")
    with col_nav2:
        move_up = st.button("⬆️")
        move_down = st.button("⬇️")
    
    buscar = st.button("Buscar Coordenadas")

# Inicializar variáveis de estado para navegação
if 'offset_x' not in st.session_state:
    st.session_state.offset_x = 0
if 'offset_y' not in st.session_state:
    st.session_state.offset_y = 0

# Atualizar offsets baseado nos botões de navegação
if move_left:
    st.session_state.offset_x -= 50
if move_right:
    st.session_state.offset_x += 50
if move_up:
    st.session_state.offset_y -= 50
if move_down:
    st.session_state.offset_y += 50

def get_zoomed_area(pix, x, y, zoom_level, offset_x=0, offset_y=0):
    # Converter o pixmap para imagem PIL
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Definir o tamanho da área de zoom
    window_size = 100 * zoom_level
    
    # Calcular as coordenadas da janela de zoom
    x_pixel = int(x)
    y_pixel = int(pix.height - y)  # Inverter Y pois PDF usa coordenadas de baixo para cima
    
    # Aplicar offsets
    x_pixel += offset_x
    y_pixel += offset_y
    
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
        width=5
    )
    
    # Redimensionar o mapa de localização para um tamanho menor
    location_map.thumbnail((500, 500), Image.Resampling.LANCZOS)
    
    # Extrair a área de zoom
    zoomed_area = np.array(img.crop((x_start, y_start, x_end, y_end)))
    
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
            
            # Mostrar a imagem completa na interface
            with col1:
                st.image(pix.tobytes(), caption="Página do PDF", use_column_width=True)
            
            if buscar:
                st.write(f"Buscando nas coordenadas: X={x}, Y={y}")
                
                # Obter a área ampliada e o mapa de localização
                zoomed_area, location_map, (x1, y1, x2, y2) = get_zoomed_area(
                    pix, x, y, zoom_level,
                    st.session_state.offset_x,
                    st.session_state.offset_y
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
                        st.info("Use os botões de navegação para explorar a área.")
            
            # Fechar o documento
            doc.close()
            
        except Exception as e:
            st.error(f"Erro ao processar o PDF: {str(e)}")
            st.info("Verifique se o arquivo PDF não está corrompido ou protegido.")
            
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")
        st.info("Por favor, tente novamente com outro arquivo PDF.") 