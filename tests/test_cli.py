from __future__ import annotations

import json

import terminologia
import terminologia._cliente as cliente_modulo
from terminologia import Terminologia
from terminologia.__main__ import main


def test_cli_sistemas_json(capsys):
    assert main(["sistemas", "--json"]) == 0
    assert len(json.loads(capsys.readouterr().out)) == 16


def test_cli_busca_e_json(servidor, capsys):
    servidor.respostas["ValueSet/$expand"] = {
        "corpo": {
            "resourceType": "ValueSet",
            "expansion": {
                "total": 1,
                "contains": [
                    {"system": "urn:synthetic", "code": "X1", "display": "Exemplo sintético"}
                ],
            },
        }
    }
    previous = cliente_modulo._CACHE_PADRAO["cliente"]
    cliente_modulo._CACHE_PADRAO["cliente"] = Terminologia(
        api_key="sk_voa_teste",
        base_url=servidor.url,
    )
    try:
        assert main(["buscar", "cid10", "exemplo"]) == 0
        assert capsys.readouterr().out == "X1  Exemplo sintético\n"
        assert main(["buscar", "cid10", "exemplo", "--json"]) == 0
        result = json.loads(capsys.readouterr().out)
        assert result["conceitos"][0]["code"] == "X1"
    finally:
        cliente_modulo._CACHE_PADRAO["cliente"] = previous


def test_cli_exit_codes_e_erros(servidor, capsys):
    cliente_modulo._CACHE_PADRAO["cliente"] = Terminologia(
        api_key="sk_voa_teste",
        base_url=servidor.url,
    )
    servidor.respostas["ValueSet/$expand"] = {
        "corpo": {"resourceType": "ValueSet", "expansion": {"contains": []}}
    }
    servidor.respostas["ValueSet/$validate-code"] = {
        "corpo": {
            "resourceType": "Parameters",
            "parameter": [
                {"name": "result", "valueBoolean": False},
                {"name": "message", "valueString": "Código inválido"},
            ],
        }
    }
    servidor.respostas["CodeSystem/$voa-search"] = {
        "corpo": {
            "resourceType": "Parameters",
            "parameter": [{"name": "search-unavailable", "valueBoolean": True}],
        }
    }
    try:
        assert main(["buscar", "cid10", "sem resultado"]) == 1
        assert main(["validar", "tuss", "não-existe"]) == 1
        assert "inválido:" in capsys.readouterr().out
        assert main(["buscar", "sistema-invalido", "x"]) == 2
        assert "Sistema desconhecido" in capsys.readouterr().err
        assert main(["buscar", "anvisa", "x"]) == 2
        assert "search-unavailable" in capsys.readouterr().err
        servidor.respostas["ValueSet/$expand"] = {
            "status": 401,
            "corpo": {"detail": "Chave inválida"},
        }
        assert main(["buscar", "cid10", "x"]) == 2
        assert "https://tiss-api.voa.health/org" in capsys.readouterr().err
    finally:
        cliente_modulo._reset_padrao()


def test_cli_traduzir_exige_para_sem_request(servidor, capsys):
    previous = cliente_modulo._CACHE_PADRAO["cliente"]
    cliente_modulo._CACHE_PADRAO["cliente"] = Terminologia(
        api_key="sk_voa_teste",
        base_url=servidor.url,
    )
    try:
        assert main(["traduzir", "cid10", "I20"]) == 2
        assert "--para SISTEMA" in capsys.readouterr().err
        assert servidor.requisicoes == []
    finally:
        cliente_modulo._CACHE_PADRAO["cliente"] = previous


def test_cli_traduzir_normaliza_cid10_e_envia_targetsystem(servidor):
    servidor.respostas["ConceptMap/$translate"] = {
        "corpo": {
            "resourceType": "Parameters",
            "parameter": [{"name": "result", "valueBoolean": True}],
        }
    }
    previous = cliente_modulo._CACHE_PADRAO["cliente"]
    cliente_modulo._CACHE_PADRAO["cliente"] = Terminologia(
        api_key="sk_voa_teste",
        base_url=servidor.url,
    )
    try:
        assert main(["traduzir", "cid10", " I20.0 ", "--para", "ciap2"]) == 0
        query = servidor.requisicoes[0]["query"]
        assert query["code"] == ["I200"]
        assert query["targetsystem"] == [terminologia.ciap2.system]
    finally:
        cliente_modulo._CACHE_PADRAO["cliente"] = previous
