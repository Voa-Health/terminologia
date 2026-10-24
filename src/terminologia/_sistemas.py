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
    busca: bool = True
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

        if not self.busca:
            raise ValueError(f"{self.nome} não tem busca textual; use lookup ou validar.")

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


_TABELAS_TISS: dict[str, tuple[str, str]] = {
    "23": ("carater-atendimento", "caráter do atendimento"),
    "25": ("codigo-despesa", "código da despesa"),
    "26": ("conselho-profissional", "conselho profissional"),
    "27": ("debitos-creditos", "débitos e créditos"),
    "28": ("dentes", "dentes"),
    "29": ("diagnostico-imagem", "diagnóstico por imagem"),
    "30": (
        "escala-capacidade-funcional",
        "escala de capacidade funcional (ECOG - escala de Zubrod)",
    ),
    "31": ("estadiamento-tumor", "estadiamento do tumor"),
    "32": ("faces-dente", "faces do dente"),
    "33": ("finalidade-tratamento", "finalidade do tratamento"),
    "34": ("forma-pagamento", "forma de pagamento"),
    "35": ("grau-participacao", "grau de participação"),
    "36": ("indicador-acidente", "indicador de acidente"),
    "37": ("indicador-debito-credito", "indicador de débito ou crédito"),
    "38": ("mensagens", "mensagens (glosas, negativas e outras)"),
    "39": ("motivo-encerramento", "motivo de encerramento"),
    "40": ("origem-guia", "origem da guia"),
    "41": ("regime-internacao", "regime de internação"),
    "42": ("regioes-boca", "regiões da boca"),
    "43": ("sexo", "sexo"),
    "44": ("situacao-inicial-dente", "situação inicial do dente"),
    "45": ("status-solicitacao", "status da solicitação"),
    "46": ("status-cancelamento", "status do cancelamento"),
    "47": ("status-protocolo", "status do protocolo"),
    "48": ("tecnica-utilizada", "técnica utilizada"),
    "49": ("tipo-acomodacao", "tipo de acomodação"),
    "50": ("tipo-atendimento", "tipo de atendimento"),
    "51": ("tipo-atendimento-odontologia", "tipo de atendimento em odontologia"),
    "52": ("tipo-consulta", "tipo de consulta"),
    "53": ("tipo-demonstrativo", "tipo de demonstrativo"),
    "54": ("tipo-guia", "tipo de guia"),
    "55": ("tipo-faturamento", "tipo de faturamento"),
    "56": ("natureza-guia", "natureza da guia"),
    "57": ("tipo-internacao", "tipo de internação"),
    "58": ("tipo-quimioterapia", "tipo de quimioterapia"),
    "59": ("unidade-federacao", "unidade da federação"),
    "60": ("unidade-medida", "unidade de medida"),
    "61": ("via-acesso", "via de acesso"),
    "62": ("via-administracao", "via de administração"),
    "63": (
        "grupos-procedimentos-ans",
        "grupos de procedimentos e itens assistenciais para envio à ANS",
    ),
    "65": ("metastases", "metástases"),
    "66": ("nodulo", "nódulo"),
    "67": ("tumor", "tumor"),
    "68": ("categoria-despesa", "categoria de despesa"),
    "69": ("versao-componente-comunicacao", "versão do componente de comunicação do padrão"),
    "70": ("forma-envio", "forma de envio do padrão"),
    "71": (
        "tipo-atendimento-operadora-intermediaria",
        "tipo de atendimento por operadora intermediária",
    ),
    "72": ("tipo-identificacao-beneficiario", "tipo de identificação do beneficiário"),
    "73": ("etapas-autorizacao", "etapas de autorização"),
    "74": ("motivos-ausencia-codigo-validacao", "motivos de ausência do código de validação"),
    "75": ("cobertura-especial", "cobertura especial"),
    "76": ("regime-atendimento", "regime de atendimento"),
    "77": ("saude-ocupacional", "saúde ocupacional"),
    "78": ("tipo-pagamento", "tipo de pagamento"),
    "79": (
        "modelos-remuneracao",
        "modelos de remuneração entre operadoras e prestadores",
    ),
    "80": ("formato-documento", "formato do documento"),
    "81": ("tipo-documento", "tipo do documento"),
    "82": ("centro-consumo", "centro de consumo"),
    "87": ("terminologias-unificadas", "relação das terminologias unificadas na saúde suplementar"),
}

_TISS = tuple(
    Sistema(
        f"tiss-{tabela}",
        f"TISS Tabela {tabela} — {titulo}",
        f"https://voa.health/fhir/CodeSystem/tiss-{slug}",
        f"https://voa.health/fhir/ValueSet/tiss-{slug}",
    )
    for tabela, (slug, titulo) in _TABELAS_TISS.items()
)

_SIGTAP = tuple(
    Sistema(
        f"sigtap-{slug}",
        f"SIGTAP — {titulo}",
        f"https://voa.health/fhir/CodeSystem/sigtap-{slug}",
        f"https://voa.health/fhir/ValueSet/sigtap-{slug}",
    )
    for slug, titulo in (
        ("grupo", "grupos de procedimento"),
        ("sub-grupo", "subgrupos de procedimento"),
        ("servico", "serviços especializados"),
        ("registro", "instrumentos de registro"),
        ("financiamento", "tipos de financiamento"),
        ("modalidade", "modalidades de atendimento"),
    )
)

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
    *_SIGTAP,
    Sistema("anvisa", "ANVISA — produtos e apresentações", "urn:voa:anvisa:registro", None),
    Sistema(
        "cbo",
        "CBO 2002 — ocupações",
        "https://voa.health/fhir/CodeSystem/cbo",
        "https://voa.health/fhir/ValueSet/cbo",
    ),
    Sistema(
        "cfm-especialidade",
        "CFM — especialidades médicas",
        "https://voa.health/fhir/CodeSystem/cfm-especialidade",
        "https://voa.health/fhir/ValueSet/cfm-especialidades",
    ),
    Sistema(
        "rol-ans",
        "Rol de Procedimentos e Eventos em Saúde da ANS",
        "https://voa.health/fhir/CodeSystem/rol-ans",
        "https://voa.health/fhir/ValueSet/rol-ans",
    ),
    Sistema(
        "dut",
        "Rol da ANS — diretrizes de utilização (DUT)",
        "https://voa.health/fhir/CodeSystem/rol-diretrizes-dut",
        "https://voa.health/fhir/ValueSet/rol-diretrizes-dut",
    ),
    # Registros grandes: o servidor resolve por código, sem busca textual.
    Sistema("cnes", "CNES — estabelecimentos de saúde", "urn:voa:br:cnes", None, busca=False),
    Sistema(
        "ans-operadora",
        "ANS — operadoras ativas",
        "urn:voa:br:ans-registro",
        "urn:voa:br:ans-registro:todos",
        busca=False,
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
    *_TISS,
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
    if str(tabela) not in _TABELAS_TISS:
        validas = ", ".join(_TABELAS_TISS)
        raise ValueError(f"Tabela TISS desconhecida. Válidas: {validas}.")
    return _POR_NOME[f"tiss-{tabela}"]


def _serialize_sistema(item: Sistema) -> dict[str, Any]:
    return {
        "nome": item.nome,
        "rotulo": item.rotulo,
        "system": item.system,
        "value_set": item.value_set,
        "atribuicao": item.atribuicao,
        "busca": item.busca,
    }
