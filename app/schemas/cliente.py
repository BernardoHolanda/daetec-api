from pydantic import BaseModel


class ClienteBase(BaseModel):
    nome: str


class ClienteCreate(ClienteBase):
    pass


class ClienteRead(ClienteBase):
    id: int

    model_config = {"from_attributes": True}
