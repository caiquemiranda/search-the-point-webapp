from fastapi import FastAPI, HTTPException, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .db.database import init_db, execute_db_query
from .api import coordinates, images
from .services.pdf_service import process_pdf_upload
from .services.coordinate_service import get_all_coordinates, delete_coordinate, save_coordinate, get_coordinates_by_image
from .models.coordinate import CoordinateCreate
import uuid
import os

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o banco de dados
init_db()

# Inclui as rotas modulares
app.include_router(images.router, prefix="/images")
app.include_router(coordinates.router, prefix="/coordinates")

# Rotas de compatibilidade com o frontend original

@app.post("/upload-pdf/")
async def upload_pdf_compat(file: UploadFile = File(...)):
    """Compatibilidade: Upload e processamento de arquivo PDF"""
    session_id = str(uuid.uuid4())
    return process_pdf_upload(file, session_id)

@app.get("/images/{session_id}/{image_name}")
async def get_image_compat(session_id: str, image_name: str):
    """Compatibilidade: Retorna uma imagem específica"""
    image_path = f"uploads/{session_id}/{image_name}"
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    return FileResponse(image_path)

@app.get("/history")
async def get_history_compat():
    """Compatibilidade: Retorna histórico de imagens processadas"""
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

@app.get("/all-coordinates")
async def get_all_coordinates_compat():
    """Compatibilidade: Busca todas as coordenadas salvas"""
    return get_all_coordinates()

@app.get("/coordinates/{image_id}")
async def get_coordinates_compat(image_id: str):
    """Compatibilidade: Busca coordenadas salvas para uma imagem"""
    return get_coordinates_by_image(image_id)

@app.post("/coordinates/{image_id}")
async def save_coordinate_compat(image_id: str, coordinate: CoordinateCreate):
    """Compatibilidade: Salva uma coordenada para uma imagem"""
    return save_coordinate(image_id, coordinate)

@app.delete("/coordinates/{coordinate_id}")
async def delete_coordinate_compat(coordinate_id: int):
    """Compatibilidade: Remove uma coordenada salva"""
    return delete_coordinate(coordinate_id)

@app.get("/image-info/{image_id}")
async def get_image_info_compat(image_id: str):
    """Compatibilidade: Busca informações de uma imagem pelo ID"""
    image = execute_db_query(
        "SELECT * FROM processed_images WHERE id = ?",
        (image_id,),
        fetch_one=True
    )
    
    if not image:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    return {
        "id": image["id"],
        "filename": image["filename"],
        "upload_date": image["upload_date"],
        "page_count": image["page_count"],
        "thumbnail_path": image["thumbnail_path"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 