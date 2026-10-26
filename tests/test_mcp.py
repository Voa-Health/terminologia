from __future__ import annotations

import json

from terminologia import SISTEMAS, _mcp
from terminologia._mcp import TOOLS, _resultado_tool, criar_servidor


def test_tools_mcp_tem_os_nomes_exatos():
    assert [tool.name for tool in TOOLS] == [
        "terminologia_buscar",
        "terminologia_lookup",
        "terminologia_validar",
        "terminologia_traduzir",
        "terminologia_sistemas",
    ]
    assert all(
        tool.model_dump(by_alias=True)["inputSchema"]["properties"].get("sistema", {}).get("enum")
        for tool in TOOLS[:4]
    )


def test_criar_servidor():
    assert criar_servidor() is not None


def test_tool_mcp_retorna_erro_com_link_de_chaves(monkeypatch):
    monkeypatch.delenv("TERMINOLOGIA_KEY", raising=False)
    result = _resultado_tool(
        "terminologia_lookup",
        {"sistema": "tuss", "codigo": "10101012"},
    )
    assert result.model_dump(by_alias=True)["isError"]
    assert "https://tiss-api.voa.health/org" in result.content[0].text


def test_tool_sistemas_responde_com_json():
    result = _resultado_tool("terminologia_sistemas", {})
    assert not result.model_dump(by_alias=True)["isError"]
    assert len(json.loads(result.content[0].text)) == len(SISTEMAS)


def test_tool_retorna_erro_para_excecao_inesperada(monkeypatch):
    def falhar(nome, arguments):
        raise RuntimeError("falha sintética")

    monkeypatch.setattr(_mcp, "_executar", falhar)
    result = _resultado_tool("terminologia_lookup", {})

    assert result.model_dump(by_alias=True)["isError"]
    assert result.content[0].text == "falha sintética"


def test_tools_aceitam_todos_os_sistemas():
    nomes = [item.nome for item in SISTEMAS]
    assert {"cnes", "ans-operadora", "tiss-38"} <= set(nomes)
    assert all(
        tool.model_dump(by_alias=True)["inputSchema"]["properties"]["sistema"]["enum"] == nomes
        for tool in TOOLS[:4]
    )
