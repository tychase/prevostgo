from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CoachBase(BaseModel):
    external_id: str
    url: Optional[str] = None
    title: Optional[str] = None
    year: Optional[int] = None
    model: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    specs: Dict[str, Any] = {}
    features: List[str] = []
    photos: List[str] = []
    seller: Dict[str, Any] = {}
    is_active: bool = True

class CoachOut(CoachBase):
    id: int
    class Config:
        from_attributes = True
