# Registro de alterações

## 0.2.0

- O endpoint padrão passa a ser `https://terminologia.voa.health/api/v2/terminology/fhir`.
  O endereço anterior deixa de responder; quem fixou `TERMINOLOGIA_URL` ou `base_url`
  precisa trocar para o novo.
- `TerminologiaError.codigo` traz o `error_code` das recusas de credencial
  (ex.: `invalid_credential`, `credential_not_supported`).

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
