"""Sistemas de codificação expostos pela fachada; a licença é definida pelo servidor."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._cliente import Terminologia

from ._modelos import Conceito, Resultado, Validacao

ATRIBUICAO_CIAP2 = (
    "CIAP-2 (ICPC-2) © WONCA International Classification Committee. "
    "Cite a WONCA ao exibir códigos CIAP-2."
)
ATRIBUICAO_LOINC = (
    "This material contains content from LOINC® (http://loinc.org). "
    "LOINC is copyright © Regenstrief Institute, Inc. and the LOINC Committee "
    "and is available at no cost under the license at http://loinc.org/license."
)


@dataclass(frozen=True)
class Sistema:
    """Um sistema de codificação FHIR consultável."""

    nome: str
    rotulo: str
    system: str
    value_set: str | None
    atribuicao: str | None = None
    _cliente: Terminologia | None = field(default=None, compare=False, repr=False)

    def com(self, cliente: Terminologia) -> Sistema:
        """Retorne uma cópia associada a um cliente."""
        return replace(self, _cliente=cliente)

    def _resolver_cliente(self) -> Terminologia:
        if self._cliente is not None:
            return self._cliente
        from ._cliente import padrao

        return padrao()

    def buscar(self, texto: str, n: int = 20) -> Resultado:
        """Busque conceitos pelo texto."""
        from ._cliente import _resultado_busca

        cliente = self._resolver_cliente()
        if self.value_set is not None:
            payload = cliente.expand(self.value_set, filter=texto, count=n)
            return _resultado_busca(payload)
        payload = cliente.search(texto, count=n)
        resultado = _resultado_busca(payload)
        conceitos = tuple(c for c in resultado.conceitos if c.system == self.system)
        return replace(resultado, conceitos=conceitos, total=None)

    def lookup(self, codigo: str) -> Conceito | None:
        """Consulte um código e retorne None quando não existir."""
        from ._cliente import _conceito_parameters
        from ._erros import TerminologiaError

        cliente = self._resolver_cliente()
        try:
            payload = cliente.lookup(self.system, codigo)
        except TerminologiaError as exc:
            if exc.status == 404 and exc.codigo == "not-found":
                return None
            raise
        return _conceito_parameters(payload)

    def validar(self, codigo: str) -> Validacao:
        """Valide um código e retorne seu display oficial quando disponível."""
        from ._cliente import _validacao_parameters

        cliente = self._resolver_cliente()
        if self.value_set is not None:
            payload = cliente.validate_code(
                codigo,
                system=self.system,
                value_set=self.value_set,
            )
        else:
            payload = cliente.validate_code(codigo, system=self.system)
        return _validacao_parameters(payload)


SISTEMAS: tuple[Sistema, ...] = (
    Sistema(
        "cid10",
        "CID-10 — variante brasileira",
        "http://hl7.org/fhir/sid/icd-10",
        "https://voa.health/fhir/ValueSet/cid10-br",
    ),
    Sistema(
        "ciap2",
        "CIAP-2 — Classificação Internacional de Atenção Primária",
        "http://hl7.org/fhir/sid/icpc-2",
        "https://voa.health/fhir/ValueSet/ciap2-br",
        ATRIBUICAO_CIAP2,
    ),
    Sistema(
        "tuss",
        "TUSS Tabela 22 — procedimentos",
        "https://voa.health/fhir/CodeSystem/tuss",
        "https://voa.health/fhir/ValueSet/tuss-tabela-22",
    ),
    Sistema(
        "tuss-diarias",
        "TUSS Tabela 18 — diárias, taxas e gases medicinais",
        "https://voa.health/fhir/CodeSystem/tuss-diarias-taxas-gases-medicinais",
        "https://voa.health/fhir/ValueSet/tuss-diarias-taxas-gases-medicinais",
    ),
    Sistema(
        "tuss-materiais",
        "TUSS Tabela 19 — materiais e OPME",
        "https://voa.health/fhir/CodeSystem/tuss-materiais-opme",
        "https://voa.health/fhir/ValueSet/tuss-materiais-opme",
    ),
    Sistema(
        "tuss-medicamentos",
        "TUSS Tabela 20 — medicamentos",
        "https://voa.health/fhir/CodeSystem/tuss-medicamentos",
        "https://voa.health/fhir/ValueSet/tuss-medicamentos",
    ),
    Sistema(
        "sigtap",
        "SIGTAP — procedimentos do SUS",
        "https://voa.health/fhir/CodeSystem/sigtap",
        "https://voa.health/fhir/ValueSet/sigtap",
    ),
    Sistema("anvisa", "ANVISA — produtos e apresentações", "urn:voa:anvisa:registro", None),
    Sistema(
        "cbo",
        "CBO 2002 — ocupações",
        "https://voa.health/fhir/CodeSystem/cbo",
        "https://voa.health/fhir/ValueSet/cbo",
    ),
    Sistema(
        "loinc",
        "LOINC — exames e observações",
        "http://loinc.org",
        "http://loinc.org/vs",
        ATRIBUICAO_LOINC,
    ),
    Sistema(
        "ucum",
        "UCUM — unidades de medida",
        "http://unitsofmeasure.org",
        "https://voa.health/fhir/ValueSet/voa-unidades-de-medida",
    ),
    Sistema(
        "tiss-50",
        "TISS Tabela 50 — tipo de atendimento",
        "https://voa.health/fhir/CodeSystem/tiss-tipo-atendimento",
        "https://voa.health/fhir/ValueSet/tiss-tipo-atendimento",
    ),
    Sistema(
        "tiss-52",
        "TISS Tabela 52 — tipo de consulta",
        "https://voa.health/fhir/CodeSystem/tiss-tipo-consulta",
        "https://voa.health/fhir/ValueSet/tiss-tipo-consulta",
    ),
    Sistema(
        "tiss-60",
        "TISS Tabela 60 — unidade de medida",
        "https://voa.health/fhir/CodeSystem/tiss-unidade-medida",
        "https://voa.health/fhir/ValueSet/tiss-unidade-medida",
    ),
    Sistema(
        "tiss-76",
        "TISS Tabela 76 — regime de atendimento",
        "https://voa.health/fhir/CodeSystem/tiss-regime-atendimento",
        "https://voa.health/fhir/ValueSet/tiss-regime-atendimento",
    ),
    Sistema(
        "voa-categoria",
        "Voa — categoria de serviço",
        "https://voa.health/fhir/CodeSystem/voa-categoria-servico",
        "https://voa.health/fhir/ValueSet/voa-categoria-servico",
    ),
)

_POR_NOME = {item.nome: item for item in SISTEMAS}
_POR_CANONICO = {
    canonical: item
    for item in SISTEMAS
    for canonical in (item.system, item.value_set)
    if canonical is not None
}


def sistema(nome_ou_url: str) -> Sistema:
    """Encontre um sistema pelo nome ou URL canônico."""
    result = _POR_NOME.get(nome_ou_url) or _POR_CANONICO.get(nome_ou_url)
    if result is None:
        nomes = ", ".join(_POR_NOME)
        raise ValueError(f"Sistema desconhecido: {nome_ou_url}. Válidos: {nomes}")
    return result


@dataclass(frozen=True)
class Tuss(Sistema):
    """TUSS Tabela 22 com atalhos tipados para suas tabelas correlatas."""

    materiais: Sistema = field(default_factory=lambda: _POR_NOME["tuss-materiais"])
    medicamentos: Sistema = field(default_factory=lambda: _POR_NOME["tuss-medicamentos"])
    diarias: Sistema = field(default_factory=lambda: _POR_NOME["tuss-diarias"])

    def com(self, cliente: Terminologia) -> Tuss:
        """Associe o cliente também às tabelas correlatas."""
        return replace(
            self,
            _cliente=cliente,
            materiais=self.materiais.com(cliente),
            medicamentos=self.medicamentos.com(cliente),
            diarias=self.diarias.com(cliente),
        )


def criar_tuss(cliente: Terminologia | None = None) -> Tuss:
    """Monte o atalho TUSS e suas tabelas correlatas."""
    base = _POR_NOME["tuss"]
    result = Tuss(
        nome=base.nome,
        rotulo=base.rotulo,
        system=base.system,
        value_set=base.value_set,
        atribuicao=base.atribuicao,
        materiais=_POR_NOME["tuss-materiais"],
        medicamentos=_POR_NOME["tuss-medicamentos"],
        diarias=_POR_NOME["tuss-diarias"],
    )
    return result.com(cliente) if cliente is not None else result


def tiss_dominio(tabela: str | int) -> Sistema:
    """Encontre um domínio TISS pelo número da tabela."""
    name = f"tiss-{tabela}"
    if name not in {"tiss-50", "tiss-52", "tiss-60", "tiss-76"}:
        raise ValueError("Tabela TISS desconhecida. Válidas: 50, 52, 60, 76.")
    return _POR_NOME[name]


def _serialize_sistema(item: Sistema) -> dict[str, Any]:
    return {
        "nome": item.nome,
        "rotulo": item.rotulo,
        "system": item.system,
        "value_set": item.value_set,
        "atribuicao": item.atribuicao,
    }
