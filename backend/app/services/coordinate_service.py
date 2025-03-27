from datetime import datetime
from ..db.database import execute_db_query
from ..models.coordinate import CoordinateCreate

def get_all_coordinates():
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
        raise Exception(f"Erro ao buscar coordenadas: {str(e)}")

def get_coordinates_by_image(image_id: str):
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
        raise Exception(f"Erro ao buscar coordenadas: {str(e)}")

def save_coordinate(image_id: str, coordinate: CoordinateCreate):
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
        raise Exception("Imagem não encontrada")
    
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
        raise Exception(f"Erro ao salvar coordenada: {str(e)}")

def delete_coordinate(coordinate_id: int):
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
            raise Exception("Coordenada não encontrada")
        
        print(f"Coordenada {coordinate_id} removida com sucesso")
        return {"success": True}
    except Exception as e:
        print(f"Erro ao remover coordenada: {e}")
        raise Exception(f"Erro ao remover coordenada: {str(e)}") 