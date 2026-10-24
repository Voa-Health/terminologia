"""Cliente Python da terminologia de saúde da Voa."""

__version__ = "0.1.0a1"

from ._cliente import Terminologia
from ._erros import (
    AcessoNegadoError,
    ChaveInvalidaError,
    CotaExcedidaError,
    RedeError,
    ServidorError,
    TempoEsgotadoError,
    TerminologiaError,
)
from ._modelos import Conceito, Resultado, Validacao
from ._sistemas import SISTEMAS, Sistema, Tuss, criar_tuss, sistema, tiss_dominio

sistemas = SISTEMAS
cid10 = sistema("cid10")
ciap2 = sistema("ciap2")
tuss = criar_tuss()
sigtap = sistema("sigtap")
anvisa = sistema("anvisa")
cbo = sistema("cbo")
loinc = sistema("loinc")
ucum = sistema("ucum")

__all__ = [
    "SISTEMAS",
    "AcessoNegadoError",
    "ChaveInvalidaError",
    "Conceito",
    "CotaExcedidaError",
    "RedeError",
    "Resultado",
    "ServidorError",
    "Sistema",
    "TempoEsgotadoError",
    "Terminologia",
    "TerminologiaError",
    "Tuss",
    "Validacao",
    "__version__",
    "anvisa",
    "cbo",
    "ciap2",
    "cid10",
    "loinc",
    "sigtap",
    "sistema",
    "sistemas",
    "tiss_dominio",
    "tuss",
    "ucum",
]
