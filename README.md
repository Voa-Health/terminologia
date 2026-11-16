<div align="center">
  <a href="https://docs.voa.health/integracao/terminologia">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Voa-Health/tiss/main/.github/images/logo-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Voa-Health/tiss/main/.github/images/logo-light.svg">
      <img alt="Voa" src="https://raw.githubusercontent.com/Voa-Health/tiss/main/.github/images/logo-light.svg" width="160">
    </picture>
  </a>
</div>

<div align="center">
  <h3>Terminologias de saúde em FHIR, para pessoas e agentes de IA.</h3>
</div>

<div align="center">
  <a href="https://github.com/Voa-Health/terminologia/actions/workflows/ci.yml"><img src="https://github.com/Voa-Health/terminologia/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI"></a>
  <a href="https://pypi.org/project/terminologia/"><img src="https://img.shields.io/pypi/v/terminologia?label=PyPI" alt="Versão no PyPI"></a>
  <a href="https://pypi.org/project/terminologia/"><img src="https://img.shields.io/pypi/pyversions/terminologia" alt="Versões do Python"></a>
  <a href="https://github.com/Voa-Health/terminologia/blob/main/LICENSE"><img src="https://img.shields.io/badge/licen%C3%A7a-Apache--2.0-blue" alt="Licença Apache-2.0"></a>
  <a href="https://registry.modelcontextprotocol.io/v0/servers?search=health.voa/terminologia"><img src="https://img.shields.io/badge/MCP-health.voa%2Fterminologia-7c3aed" alt="MCP Registry"></a>
</div>

<div align="center">
  <a href="https://docs.voa.health/integracao/terminologia">Documentação</a> ·
  <a href="https://tiss-api.voa.health/org">Chaves</a> ·
  <a href="https://registry.modelcontextprotocol.io/v0/servers?search=health.voa/terminologia">MCP Registry</a> ·
  <a href="https://github.com/Voa-Health/tiss">tiss</a>
</div>

<br>

Busque, consulte, valide e traduza códigos de CID-10, CIAP-2, TUSS, tabelas de
domínio TISS, SIGTAP, CNES, ANVISA, CBO, LOINC, UCUM e outros sistemas, sempre
como `Coding` FHIR: um cliente Python sem dependências, uma CLI e um MCP local
para o seu agente de IA.

<!-- mcp-name: health.voa/terminologia -->

> [!TIP]
> Usa Claude Code, Codex ou Cursor? Conecte o MCP e peça em português, por
> exemplo "qual o CID-10 de dor torácica?". Veja
> [Conectar agentes](#conectar-agentes).

## Início rápido

```sh
pip install terminologia
```

Crie a chave `sk_voa_` da organização no
[painel da organização](https://tiss-api.voa.health/org) e configure:

```sh
export TERMINOLOGIA_KEY=sk_voa_...
```

```python
import terminologia

for conceito in terminologia.cid10.buscar("dor torácica", n=3):
    print(conceito.coding())

validacao = terminologia.cid10.validar("R07.4")
print(validacao.valido, validacao.conceito)

consulta = terminologia.tuss.lookup("10101012")
if consulta:
    print(consulta.display)
```

Cada conceito traz `system`, `code`, `display` e `version`, prontos para um
`Coding` FHIR. Requer Python 3.10+.

## CLI

Execute sem instalar com `uvx terminologia buscar cid10 "dor torácica"`.

| Comando | Uso |
| --- | --- |
| `terminologia buscar <sistema> <texto> [-n N]` | Busca conceitos pelo texto. |
| `terminologia lookup <sistema> <código>` | Consulta um código. |
| `terminologia validar <sistema> <código>` | Valida um código. |
| `terminologia traduzir <sistema> <código> --para SISTEMA` | Traduz um código para outro sistema. |
| `terminologia sistemas` | Lista os sistemas. |
| `terminologia mcp` | Inicia o MCP local em stdio; requer `terminologia[mcp]`. |

Use `--json` nos comandos, exceto `mcp`, para receber JSON. Os códigos de saída
são `0` para sucesso, `1` quando não há resultado ou o código é inválido e `2`
para uso inválido ou erros de chave, acesso, cota, rede ou servidor.

## Como funciona

Você não precisa decorar códigos nem montar requisições FHIR à mão:

1. **Busque** o conceito pelo texto com `buscar`.
2. **Confira** o display oficial com `lookup`.
3. **Valide** o código com `validar` antes de gravá-lo em um recurso FHIR.
4. **Use** o `system` devolvido como `Coding.system`.

Cada busca informa em `degradado` quando a resposta é parcial; isso não
significa que o código não existe. CID-10 aceita o código com ou sem ponto.

## Conectar agentes

O MCP local roda em stdio e expõe `terminologia_buscar`, `terminologia_lookup`,
`terminologia_validar`, `terminologia_traduzir` e `terminologia_sistemas`:

```sh
claude mcp add terminologia -e TERMINOLOGIA_KEY=sk_voa_... -- \
  uvx --from "terminologia[mcp]" terminologia mcp
```

Agentes encontram instruções em
[AGENTS.md](https://github.com/Voa-Health/terminologia/blob/main/AGENTS.md) e em
[llms.txt](https://github.com/Voa-Health/terminologia/blob/main/llms.txt).

### Codex e Cursor

<details>
<summary>Ver detalhes</summary>

No Codex, adicione a `~/.codex/config.toml`:

```toml
[mcp_servers.terminologia]
command = "uvx"
args = ["--from", "terminologia[mcp]", "terminologia", "mcp"]

[mcp_servers.terminologia.env]
TERMINOLOGIA_KEY = "sk_voa_..."
```

No Cursor, adicione ao `mcp.json`:

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

</details>

## Configuração

<details>
<summary>Ver detalhes</summary>

| Variável | Uso |
| --- | --- |
| `TERMINOLOGIA_KEY` | Chave `sk_voa_` da organização; chaves `sk_tiss_` com o escopo `terminology:read` também valem. |
| `TERMINOLOGIA_URL` | Endpoint FHIR; o padrão é `https://terminologia.voa.health/api/v2/terminology/fhir`. |

Os argumentos `api_key` e `base_url` de `Terminologia` têm precedência sobre as
variáveis. Cada consulta entra na cota da organização; ao excedê-la, o cliente
levanta `CotaExcedidaError` com `retry_after`.

O cliente segue redirects apenas na mesma origem (esquema, host e porta) e
levanta `TerminologiaError` antes de enviar a chave a outra origem.

O transporte usa um opener próprio criado ao importar o pacote. Defina
`HTTP_PROXY`, `HTTPS_PROXY` e `NO_PROXY` antes do import; openers globais de
`urllib.request.install_opener()` não são usados.

</details>

## Sistemas

| Nome | Sistema | Canônico |
| --- | --- | --- |
| `cid10` | CID-10 — variante brasileira | `http://hl7.org/fhir/sid/icd-10` |
| `ciap2` | CIAP-2 — Classificação Internacional de Atenção Primária | `http://hl7.org/fhir/sid/icpc-2` |
| `tuss` | TUSS Tabela 22 — procedimentos | `https://voa.health/fhir/CodeSystem/tuss` |
| `tuss-diarias` | TUSS Tabela 18 — diárias, taxas e gases medicinais | `https://voa.health/fhir/CodeSystem/tuss-diarias-taxas-gases-medicinais` |
| `tuss-materiais` | TUSS Tabela 19 — materiais e OPME | `https://voa.health/fhir/CodeSystem/tuss-materiais-opme` |
| `tuss-medicamentos` | TUSS Tabela 20 — medicamentos | `https://voa.health/fhir/CodeSystem/tuss-medicamentos` |
| `sigtap` | SIGTAP — procedimentos do SUS | `https://voa.health/fhir/CodeSystem/sigtap` |
| `sigtap-grupo` | SIGTAP — grupos de procedimento | `https://voa.health/fhir/CodeSystem/sigtap-grupo` |
| `sigtap-sub-grupo` | SIGTAP — subgrupos de procedimento | `https://voa.health/fhir/CodeSystem/sigtap-sub-grupo` |
| `sigtap-servico` | SIGTAP — serviços especializados | `https://voa.health/fhir/CodeSystem/sigtap-servico` |
| `sigtap-registro` | SIGTAP — instrumentos de registro | `https://voa.health/fhir/CodeSystem/sigtap-registro` |
| `sigtap-financiamento` | SIGTAP — tipos de financiamento | `https://voa.health/fhir/CodeSystem/sigtap-financiamento` |
| `sigtap-modalidade` | SIGTAP — modalidades de atendimento | `https://voa.health/fhir/CodeSystem/sigtap-modalidade` |
| `anvisa` | ANVISA — produtos e apresentações | `urn:voa:anvisa:registro` |
| `cbo` | CBO 2002 — ocupações | `https://voa.health/fhir/CodeSystem/cbo` |
| `cfm-especialidade` | CFM — especialidades médicas | `https://voa.health/fhir/CodeSystem/cfm-especialidade` |
| `rol-ans` | Rol de Procedimentos e Eventos em Saúde da ANS | `https://voa.health/fhir/CodeSystem/rol-ans` |
| `dut` | Rol da ANS — diretrizes de utilização (DUT) | `https://voa.health/fhir/CodeSystem/rol-diretrizes-dut` |
| `cnes` | CNES — estabelecimentos de saúde | `urn:voa:br:cnes` |
| `ans-operadora` | ANS — operadoras ativas | `urn:voa:br:ans-registro` |
| `loinc` | LOINC — exames e observações | `http://loinc.org` |
| `ucum` | UCUM — unidades de medida | `http://unitsofmeasure.org` |
| `voa-categoria` | Voa — categoria de serviço | `https://voa.health/fhir/CodeSystem/voa-categoria-servico` |

<details>
<summary>Tabelas de domínio TISS (59)</summary>

Também acessíveis por `terminologia.tiss_dominio(<número>)`.

| Nome | Tabela | Canônico |
| --- | --- | --- |
| `tiss-23` | TISS Tabela 23 — caráter do atendimento | `https://voa.health/fhir/CodeSystem/tiss-carater-atendimento` |
| `tiss-25` | TISS Tabela 25 — código da despesa | `https://voa.health/fhir/CodeSystem/tiss-codigo-despesa` |
| `tiss-26` | TISS Tabela 26 — conselho profissional | `https://voa.health/fhir/CodeSystem/tiss-conselho-profissional` |
| `tiss-27` | TISS Tabela 27 — débitos e créditos | `https://voa.health/fhir/CodeSystem/tiss-debitos-creditos` |
| `tiss-28` | TISS Tabela 28 — dentes | `https://voa.health/fhir/CodeSystem/tiss-dentes` |
| `tiss-29` | TISS Tabela 29 — diagnóstico por imagem | `https://voa.health/fhir/CodeSystem/tiss-diagnostico-imagem` |
| `tiss-30` | TISS Tabela 30 — escala de capacidade funcional (ECOG - escala de Zubrod) | `https://voa.health/fhir/CodeSystem/tiss-escala-capacidade-funcional` |
| `tiss-31` | TISS Tabela 31 — estadiamento do tumor | `https://voa.health/fhir/CodeSystem/tiss-estadiamento-tumor` |
| `tiss-32` | TISS Tabela 32 — faces do dente | `https://voa.health/fhir/CodeSystem/tiss-faces-dente` |
| `tiss-33` | TISS Tabela 33 — finalidade do tratamento | `https://voa.health/fhir/CodeSystem/tiss-finalidade-tratamento` |
| `tiss-34` | TISS Tabela 34 — forma de pagamento | `https://voa.health/fhir/CodeSystem/tiss-forma-pagamento` |
| `tiss-35` | TISS Tabela 35 — grau de participação | `https://voa.health/fhir/CodeSystem/tiss-grau-participacao` |
| `tiss-36` | TISS Tabela 36 — indicador de acidente | `https://voa.health/fhir/CodeSystem/tiss-indicador-acidente` |
| `tiss-37` | TISS Tabela 37 — indicador de débito ou crédito | `https://voa.health/fhir/CodeSystem/tiss-indicador-debito-credito` |
| `tiss-38` | TISS Tabela 38 — mensagens (glosas, negativas e outras) | `https://voa.health/fhir/CodeSystem/tiss-mensagens` |
| `tiss-39` | TISS Tabela 39 — motivo de encerramento | `https://voa.health/fhir/CodeSystem/tiss-motivo-encerramento` |
| `tiss-40` | TISS Tabela 40 — origem da guia | `https://voa.health/fhir/CodeSystem/tiss-origem-guia` |
| `tiss-41` | TISS Tabela 41 — regime de internação | `https://voa.health/fhir/CodeSystem/tiss-regime-internacao` |
| `tiss-42` | TISS Tabela 42 — regiões da boca | `https://voa.health/fhir/CodeSystem/tiss-regioes-boca` |
| `tiss-43` | TISS Tabela 43 — sexo | `https://voa.health/fhir/CodeSystem/tiss-sexo` |
| `tiss-44` | TISS Tabela 44 — situação inicial do dente | `https://voa.health/fhir/CodeSystem/tiss-situacao-inicial-dente` |
| `tiss-45` | TISS Tabela 45 — status da solicitação | `https://voa.health/fhir/CodeSystem/tiss-status-solicitacao` |
| `tiss-46` | TISS Tabela 46 — status do cancelamento | `https://voa.health/fhir/CodeSystem/tiss-status-cancelamento` |
| `tiss-47` | TISS Tabela 47 — status do protocolo | `https://voa.health/fhir/CodeSystem/tiss-status-protocolo` |
| `tiss-48` | TISS Tabela 48 — técnica utilizada | `https://voa.health/fhir/CodeSystem/tiss-tecnica-utilizada` |
| `tiss-49` | TISS Tabela 49 — tipo de acomodação | `https://voa.health/fhir/CodeSystem/tiss-tipo-acomodacao` |
| `tiss-50` | TISS Tabela 50 — tipo de atendimento | `https://voa.health/fhir/CodeSystem/tiss-tipo-atendimento` |
| `tiss-51` | TISS Tabela 51 — tipo de atendimento em odontologia | `https://voa.health/fhir/CodeSystem/tiss-tipo-atendimento-odontologia` |
| `tiss-52` | TISS Tabela 52 — tipo de consulta | `https://voa.health/fhir/CodeSystem/tiss-tipo-consulta` |
| `tiss-53` | TISS Tabela 53 — tipo de demonstrativo | `https://voa.health/fhir/CodeSystem/tiss-tipo-demonstrativo` |
| `tiss-54` | TISS Tabela 54 — tipo de guia | `https://voa.health/fhir/CodeSystem/tiss-tipo-guia` |
| `tiss-55` | TISS Tabela 55 — tipo de faturamento | `https://voa.health/fhir/CodeSystem/tiss-tipo-faturamento` |
| `tiss-56` | TISS Tabela 56 — natureza da guia | `https://voa.health/fhir/CodeSystem/tiss-natureza-guia` |
| `tiss-57` | TISS Tabela 57 — tipo de internação | `https://voa.health/fhir/CodeSystem/tiss-tipo-internacao` |
| `tiss-58` | TISS Tabela 58 — tipo de quimioterapia | `https://voa.health/fhir/CodeSystem/tiss-tipo-quimioterapia` |
| `tiss-59` | TISS Tabela 59 — unidade da federação | `https://voa.health/fhir/CodeSystem/tiss-unidade-federacao` |
| `tiss-60` | TISS Tabela 60 — unidade de medida | `https://voa.health/fhir/CodeSystem/tiss-unidade-medida` |
| `tiss-61` | TISS Tabela 61 — via de acesso | `https://voa.health/fhir/CodeSystem/tiss-via-acesso` |
| `tiss-62` | TISS Tabela 62 — via de administração | `https://voa.health/fhir/CodeSystem/tiss-via-administracao` |
| `tiss-63` | TISS Tabela 63 — grupos de procedimentos e itens assistenciais para envio à ANS | `https://voa.health/fhir/CodeSystem/tiss-grupos-procedimentos-ans` |
| `tiss-65` | TISS Tabela 65 — metástases | `https://voa.health/fhir/CodeSystem/tiss-metastases` |
| `tiss-66` | TISS Tabela 66 — nódulo | `https://voa.health/fhir/CodeSystem/tiss-nodulo` |
| `tiss-67` | TISS Tabela 67 — tumor | `https://voa.health/fhir/CodeSystem/tiss-tumor` |
| `tiss-68` | TISS Tabela 68 — categoria de despesa | `https://voa.health/fhir/CodeSystem/tiss-categoria-despesa` |
| `tiss-69` | TISS Tabela 69 — versão do componente de comunicação do padrão | `https://voa.health/fhir/CodeSystem/tiss-versao-componente-comunicacao` |
| `tiss-70` | TISS Tabela 70 — forma de envio do padrão | `https://voa.health/fhir/CodeSystem/tiss-forma-envio` |
| `tiss-71` | TISS Tabela 71 — tipo de atendimento por operadora intermediária | `https://voa.health/fhir/CodeSystem/tiss-tipo-atendimento-operadora-intermediaria` |
| `tiss-72` | TISS Tabela 72 — tipo de identificação do beneficiário | `https://voa.health/fhir/CodeSystem/tiss-tipo-identificacao-beneficiario` |
| `tiss-73` | TISS Tabela 73 — etapas de autorização | `https://voa.health/fhir/CodeSystem/tiss-etapas-autorizacao` |
| `tiss-74` | TISS Tabela 74 — motivos de ausência do código de validação | `https://voa.health/fhir/CodeSystem/tiss-motivos-ausencia-codigo-validacao` |
| `tiss-75` | TISS Tabela 75 — cobertura especial | `https://voa.health/fhir/CodeSystem/tiss-cobertura-especial` |
| `tiss-76` | TISS Tabela 76 — regime de atendimento | `https://voa.health/fhir/CodeSystem/tiss-regime-atendimento` |
| `tiss-77` | TISS Tabela 77 — saúde ocupacional | `https://voa.health/fhir/CodeSystem/tiss-saude-ocupacional` |
| `tiss-78` | TISS Tabela 78 — tipo de pagamento | `https://voa.health/fhir/CodeSystem/tiss-tipo-pagamento` |
| `tiss-79` | TISS Tabela 79 — modelos de remuneração entre operadoras e prestadores | `https://voa.health/fhir/CodeSystem/tiss-modelos-remuneracao` |
| `tiss-80` | TISS Tabela 80 — formato do documento | `https://voa.health/fhir/CodeSystem/tiss-formato-documento` |
| `tiss-81` | TISS Tabela 81 — tipo do documento | `https://voa.health/fhir/CodeSystem/tiss-tipo-documento` |
| `tiss-82` | TISS Tabela 82 — centro de consumo | `https://voa.health/fhir/CodeSystem/tiss-centro-consumo` |
| `tiss-87` | TISS Tabela 87 — relação das terminologias unificadas na saúde suplementar | `https://voa.health/fhir/CodeSystem/tiss-terminologias-unificadas` |

</details>

O servidor define quais sistemas cada chave pode consultar.

### Atribuição

- CIAP-2 (ICPC-2) © WONCA International Classification Committee. Cite a
  WONCA ao exibir códigos CIAP-2.
- This material contains content from LOINC® (http://loinc.org). LOINC is
  copyright © Regenstrief Institute, Inc. and the LOINC Committee and is
  available at no cost under the license at http://loinc.org/license.

A CLI imprime a atribuição em stderr ao consultar esses sistemas.

## Referência

### Símbolos da biblioteca

<details>
<summary>Ver detalhes</summary>

| Símbolo | Uso |
| --- | --- |
| `cid10`, `ciap2`, `tuss`, `sigtap`, `anvisa`, `cbo`, `loinc`, `ucum` | Atalhos para os sistemas mais usados. |
| `tuss.materiais` / `tuss.medicamentos` / `tuss.diarias` | Tabelas TUSS 19, 20 e 18. |
| `sistema` | Encontra um sistema pelo nome ou URL canônico. |
| `tiss_dominio` | Encontra uma tabela de domínio TISS pelo número. |
| `sistemas` / `SISTEMAS` | Lista todos os sistemas. |
| `Sistema.buscar` | Busca conceitos e retorna um `Resultado`. |
| `Sistema.lookup` | Consulta um código e retorna um `Conceito` ou `None`. |
| `Sistema.validar` | Valida um código e retorna uma `Validacao`. |
| `Terminologia` | Cliente com chave, endpoint e `timeout` próprios. |
| `Terminologia.sistema` | Associa um sistema a esse cliente. |
| `Terminologia.expand` / `lookup` / `validate_code` / `translate` / `subsumes` | Operações FHIR `$expand`, `$lookup`, `$validate-code`, `$translate` e `$subsumes`. |
| `Conceito.coding` | Retorna o conceito como `Coding` FHIR. |

```python
from terminologia import Terminologia

cliente = Terminologia(api_key="sk_voa_...", timeout=30)
for estabelecimento in cliente.sistema("cnes").buscar("hospital das clínicas", n=5):
    print(estabelecimento.code, estabelecimento.display)
```

</details>

### Erros

<details>
<summary>Ver detalhes</summary>

Todas as exceções herdam de `TerminologiaError`, que traz `status`, `codigo` e
`mensagem`.

| Exceção | Significado |
| --- | --- |
| `ChaveInvalidaError` | Chave ausente ou inválida (`401`). |
| `AcessoNegadoError` | A chave não tem acesso ao sistema (`403`). |
| `CotaExcedidaError` | Cota excedida (`429`); consulte `retry_after`. |
| `RedeError` | Falha de conexão. |
| `TempoEsgotadoError` | Tempo limite excedido. |
| `ServidorError` | Erro retornado pelo serviço. |

</details>

## terminologia ou tiss.tuss?

`tiss.tuss` consulta offline a tabela TUSS embutida no pacote
[tiss](https://github.com/Voa-Health/tiss). `terminologia` consulta online
todos os sistemas acima na versão publicada; requer chave e entra na cota da
organização.

## Mais

- [Changelog](https://github.com/Voa-Health/terminologia/blob/main/CHANGELOG.md) · [Contribuição](https://github.com/Voa-Health/terminologia/blob/main/CONTRIBUTING.md) ·
  [Código de conduta](https://github.com/Voa-Health/terminologia/blob/main/CODE_OF_CONDUCT.md) · [Segurança](https://github.com/Voa-Health/terminologia/blob/main/SECURITY.md)
- [Licença Apache-2.0](https://github.com/Voa-Health/terminologia/blob/main/LICENSE)
