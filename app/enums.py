from enum import Enum


class FormaPagamento(str, Enum):
    PIX = "pix"
    DINHEIRO = "dinheiro"
    DEBITO = "debito"
    CREDITO = "credito"
