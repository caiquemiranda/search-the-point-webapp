# Backend (app.py) - FastAPI
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import fitz  # PyMuPDF
import os
import uuid
import shutil
from typing import List, Dict, Any, Optional
import sqlite3
from pydantic import BaseModel
import json
from datetime import datetime
from contextlib import contextmanager

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diretório para armazenar arquivos processados
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Configuração do banco de dados SQLite
DB_FILE = "coordinates.db"

# Usando contextmanager para garantir conexões thread-safe
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Nova função para execução segura de queries
def execute_db_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if commit:
            conn.commit()
            return cursor.lastrowid
        
        if fetch_one:
            return cursor.fetchone()
        
        if fetch_all:
            return cursor.fetchall()
        
        return None

# Inicializar banco de dados
def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Tabela para armazenar informações sobre as imagens processadas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_images (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            page_count INTEGER NOT NULL,
            thumbnail_path TEXT
        )
        ''')
        
        # Tabela para armazenar coordenadas salvas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_coordinates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id TEXT NOT NULL,
            name TEXT NOT NULL,
            x REAL NOT NULL,
            y REAL NOT NULL,
            page INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (image_id) REFERENCES processed_images (id)
        )
        ''')
        
        conn.commit()

# Inicializa o banco de dados na inicialização do app
init_db()

# Modelos Pydantic
class CoordinateCreate(BaseModel):
    name: str
    x: float
    y: float
    page: int

class Coordinate(CoordinateCreate):
    id: int
    image_id: str
    created_at: str

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
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    return FileResponse(image_path)

@app.get("/history")
async def get_processed_images():
    """Retorna histórico de imagens processadas"""
    rows = execute_db_query(
        "SELECT * FROM processed_images ORDER BY upload_date DESC",
        fetch_all=True
    )
    
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "filename": row["filename"],
            "upload_date": row["upload_date"],
            "page_count": row["page_count"],
            "thumbnail_path": row["thumbnail_path"]
        })
    
    return result

@app.post("/coordinates/{image_id}")
async def save_coordinate(
    image_id: str, 
    coordinate: CoordinateCreate
):
    """Salva uma coordenada para uma imagem"""
    # Verifica se a imagem existe
    image = execute_db_query(
        "SELECT id FROM processed_images WHERE id = ?", 
        (image_id,),
        fetch_one=True
    )
    
    if not image:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    # Salva a coordenada
    created_at = datetime.now().isoformat()
    coord_id = execute_db_query(
        "INSERT INTO saved_coordinates (image_id, name, x, y, page, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (image_id, coordinate.name, coordinate.x, coordinate.y, coordinate.page, created_at),
        commit=True
    )
    
    # Retorna o ID da coordenada criada
    return {
        "id": coord_id,
        "image_id": image_id,
        "name": coordinate.name,
        "x": coordinate.x,
        "y": coordinate.y,
        "page": coordinate.page,
        "created_at": created_at
    }

@app.get("/coordinates/{image_id}")
async def get_coordinates(image_id: str):
    """Busca coordenadas salvas para uma imagem"""
    rows = execute_db_query(
        "SELECT * FROM saved_coordinates WHERE image_id = ? ORDER BY created_at DESC",
        (image_id,),
        fetch_all=True
    )
    
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "image_id": row["image_id"],
            "name": row["name"],
            "x": row["x"],
            "y": row["y"],
            "page": row["page"],
            "created_at": row["created_at"]
        })
    
    return result

@app.delete("/coordinates/{coordinate_id}")
async def delete_coordinate(coordinate_id: int):
    """Remove uma coordenada salva"""
    rows_affected = execute_db_query(
        "DELETE FROM saved_coordinates WHERE id = ?", 
        (coordinate_id,),
        commit=True
    )
    
    if not rows_affected:
        raise HTTPException(status_code=404, detail="Coordenada não encontrada")
    
    return {"success": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)