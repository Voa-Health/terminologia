from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from terminologia import __version__
from terminologia._mcp import TOOLS

PACKAGE = Path(__file__).resolve().parents[1] / "plugins" / "chatgpt"
CASES = json.loads((PACKAGE / "review-cases.json").read_text())["test_cases"]
TOOL_NAMES = {tool.name for tool in TOOLS}
IDENTIFIERS = (
    r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}[- .]?\d{2}(?!\d)",
    r"(?<!\d)\d{3}[ .]?\d{4}[ .]?\d{4}[ .]?\d{4}(?!\d)",
    r"(?<!\d)(?:\+?55[ .-]?)?(?:\(\d{2}\)|\d{2})[ .-]?\d{4,5}[- .]?\d{4}(?!\d)",
)


@pytest.mark.parametrize("path", ["skills/terminologia/SKILL.md", "review-cases.json"])
def test_documented_tools_match_stdio(path):
    text = (PACKAGE / path).read_text()
    assert set(re.findall(r"\bterminologia_[a-z_]+\b", text)) == TOOL_NAMES


def test_remote_mcp_contract():
    mcp_config = json.loads((PACKAGE / "mcp.json").read_text())
    assert list(mcp_config) == ["$schema", "mcpServers"]
    assert mcp_config["$schema"] == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
    servers = mcp_config["mcpServers"]
    assert servers == {
        "terminologia": {
            "type": "streamable-http",
            "url": "https://api.voa.health/mcp/terminology/",
            "extensions": {
                "com.openai": {
                    "auth": {
                        "type": "oauth",
                        "client": {"mode": "cimd"},
                        "baseScopes": ["voa:terminology:read"],
                    }
                }
            },
        }
    }
    manifest = json.loads((PACKAGE / "plugin.json").read_text())
    assert manifest["version"] == __version__
    assert manifest["name"] == "terminologia"
    assert manifest["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"


def test_openai_listing_metadata():
    manifest = json.loads((PACKAGE / "plugin.json").read_text())
    interface = manifest["extensions"]["com.openai"]["interface"]
    assert interface["developerName"] == "Voa Health"
    assert interface["category"] == "Healthcare"
    assert interface["capabilities"] == []
    assert len(interface["displayName"]) <= 30
    assert len(interface["shortDescription"]) <= 30
    assert len(interface["longDescription"]) <= 4000
    assert interface["defaultPrompt"] == [
        "Busque o código CID-10 de hipertensão essencial.",
        "Quais terminologias de saúde estão disponíveis?",
        "Busque a ocupação CBO de médico clínico.",
    ]
    assert len(interface["defaultPrompt"]) <= 3
    assert all(len(prompt) <= 128 for prompt in interface["defaultPrompt"])
    assert {
        key: interface[key]
        for key in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL")
    } == {
        "websiteURL": "https://docs.voa.health/integracao/terminologia",
        "supportURL": "https://docs.voa.health/integracao/terminologia",
        "privacyPolicyURL": "https://app.voa.health/legal/privacidade",
        "termsOfServiceURL": "https://app.voa.health/legal/termos",
    }
    assert all(
        interface[key].startswith("https://")
        for key in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL")
    )
    icon_paths = (
        "logo",
        "logoDark",
        "composerIcon",
        "composerIconDark",
    )
    assert all((PACKAGE / interface[key].removeprefix("./")).is_file() for key in icon_paths)


@pytest.mark.parametrize("group,count", [("positive", 5), ("negative", 3)])
def test_review_tool_coverage(group, count):
    assert len(CASES[group]) == count
    expected = TOOL_NAMES if group == "positive" else {""}
    assert {case["tools_triggered"] for case in CASES[group]} == expected


@pytest.mark.parametrize(
    "case",
    [
        pytest.param(case, id=f"{group}-{index}")
        for group, cases in CASES.items()
        for index, case in enumerate(cases)
    ],
)
def test_review_cases_have_no_identifiers(case):
    assert case["prompt"] and case["expected_behavior"]
    text = json.dumps(case, ensure_ascii=False)
    assert not any(re.search(pattern, text) for pattern in IDENTIFIERS)
