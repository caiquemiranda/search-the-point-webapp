from pydantic import BaseModel
from typing import Optional

class CoordinateCreate(BaseModel):
    name: str
    x: float
    y: float
    page: int
    source: Optional[str] = None

class Coordinate(CoordinateCreate):
    id: int
    image_id: str
    created_at: str 