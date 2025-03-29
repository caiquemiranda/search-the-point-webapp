import fitz  # PyMuPDF
import os
import shutil
from datetime import datetime
from ..db.database import execute_db_query

# Diretório para armazenar arquivos processados
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def convert_pdf_to_images(pdf_path, output_dir, dpi=300):
    """Converte PDF em imagens de alta resolução"""
    doc = fitz.open(pdf_path)
    images_info = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Renderiza página como imagem com alta resolução
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
        
        # Salva a imagem
        image_name = f"page_{page_num+1}.png"
        image_path = os.path.join(output_dir, image_name)
        pix.save(image_path)
        
        # Informações sobre a imagem
        images_info.append({
            "page_num": page_num + 1,
            "width": pix.width,
            "height": pix.height,
            "path": f"/backend/images/{os.path.basename(output_dir)}/{image_name}"
        })
    
    return images_info

def process_pdf_upload(file, session_id):
    """Processa o upload de um arquivo PDF"""
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Salva o arquivo PDF
    pdf_path = os.path.join(session_dir, file.filename)
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Converte PDF para imagens
    images_info = convert_pdf_to_images(pdf_path, session_dir)
    
    # Salva informação da imagem no banco de dados
    thumbnail_path = f"/images/{session_id}/page_1.png"  # Usa a primeira página como thumbnail
    
    # Executa query segura para inserir imagem
    execute_db_query(
        "INSERT INTO processed_images (id, filename, upload_date, page_count, thumbnail_path) VALUES (?, ?, ?, ?, ?)",
        (session_id, file.filename, datetime.now().isoformat(), len(images_info), thumbnail_path),
        commit=True
    )
    
    return {
        "session_id": session_id,
        "filename": file.filename,
        "pages": images_info
    } 