# Registro de alterações

## Não lançado

- O cliente segue redirects apenas para a mesma origem (esquema, host e porta), preservando a chave de acesso nesse destino.
- Redirects para outra origem são recusados antes do envio, sem expor a URL de destino na mensagem.

## 0.1.1

- O servidor MCP local passa a funcionar com o SDK `mcp` 2.x, mantendo suporte ao 1.x.
- Falhas inesperadas numa tool voltam como resultado com `isError`.

## 0.1.0

- Primeira versão estável do cliente, da CLI e do servidor MCP.

## 0.1.0a2

- Atualiza o endpoint FHIR e permite configurar `TERMINOLOGIA_URL`.
- Normaliza códigos CID-10 e exige `--para` na CLI de tradução.

## 0.1.0a1

- Cliente Python para consulta de terminologias FHIR.
