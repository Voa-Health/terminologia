<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Voa-Health/tiss/main/.github/images/logo-dark.svg">
    <img alt="Voa Health" src="https://raw.githubusercontent.com/Voa-Health/tiss/main/.github/images/logo-light.svg" width="220">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/Voa-Health/terminologia/actions/workflows/ci.yml"><img src="https://github.com/Voa-Health/terminologia/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/terminologia/"><img src="https://img.shields.io/pypi/v/terminologia" alt="PyPI"></a>
  <a href="https://pypi.org/project/terminologia/"><img src="https://img.shields.io/pypi/pyversions/terminologia" alt="Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/pypi/l/terminologia" alt="Licença"></a>
  <a href="https://registry.modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP-registry-blue" alt="MCP"></a>
</p>

<p align="center">
  <a href="https://docs.voa.health/integracao/terminologia">Documentação</a> ·
  <a href="https://github.com/Voa-Health/tiss">tiss</a>
</p>

<!-- mcp-name: health.voa/terminologia -->

# terminologia

Cliente Python e ferramentas MCP para consultar CID-10, CIAP-2, TUSS, SIGTAP,
ANVISA, CBO, LOINC, UCUM e outros sistemas de terminologia em FHIR.

## Início rápido

```sh
pip install terminologia
```

Crie uma chave de produto da organização em
<https://tiss-api.voa.health/org> e configure:

```sh
export TERMINOLOGIA_KEY=sk_voa_...
```

Chaves `sk_tiss_` existentes também podem ser usadas quando possuem o escopo
`terminology:read`.

```python
import terminologia

resultado = terminologia.cid10.buscar("dor torácica")
for conceito in resultado:
    print(conceito.coding())

consulta = terminologia.tuss.lookup("10101012")
if consulta:
    print(consulta.display)
```

## CLI

| Comando | Uso |
|---|---|
| `terminologia buscar <sistema> <texto> [-n N]` | Buscar conceitos |
| `terminologia lookup <sistema> <código>` | Consultar um código |
| `terminologia validar <sistema> <código>` | Validar um código |
| `terminologia traduzir <sistema> <código> [--para SISTEMA]` | Traduzir um código |
| `terminologia sistemas` | Listar os sistemas |
| `terminologia mcp` | Iniciar o servidor MCP local |

Use `--json` nos comandos, exceto `mcp`, para receber JSON. O código de saída
é `0` para sucesso, `1` quando não há resultado ou o código é inválido e `2`
para erros de uso, chave, acesso, cota, rede ou servidor.

## Conectar agentes

Claude Code:

```sh
claude mcp add terminologia -e TERMINOLOGIA_KEY=sk_voa_... -- \
  uvx --from "terminologia[mcp]" terminologia mcp
```

Codex (`~/.codex/config.toml`):

```toml
[mcp_servers.terminologia]
command = "uvx"
args = ["--from", "terminologia[mcp]", "terminologia", "mcp"]

[mcp_servers.terminologia.env]
TERMINOLOGIA_KEY = "sk_voa_..."
```

Cursor (`mcp.json`):

```json
{
  "mcpServers": {
    "terminologia": {
      "command": "uvx",
      "args": ["--from", "terminologia[mcp]", "terminologia", "mcp"],
      "env": {
        "TERMINOLOGIA_KEY": "sk_voa_..."
      }
    }
  }
}
```

## Sistemas

| Nome | Canônico |
|---|---|
| `cid10` | `http://hl7.org/fhir/sid/icd-10` |
| `ciap2` | `http://hl7.org/fhir/sid/icpc-2` |
| `tuss` | `https://voa.health/fhir/CodeSystem/tuss` |
| `tuss-diarias` | `https://voa.health/fhir/CodeSystem/tuss-diarias-taxas-gases-medicinais` |
| `tuss-materiais` | `https://voa.health/fhir/CodeSystem/tuss-materiais-opme` |
| `tuss-medicamentos` | `https://voa.health/fhir/CodeSystem/tuss-medicamentos` |
| `sigtap` | `https://voa.health/fhir/CodeSystem/sigtap` |
| `anvisa` | `urn:voa:anvisa:registro` |
| `cbo` | `https://voa.health/fhir/CodeSystem/cbo` |
| `loinc` | `http://loinc.org` |
| `ucum` | `http://unitsofmeasure.org` |
| `tiss-50` | `https://voa.health/fhir/CodeSystem/tiss-tipo-atendimento` |
| `tiss-52` | `https://voa.health/fhir/CodeSystem/tiss-tipo-consulta` |
| `tiss-60` | `https://voa.health/fhir/CodeSystem/tiss-unidade-medida` |
| `tiss-76` | `https://voa.health/fhir/CodeSystem/tiss-regime-atendimento` |
| `voa-categoria` | `https://voa.health/fhir/CodeSystem/voa-categoria-servico` |

A allowlist de licença é definida pelo servidor.

## Atribuição

- CIAP-2 (ICPC-2) © WONCA International Classification Committee. Cite a
  WONCA ao exibir códigos CIAP-2.
- This material contains content from LOINC® (http://loinc.org). LOINC is
  copyright © Regenstrief Institute, Inc. and the LOINC Committee and is
  available at no cost under the license at http://loinc.org/license.

## Erros

| Exceção | Significado |
|---|---|
| `ChaveInvalidaError` | Chave ausente ou inválida |
| `AcessoNegadoError` | A chave não tem acesso ao sistema |
| `CotaExcedidaError` | Cota excedida; consulte `retry_after` |
| `RedeError` | Falha de conexão |
| `TempoEsgotadoError` | Tempo limite excedido |
| `ServidorError` | Erro retornado pelo serviço |

## terminologia ou tiss.tuss?

`tiss.tuss` consulta a tabela TUSS offline embutida no pacote `tiss`.
`terminologia` é o cliente online da terminologia servida pela Voa, cobre todos
os sistemas e valida na versão publicada. Requer chave e está sujeito à cota
da organização.

## Licença

Apache-2.0. Consulte [LICENSE](LICENSE).
