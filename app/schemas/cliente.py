from pydantic import BaseModel

from app.schemas.common import NomeNormalizado


class ClienteBase(BaseModel):
    nome: NomeNormalizado


class ClienteCreate(ClienteBase):
    pass


class ClienteRead(ClienteBase):
    id: int

    model_config = {"from_attributes": True}
