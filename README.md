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

Cliente Python e ferramentas MCP para consultar CID-10, CIAP-2, TUSS, TISS,
SIGTAP, CNES, ANVISA, CBO, LOINC, UCUM e outros sistemas de terminologia em FHIR.

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

O endpoint padrão é `https://terminologia.voa.health/api/v2/terminology/fhir`. O argumento
`base_url` do cliente tem precedência; sem ele, defina `TERMINOLOGIA_URL` para
usar outro endpoint.

O cliente segue redirects apenas na mesma origem (esquema, host e porta).
Qualquer mudança gera `TerminologiaError` antes do envio da requisição redirecionada.

O transporte usa um opener próprio criado ao importar o pacote. Defina
`HTTP_PROXY`, `HTTPS_PROXY` e `NO_PROXY` antes do import; openers globais de
`urllib.request.install_opener()` não são usados.

```python
import terminologia

resultado = terminologia.cid10.buscar("dor torácica")
for conceito in resultado:
    print(conceito.coding())

consulta = terminologia.tuss.lookup("10101012")
if consulta:
    print(consulta.display)

for estabelecimento in terminologia.sistema("cnes").buscar("hospital das clínicas", n=5):
    print(estabelecimento.code, estabelecimento.display)
```

## CLI

| Comando | Uso |
|---|---|
| `terminologia buscar <sistema> <texto> [-n N]` | Buscar conceitos |
| `terminologia lookup <sistema> <código>` | Consultar um código |
| `terminologia validar <sistema> <código>` | Validar um código |
| `terminologia traduzir <sistema> <código> --para SISTEMA` | Traduzir um código |
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
| `sigtap-grupo` | `https://voa.health/fhir/CodeSystem/sigtap-grupo` |
| `sigtap-sub-grupo` | `https://voa.health/fhir/CodeSystem/sigtap-sub-grupo` |
| `sigtap-servico` | `https://voa.health/fhir/CodeSystem/sigtap-servico` |
| `sigtap-registro` | `https://voa.health/fhir/CodeSystem/sigtap-registro` |
| `sigtap-financiamento` | `https://voa.health/fhir/CodeSystem/sigtap-financiamento` |
| `sigtap-modalidade` | `https://voa.health/fhir/CodeSystem/sigtap-modalidade` |
| `anvisa` | `urn:voa:anvisa:registro` |
| `cbo` | `https://voa.health/fhir/CodeSystem/cbo` |
| `cfm-especialidade` | `https://voa.health/fhir/CodeSystem/cfm-especialidade` |
| `rol-ans` | `https://voa.health/fhir/CodeSystem/rol-ans` |
| `dut` | `https://voa.health/fhir/CodeSystem/rol-diretrizes-dut` |
| `cnes` | `urn:voa:br:cnes` |
| `ans-operadora` | `urn:voa:br:ans-registro` |
| `loinc` | `http://loinc.org` |
| `ucum` | `http://unitsofmeasure.org` |
| `voa-categoria` | `https://voa.health/fhir/CodeSystem/voa-categoria-servico` |

<details>
<summary>Tabelas de domínio TISS (59)</summary>

Também acessíveis por `terminologia.tiss_dominio(<número>)`.

| Nome | Canônico |
|---|---|
| `tiss-23` | `https://voa.health/fhir/CodeSystem/tiss-carater-atendimento` |
| `tiss-25` | `https://voa.health/fhir/CodeSystem/tiss-codigo-despesa` |
| `tiss-26` | `https://voa.health/fhir/CodeSystem/tiss-conselho-profissional` |
| `tiss-27` | `https://voa.health/fhir/CodeSystem/tiss-debitos-creditos` |
| `tiss-28` | `https://voa.health/fhir/CodeSystem/tiss-dentes` |
| `tiss-29` | `https://voa.health/fhir/CodeSystem/tiss-diagnostico-imagem` |
| `tiss-30` | `https://voa.health/fhir/CodeSystem/tiss-escala-capacidade-funcional` |
| `tiss-31` | `https://voa.health/fhir/CodeSystem/tiss-estadiamento-tumor` |
| `tiss-32` | `https://voa.health/fhir/CodeSystem/tiss-faces-dente` |
| `tiss-33` | `https://voa.health/fhir/CodeSystem/tiss-finalidade-tratamento` |
| `tiss-34` | `https://voa.health/fhir/CodeSystem/tiss-forma-pagamento` |
| `tiss-35` | `https://voa.health/fhir/CodeSystem/tiss-grau-participacao` |
| `tiss-36` | `https://voa.health/fhir/CodeSystem/tiss-indicador-acidente` |
| `tiss-37` | `https://voa.health/fhir/CodeSystem/tiss-indicador-debito-credito` |
| `tiss-38` | `https://voa.health/fhir/CodeSystem/tiss-mensagens` |
| `tiss-39` | `https://voa.health/fhir/CodeSystem/tiss-motivo-encerramento` |
| `tiss-40` | `https://voa.health/fhir/CodeSystem/tiss-origem-guia` |
| `tiss-41` | `https://voa.health/fhir/CodeSystem/tiss-regime-internacao` |
| `tiss-42` | `https://voa.health/fhir/CodeSystem/tiss-regioes-boca` |
| `tiss-43` | `https://voa.health/fhir/CodeSystem/tiss-sexo` |
| `tiss-44` | `https://voa.health/fhir/CodeSystem/tiss-situacao-inicial-dente` |
| `tiss-45` | `https://voa.health/fhir/CodeSystem/tiss-status-solicitacao` |
| `tiss-46` | `https://voa.health/fhir/CodeSystem/tiss-status-cancelamento` |
| `tiss-47` | `https://voa.health/fhir/CodeSystem/tiss-status-protocolo` |
| `tiss-48` | `https://voa.health/fhir/CodeSystem/tiss-tecnica-utilizada` |
| `tiss-49` | `https://voa.health/fhir/CodeSystem/tiss-tipo-acomodacao` |
| `tiss-50` | `https://voa.health/fhir/CodeSystem/tiss-tipo-atendimento` |
| `tiss-51` | `https://voa.health/fhir/CodeSystem/tiss-tipo-atendimento-odontologia` |
| `tiss-52` | `https://voa.health/fhir/CodeSystem/tiss-tipo-consulta` |
| `tiss-53` | `https://voa.health/fhir/CodeSystem/tiss-tipo-demonstrativo` |
| `tiss-54` | `https://voa.health/fhir/CodeSystem/tiss-tipo-guia` |
| `tiss-55` | `https://voa.health/fhir/CodeSystem/tiss-tipo-faturamento` |
| `tiss-56` | `https://voa.health/fhir/CodeSystem/tiss-natureza-guia` |
| `tiss-57` | `https://voa.health/fhir/CodeSystem/tiss-tipo-internacao` |
| `tiss-58` | `https://voa.health/fhir/CodeSystem/tiss-tipo-quimioterapia` |
| `tiss-59` | `https://voa.health/fhir/CodeSystem/tiss-unidade-federacao` |
| `tiss-60` | `https://voa.health/fhir/CodeSystem/tiss-unidade-medida` |
| `tiss-61` | `https://voa.health/fhir/CodeSystem/tiss-via-acesso` |
| `tiss-62` | `https://voa.health/fhir/CodeSystem/tiss-via-administracao` |
| `tiss-63` | `https://voa.health/fhir/CodeSystem/tiss-grupos-procedimentos-ans` |
| `tiss-65` | `https://voa.health/fhir/CodeSystem/tiss-metastases` |
| `tiss-66` | `https://voa.health/fhir/CodeSystem/tiss-nodulo` |
| `tiss-67` | `https://voa.health/fhir/CodeSystem/tiss-tumor` |
| `tiss-68` | `https://voa.health/fhir/CodeSystem/tiss-categoria-despesa` |
| `tiss-69` | `https://voa.health/fhir/CodeSystem/tiss-versao-componente-comunicacao` |
| `tiss-70` | `https://voa.health/fhir/CodeSystem/tiss-forma-envio` |
| `tiss-71` | `https://voa.health/fhir/CodeSystem/tiss-tipo-atendimento-operadora-intermediaria` |
| `tiss-72` | `https://voa.health/fhir/CodeSystem/tiss-tipo-identificacao-beneficiario` |
| `tiss-73` | `https://voa.health/fhir/CodeSystem/tiss-etapas-autorizacao` |
| `tiss-74` | `https://voa.health/fhir/CodeSystem/tiss-motivos-ausencia-codigo-validacao` |
| `tiss-75` | `https://voa.health/fhir/CodeSystem/tiss-cobertura-especial` |
| `tiss-76` | `https://voa.health/fhir/CodeSystem/tiss-regime-atendimento` |
| `tiss-77` | `https://voa.health/fhir/CodeSystem/tiss-saude-ocupacional` |
| `tiss-78` | `https://voa.health/fhir/CodeSystem/tiss-tipo-pagamento` |
| `tiss-79` | `https://voa.health/fhir/CodeSystem/tiss-modelos-remuneracao` |
| `tiss-80` | `https://voa.health/fhir/CodeSystem/tiss-formato-documento` |
| `tiss-81` | `https://voa.health/fhir/CodeSystem/tiss-tipo-documento` |
| `tiss-82` | `https://voa.health/fhir/CodeSystem/tiss-centro-consumo` |
| `tiss-87` | `https://voa.health/fhir/CodeSystem/tiss-terminologias-unificadas` |

</details>

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
