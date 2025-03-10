# Backend (app.py) - FastAPI
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import fitz  # PyMuPDF
import os
import uuid
import shutil

app = FastAPI()

# Configuração CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique a origem exata
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diretório para armazenar arquivos temporários
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    # Gera um ID único para este upload
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Salva o arquivo PDF
    pdf_path = os.path.join(session_dir, file.filename)
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Converte PDF para imagens
    images_info = convert_pdf_to_images(pdf_path, session_dir)
    
    return {
        "session_id": session_id,
        "filename": file.filename,
        "pages": images_info
    }

def convert_pdf_to_images(pdf_path, output_dir, dpi=300):
    """Converte PDF em imagens de alta resolução"""
    doc = fitz.open(pdf_path)
    images_info = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Renderiza página como imagem com alta resolução
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
        
        # Salva a imagem
        image_path = os.path.join(output_dir, f"page_{page_num+1}.png")
        pix.save(image_path)
        
        # Informações sobre a imagem
        images_info.append({
            "page_num": page_num + 1,
            "width": pix.width,
            "height": pix.height,
            "path": f"/images/{os.path.basename(output_dir)}/page_{page_num+1}.png"
        })
    
    return images_info

@app.get("/images/{session_id}/{image_name}")
async def get_image(session_id: str, image_name: str):
    image_path = os.path.join(UPLOAD_DIR, session_id, image_name)
    return FileResponse(image_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)