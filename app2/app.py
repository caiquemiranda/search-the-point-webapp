import streamlit as st
import fitz  # PyMuPDF
import tempfile
import os

st.set_page_config(page_title="Buscador de Coordenadas PDF", layout="wide")

st.title("Buscador de Coordenadas em PDF")

# Criar duas colunas
col1, col2 = st.columns([2, 1])

# Coluna para upload do PDF
with col1:
    uploaded_file = st.file_uploader("Faça upload do arquivo PDF", type=['pdf'])
    
# Coluna para inputs de coordenadas
with col2:
    st.subheader("Coordenadas")
    x = st.number_input("Coordenada X", value=0.0, step=0.1)
    y = st.number_input("Coordenada Y", value=0.0, step=0.1)
    buscar = st.button("Buscar Coordenadas")

if uploaded_file is not None:
    # Criar arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        # Abrir o PDF
        doc = fitz.open(tmp_path)
        
        # Mostrar a primeira página do PDF
        page = doc[0]
        pix = page.get_pixmap()
        
        # Salvar a imagem temporariamente
        temp_img_path = "temp_page.png"
        pix.save(temp_img_path)
        
        # Mostrar a imagem na interface
        with col1:
            st.image(temp_img_path, caption="Página do PDF", use_column_width=True)
        
        if buscar:
            # Aqui você pode implementar a lógica para buscar nas coordenadas
            st.write(f"Buscando nas coordenadas: X={x}, Y={y}")
            
            # Exemplo de como obter o conteúdo próximo às coordenadas
            words = page.get_text("words")
            for word in words:
                # word = (x0, y0, x1, y1, "palavra", block_no, line_no, word_no)
                if abs(word[0] - x) < 20 and abs(word[1] - y) < 20:
                    st.success(f"Encontrado texto próximo às coordenadas: {word[4]}")
        
        # Limpar arquivos temporários
        doc.close()
        os.remove(tmp_path)
        os.remove(temp_img_path)
        
    except Exception as e:
        st.error(f"Erro ao processar o PDF: {str(e)}") 