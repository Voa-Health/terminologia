from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import terminologia
from terminologia import (
    AcessoNegadoError,
    ChaveInvalidaError,
    CotaExcedidaError,
    RedeError,
    TempoEsgotadoError,
    Terminologia,
    sistema,
    tiss_dominio,
    tuss,
)

PARAMETERS_VALID = {
    "resourceType": "Parameters",
    "parameter": [
        {"name": "result", "valueBoolean": True},
        {"name": "code", "valueCode": "10101012"},
        {"name": "system", "valueUri": "https://voa.health/fhir/CodeSystem/tuss"},
        {"name": "display", "valueString": "Consulta"},
        {"name": "version", "valueString": "2025"},
    ],
}


def _configurar(servidor: Any, path: str, body: dict[str, Any]) -> None:
    servidor.respostas[path] = {"corpo": body}


@pytest.mark.parametrize(
    ("call", "path", "query"),
    [
        (
            lambda client: client.expand("https://example.test/vs"),
            "ValueSet/$expand",
            {"url": "https://example.test/vs"},
        ),
        (
            lambda client: client.lookup("urn:example", "x"),
            "CodeSystem/$lookup",
            {"system": "urn:example", "code": "x"},
        ),
        (
            lambda client: client.validate_code("x", value_set="https://example.test/vs"),
            "ValueSet/$validate-code",
            {"url": "https://example.test/vs", "code": "x"},
        ),
        (
            lambda client: client.translate("urn:example", "x"),
            "ConceptMap/$translate",
            {"system": "urn:example", "code": "x"},
        ),
        (
            lambda client: client.translate("urn:example", "x", target_system="urn:target"),
            "ConceptMap/$translate",
            {"system": "urn:example", "code": "x", "targetsystem": "urn:target"},
        ),
        (
            lambda client: client.subsumes("urn:example", "a", "b"),
            "CodeSystem/$subsumes",
            {"system": "urn:example", "codeA": "a", "codeB": "b"},
        ),
        (
            lambda client: client.search("texto"),
            "CodeSystem/$voa-search",
            {"filter": "texto"},
        ),
    ],
)
def test_metodos_crus_montam_consulta(cliente, servidor, call, path, query):
    call(cliente)

    request = servidor.requisicoes[0]
    assert request["path"] == f"/{path}"
    assert request["query"] == {key: [value] for key, value in query.items()}
    assert request["headers"]["Authorization"] == "Bearer sk_voa_teste"
    assert request["headers"]["Accept"] == "application/fhir+json, application/json;q=0.9"
    assert request["headers"]["User-Agent"] == f"terminologia/{terminologia.__version__}"
    assert request["headers"]["X-Client"] == f"terminologia/{terminologia.__version__}"
    assert "semantic" not in request["query"]


def test_url_base_respeita_argumento_ambiente_e_padrao(monkeypatch):
    monkeypatch.delenv("TERMINOLOGIA_URL", raising=False)
    assert Terminologia().base_url == "https://terminologia.voa.health/api/v2/terminology/fhir"

    monkeypatch.setenv("TERMINOLOGIA_URL", "https://env.example/fhir/")
    assert Terminologia().base_url == "https://env.example/fhir"
    assert Terminologia(base_url="https://arg.example/fhir/").base_url == "https://arg.example/fhir"


def test_cid10_normaliza_pontos_e_espacos(servidor):
    _configurar(
        servidor,
        "CodeSystem/$lookup",
        {
            "resourceType": "Parameters",
            "parameter": [
                {"name": "system", "valueUri": terminologia.cid10.system},
                {"name": "code", "valueCode": "I200"},
                {"name": "display", "valueString": "Angina instável sintética"},
            ],
        },
    )
    _configurar(
        servidor,
        "ValueSet/$validate-code",
        {
            "resourceType": "Parameters",
            "parameter": [
                {"name": "result", "valueBoolean": True},
                {"name": "code", "valueCode": "I200"},
                {"name": "system", "valueUri": terminologia.cid10.system},
            ],
        },
    )
    sistema_cid10 = terminologia.cid10.com(
        Terminologia(api_key="sk_voa_teste", base_url=servidor.url)
    )

    assert sistema_cid10.lookup(" I20.0 ").code == "I200"
    assert sistema_cid10.validar(" I20.0 ").valido
    assert servidor.requisicoes[0]["query"]["code"] == ["I200"]
    assert servidor.requisicoes[1]["query"]["code"] == ["I200"]


@pytest.mark.parametrize(
    ("call", "path", "query"),
    [
        (
            lambda client: terminologia.cid10.com(client).buscar("sintoma"),
            "/ValueSet/$expand",
            {
                "url": ["https://voa.health/fhir/ValueSet/cid10-br"],
                "filter": ["sintoma"],
                "count": ["20"],
            },
        ),
        (
            lambda client: tuss.com(client).lookup("10101012"),
            "/CodeSystem/$lookup",
            {"system": ["https://voa.health/fhir/CodeSystem/tuss"], "code": ["10101012"]},
        ),
        (
            lambda client: tuss.com(client).validar("10101012"),
            "/ValueSet/$validate-code",
            {
                "url": ["https://voa.health/fhir/ValueSet/tuss-tabela-22"],
                "code": ["10101012"],
                "system": ["https://voa.health/fhir/CodeSystem/tuss"],
            },
        ),
        (
            lambda client: terminologia.anvisa.com(client).buscar("medicamento"),
            "/CodeSystem/$voa-search",
            {"filter": ["medicamento"], "count": ["20"]},
        ),
        (
            lambda client: tuss.materiais.com(client).buscar("material"),
            "/ValueSet/$expand",
            {
                "url": ["https://voa.health/fhir/ValueSet/tuss-materiais-opme"],
                "filter": ["material"],
                "count": ["20"],
            },
        ),
        (
            lambda client: tiss_dominio(52).com(client).validar("1"),
            "/ValueSet/$validate-code",
            {
                "url": ["https://voa.health/fhir/ValueSet/tiss-tipo-consulta"],
                "code": ["1"],
                "system": ["https://voa.health/fhir/CodeSystem/tiss-tipo-consulta"],
            },
        ),
        (
            lambda client: sistema("cnes").com(client).lookup("0000000"),
            "/CodeSystem/$lookup",
            {"system": ["urn:voa:br:cnes"], "code": ["0000000"]},
        ),
        (
            lambda client: sistema("cnes").com(client).validar("0000000"),
            "/ValueSet/$validate-code",
            {
                "url": ["urn:voa:br:cnes:todos"],
                "code": ["0000000"],
                "system": ["urn:voa:br:cnes"],
            },
        ),
        (
            lambda client: sistema("cnes").com(client).buscar("hospital exemplo", n=5),
            "/ValueSet/$expand",
            {"url": ["urn:voa:br:cnes:todos"], "filter": ["hospital exemplo"], "count": ["5"]},
        ),
        (
            lambda client: sistema("ans-operadora").com(client).buscar("operadora exemplo"),
            "/ValueSet/$expand",
            {
                "url": ["urn:voa:br:ans-registro:todos"],
                "filter": ["operadora exemplo"],
                "count": ["20"],
            },
        ),
        (
            lambda client: sistema("ans-operadora").com(client).validar("000000"),
            "/ValueSet/$validate-code",
            {
                "url": ["urn:voa:br:ans-registro:todos"],
                "code": ["000000"],
                "system": ["urn:voa:br:ans-registro"],
            },
        ),
    ],
)
def test_atalhos_usam_sistema_e_endpoint_canonicos(servidor, call, path, query):
    cliente = Terminologia(api_key="sk_voa_teste", base_url=servidor.url)
    servidor.respostas[path.removeprefix("/")] = {"corpo": PARAMETERS_VALID}
    call(cliente)
    assert servidor.requisicoes[0]["path"] == path
    assert servidor.requisicoes[0]["query"] == query


def test_anvisa_busca_no_indice_e_filtra_sistema(servidor):
    servidor.respostas["CodeSystem/$voa-search"] = {
        "corpo": {
            "resourceType": "Parameters",
            "parameter": [
                {
                    "name": "match",
                    "part": [
                        {
                            "name": "concept",
                            "valueCoding": {
                                "system": "urn:voa:anvisa:registro",
                                "code": "123",
                                "display": "Produto sintético",
                            },
                        }
                    ],
                },
                {
                    "name": "match",
                    "part": [
                        {
                            "name": "concept",
                            "valueCoding": {
                                "system": "urn:other",
                                "code": "456",
                                "display": "Outro",
                            },
                        }
                    ],
                },
            ],
        }
    }
    result = terminologia.anvisa.com(
        Terminologia(api_key="sk_voa_teste", base_url=servidor.url)
    ).buscar("produto")
    assert [concept.code for concept in result] == ["123"]
    assert result.total is None
    assert servidor.requisicoes[0]["path"] == "/CodeSystem/$voa-search"


def test_parse_coding_raw_marcadores_e_total_parcial(servidor):
    server_result = {
        "resourceType": "ValueSet",
        "expansion": {
            "total": 4,
            "parameter": [
                {"name": "semantic-degraded", "valueBoolean": True},
                {"name": "lexical-degraded", "valueBoolean": True},
                {"name": "search-unavailable", "valueBoolean": True},
                {"name": "total-partial", "valueBoolean": True},
            ],
            "contains": [
                {"system": "urn:sample", "code": "A", "display": "Conceito", "version": "v1"}
            ],
        },
    }
    servidor.respostas["ValueSet/$expand"] = {"corpo": server_result}
    result = terminologia.cid10.com(
        Terminologia(api_key="sk_voa_teste", base_url=servidor.url)
    ).buscar("amostra")
    assert result.degradado == {
        "semantic-degraded",
        "lexical-degraded",
        "search-unavailable",
    }
    assert result.total_parcial is True
    assert result.total == 4
    assert result.conceitos[0].coding() == {
        "system": "urn:sample",
        "code": "A",
        "display": "Conceito",
        "version": "v1",
    }
    assert result.conceitos[0].raw == server_result["expansion"]["contains"][0]


def test_parse_validacao_e_lookups(servidor):
    servidor.respostas["CodeSystem/$lookup"] = {"corpo": PARAMETERS_VALID}
    servidor.respostas["ValueSet/$validate-code"] = {"corpo": PARAMETERS_VALID}
    client = Terminologia(api_key="sk_voa_teste", base_url=servidor.url)
    concept = client.sistema("tuss").lookup("10101012")
    valid = client.sistema("tuss").validar("10101012")
    assert concept is not None
    assert concept.display == "Consulta"
    assert concept.version == "2025"
    assert bool(valid)
    assert valid.conceito == concept


def test_lookup_retorna_none_em_not_found(servidor):
    servidor.respostas["CodeSystem/$lookup"] = {
        "status": 404,
        "corpo": {
            "resourceType": "OperationOutcome",
            "issue": [{"code": "not-found", "diagnostics": "Código ausente"}],
        },
    }
    client = Terminologia(api_key="sk_voa_teste", base_url=servidor.url)
    assert client.sistema("tuss").lookup("ausente") is None


@pytest.mark.parametrize(
    "case",
    [
        (
            401,
            {"error_code": "invalid_credential", "detail": "Chave inválida"},
            {},
            ChaveInvalidaError,
            "Chave inválida",
            "invalid_credential",
        ),
        (
            403,
            {
                "issue": [
                    {
                        "code": "license-restricted",
                        "diagnostics": "Sistema não permitido",
                    }
                ]
            },
            {},
            AcessoNegadoError,
            "Sistema não permitido",
            "license-restricted",
        ),
        (
            429,
            {"issue": [{"code": "too-costly", "diagnostics": "Cota excedida"}]},
            {"Retry-After": "30"},
            CotaExcedidaError,
            "Cota excedida",
            "too-costly",
        ),
    ],
)
def test_erros_http(servidor, case):
    status, body, headers, error, message, code = case
    servidor.respostas["CodeSystem/$lookup"] = {
        "status": status,
        "corpo": body,
        "headers": headers,
    }
    client = Terminologia(api_key="sk_voa_teste", base_url=servidor.url)
    with pytest.raises(error) as exc:
        client.lookup("urn:sample", "x")
    assert message in exc.value.mensagem
    assert exc.value.codigo == code
    if status in {401, 403}:
        assert "https://tiss-api.voa.health/org" in exc.value.mensagem
    if status == 429:
        assert exc.value.retry_after == 30


def test_chave_ausente_na_primeira_chamada(monkeypatch, servidor):
    monkeypatch.delenv("TERMINOLOGIA_KEY", raising=False)
    client = Terminologia(base_url=servidor.url)
    assert terminologia.SISTEMAS
    with pytest.raises(ChaveInvalidaError):
        client.search("texto")
    assert servidor.requisicoes == []


def test_timeout_e_conexao_recusada(servidor):
    servidor.respostas["CodeSystem/$voa-search"] = {
        "atraso": 0.7,
        "corpo": {"resourceType": "Parameters", "parameter": []},
    }
    client = Terminologia(api_key="sk_voa_teste", base_url=servidor.url, timeout=0.05)
    with pytest.raises(TempoEsgotadoError):
        client.search("lento")
    client = Terminologia(api_key="sk_voa_teste", base_url="http://127.0.0.1:1", timeout=0.5)
    with pytest.raises(RedeError):
        client.search("offline")


def test_cache_lru_reutiliza_respostas_200(servidor):
    servidor.respostas["CodeSystem/$voa-search"] = {
        "corpo": {"resourceType": "Parameters", "parameter": []}
    }
    client = Terminologia(api_key="sk_voa_teste", base_url=servidor.url)
    client.search("amostra")
    client.search("amostra")
    assert len(servidor.requisicoes) == 1


def test_sistemas_snapshot_e_aliases():
    snapshot = json.loads((Path(__file__).parent / "servidos.json").read_text(encoding="utf-8"))
    assert {(row["system"], row["value_set"]) for row in snapshot} == {
        (item.system, item.value_set) for item in terminologia.SISTEMAS
    }
    assert terminologia.sistemas is terminologia.SISTEMAS
    assert sistema("https://voa.health/fhir/ValueSet/cid10-br").nome == "cid10"
    assert tuss.materiais.nome == "tuss-materiais"
    assert tuss.medicamentos.nome == "tuss-medicamentos"
    assert tuss.diarias.nome == "tuss-diarias"
    assert terminologia.Tuss
    assert sistema("cid10").com(Terminologia(api_key="sk_voa_teste"))._cliente is not None
    with pytest.raises(ValueError, match="Válidos"):
        sistema("inexistente")
    with pytest.raises(ValueError, match="Válidas: 23, 25"):
        tiss_dominio(24)


@pytest.mark.parametrize(
    ("nome", "system", "value_set"),
    [
        (
            "tiss-38",
            "https://voa.health/fhir/CodeSystem/tiss-mensagens",
            "https://voa.health/fhir/ValueSet/tiss-mensagens",
        ),
        (
            "tiss-23",
            "https://voa.health/fhir/CodeSystem/tiss-carater-atendimento",
            "https://voa.health/fhir/ValueSet/tiss-carater-atendimento",
        ),
        ("cnes", "urn:voa:br:cnes", "urn:voa:br:cnes:todos"),
        ("ans-operadora", "urn:voa:br:ans-registro", "urn:voa:br:ans-registro:todos"),
        (
            "rol-ans",
            "https://voa.health/fhir/CodeSystem/rol-ans",
            "https://voa.health/fhir/ValueSet/rol-ans",
        ),
        (
            "dut",
            "https://voa.health/fhir/CodeSystem/rol-diretrizes-dut",
            "https://voa.health/fhir/ValueSet/rol-diretrizes-dut",
        ),
        (
            "cfm-especialidade",
            "https://voa.health/fhir/CodeSystem/cfm-especialidade",
            "https://voa.health/fhir/ValueSet/cfm-especialidades",
        ),
        (
            "sigtap-sub-grupo",
            "https://voa.health/fhir/CodeSystem/sigtap-sub-grupo",
            "https://voa.health/fhir/ValueSet/sigtap-sub-grupo",
        ),
    ],
)
def test_sistema_resolve_nome_e_canonicos(nome, system, value_set):
    item = sistema(nome)
    assert (item.system, item.value_set) == (system, value_set)
    assert sistema(system) is item
    if value_set is not None:
        assert sistema(value_set) is item


def test_tiss_dominio_aceita_numero_e_texto():
    assert tiss_dominio(38) is tiss_dominio("38") is sistema("tiss-38")
