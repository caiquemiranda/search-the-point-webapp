from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import uuid
from ..services.pdf_service import process_pdf_upload
from ..db.database import execute_db_query
import os

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/upload-pdf/")
async def upload_pdf_route(file: UploadFile = File(...)):
    """Upload e processamento de arquivo PDF"""
    try:
        session_id = str(uuid.uuid4())
        return await process_pdf_upload(file, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/{image_name}")
async def get_image_route(session_id: str, image_name: str):
    """Retorna uma imagem específica"""
    try:
        image_path = f"uploads/{session_id}/{image_name}"
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Imagem não encontrada")
        return FileResponse(image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info/{image_id}")
async def get_image_info_route(image_id: str):
    """Busca informações de uma imagem pelo ID"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_processed_images_route():
    """Retorna histórico de imagens processadas"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 