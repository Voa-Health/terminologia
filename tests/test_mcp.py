from __future__ import annotations

import json

from terminologia import SISTEMAS
from terminologia._mcp import TOOLS, _resultado_tool


def test_tools_mcp_tem_os_nomes_exatos():
    assert [tool.name for tool in TOOLS] == [
        "terminologia_buscar",
        "terminologia_lookup",
        "terminologia_validar",
        "terminologia_traduzir",
        "terminologia_sistemas",
    ]
    assert all(tool.inputSchema["properties"].get("sistema", {}).get("enum") for tool in TOOLS[:4])


def test_tool_mcp_retorna_erro_com_link_de_chaves(monkeypatch):
    monkeypatch.delenv("TERMINOLOGIA_KEY", raising=False)
    result = _resultado_tool(
        "terminologia_lookup",
        {"sistema": "tuss", "codigo": "10101012"},
    )
    assert result.isError
    assert "https://tiss-api.voa.health/org" in result.content[0].text


def test_tool_sistemas_responde_com_json():
    result = _resultado_tool("terminologia_sistemas", {})
    assert not result.isError
    assert len(json.loads(result.content[0].text)) == len(SISTEMAS)


def test_tool_buscar_omite_sistemas_sem_busca():
    enums = {tool.name: tool.inputSchema["properties"]["sistema"]["enum"] for tool in TOOLS[:4]}
    assert {"cnes", "ans-operadora"}.isdisjoint(enums["terminologia_buscar"])
    assert "tiss-38" in enums["terminologia_buscar"]
    assert {"cnes", "ans-operadora", "tiss-38"} <= set(enums["terminologia_lookup"])
    result = _resultado_tool("terminologia_buscar", {"sistema": "cnes", "texto": "hospital"})
    assert result.isError
    assert "busca textual" in result.content[0].text
