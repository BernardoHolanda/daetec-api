from typing import Annotated

from pydantic import AfterValidator


def _normaliza_nome(v: str) -> str:
    v = v.strip().upper()
    if not v:
        raise ValueError("não pode ser vazio")
    return v


NomeNormalizado = Annotated[str, AfterValidator(_normaliza_nome)]
