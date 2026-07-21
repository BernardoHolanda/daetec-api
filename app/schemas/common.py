from typing import Annotated

from pydantic import AfterValidator


def _normaliza_nome(v: str) -> str:
    v = v.strip().upper()
    if not v:
        raise ValueError("não pode ser vazio")
    return v


NomeNormalizado = Annotated[str, AfterValidator(_normaliza_nome)]


def _valida_senha(v: str) -> str:
    if len(v) < 8:
        raise ValueError("deve ter ao menos 8 caracteres")
    if not any(c.isdigit() for c in v):
        raise ValueError("deve ter ao menos um número")
    if not any(c.isupper() for c in v):
        raise ValueError("deve ter ao menos uma letra maiúscula")
    return v


SenhaForte = Annotated[str, AfterValidator(_valida_senha)]
