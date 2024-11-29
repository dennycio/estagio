from pydantic import BaseModel

# Modelo de exemplo
class Item(BaseModel):
    name: str
    description: str
    price: float
    on_offer: bool
