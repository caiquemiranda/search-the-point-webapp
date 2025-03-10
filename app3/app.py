import streamlit as st
import fitz  # PyMuPDF
import tempfile
import os
import io
from PIL import Image, ImageDraw
import numpy as np
from db import init_db, salvar_ponto, carregar_pontos, deletar_ponto
import base64
from streamlit.components.v1 import html

# Inicializar o banco de dados
init_db()

# Configurações do Streamlit
st.set_page_config(
    page_title="Buscador de Coordenadas PDF",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar estados
if 'temp_coords' not in st.session_state:
    st.session_state.temp_coords = None
if 'last_click' not in st.session_state:
    st.session_state.last_click = None

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
    
    return zoomed_img, location_map

def create_clickable_image(img, height=800):
    """Cria uma imagem clicável usando HTML/JavaScript"""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    html_code = f"""
        <div style="position: relative;">
            <img src="data:image/png;base64,{img_str}" 
                 style="width: 100%; cursor: crosshair; max-height: {height}px;" 
                 onclick="handleClick(event)" 
                 id="pdf_img"/>
        </div>
        <script>
            function handleClick(event) {{
                const img = event.target;
                const rect = img.getBoundingClientRect();
                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;
                const scaleX = img.naturalWidth / img.width;
                const scaleY = img.naturalHeight / img.height;
                const realX = x * scaleX;
                const realY = y * scaleY;
                
                window.parent.postMessage({{
                    type: 'streamlit:set_widget_value',
                    key: 'click_coords',
                    value: {{x: realX, y: realY}}
                }}, '*');
            }}
        </script>
    """
    return html_code

# Criar abas
tab1, tab2 = st.tabs(["Buscar Coordenadas", "Capturar Coordenadas"])

with tab1:
    st.title("Buscar Coordenadas em PDF")
    
    # Criar três colunas
    col1, col2, col3 = st.columns([2, 1, 1])
    
    # Coluna para upload do PDF
    with col1:
        uploaded_file = st.file_uploader(
            "Faça upload do arquivo PDF",
            type=['pdf'],
            help="Selecione um arquivo PDF",
            key="upload1"
        )
    
    # Coluna para inputs de coordenadas
    with col2:
        st.subheader("Coordenadas")
        
        # Adicionar seleção de coordenadas salvas
        pontos_salvos = carregar_pontos()
        if pontos_salvos:
            ponto_salvo = st.selectbox("Selecionar ponto salvo", [""] + list(pontos_salvos.keys()))
            if ponto_salvo:
                x = pontos_salvos[ponto_salvo]["x"]
                y = pontos_salvos[ponto_salvo]["y"]
                st.write(f"Coordenadas carregadas: X={x:.1f}, Y={y:.1f}")
            else:
                x = st.number_input("Coordenada X", value=0.0, step=0.1, key="x1")
                y = st.number_input("Coordenada Y", value=0.0, step=0.1, key="y1")
        else:
            x = st.number_input("Coordenada X", value=0.0, step=0.1, key="x1")
            y = st.number_input("Coordenada Y", value=0.0, step=0.1, key="y1")
        
        zoom_level = st.slider("Nível de Zoom", min_value=1, max_value=10, value=2, key="zoom1")
        buscar = st.button("Buscar Coordenadas")

with tab2:
    st.title("Capturar Coordenadas do PDF")
    
    # Criar duas colunas
    col1, col2 = st.columns([2, 1])
    
    # Coluna para upload do PDF
    with col1:
        uploaded_file2 = st.file_uploader(
            "Faça upload do arquivo PDF",
            type=['pdf'],
            help="Selecione um arquivo PDF",
            key="upload2"
        )
        
        if uploaded_file2:
            # Processar o PDF
            pdf_data = uploaded_file2.read()
            pdf_stream = io.BytesIO(pdf_data)
            doc = fitz.open(stream=pdf_stream, filetype="pdf")
            page = doc[0]
            zoom_matrix = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=zoom_matrix, alpha=False)
            
            # Converter para imagem
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_draw = ImageDraw.Draw(img)
            
            # Mostrar pontos salvos na imagem
            pontos_salvos = carregar_pontos()
            for nome, coords in pontos_salvos.items():
                y_pixel = int(pix.height - coords["y"])
                draw_point(img_draw, int(coords["x"]), y_pixel, "blue", 15)
            
            # Mostrar ponto temporário se existir
            if st.session_state.temp_coords:
                x_temp, y_temp = st.session_state.temp_coords
                y_pixel = int(pix.height - y_temp)
                draw_point(img_draw, int(x_temp), y_pixel, "red", 20)
            
            # Criar imagem clicável
            html(create_clickable_image(img), height=800)
            
            # Capturar cliques
            click_coords = st.session_state.get('click_coords')
            if click_coords and click_coords != st.session_state.last_click:
                st.session_state.temp_coords = (click_coords['x'], click_coords['y'])
                st.session_state.last_click = click_coords
                st.experimental_rerun()
            
            # Coluna para inputs
            with col2:
                st.subheader("Capturar Novo Ponto")
                if st.session_state.temp_coords:
                    x_click, y_click = st.session_state.temp_coords
                    st.write(f"Coordenadas selecionadas:")
                    st.write(f"X: {x_click:.1f}")
                    st.write(f"Y: {y_click:.1f}")
                    
                    nome_ponto = st.text_input("Nome do ponto")
                    if st.button("Salvar Ponto") and nome_ponto:
                        if salvar_ponto(nome_ponto, x_click, y_click):
                            st.success(f"Ponto '{nome_ponto}' salvo com sucesso!")
                            st.session_state.temp_coords = None
                            st.session_state.last_click = None
                            st.experimental_rerun()
                        else:
                            st.error("Nome do ponto já existe!")
                else:
                    st.info("Clique em um ponto no PDF para capturar as coordenadas")
                
                # Mostrar pontos salvos
                st.subheader("Pontos Salvos")
                for nome, coords in pontos_salvos.items():
                    col_ponto1, col_ponto2 = st.columns([3, 1])
                    with col_ponto1:
                        st.write(f"{nome}: X={coords['x']:.1f}, Y={coords['y']:.1f}")
                    with col_ponto2:
                        if st.button(f"Excluir", key=f"del_{nome}"):
                            deletar_ponto(nome)
                            st.experimental_rerun()
            
            doc.close()

# Processar PDF na aba de busca
if uploaded_file is not None and buscar:
    try:
        pdf_data = uploaded_file.read()
        pdf_stream = io.BytesIO(pdf_data)
        
        try:
            doc = fitz.open(stream=pdf_stream, filetype="pdf")
            page = doc[0]
            zoom_matrix = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=zoom_matrix, alpha=False)
            
            base_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            base_draw = ImageDraw.Draw(base_img)
            
            # Desenhar ponto vermelho nas coordenadas exatas
            y_pixel = int(pix.height - y)
            draw_point(base_draw, int(x), y_pixel, "red", 20)
            
            # Mostrar pontos salvos em azul
            pontos_salvos = carregar_pontos()
            for nome, coords in pontos_salvos.items():
                if nome != ponto_salvo:  # Não desenhar o ponto selecionado duas vezes
                    y_pixel = int(pix.height - coords["y"])
                    draw_point(base_draw, int(coords["x"]), y_pixel, "blue", 15)
            
            with tab1:
                col1.image(base_img, caption="Página do PDF com pontos", use_column_width=True)
            
            zoomed_area, location_map = get_zoomed_area(
                pix, x, y, zoom_level
            )
            
            with tab1:
                with col3:
                    st.subheader("Área Ampliada")
                    st.image(zoomed_area, caption=f"Zoom nas coordenadas (X={x}, Y={y})")
                    
                    st.subheader("Mapa de Localização")
                    st.image(location_map, caption="Área selecionada em vermelho")
            
            words = page.get_text("words")
            encontrou = False
            
            for word in words:
                if abs(word[0] - x) < 20 and abs(word[1] - y) < 20:
                    with col2:
                        st.success(f"Texto encontrado: {word[4]}")
                        st.write(f"Posição exata: X={word[0]:.1f}, Y={word[1]:.1f}")
                    encontrou = True
            
            if not encontrou:
                with col2:
                    st.warning("Nenhum texto encontrado próximo a essas coordenadas.")
            
            doc.close()
            
        except Exception as e:
            st.error(f"Erro ao processar o PDF: {str(e)}")
            st.info("Verifique se o arquivo PDF não está corrompido ou protegido.")
            
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")
        st.info("Por favor, tente novamente com outro arquivo PDF.") 