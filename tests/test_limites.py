from __future__ import annotations

import io
import json
import urllib.error

import pytest

from terminologia import CotaExcedidaError, PagamentoNecessarioError, Terminologia
from terminologia import _cliente as cliente_modulo
from terminologia.__main__ import main
from terminologia._mcp import _resultado_tool


@pytest.mark.parametrize(
    ("body", "headers", "retry_after"),
    [
        (b'{"retry_after": 120}', {}, 120),
        (b'{"retry_after": 120}', {"Retry-After": "30"}, 120),
        (b"{}", {}, None),
        (b"limite sint\xc3\xa9tico", {}, None),
        (b"\xff", {"Retry-After": "30"}, 30),
        (b"[]", {"Retry-After": "inv\xc3\xa1lido"}, None),
        (b'{"retry_after": "inv\xc3\xa1lido"}', {}, None),
        (b'{"retry_after": "abc"}', {"Retry-After": "30"}, 30),
    ],
)
def test_cota_excedida(monkeypatch, body, headers, retry_after):
    def abrir(request, **kwargs):
        raise urllib.error.HTTPError(request.full_url, 429, "", headers, io.BytesIO(body))

    monkeypatch.setattr(cliente_modulo._OPENER, "open", abrir)
    client = Terminologia(api_key="sk_user_sintetica")
    with pytest.raises(CotaExcedidaError) as erro:
        client.lookup("urn:synthetic", "X1")
    assert erro.value.status == 429
    assert erro.value.retry_after == retry_after
    assert "Cota diária compartilhada" in str(erro.value)
    assert "https://tiss-api.voa.health/org" in str(erro.value)
    if retry_after is not None:
        assert f"{retry_after} segundos" in str(erro.value)


@pytest.mark.parametrize(
    ("payload", "url"),
    [
        (
            {"metadata": {"billing_url": "https://example.org/billing"}},
            "https://example.org/billing",
        ),
        ({}, "https://tiss-api.voa.health/org"),
        ({"metadata": None}, "https://tiss-api.voa.health/org"),
        ({"metadata": {"billing_url": ""}}, "https://tiss-api.voa.health/org"),
        ({"metadata": {"billing_url": 42}}, "https://tiss-api.voa.health/org"),
        (None, "https://tiss-api.voa.health/org"),
    ],
)
def test_pagamento_necessario(monkeypatch, payload, url):
    body = (
        json.dumps({"error_name": "PAYMENT_REQUIRED", **payload}).encode()
        if payload is not None
        else b"nao JSON"
    )

    def abrir(request, **kwargs):
        raise urllib.error.HTTPError(request.full_url, 402, "", {}, io.BytesIO(body))

    monkeypatch.setattr(cliente_modulo._OPENER, "open", abrir)
    with pytest.raises(PagamentoNecessarioError) as erro:
        Terminologia(api_key="sk_voa_sintetica").lookup("urn:synthetic", "X1")
    assert erro.value.status == 402
    assert "Pagamento necessário" in str(erro.value)
    assert url in str(erro.value)


@pytest.mark.parametrize("status", [429, 402])
def test_cli_e_mcp_exibem_link_de_acesso(monkeypatch, capsys, status):
    def abrir(request, **kwargs):
        raise urllib.error.HTTPError(request.full_url, status, "", {}, io.BytesIO(b"{}"))

    monkeypatch.setattr(cliente_modulo._OPENER, "open", abrir)
    monkeypatch.setitem(
        cliente_modulo._CACHE_PADRAO, "cliente", Terminologia(api_key="sk_voa_sintetica")
    )
    assert main(["lookup", "tuss", "X1"]) == 2
    assert "https://tiss-api.voa.health/org" in capsys.readouterr().err
    result = _resultado_tool("terminologia_lookup", {"sistema": "tuss", "codigo": "X1"})
    assert result.model_dump(by_alias=True)["isError"]
    assert "https://tiss-api.voa.health/org" in result.content[0].text
