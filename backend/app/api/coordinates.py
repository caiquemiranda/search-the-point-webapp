from fastapi import APIRouter, HTTPException
from ..models.coordinate import CoordinateCreate
from ..services.coordinate_service import (
    get_all_coordinates,
    get_coordinates_by_image,
    save_coordinate,
    delete_coordinate
)

router = APIRouter(prefix="/coordinates", tags=["coordinates"])

@router.get("/all")
async def get_all_coordinates_route():
    """Busca todas as coordenadas salvas"""
    try:
        return await get_all_coordinates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{image_id}")
async def get_coordinates_route(image_id: str):
    """Busca coordenadas salvas para uma imagem"""
    try:
        return await get_coordinates_by_image(image_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{image_id}")
async def save_coordinate_route(image_id: str, coordinate: CoordinateCreate):
    """Salva uma coordenada para uma imagem"""
    try:
        return await save_coordinate(image_id, coordinate)
    except Exception as e:
        if "não encontrada" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{coordinate_id}")
async def delete_coordinate_route(coordinate_id: int):
    """Remove uma coordenada salva"""
    try:
        return await delete_coordinate(coordinate_id)
    except Exception as e:
        if "não encontrada" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 