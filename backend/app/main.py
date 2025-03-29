from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
import os
import uuid
import csv
from io import StringIO
from datetime import datetime
from .db.database import execute_db_query, init_db
from .services.pdf_service import convert_pdf_to_images
from .models.coordinate import CoordinateCreate

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
UPLOAD_DIR = "/app/uploads"  # Caminho absoluto no container
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Inicializa o banco de dados
init_db()

@app.get("/health")
async def health_check():
    """Endpoint para verificação de saúde da API"""
    return {
        "status": "online",
        "time": datetime.now().isoformat(),
        "service": "search-the-point-backend"
    }

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload e processamento de arquivo PDF"""
    try:
        # Gera um ID único para este upload
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(UPLOAD_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Salva o arquivo PDF
        pdf_path = os.path.join(session_dir, file.filename)
        with open(pdf_path, "wb") as buffer:
            buffer.write(await file.read())
        
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
    except Exception as e:
        print(f"Erro ao processar PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar PDF: {str(e)}")

@app.get("/images/{session_id}/{image_name}")
async def get_image(session_id: str, image_name: str):
    """Retorna uma imagem específica"""
    try:
        image_path = os.path.join(UPLOAD_DIR, session_id, image_name)
        if not os.path.exists(image_path):
            print(f"Imagem não encontrada: {image_path}")
            raise HTTPException(status_code=404, detail="Imagem não encontrada")
        return FileResponse(image_path, media_type="image/png")
    except Exception as e:
        print(f"Erro ao buscar imagem: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar imagem: {str(e)}")

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

@app.get("/all-coordinates", tags=["coordinates"])
async def get_all_coordinates():
    """Busca todas as coordenadas salvas"""
    print("Buscando todas as coordenadas...")
    try:
        rows = execute_db_query(
            """
            SELECT sc.*, pi.filename 
            FROM saved_coordinates sc
            JOIN processed_images pi ON sc.image_id = pi.id
            ORDER BY sc.created_at DESC
            """,
            fetch_all=True
        )
        
        print(f"Encontradas {len(rows) if rows else 0} coordenadas no banco de dados")
        
        result = []
        for row in rows:
            source = row["source"] if row["source"] else row["filename"]
            result.append({
                "id": row["id"],
                "image_id": row["image_id"],
                "name": row["name"],
                "x": row["x"],
                "y": row["y"],
                "page": row["page"],
                "created_at": row["created_at"],
                "source": source,
                "filename": row["filename"]
            })
        
        return result
    except Exception as e:
        print(f"Erro ao buscar todas as coordenadas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar coordenadas: {str(e)}")

@app.get("/coordinates/export/{image_id}", tags=["coordinates"])
async def export_coordinates_csv(image_id: str):
    """Exporta coordenadas para CSV"""
    # Busca as coordenadas
    rows = execute_db_query(
        "SELECT * FROM saved_coordinates WHERE image_id = ? ORDER BY created_at",
        (image_id,),
        fetch_all=True
    )
    
    # Busca informações da imagem
    image = execute_db_query(
        "SELECT filename FROM processed_images WHERE id = ?",
        (image_id,),
        fetch_one=True
    )
    
    if not image:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    # Cria arquivo CSV em memória
    output = StringIO()
    writer = csv.writer(output)
    
    # Escreve cabeçalho
    writer.writerow(["id", "nome", "x", "y", "pagina", "data_criacao", "fonte"])
    
    # Escreve dados
    for row in rows:
        source = row["source"] if row["source"] else "Desconhecido"
        writer.writerow([
            row["id"],
            row["name"],
            row["x"],
            row["y"],
            row["page"],
            row["created_at"],
            source
        ])
    
    # Prepara o arquivo para download
    output.seek(0)
    filename = f"coordenadas_{image['filename'].replace('.pdf', '')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/coordinates/{image_id}", tags=["coordinates"])
async def save_coordinate(
    image_id: str, 
    coordinate: CoordinateCreate
):
    """Salva uma coordenada para uma imagem"""
    print(f"Salvando coordenada para imagem {image_id}: {coordinate}")
    # Verifica se a imagem existe
    image = execute_db_query(
        "SELECT id, filename FROM processed_images WHERE id = ?", 
        (image_id,),
        fetch_one=True
    )
    
    if not image:
        print(f"Imagem {image_id} não encontrada no banco de dados")
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    # Se não foi fornecido um source, usa o nome do arquivo como source
    source = coordinate.source if coordinate.source else image["filename"]
    
    # Salva a coordenada
    created_at = datetime.now().isoformat()
    try:
        coord_id = execute_db_query(
            "INSERT INTO saved_coordinates (image_id, name, x, y, page, created_at, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (image_id, coordinate.name, coordinate.x, coordinate.y, coordinate.page, created_at, source),
            commit=True
        )
        print(f"Coordenada salva com sucesso, ID: {coord_id}")
        
        # Retorna o ID da coordenada criada
        return {
            "id": coord_id,
            "image_id": image_id,
            "name": coordinate.name,
            "x": coordinate.x,
            "y": coordinate.y,
            "page": coordinate.page,
            "created_at": created_at,
            "source": source
        }
    except Exception as e:
        print(f"Erro ao salvar coordenada: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar coordenada: {str(e)}")

@app.get("/coordinates/{image_id}", tags=["coordinates"])
async def get_coordinates(image_id: str):
    """Busca coordenadas salvas para uma imagem"""
    print(f"Buscando coordenadas para imagem {image_id}")
    try:
        rows = execute_db_query(
            "SELECT * FROM saved_coordinates WHERE image_id = ? ORDER BY created_at DESC",
            (image_id,),
            fetch_all=True
        )
        
        print(f"Encontradas {len(rows) if rows else 0} coordenadas para imagem {image_id}")
        
        result = []
        for row in rows:
            source = row["source"] if row["source"] else ""
            result.append({
                "id": row["id"],
                "image_id": row["image_id"],
                "name": row["name"],
                "x": row["x"],
                "y": row["y"],
                "page": row["page"],
                "created_at": row["created_at"],
                "source": source
            })
        
        return result
    except Exception as e:
        print(f"Erro ao buscar coordenadas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar coordenadas: {str(e)}")

@app.delete("/coordinates/{coordinate_id}", tags=["coordinates"])
async def delete_coordinate(coordinate_id: int):
    """Remove uma coordenada salva"""
    print(f"Removendo coordenada {coordinate_id}")
    try:
        rows_affected = execute_db_query(
            "DELETE FROM saved_coordinates WHERE id = ?", 
            (coordinate_id,),
            commit=True
        )
        
        if not rows_affected:
            print(f"Coordenada {coordinate_id} não encontrada para remoção")
            raise HTTPException(status_code=404, detail="Coordenada não encontrada")
        
        print(f"Coordenada {coordinate_id} removida com sucesso")
        return {"success": True}
    except Exception as e:
        print(f"Erro ao remover coordenada: {e}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Coordenada não encontrada")
        raise HTTPException(status_code=500, detail=f"Erro ao remover coordenada: {str(e)}")

@app.get("/image-info/{image_id}")
async def get_image_info(image_id: str):
    """Busca informações de uma imagem pelo ID"""
    print(f"Buscando informações da imagem {image_id}")
    try:
        image = execute_db_query(
            "SELECT * FROM processed_images WHERE id = ?",
            (image_id,),
            fetch_one=True
        )
        
        if not image:
            print(f"Imagem {image_id} não encontrada")
            raise HTTPException(status_code=404, detail="Imagem não encontrada")
        
        print(f"Informações da imagem {image_id} encontradas: {image['filename']}")
        return {
            "id": image["id"],
            "filename": image["filename"],
            "upload_date": image["upload_date"],
            "page_count": image["page_count"],
            "thumbnail_path": image["thumbnail_path"]
        }
    except Exception as e:
        print(f"Erro ao buscar informações da imagem: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar informações da imagem: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 